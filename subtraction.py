from pathlib import Path
import shutil
from astropy.io import fits
import heasoftpy as hsp


def write_crop_fits(image, header, extname, output_path):
    """
    Save a cropped image as a FITS file.
    """
    image_header = header.copy()
    image_header["EXTNAME"] = extname

    hdul = fits.HDUList([
        fits.PrimaryHDU(),
        fits.ImageHDU(data=image, header=image_header, name=extname),
    ])
    hdul.writeto(output_path, overwrite=True)

    return output_path


def prepare_weights(obs_exposure, ref_exposure):
    """
    Compute exposure weights for uvotimsum.
    """

    if obs_exposure >= ref_exposure:
        obs_weight = ref_exposure / obs_exposure
        ref_weight = -1.0
    
    else:
        obs_weight = 1.0 
        ref_weight = -(obs_exposure / ref_exposure)


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
        f.write(f"{obs_filename}:{obs_weight}\n")
        f.write(f"{ref_filename}:{ref_weight}\n")

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


    # Directory structure
    output_dir = Path(output_dir)
    processed_dir = output_dir
    legacy_dir = output_dir / "output"
    print(processed_dir)

    processed_dir.mkdir(parents=True, exist_ok=True)
    legacy_dir.mkdir(parents=True, exist_ok=True)


    obs_hdu_name = f"{obs_header.get('EXTNAME', 'OBS')}_INPUT"
    ref_hdu_name = f"{ref_header.get('EXTNAME', 'REF')}_REFERENCE"

    # Save cropped images
    obs_file = write_crop_fits(
        obs_crop,
        obs_header,
        obs_hdu_name,
        processed_dir / "ObsCrop.fits",
    )

    ref_file = write_crop_fits(
        ref_crop,
        ref_header,
        ref_hdu_name,
        processed_dir / "RefCrop.fits",
    )

    
    # Exposure weights
    obs_weight, ref_weight = prepare_weights(
        obs_exposure,
        ref_exposure,
    )

    weight_file = write_weight_file(
        obs_hdu_name,
        ref_hdu_name,
        obs_weight,
        ref_weight,
        processed_dir / "uvotimsum_weights.txt",
    )

    # Run uvotimsum
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
