#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jacob Vider, jacobisaacvider@gmail.com
Date:   Wed Aug 26 2026
"""
from pathlib import Path
import heasoftpy as hsp
from astropy.table import Table


def detect_sources(
    difference_image,          # Input difference image (FITS)
    output_dir,  # Directory where outputs will be written
    threshold=5,               # Detection threshold in sigma
):
    """
    Run HEASoft uvotdetect on a difference image.

    Parameters
    ----------
    difference_image : str or Path
        Difference image produced by uvotimsum.

    output_dir : str or Path
        Directory for output products.

    threshold : float
        Detection threshold (sigma).
    """

    # Convert the input filename into a Path object
    difference_image = Path(difference_image)

    if output_dir is None:
        output_dir = difference_image.parent
    else:
        output_dir = Path(output_dir)
    # Convert the output directory into a Path object
    output_dir = Path(output_dir)

    # Create the output directory if it does not already exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Output FITS catalog containing detected sources
    output_fits = output_dir / "uvotDetect.fits"

    # DS9 region file showing detected source locations
    output_region = output_dir / "uvotDetect.reg"

    # Delete the previous source catalog if it exists
    if output_fits.exists():
        output_fits.unlink()

    # Delete the previous DS9 region file if it exists
    if output_region.exists():
        output_region.unlink()

    # Print progress information
    print("Running source detection...")
    print(f"Input: {difference_image}")

    # Create a Python wrapper around the HEASoft uvotdetect task
    uvotdetect = hsp.HSPTask("uvotdetect")

    # ---------------------------------------------------------
    # Run uvotdetect
    # ---------------------------------------------------------

    result = uvotdetect(

        # Input difference image
        infile=str(difference_image),

        # Output FITS source catalog
        outfile=str(output_fits),

        # Output DS9 region file
        regfile=str(output_region),

        # Additional SExtractor options
        # Estimate the background automatically using
        # 32×32 pixel background meshes.
        sexargs="-BACK_TYPE AUTO -BACK_SIZE 32,32",

        # No separate exposure map supplied
        expfile="NONE",

        # Treat zero-valued pixels as background
        zerobkg=2,

        # Do not create diagnostic plots
        plotsrc="no",

        # Detection significance threshold (sigma)
        threshold=threshold,

        # Verbosity level
        chatter=5,

        # Run non-interactively
        noprompt="True",

        # Overwrite existing output files
        clobber="yes",
    )

    # Print the full HEASoft execution result
    print(result)

    if result.returncode != 0:
        print(f"WARNING: uvotdetect failed (return code {result.returncode})")
        print(result.stdout)
        return None, None

    if not output_fits.exists():
        print(f"WARNING: {output_fits} was not created.")
        return None, None

    if not output_region.exists():
        print(f"WARNING: {output_region} was not created.")
        return None, None

    # Occasionally uvotdetect exits without creating its outputs.
    # Check that the expected files actually exist.
    if not output_fits.exists():
        print(
            f"WARNING: uvotdetect did not create {output_fits}. "
            "Skipping this observation."
        )
        return None, None

    if not output_region.exists():
        print(
            f"WARNING: uvotdetect did not create {output_region}. "
            "Skipping this observation."
        )
        return None, None

    # Inform the user that source detection finished successfully
    print("Detection complete.")

    # Print the location of the output FITS catalog
    print(f"Catalog : {output_fits}")

    # Print the location of the DS9 region file
    print(f"Regions : {output_region}")

    # Return both output filenames so the next stage of the
    # pipeline can use them

    catalog = Table.read(output_fits)

    return catalog, output_region

    
