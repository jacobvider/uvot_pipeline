
# Swift UVOT Transient Detection Pipeline

A Python-based pipeline for automatically processing NASA Swift Ultraviolet/Optical Telescope (UVOT) observations and identifying astronomical transient candidates through image subtraction and source detection.

**Author:** Jacob Vider  
**Contact:** jacobisaacvider@gmail.com

For questions, installation assistance, or collaboration inquiries, contact jacobisaacvider@gmail.com.

## GitHub Repository

This repository contains the pipeline's source code, documentation, and development history.

Users can:
- Browse the source code and documentation.
- Report bugs or request features through GitHub Issues.
- Track development tasks and milestones through the Issues page.

---

## Features

- Retrieve and organize Swift UVOT observations.
- Select archival reference observations.
- Read FITS images and observation metadata.
- Identify overlapping sky regions using WCS information.
- Crop observation and reference images.
- Perform exposure-weighted image subtraction using HEASoft `uvotimsum`.
- Generate an overlap mask to exclude pixels outside common image coverage.
- Detect transient candidates using HEASoft `uvotdetect`.
- Validate detected sources and generate FITS catalogs and region files.
- Produce intermediate and final output products for inspection.

## Project Structure

The pipeline is organized into modules responsible for different processing stages.

```text
uvot_pipeline/
├── main.py
├── processing.py
├── registration.py
├── subtraction.py
├── detection.py
├── validation.py
├── uvot_io/
│   ├── archive.py
│   └── fits.py
├── docs/
├── Dockerfile
├── environment.yml
└── README.md
```

The directory structure above illustrates the main modules and supporting files.

## Status

**Under active development.**

The pipeline has been successfully executed inside Docker using HEASoft 6.36 and Swift CALDB for a test UVOT observation.

The software has not yet been comprehensively validated across different observations, filters, operating environments, and scientific use cases.

---

# Installation and Reproducibility

## 1. Overview

The pipeline uses Docker to provide a consistent Python execution environment.

**HEASoft and Swift CALDB are installed separately on the user's host computer and mounted into the Docker container at runtime.**

This approach avoids requiring users to install HEASoft inside the Docker image.

The installation consists of:

1. Installing Docker.
2. Installing HEASoft on the host.
3. Installing Swift CALDB on the host.
4. Cloning the pipeline repository.
5. Configuring local installation paths.
6. Building the Docker image.
7. Running the pipeline.

The following instructions assume Linux or Windows Subsystem for Linux (WSL2) with Bash.

## 2. Prerequisites

Users need:

- Docker Engine or Docker Desktop with WSL2 integration.
- A compatible Linux or WSL2 environment.
- HEASoft, including Swift/UVOT tools.
- Swift CALDB calibration files.
- A local directory containing Swift UVOT observation data.
- Internet access for archival reference retrieval.

### Operating System

The pipeline has been tested using Docker from a WSL2 environment.

Other Linux environments may work but have not been independently verified.

### Docker

Install Docker using the official documentation:

https://docs.docker.com/get-docker/

Verify the installation:

```bash
docker --version
docker info
```

If Docker requires elevated permissions, use `sudo docker` instead of `docker`.

## 3. Install HEASoft on the Host

HEASoft provides the astronomical data-analysis tools used by the pipeline.

The pipeline requires HEASoft utilities including:

- `uvotimsum` for image combination and subtraction.
- `uvotdetect` for source detection.

### Download HEASoft

Official NASA HEASARC resources:

- [HEASoft download](https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/download.html)
- [HEASoft Linux installation](https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/linux.html)

**Tested version: HEASoft 6.36**

Other HEASoft versions may work but have not been validated against this pipeline.

Follow the official installation instructions for your Linux distribution.

After installation, locate the directory containing the HEASoft platform-specific installation and `headas-init.sh`.

An example host installation is:

```text
/home/jacob/heasoft-6.36/
```

Within that installation, the platform directory may resemble:

```text
x86_64-pc-linux-gnu-libc2.39/
```

The actual directory name depends on the operating system and HEASoft build.

## 4. Install Swift CALDB

The Calibration Database (CALDB) provides instrument calibration products required by HEASoft.

Official resources:

