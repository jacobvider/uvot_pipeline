
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

directory = Path("/app/data/processed/00010375194_U")

def load_image(filename):
    with fits.open(directory / filename) as hdul:
        for hdu in hdul:
            if hdu.data is not None and hdu.data.ndim == 2:
                return np.asarray(hdu.data, dtype=float), WCS(hdu.header).celestial
    raise ValueError(f"No 2D image found in {filename}")

obs, obs_wcs = load_image("ObsCrop.fits")
ref, ref_wcs = load_image("RefCrop.fits")
diff, diff_wcs = load_image("imsum_crop.fits")

print("\n1. WCS ALIGNMENT")
print("Observation shape:", obs.shape)
print("Reference shape:", ref.shape)
print("Difference shape:", diff.shape)

for name, wcs, image in [
    ("Observation", obs_wcs, obs),
    ("Reference", ref_wcs, ref),
    ("Difference", diff_wcs, diff),
]:
    y, x = np.array(image.shape) / 2
    ra, dec = wcs.pixel_to_world_values(x, y)
    print(f"{name} center: RA={ra:.6f}, Dec={dec:.6f}")

# Compare sky coordinates at identical pixel positions,
# only when observation and reference grids have the same shape.
if obs.shape == ref.shape:
    y, x = np.indices(obs.shape)
    sample = (slice(None, None, 100), slice(None, None, 100))
    ra1, dec1 = obs_wcs.pixel_to_world_values(x[sample], y[sample])
    ra2, dec2 = ref_wcs.pixel_to_world_values(x[sample], y[sample])
    dra = (ra1 - ra2 + 180) % 360 - 180
    separation = np.hypot(dra * np.cos(np.deg2rad(dec1)), dec1 - dec2) * 3600
    print(f"Maximum sampled WCS separation: {np.nanmax(separation):.3f} arcsec")
else:
    print("Different image shapes: direct pixel-by-pixel WCS comparison skipped.")

print("\n2. VALID-PIXEL COVERAGE")

# Approximate valid-data masks. Zero may represent legitimate
# image data, so this is only a preliminary diagnostic.
obs_valid = np.isfinite(obs) & (obs != 0)
ref_valid = np.isfinite(ref) & (ref != 0)

print("Observation nonzero finite fraction:", obs_valid.mean())
print("Reference nonzero finite fraction:", ref_valid.mean())


from scipy.ndimage import map_coordinates

# Map difference-image pixels into the observation and reference.
y, x = np.indices(diff.shape)
ra, dec = diff_wcs.pixel_to_world_values(x, y)

obs_x, obs_y = obs_wcs.world_to_pixel_values(ra, dec)
ref_x, ref_y = ref_wcs.world_to_pixel_values(ra, dec)

def sample_mask(mask, px, py):
    valid = np.isfinite(px) & np.isfinite(py)
    px = np.where(valid, px, -1)
    py = np.where(valid, py, -1)

    sampled = map_coordinates(
        mask.astype(float),
        [py, px],
        order=0,
        mode="constant",
        cval=0.0
    )
    return valid & (sampled > 0.5)

obs_on_diff = sample_mask(obs_valid, obs_x, obs_y)
ref_on_diff = sample_mask(ref_valid, ref_x, ref_y)

overlap = obs_on_diff & ref_on_diff
only_obs = obs_on_diff & ~ref_on_diff
only_ref = ref_on_diff & ~obs_on_diff

print("\n2. COVERAGE ON DIFFERENCE-IMAGE GRID")
print("Common valid coverage:", overlap.sum(), "pixels")
print("Observation-only coverage:", only_obs.sum(), "pixels")
print("Reference-only coverage:", only_ref.sum(), "pixels")
print("Overlap fraction of difference image:", overlap.mean())

print("\n3. DIFFERENCE SIGNAL OUTSIDE OVERLAP")

for name, mask in [
    ("Common coverage", overlap),
    ("Observation only", only_obs),
    ("Reference only", only_ref),
]:
    values = diff[mask & np.isfinite(diff)]
    if len(values):
        print(
            f"{name}: pixels={len(values)}, "
            f"median={np.median(values):.5g}, "
            f"mean_abs={np.mean(np.abs(values)):.5g}"
        )
    else:
        print(f"{name}: no finite pixels")

print("\n4. RESIDUAL STATISTICS INSIDE OVERLAP")

values = diff[overlap & np.isfinite(diff)]

if len(values):
    median = np.median(values)
    mad = np.median(np.abs(values - median))
    robust_sigma = 1.4826 * mad

    print("Median residual:", median)
    print("Mean residual:", np.mean(values))
    print("Robust noise sigma (MAD):", robust_sigma)
    print(
        "Median / robust sigma:",
        median / robust_sigma if robust_sigma else "undefined"
    )
    print("Fraction of positive pixels:", np.mean(values > 0))
else:
    print("No valid overlapping pixels found.")

print("\nDiagnostic complete.")
