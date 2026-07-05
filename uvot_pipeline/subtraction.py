from pathlib import Path
from astropy.io import fits
# import heasoftpy as hsp


def write_crop_fits(image, header, output_path):
    """
    Save a cropped image as a FITS file.
    """

    hdu = fits.PrimaryHDU(data=image, header=header)
    hdu.writeto(output_path, overwrite=True)

    return output_path


def prepare_weights(obs_exposure, ref_exposure):
    """
    Compute exposure weights for uvotimsum.
    """

    if obs_exposure >= ref_exposure:
        obs_weight = 1.0
        ref_weight = obs_exposure / ref_exposure
    else:
        obs_weight = ref_exposure / obs_exposure
        ref_weight = 1.0

    return obs_weight, ref_weight


def write_weight_file(
    obs_filename,
    ref_filename,
    obs_weight,
    ref_weight,
    output_file,
):
    """
    Write the uvotimsum weight file.
    """

    with open(output_file, "w") as f:
        f.write(f"{obs_filename} {obs_weight}\n")
        f.write(f"{ref_filename} {ref_weight}\n")

    return output_file

def run_uvotimsum(*args, **kwargs):
    raise NotImplementedError(
        "HEASoft is not installed."
    )

# def run_uvotimsum(
#     observation_file,
#     reference_file,
#     weight_file,
#     output_file,
# ):
#     """
#     Run the HEASoft uvotimsum task.
#     """

#     uvotimsum = hsp.HSPTask("uvotimsum")

#     infile = f"{observation_file},{reference_file}"

#     result = uvotimsum(
#         infile=infile,
#         outfile=output_file,
#         method="GRID",
#         weightfile=weight_file,
#         exclude="NONE",
#         ignoreframetime="yes",
#     )

#     if result.returncode != 0:
#         raise RuntimeError(result.stderr)

#     return output_file


def subtract_images(
    obs_crop,
    obs_header,
    obs_exposure,
    ref_crop,
    ref_header,
    ref_exposure,
    output_dir,
):
    """
    Save cropped images and create a difference image with uvotimsum.
    """

    output_dir = Path(output_dir)

    # Save cropped FITS images
    obs_file = write_crop_fits(
        obs_crop,
        obs_header,
        output_dir / "ObsCrop.fits",
    )

    ref_file = write_crop_fits(
        ref_crop,
        ref_header,
        output_dir / "RefCrop.fits",
    )

    # Compute exposure weights
    obs_weight, ref_weight = prepare_weights(
        obs_exposure,
        ref_exposure,
    )

    # Write uvotimsum weight file
    weight_file = write_weight_file(
        obs_file.name,
        ref_file.name,
        obs_weight,
        ref_weight,
        output_dir / "uvotimsum_weights.txt",
    )

    # Run uvotimsum
    output_file = run_uvotimsum(
        obs_file,
        ref_file,
        weight_file,
        output_dir / "imsum_crop.fits",
    )

    return output_file
