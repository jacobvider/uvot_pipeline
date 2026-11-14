
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from scipy.ndimage import map_coordinates

folder = "/app/data/processed/00010375194_U/"

def load(name):
    with fits.open(folder + name) as hdul:
        hdu = next(h for h in hdul if h.data is not None and h.data.ndim == 2)
        return np.array(hdu.data, dtype=float), WCS(hdu.header).celestial

obs, ow = load("ObsCrop.fits")
ref, rw = load("RefCrop.fits")
diff, dw = load("imsum_crop.fits")

y, x = np.indices(diff.shape)
ra, dec = dw.pixel_to_world_values(x, y)

def project(data, wcs):
    px, py = wcs.world_to_pixel_values(ra, dec)
    valid = (
        np.isfinite(px) & np.isfinite(py) &
        (px >= 0) & (py >= 0) &
        (px < data.shape[1] - 1) &
        (py < data.shape[0] - 1)
    )
    px = np.where(valid, px, -1)
    py = np.where(valid, py, -1)
    values = map_coordinates(
        data, [py, px], order=1,
        mode="constant", cval=np.nan
    )
    return values, valid

o, ov = project(obs, ow)
r, rv = project(ref, rw)

mask = (
    ov & rv &
    np.isfinite(o) & np.isfinite(r) &
    np.isfinite(diff) &
    (o > 0) & (r > 0)
)

weight = -38.2668037302389 / 889.431478065953

expected_subtraction = o + weight * r
expected_addition = o - weight * r

print("Overlap pixels:", mask.sum())
print("Reference weight:", weight)

for name, predicted in [
    ("Subtraction", expected_subtraction),
    ("Addition", expected_addition),
    ("Observation only", o),
    ("Reference only", r),
]:
    error = np.median(np.abs(diff[mask] - predicted[mask]))
    print(name, "median absolute error:", error)

print("Actual output median:", np.median(diff[mask]))
print("Expected subtraction median:", np.median(expected_subtraction[mask]))
print("Expected addition median:", np.median(expected_addition[mask]))
