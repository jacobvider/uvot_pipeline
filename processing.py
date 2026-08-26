"""Organize the pipeline."""



"""
This script does the following:

1. opens a fits observation <- fits.py
2. gets metadata (ra, dec, obsid, filter, etc) <- fits.py
3. search swift archive for reference image <- archive.py
4. download the reference image <- archive.py
5. opens the reference fits file <- fits.py
6. choose image extension w/ longest exptime <- fits.py
7. find overlapping region of sky <- registration.py
8. convert overlap into pixel boundaries <- registration.py
9. crop both images <- registration.py
10. subtraction.py





"""
from pathlib import Path

print("In processing.py: import archive.py")
# Search the Swift archive for ref image.
from uvot_io.archive import (
    find_reference_image,
    # Download ref image from HEASARC.
    download_reference_image,
    download_image,
)

print("In processing.py: import fits.py functions, load_observation, get_observation_metadata, and select_longest_extension")

from uvot_io.fits import (

    # Open a FITS observation.
    load_observation,

    # gets ra, dec, obs_id, filter, exptime
    get_observation_metadata,

    # select img extension with the longest exposure time? (not sure how else to pick?)
    select_longest_extension,
)

from registration import (

    # finds overlapping sky region
    # shared by the observation and reference.
    find_overlap,

    # convert the overlap into pixel boundaries.
    crop_bound,

    # crop both images so they contain exactly the same sky region.
    crop_images,
)


from subtraction import subtract_images

# subtract_images()
# Creates temporary FITS files (ObsCrop.fits, RefCrop.fits)
# Runs HEASoft uvotimsum
# returns imsum_crop.fits (difference image)


from detection import detect_sources

# Runs HEASoft uvotdetect on the difference image
# to locate candidate transient sources.

from validation import validate_transients

# Verify the candidate catalog produced by the local detection step.

print("In processing.py: import process")
def process(observation_path):
    """
    Process a single Swift UVOT observation.
    """

    obs_hdul = load_observation(observation_path)

    # reads metadata from the observation (RA, Dec, ObsID, Filter, Exposure time)
    metadata = get_observation_metadata(obs_hdul)

    # Search the Swift archive for nearby observations.
    #
    # Filters candidates by same filter, different ObsID, exposure > 60 s

    # Returns the longest exposure image.
    print("In processing.py, from archive.py: run find_reference_image")
    best = find_reference_image(metadata)
    print(best)
    print("In processing.py: Returned from find_reference_image()")

    print("Selected reference:")
    print(best["OBSID"])
    print(best["FILTER"])
    print(best["START_TIME"])

    # Download the selected archival reference image.
    reference_path = download_reference_image(best)

    # Open the reference FITS file.
    ref_hdul = load_observation(reference_path)

    # Select image extensions.
    # Observation currently assumes extension 1.
    # Reference uses the extension with the
    # longest exposure.
    obs_extension = 1
    ref_extension = select_longest_extension(ref_hdul)

    # Determine the region of sky visible in both images (wcs)
    sk_min, sk_max, obs_header, ref_header = find_overlap(
        obs_hdul,
        obs_extension,
        ref_hdul,
        ref_extension,
    )

    # Convert the overlapping sky region into pixel limits for each image.
    xLimObs, yLimObs, xLimRef, yLimRef = crop_bound(
        sk_min,
        sk_max,
        obs_header,
        ref_header,
    )

    # Crop both images so they contain exactly the same region of sky.
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

    # image subtraction.
    # 1. Writes ObsCrop.fits
    # 2. Writes RefCrop.fits
    # 3. Computes exposure weights
    # 4. Runs uvotimsum
    # 5. Produces imsum_crop.fits
    print("Subtracting images...")

    difference_image = subtract_images(
        obs_crop,
        obs_header,
        metadata["exposure"],
        ref_crop,
        ref_header,
        ref_hdul[ref_extension].header["EXPOSURE"],
        "data",
        metadata["obs_id"],
        obs_extension,
    )
    print("Finished subtraction.")

    # Run uvotdetect on the difference image (uvotDetect.fits, uvotDetect.reg) containing every detected source.
    print("Running uvotdetect...")

    catalog, region = detect_sources(
        difference_image,
        output_dir="data/processed",
        threshold=5,
    )

    if catalog is None:
        print(
            f"Skipping ObsID {metadata['obs_id']} because "
            "uvotdetect did not produce an output catalog."
        )
        return []
    print("Finished uvotdetect.")

    print("Validating detection catalog...")
    validated = validate_transients(catalog)
    print("Finished validation.")

    print("Registration complete.")

    return validated
