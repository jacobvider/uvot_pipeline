import numpy as np
from astropy.wcs.utils import skycoord_to_pixel, pixel_to_skycoord
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS


def find_overlap(obs_hdul, obs_extension, ref_hdul, ref_extension):
    """
    Find the overlapping sky region between the observation and
    reference image.
    """

    # -----------------------------
    # Reference image
    # -----------------------------

    reference_header = ref_hdul[ref_extension].header

    nx_ref = reference_header["NAXIS1"]
    ny_ref = reference_header["NAXIS2"]

    x = np.arange(nx_ref)
    y = np.arange(ny_ref)
    X, Y = np.meshgrid(x, y)

    ref_sky = pixel_to_skycoord(X, Y, WCS(reference_header))
    ra_ref = ref_sky.ra
    dec_ref = ref_sky.dec

    # -----------------------------
    # Observation image
    # -----------------------------

    observation_header = obs_hdul[obs_extension].header

    nx_obs = observation_header["NAXIS1"]
    ny_obs = observation_header["NAXIS2"]

    x = np.arange(nx_obs)
    y = np.arange(ny_obs)
    X, Y = np.meshgrid(x, y)

    obs_sky = pixel_to_skycoord(X, Y, WCS(observation_header))
    ra_obs = obs_sky.ra
    dec_obs = obs_sky.dec

    # -----------------------------
    # Overlapping sky region
    # -----------------------------

    ra_min = max(np.min(ra_ref), np.min(ra_obs))
    ra_max = min(np.max(ra_ref), np.max(ra_obs))

    dec_min = max(np.min(dec_ref), np.min(dec_obs))
    dec_max = min(np.max(dec_ref), np.max(dec_obs))

    sk_min = SkyCoord(ra_min, dec_min)
    sk_max = SkyCoord(ra_max, dec_max)

    return sk_min, sk_max, observation_header, reference_header


def crop_bound(sk_min, sk_max,
               observation_header,
               reference_header):
    """
    Compute crop limits for the observation and reference images.
    """

    pix_rx1, pix_ry1 = skycoord_to_pixel(
        sk_min,
        WCS(reference_header),
    )

    pix_ox1, pix_oy1 = skycoord_to_pixel(
        sk_min,
        WCS(observation_header),
    )

    pix_rx2, pix_ry2 = skycoord_to_pixel(
        sk_max,
        WCS(reference_header),
    )

    pix_ox2, pix_oy2 = skycoord_to_pixel(
        sk_max,
        WCS(observation_header),
    )

    cut = 100

    x_lim_obs = [
        int(pix_ox2) + cut,
        int(pix_ox1) - cut,
    ]

    y_lim_obs = [
        int(pix_oy1) + cut,
        int(pix_oy2) - cut,
    ]

    x_lim_ref = [
        int(pix_rx2) + cut,
        int(pix_rx1) - cut,
    ]

    y_lim_ref = [
        int(pix_ry1) + cut,
        int(pix_ry2) - cut,
    ]

    return x_lim_obs, y_lim_obs, x_lim_ref, y_lim_ref

def crop_image(image, x_limits, y_limits):
    """
    Crop an image
    """
    return image[
        y_limits[0]:y_limits[1],
        x_limits[0]:x_limits[1],
    ]

def crop_images(
    obs_hdul,
    obs_extension,
    ref_hdul,
    ref_extension,
    xLimObs,
    yLimObs,
    xLimRef,
    yLimRef,
):
    """
    Crop both the observation and reference images.
    """

    obs_crop = crop_image(
        obs_hdul[obs_extension].data,
        xLimObs,
        yLimObs,
    )

    ref_crop = crop_image(
        ref_hdul[ref_extension].data,
        xLimRef,
        yLimRef,
    )

    return obs_crop, ref_crop
