"""Read fits files and extract metadata"""

from astropy.coordinates import SkyCoord
import astropy.units as u
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
    
def save_observation(path):
    pass

def get_observation_metadata(hdul, extension=1):
    """
    Extract metadata from a Swift UVOT observation.
    """

    header = hdul[extension].header

    ra = header.get("RA_PNT")
    dec = header.get("DEC_PNT")

    skycoord = SkyCoord(
        ra=ra * u.deg,
        dec=dec * u.deg,
        frame="icrs",
    )

    return {
        "obs_id": header.get("OBS_ID"),
        "filter": header.get("FILTER"),
        "exposure": header.get("EXPOSURE"),
        "ra": ra,
        "dec": dec,
        "skycoord": skycoord,
    }



def select_longest_extension(hdul):
    """
    Return the extension with the longest exposure.
    """

    longest = 1
    max_exposure = hdul[1].header["EXPOSURE"]

    for i in range(2, len(hdul)):
        exposure = hdul[i].header["EXPOSURE"]

        if exposure > max_exposure:
            max_exposure = exposure
            longest = i

    return longest


