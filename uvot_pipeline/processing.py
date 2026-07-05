"""Organize the pipeline"""

from pathlib import Path

from uvot_pipeline.io.archive import (
    find_reference_image,
    download_reference_image,
)

from uvot_pipeline.io.fits import (
    load_observation,
    get_observation_metadata,
    select_longest_extension,
)

from uvot_pipeline.registration import (
    find_overlap,
    crop_bound,
    crop_images,
)

from uvot_pipeline.subtraction import subtract_images

from uvot_pipeline.detection import detect_sources

def process(observation_path):
        # Load observation
    obs_hdul = load_observation(observation_path)

    metadata = get_observation_metadata(obs_hdul)

    # Download reference
    best = find_reference_image(metadata)

    reference_path = download_reference_image(best)

    ref_hdul = load_observation(reference_path)

    # Choose extensions
    obs_extension = 1
    ref_extension = select_longest_extension(ref_hdul)

    # Registration
    sk_min, sk_max, obs_header, ref_header = find_overlap(
        obs_hdul,
        obs_extension,
        ref_hdul,
        ref_extension,
    )

    xLimObs, yLimObs, xLimRef, yLimRef = crop_bound(
        sk_min,
        sk_max,
        obs_header,
        ref_header,
    )

    # Crop images
    obs_crop, ref_crop = crop_images(
        obs_hdul,
        obs_extension,
        ref_hdul,
        ref_extension,
        xLimObs,
        yLimObs,
        xLimRef,
        yLimRef,
    )

    # # Subtraction
    # difference_image = subtract_images(
    #     obs_crop,
    #     obs_header,
    #     metadata["exposure"],
    #     ref_crop,
    #     ref_header,
    #     ref_hdul[ref_extension].header["EXPOSURE"],
    #     "data/processed",
    # )

    # # Detection
    # detect_sources(difference_image)

    difference_image = Path("data/processed/imsum_crop.fits")

    # Detection
    detect_sources(difference_image)
    print("Registration complete.")
    print("Subtraction skipped (HEASoft not installed).")

    return






# def clean_output_directory(output_dir: Path):
#     """
#     Remove intermediate files from a previous pipeline run.
#     """

#     files_to_remove = [
#         "observation.fits",
#         "reference.fits",
#         "observation_crop.fits",
#         "reference_crop.fits",
#         "difference_image.fits",
#         "detected_sources.fits",
#         "detected_sources_reference.fits",
#         "detected_sources_observation.fits",
#         "detected_sources.reg",
#         "detected_sources_observation.reg",
#         "detected_sources_reference.reg",
#     ]

#     for filename in files_to_remove:
#         filepath = output_dir / filename

#         if filepath.exists():
#             filepath.unlink()

# def process_observation(observation_path):

#     hdul = load_observation(observation_path)

#     metadata = get_observation_metadata(hdul)

#     validate_observation(metadata)

#     reference = find_reference_image(metadata)

#     result = detect_transients(
#         observation_path,
#         reference,
#     )

#     return result


# def process_directory()
