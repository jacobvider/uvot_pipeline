# Updated UVOT Pipeline (August 2026)

Author: Jacob Vider

Email: jacobisaacvider@gmail.com

## High-Level Description of Code

#### Input:

Run single observation mode:

```bash
python main.py single <obsid> <filter>
```

Or run batch processing mode using a manifest:

```bash
python main.py batch --manifest path/to/manifest.txt
```

#### Output:

* Output files are located in `data/processed/<obsid>_<filter>/` (or `data/processed/<obsid>_<filter>_<extension>/`).
* It generates four FITS files (`ObsCrop.fits`, `RefCrop.fits`, `imsum_crop.fits`, `imsum_masked.fits`), source catalog files (`uvotDetect.fits`), and DS9 region overlays (`uvotDetect.reg`).
* Reference FITS files from the Swift archive are stored in `data/reference/`.
* *Note:* Interactive image visualization via DS9 is external and not directly launched by the Python pipeline execution.

## Low-Level Description of Code

 1. Opens input FITS file observation (`fits.py`).
 2. Extracts target and HDU metadata (RA, Dec, ObsID, filter, exposure time) (`fits.py`).
 3. Searches for reference images in the Swift archive (within 6 arcmin radius) (`archive.py`).
 4. Filters reference candidates to meet criteria (`archive.py`):
    * Different observation ID (`obsid`)
    * Same filter
    * Exposure time $> 60$ seconds
 5. Selects the archival reference candidate with the longest exposure time and downloads it (`archive.py`).
 6. Opens the reference FITS file and selects the extension with the longest exposure. For input observations, it dynamically resolves the matching FITS extension name (`EXTNAME`) when provided, falling back to extension 1 if omitted (`fits.py`, `processing.py`).
 7. Uses WCS coordinates to determine the overlapping sky region between observation and reference images (`registration.py`).
 8. Crops both observation and reference images to their common sky boundary (`registration.py`).
 9. Computes relative exposure weights (`subtraction.prepare_weights`) and runs HEASoft `uvotimsum` to produce exposure-scaled subtraction image `imsum_crop.fits` (`subtraction.py`).
10. Builds a pixel-level coverage mask across common valid footprints (`registration.create_overlap_mask`) and masks out non-overlapping pixels as `NaN` to produce `imsum_masked.fits` (`detection.py`).
11. Runs HEASoft `uvotdetect` on `imsum_masked.fits` (`detection.py`).
12. Generates `uvotDetect.fits` (detected source catalog) and `uvotDetect.reg` (DS9 overlay region file).
13. Validates candidate detections (`validation.validate_transients`) and checks against maximum target limits (`archive.has_acceptable_target_count`).

## What Files Are Returned?

### `ObsCrop.fits`

* Input observation image cropped to the overlapping sky boundary shared with the selected reference image (`registration.py`, `subtraction.py`).

### `RefCrop.fits`

* Reference image downloaded from the Swift archive and cropped to the matching footprint (`registration.py`, `subtraction.py`).

### `imsum_crop.fits`

* Scaled difference image produced by `uvotimsum` applying exposure-ratio weights between observation and reference images (`subtraction.py`).

### `imsum_masked.fits`

* Masked copy of `imsum_crop.fits` where pixels outside the mutual valid WCS footprint are set to `NaN` prior to source detection (`detection.py`).

### `uvotDetect.fits`

* FITS binary table containing detected source parameters from `uvotdetect` (RA, Dec, Rate, Rate Error, fit shapes, quality flags).

### `uvotDetect.reg`

* DS9 region file containing circle overlays for detected sources found in the difference image (`detection.py`).

## Detailed Breakdown of `main.py`

`main.py` serves as the CLI entry point for the UVOT subtraction pipeline, supporting single-observation execution and manifest-driven batch processing.

### Execution Modes

1. **Single Observation Mode (`main`)**
   * **Entry Point:** Invoked via `python main.py single <obsid> <filter_name>` (or legacy positional syntax `python main.py <obsid> <filter_name>`).
   * **Functionality:** 
     * Resolves the observation file path via `uvot_io.archive.get_obs_path`.
     * Calls `processing.process` targeting output directory `data/processed/<obsid>_<filter_name>`.
     * Downloads needed reference images into `data/reference`.

2. **Batch Mode (`batch_main`)**
   * **Entry Point:** Invoked via `python main.py batch --manifest <path> [options]`.
   * **Functionality:**
     * **Manifest Parsing:** Parses structured entries (`filename|version|EXTNAME`) via `parse_manifest`.
     * **Archive Indexing:** Indexes inputs from ZIP archives (`--archive`) or uncompressed directories (`--source-dir`) via `index_inputs`.
     * **Missing Input Verification:** Validates presence of all manifest inputs; raises a descriptive error (`_format_missing_inputs`) unless `--allow-missing` is flagged.
     * **Iterative Pipeline Execution:** Extracts specific FITS extensions via `extract_input` into `--input-dir` and runs `processing.process` for each extension.
     * **Error Handling & Failure Logging:** Captures pipeline exceptions per entry. Halts execution early if `--fail-fast` is passed, or completes batch and prints a summary report of successes, failures, and missing files.

### Command-Line Arguments (`build_parser`)

* **`single` subcommand:**
  * `obsid`: Swift Observation Identifier.
  * `filter_name`: UVOT filter identifier (e.g., `UVW1`, `U`).
* **`batch` subcommand:**
  * `--manifest` (Required): Path to manifest file containing target lines.
  * `--archive`: Split ZIP file path containing compressed inputs (can be specified multiple times).
  * `--source-dir`: Directory containing extracted `*.img.gz` files.
  * `--input-dir`: Directory where extracted FITS extensions are staged (`data/input` by default).
  * `--output-dir`: Root output directory for processed results (`data/processed` by default).
  * `--reference-dir`: Directory for archival reference storage (`data/reference` by default).
  * `--allow-missing`: Flag to skip unindexed manifest entries instead of aborting.
  * `--fail-fast`: Flag to immediately stop batch execution upon encountering a pipeline processing error.

## Subtraction & Execution Functions

### `processing.process`

Pipeline orchestrator inside `processing.py`:

* `fits.load_observation(observation_path)`
* `fits.find_image_extension` / `fits.get_observation_metadata`
* `archive.find_reference_image`
  * `archive.query_archive`
  * `archive.filter_reference_candidates`
  * `archive.select_best_references`
* `archive.download_reference_image`
* `fits.load_observation(reference_path)`
* `fits.select_longest_extension`
* `registration.find_overlap`
* `registration.crop_bound`
* `registration.crop_images`
* `subtraction.subtract_images`
  * `subtraction.prepare_weights`
  * `subtraction.run_uvotimsum`
* `registration.create_overlap_mask`
* `detection.create_masked_difference_image`
* `detection.detect_sources`
* `validation.validate_transients`
* `archive.has_acceptable_target_count`

### `main.py` Summary

* `main(obsid, filter_name)`: Single-run helper.
* `batch_main(args)`: Manifest execution loop with exception tracking.
* `_format_missing_inputs(missing)`: Formatter for missing batch files.
* `build_parser()`: `argparse` configuration for CLI commands.