- [Swift CALDB](https://swift.gsfc.nasa.gov/caldb/)
- [HEASARC CALDB installation instructions](https://heasarc.gsfc.nasa.gov/docs/heasarc/caldb/install.html)

Install the CALDB configuration files and the calibration products needed for Swift UVOT processing, including applicable Swift common calibration files.

A typical installation layout is:

```text
caldb/
├── software/
│   └── tools/
│       ├── caldb.config
│       └── alias_config.fits
└── data/
    └── swift/
        ├── uvota/
        └── mis/
```

The precise contents depend on the CALDB release.

Follow the official HEASARC instructions to ensure the calibration files and configuration are correctly installed.

## 5. Clone the Repository

Clone the source code:

```bash
git clone https://github.com/jacobvider/uvot_pipeline.git
cd uvot_pipeline
```

The repository contains the Python pipeline, Dockerfile, and Conda environment configuration.

## 6. Configure Local Installation Paths

Define the host installation directories in your Linux or WSL terminal.

For example:

```bash
export HEASOFT_HOST="$HOME/heasoft-6.36"
export CALDB_HOST="$HOME/caldb"
export UVOT_DATA_HOST="$HOME/uvot-data"
```

Replace these paths with the actual locations on your computer.

### Verify HEASoft

Locate the HEASoft initialization script:

```bash
find "$HEASOFT_HOST" -name headas-init.sh
```

Record the directory containing that script.

For example:

```bash
export HEASOFT_PLATFORM="x86_64-pc-linux-gnu-libc2.39"
```

This platform name is an example from the tested installation and may differ on other computers.

### Verify CALDB

Check that the expected calibration configuration files exist:

```bash
test -f "$CALDB_HOST/software/tools/caldb.config"
test -f "$CALDB_HOST/software/tools/alias_config.fits"
test -d "$CALDB_HOST/data/swift/uvota"
```

If any command fails, inspect the CALDB installation before continuing.

### Prepare the Data Directory

Create a local data directory if necessary:

```bash
mkdir -p "$UVOT_DATA_HOST"
```

Place the required Swift UVOT observation files in this directory.

The pipeline also requires access to archival reference observations through its reference-selection workflow.

## 7. Build the Docker Image

From the repository root:

```bash
docker build -t uvot-pipeline .
```

The Dockerfile builds the Python execution environment using the repository's environment configuration.

HEASoft and CALDB are not bundled into the Docker image.

Instead, they are mounted from the host computer when the container starts.

If the build completes successfully, Docker creates an image named:

```text
uvot-pipeline
```

## 8. Run the Pipeline

The following command runs the pipeline for a single Swift UVOT observation.

**Example observation:**
- ObsID: `00010375194`
- Filter: `U`

The command uses the host paths configured previously.

```bash
docker run --rm \
  --entrypoint /bin/bash \
  -v "$HEASOFT_HOST:/opt/heasoft:ro" \
  -v "$CALDB_HOST:/caldb:ro" \
  -v "$UVOT_DATA_HOST:/app/data" \
  -e CALDB=/caldb \
  -e CALDBCONFIG=/caldb/software/tools/caldb.config \
  -e CALDBALIAS=/caldb/software/tools/alias_config.fits \
  -e HEASOFT_PLATFORM="$HEASOFT_PLATFORM" \
  uvot-pipeline \
  -c '
    set -e

    export HEADAS="/opt/heasoft/$HEASOFT_PLATFORM"
    source "$HEADAS/BUILD_DIR/headas-init.sh"

    export CALDB=/caldb
    export CALDBCONFIG=/caldb/software/tools/caldb.config
    export CALDBALIAS=/caldb/software/tools/alias_config.fits

    cd /app/data

    python -u /app/main.py single 00010375194 U
  '
```

**Important:** The HEASoft initialization path must match the installed HEASoft directory structure. The `BUILD_DIR` location shown above matches the previously tested environment.

Other installations may require:

```bash
source "$HEADAS/headas-init.sh"
```

Check the actual location of `headas-init.sh` before running the container.

### Docker Mounts

The command mounts three directories:

| Host directory | Container directory | Access |
|---|---|---|
| HEASoft installation | `/opt/heasoft` | Read-only |
| Swift CALDB | `/caldb` | Read-only |
| UVOT data | `/app/data` | Read/write |

The read-only mounts protect the external HEASoft and calibration installations from modification by the container.

The data mount allows output products to persist on the host computer after the container exits.

### Compatibility Note

Mounting HEASoft into Docker does not automatically guarantee binary compatibility.

The host-installed HEASoft binaries must be compatible with the libraries and runtime environment inside the container.

This configuration has been tested with the author's HEASoft 6.36 installation but has not yet been verified on an independently configured machine.

## 9. Verify HEASoft and CALDB

Before running scientific processing, verify that the container can access the required tools.

After initializing HEASoft inside the container, run:

```bash
command -v uvotimsum
command -v uvotdetect
fversion
```

Verify CALDB environment variables:

```bash
echo "$CALDB"
echo "$CALDBCONFIG"
echo "$CALDBALIAS"
```

Check the CALDB configuration and available calibration files using the appropriate HEASoft CALDB utilities.

If HEASoft commands cannot be found, verify that the initialization script was sourced correctly.

If calibration files cannot be found, verify the CALDB directory mount and configuration paths.

## 10. Expected Output Products

For the example observation, the pipeline writes output files under:

```text
/app/data/processed/00010375194_U/
```

Because `/app/data` is mounted from the host, these files remain accessible after the Docker container exits.

Expected output products include:

| File | Description |
|---|---|
| `ObsCrop.fits` | Cropped observation image |
| `RefCrop.fits` | Cropped reference image |
| `imsum_crop.fits` | Original subtraction image |
| `imsum_masked.fits` | Subtraction image with non-overlapping pixels masked |
| `uvotimsum_weights.txt` | Image subtraction weights |
| `uvotDetect.fits` | Source detection catalog, when generated |
| `uvotDetect.reg` | Region file containing detected sources, when generated |

### Overlap Masking

The pipeline calculates the region of valid common coverage between the observation and reference images.

Pixels outside the selected overlap region are assigned `NaN` values in `imsum_masked.fits`.

The original subtraction image is preserved separately as `imsum_crop.fits`.

Source detection is then performed on the masked image.

### Photometry Warning

HEASoft `uvotimsum` may warn that photometry should not be performed directly on its weighted output.

The subtraction image is intended for candidate detection, not as a substitute for calibrated photometric measurements on the original observation data.

## 11. Reproducibility

Reproducibility is a primary design objective of this project.

Docker helps provide a consistent Python environment, while external HEASoft and CALDB installations supply the astronomical processing tools and calibration data.

For reproducible scientific results, users should record:

- Git commit or software release version.
- Docker image digest.
- Python and package versions.
- HEASoft version and build platform.
- Swift CALDB release and calibration file versions.
- Observation IDs and FITS image extensions.
- Reference observation IDs and FITS image extensions.
- Processing parameters.
- Output files and validation results.

### Reference Selection

The pipeline automatically selects reference observations from archival data.

Because archive contents may change over time, repeated processing at different dates may select different reference observations.

For exact reproducibility, users should record the reference observation and image extension selected for each run.

### Numerical Reproducibility

Identical input data, software versions, calibration products, and processing parameters should be used when comparing results.

Small numerical differences may arise across operating environments or dependency versions.

Scientific regression tests should compare outputs using justified numerical tolerances rather than relying exclusively on byte-identical FITS files.

## 12. Testing and Validation

The pipeline has been successfully executed in Docker for observation `00010375194`, filter `U`.

In this test:

- Image subtraction completed successfully.
- The overlap mask identified 423,516 overlapping pixels.
- The overlap fraction was approximately 33.08%.
- The masked FITS image contained 423,516 finite pixels.
- `uvotdetect` produced one detected source.
- The detected source was located within the overlap region.

These results demonstrate successful execution for the tested observation.

They do not establish comprehensive scientific validation across the full Swift UVOT archive.

Further validation should include:

- Multiple observations and filters.
- Different exposure times.
- Small and empty overlap regions.
- Known transient recovery.
- False-positive characterization.
- Astrometric and photometric verification.
- Reproducibility on independently configured systems.

## 13. Troubleshooting

### Docker permission errors

If Docker cannot access the daemon, verify that Docker is running.

Depending on the system configuration, Docker commands may require `sudo`.

### HEASoft command not found

Verify that the correct `headas-init.sh` script is being sourced.

Check:

```bash
echo "$HEADAS"
command -v uvotimsum
command -v uvotdetect
```

### Missing calibration files

Verify:

```bash
echo "$CALDB"
ls "$CALDB/software/tools/"
ls "$CALDB/data/swift/"
```

Check that the host CALDB directory is mounted at `/caldb`.

### HEASoft shared-library errors

A host-installed HEASoft build may depend on libraries not present inside the Docker image.

Verify compatibility between the HEASoft build and the container operating system.

If necessary, use a compatible HEASoft build or adjust the container dependencies.

### No source catalog generated

An absent source catalog does not necessarily indicate a software failure.

It may indicate that no sources were detected or that processing was skipped.

Inspect the pipeline logs and intermediate FITS products to distinguish valid empty results from execution failures.

---

## About

This repository is a rewrite of the Swift UVOT transient detection pipeline, with an emphasis on:

- Clean, modular Python code.
- Reproducible scientific processing.
- Automated image subtraction and transient detection.
- Software testing and validation.
- Comprehensive documentation.
- Maintainability and extensibility.

## Author

**Jacob Vider**

**Contact:** jacobisaacvider@gmail.com

For questions, bug reports, installation assistance, or collaboration inquiries, contact the author or open a GitHub Issue.

## Development Status

This project is under active development.

The software and documentation may change as testing, scientific validation, and packaging improvements continue.
