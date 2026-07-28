"""
validation.py

Wrapper around the original validation code.

Rather than rewriting the original
checkValidTransients_uvot_tdrss.py,
this module exposes a cleaner interface
for the new pipeline.
"""

from pathlib import Path
import sys


# -------------------------------------------------------------------------
# Location of the original pipeline
# -------------------------------------------------------------------------

ORIGINAL_PIPELINE = (
    Path(__file__).resolve().parents[1]
    / "spring_2026"
    / "image_subtraction_pipeline_to_process"
    / "Python_Code"
)

sys.path.insert(0, str(ORIGINAL_PIPELINE))

from checkValidTransients_uvot_tdrss import checkValidTransients


def validate_transients(
    observation_path,
    observation_extension,
    observation_id,
    reference_path,
    reference_extension,
    output_directory,
    criteria=(1, 2, 3, 4, 5, 6, 7, 8),
    threshold=5,
    match_radius_arcsec=2.0,
    logfile=None,
):
    """
    Run the original transient validation routine.

    Parameters
    ----------
    observation_path : Path or str
        Observation FITS file.

    observation_extension : int
        FITS extension containing the observation image.

    observation_id : str
        Swift observation ID.

    reference_path : Path or str
        Reference FITS image.

    reference_extension : int
        FITS extension for the reference image.

    output_directory : Path or str
        Directory containing

            output/
                *_imsum_crop.fits
                *_uvotDetect.fits

        exactly as expected by the original code.

    criteria : iterable[int]
        Validation criteria to apply.

    threshold : float
        uvotdetect detection threshold.

    match_radius_arcsec : float
        Matching radius.

    logfile : file-like object, optional

    Returns
    -------
    tuple

        (
            validSrc1,
            validSrc2,
            validSrc3,
            validSrc4,
            validSrc5,
            validSrc6,
            validSrc7,
            validSrc8,
            validSrcArr,
            mag_obs_arr,
            mag_obs_err_arr,
        )
    """

    output_directory = Path(output_directory)

    if logfile is None:
        class DummyLog:
            def write(self, *args, **kwargs):
                pass

        logfile = DummyLog()

    return checkValidTransients(
        ref=str(reference_path),
        refInd=reference_extension,
        obs=str(observation_path),
        obsInd=observation_extension,
        obsID=str(observation_id),
        criteria=list(criteria),
        thresh=threshold,
        arcsec_rad=match_radius_arcsec,
        LogFile=logfile,
        DataLoc=str(output_directory) + "/",
    )