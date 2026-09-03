#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jacob Vider, jacobisaacvider@gmail.com
Date:   Wed Aug 26 2026
"""

"""Run reference selection, subtraction, and source detection for one UVOT HDU."""

from pathlib import Path

from detection import detect_sources
from registration import crop_bound, crop_images, find_overlap
from subtraction import subtract_images
from uvot_io.archive import (
    MAX_TARGETS,
    count_targets,
    download_reference_image,
    find_reference_image,
    has_acceptable_target_count,
)
from uvot_io.fits import (
    find_image_extension,
    get_observation_metadata,
    load_observation,
    select_longest_extension,
)
from validation import validate_transients


def process(
    observation_path: str | Path,
    obsid: int | str | None = None,
    *,
    obs_extension_name: str | None = None,
    output_dir: str | Path | None = None,
    reference_dir: str | Path | None = None,
):
    """Process one specified UVOT image extension.

    ``obs_extension_name`` is a FITS ``EXTNAME`` such as ``uu791525963I``.
    When it is omitted, the legacy first image extension (HDU 1) is used.
    """

    observation_path = Path(observation_path)
    with load_observation(observation_path) as obs_hdul:
        obs_extension = (
            find_image_extension(obs_hdul, obs_extension_name)
            if obs_extension_name is not None
            else 1
        )
        metadata = get_observation_metadata(obs_hdul, obs_extension)

        if output_dir is None:
            output_dir = Path("data") / "processed" / (
                f"{metadata['obs_id']}_{metadata['filter']}_{obs_extension_name or obs_extension}"
            )
        output_dir = Path(output_dir)

        catalog_path = output_dir / "uvotDetect.fits"
        existing_target_count = count_targets(catalog_path)
        if not has_acceptable_target_count(catalog_path):
            print(
                f"Skipping ObsID {metadata['obs_id']} EXTNAME "
                f"{obs_extension_name or obs_extension}: its existing detection "
                f"catalog contains {existing_target_count} targets, exceeding "
                f"the limit of {MAX_TARGETS}."
            )
            return []

        best_reference = find_reference_image(metadata)
        reference_path = download_reference_image(
            best_reference, directory=reference_dir
        )

        with load_observation(reference_path) as ref_hdul:
            ref_extension = select_longest_extension(ref_hdul)
            sk_min, sk_max, obs_header, ref_header = find_overlap(
                obs_hdul,
                obs_extension,
                ref_hdul,
                ref_extension,
            )
            x_lim_obs, y_lim_obs, x_lim_ref, y_lim_ref = crop_bound(
                sk_min,
                sk_max,
                obs_header,
                ref_header,
            )
            obs_crop, ref_crop = crop_images(
                obs_hdul,
                obs_extension,
                ref_hdul,
                ref_extension,
                x_lim_obs,
                y_lim_obs,
                x_lim_ref,
                y_lim_ref,
            )
            difference_image = subtract_images(
                obs_crop,
                obs_header,
                metadata["exposure"],
                ref_crop,
                ref_header,
                ref_hdul[ref_extension].header["EXPOSURE"],
                output_dir,
                metadata["obs_id"],
                obs_extension,
            )

    catalog, _region = detect_sources(
        difference_image, output_dir=output_dir, threshold=5
    )
    if catalog is None:
        print(
            f"Skipping ObsID {metadata['obs_id']} because uvotdetect did not "
            "produce an output catalog."
        )
        return []

    validated = validate_transients(catalog)
    target_count = count_targets(validated)
    if not has_acceptable_target_count(validated):
        print(
            f"Skipping ObsID {metadata['obs_id']}: detected {target_count} "
            f"targets, exceeding the limit of {MAX_TARGETS}."
        )
        return []

    return validated
