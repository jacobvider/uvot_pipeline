from pathlib import Path
import shutil

from astropy.io import fits
import heasoftpy as hsp


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


def run_uvotimsum(
    observation_file,
    reference_file,
    weight_file,
    output_file,
):
    """
    Run the HEASoft uvotimsum task.
    """

    uvotimsum = hsp.HSPTask("uvotimsum")

    infile = f"{observation_file},{reference_file}"

    result = uvotimsum(
        infile=infile,
        outfile=output_file,
        method="GRID",
        weightfile=weight_file,
        exclude="NONE",
        ignoreframetime="yes",
        clobber="yes",
    )

    print(result)
    print(result.returncode)
    print(result.stdout)
    print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return output_file


def subtract_images(
    obs_crop,
    obs_header,
    obs_exposure,
    ref_crop,
    ref_header,
    ref_exposure,
    output_dir,
    obs_id,
    obs_extension,
):
    """
    Save cropped FITS images, run uvotimsum, and create both the
    new pipeline outputs and the legacy filenames expected by
    checkValidTransients_uvot_tdrss.py.
    """

    output_dir = Path(output_dir)

    #
    # Directory structure
    #
    processed_dir = output_dir / "processed"
    legacy_dir = output_dir / "output"

    processed_dir.mkdir(parents=True, exist_ok=True)
    legacy_dir.mkdir(parents=True, exist_ok=True)

    #
    # Save cropped images
    #
    obs_file = write_crop_fits(
        obs_crop,
        obs_header,
        processed_dir / "ObsCrop.fits",
    )

    ref_file = write_crop_fits(
        ref_crop,
        ref_header,
        processed_dir / "RefCrop.fits",
    )

    #
    # Exposure weights
    #
    obs_weight, ref_weight = prepare_weights(
        obs_exposure,
        ref_exposure,
    )

    weight_file = write_weight_file(
        obs_file.name,
        ref_file.name,
        obs_weight,
        ref_weight,
        processed_dir / "uvotimsum_weights.txt",
    )

    #
    # Run uvotimsum
    #
    output_file = run_uvotimsum(
        obs_file,
        ref_file,
        weight_file,
        processed_dir / "imsum_crop.fits",
    )


    legacy_output = (
        legacy_dir /
        f"{obs_id}_{obs_extension}_imsum_crop.fits"
    )

    shutil.copy2(output_file, legacy_output)

    return output_file