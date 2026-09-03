"""Read UVOT FITS files and select their image extensions."""

from pathlib import Path

from astropy.coordinates import SkyCoord
from astropy.io import fits
import astropy.units as u


def load_observation(path: str | Path) -> fits.HDUList:
    """Open a Swift UVOT FITS image without memory-mapping the input."""

    return fits.open(path, memmap=False)


def get_observation_metadata(hdul: fits.HDUList, extension: int = 1) -> dict:
    """Extract the metadata for a particular UVOT image extension."""

    header = hdul[extension].header
    ra = header.get("RA_PNT")
    dec = header.get("DEC_PNT")
    if ra is None or dec is None:
        raise ValueError(
            f"HDU {extension} is missing RA_PNT or DEC_PNT metadata"
        )

    return {
        "obs_id": str(header.get("OBS_ID")).strip(),
        "filter": str(header.get("FILTER")).strip(),
        "exposure": header.get("EXPOSURE"),
        "ra": ra,
        "dec": dec,
        "skycoord": SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame="icrs"),
    }


def find_image_extension(hdul: fits.HDUList, extension_name: str) -> int:
    """Return the image HDU whose FITS ``EXTNAME`` matches *extension_name*."""

    expected = str(extension_name).strip()
    for index, hdu in enumerate(hdul):
        actual = str(hdu.header.get("EXTNAME", "")).strip()
        if hdu.header.get("XTENSION") == "IMAGE" and actual == expected:
            return index

    available = [
        str(hdu.header.get("EXTNAME", "")).strip()
        for hdu in hdul
        if hdu.header.get("XTENSION") == "IMAGE"
    ]
    raise KeyError(
        f"Image extension {expected!r} was not found; available EXTNAME values: "
        f"{', '.join(available) or '(none)'}"
    )


def select_longest_extension(hdul: fits.HDUList) -> int:
    """Return the image extension with the greatest positive exposure."""

    candidates = [
        (index, hdu.header.get("EXPOSURE", 0))
        for index, hdu in enumerate(hdul)
        if hdu.header.get("XTENSION") == "IMAGE"
    ]
    if not candidates:
        raise ValueError("FITS file contains no image extensions")
    return max(candidates, key=lambda candidate: candidate[1])[0]
