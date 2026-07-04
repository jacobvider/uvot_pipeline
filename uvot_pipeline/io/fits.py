# def load_fits(...):
#     ...

# def save_fits(...):
#     ...

from astropy.io import fits

def load_observation(path):
    """Load a Swift UVOT observation.
       Parameters
    ----------
    path : Path
        Path to a UVOT FITS image.

    Returns
    -------
    Observation
        A loaded observation.
    """
    return fits.open(path)