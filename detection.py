#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jacob Vider, jacobisaacvider@gmail.com
Date:   Wed Aug 26 2026
"""
"""Source detection for UVOT difference images."""

from pathlib import Path

from astropy.table import Table
import heasoftpy as hsp


import numpy as np
from astropy.io import fits


def create_masked_difference_image(
    difference_image,
    overlap_mask,
    output_dir,
):
    """
    Save a masked copy of the subtraction image.

    Pixels outside the common observation/reference
    footprint are marked as NaN.

    The original subtraction image is not modified.
    """
    difference_image = Path(difference_image)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    masked_path = output_dir / "imsum_masked.fits"

    with fits.open(difference_image) as hdul:
        image_hdu = hdul[1]
        image = np.asarray(image_hdu.data, dtype=float)

        if image.shape != overlap_mask.shape:
            raise ValueError(
                "Overlap mask and difference image "
                "have different dimensions."
            )

        masked_image = image.copy()
        masked_image[~overlap_mask] = np.nan

        image_hdu.data = masked_image

        hdul.writeto(masked_path, overwrite=True)

    return masked_path


def detect_sources(
    difference_image: str | Path,
    *,
    output_dir: str | Path,
    threshold: float,
) -> tuple[Table | None, Path]:
    """Run HEASoft ``uvotdetect`` on the first image HDU of a summed image."""

    difference_image = Path(difference_image)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = output_dir / "uvotDetect.fits"
    region_path = output_dir / "uvotDetect.reg"

    task = hsp.HSPTask("uvotdetect")
    result = task(
        infile=f"{difference_image}+1",
        outfile=str(catalog_path),
        expfile="NONE",
        threshold=threshold,
        sexfile="DEFAULT",
        plotsrc="yes",
        expopt="ALPHA",
        calibrate="no",
        regfile=str(region_path),
        clobber="yes",
        cleanup="yes",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    if not catalog_path.is_file():
        return None, region_path
    return Table.read(catalog_path), region_path
