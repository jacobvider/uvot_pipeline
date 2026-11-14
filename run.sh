#!/usr/bin/env bash
### @author: Jacob Vider, jacobisaacvider@gmail.com
### Date:   Wed Aug 26 2026
### Usage: ./run.sh target_observed filter output_filename.jpg
### Default batch: ./run.sh batch --manifest /path/to/manifest.log --source-dir /path/to/files
### Custom batch: ./run.sh batch --manifest /path/to_process.log --source-dir /path/to/files
### Example: ./run.sh 30010013 UVW1 uvot_30010013_UVW1.jpg

set -e

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
UVOT_ENVIRONMENT="uvot"

# -------------------------------------------------
# HEASoft configuration (parameterized)
# -------------------------------------------------
# Prefer the environment variable HEADAS if it is already set.
# Fall back to a conventional location. Users on other machines
# should export HEADAS before running the script.
DEFAULT_HEADAS="${HEADAS:-/opt/heasoft}"

activate_uvot_environment() {
    if ! command -v conda >/dev/null 2>&1; then
        if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
            source "$HOME/miniconda3/etc/profile.d/conda.sh"
        elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
            source "$HOME/anaconda3/etc/profile.d/conda.sh"
        else
            echo "Conda was not found. Install Miniconda/Anaconda or make sure it is on PATH." >&2
            exit 1
        fi
    fi

    source "$(conda info --base)/etc/profile.d/conda.sh"
    if ! conda env list | awk '{print $1}' | sed 's/^\*//' | grep -qx "$UVOT_ENVIRONMENT"; then
        echo "Conda environment '$UVOT_ENVIRONMENT' does not exist." >&2
        echo "Create it once with:" >&2
        echo "  cd $PROJECT_DIR && conda env create -f environment.yml" >&2
        exit 1
    fi
    conda activate "$UVOT_ENVIRONMENT"
}

initialize_heasoft() {
    HEADAS="${HEADAS:-$DEFAULT_HEADAS}"

    if [ ! -f "$HEADAS/headas-init.sh" ]; then
        echo "HEASoft initialization script was not found at: $HEADAS/headas-init.sh" >&2
        echo "Set the environment variable HEADAS to your HEASoft installation and retry." >&2
        echo "Example:" >&2
        echo "  export HEADAS=/path/to/heasoft-6.36/x86_64-pc-linux-gnu-libc2.39" >&2
        exit 1
    fi

    export HEADAS
    # shellcheck source=/dev/null
    source "$HEADAS/headas-init.sh"
}

activate_uvot_environment
initialize_heasoft

# -------------------------------------------------
# Batch mode
# -------------------------------------------------
# Batch mode deliberately skips DS9 (opening a window for every
# entry is not useful when processing hundreds of images).
if [ "$1" = "batch" ]; then
    shift
    cd "$PROJECT_DIR"

    if [ "$#" -eq 0 ]; then
        echo "Batch mode requires arguments." >&2
        echo "Usage:" >&2
        echo "  ./run.sh batch --manifest /path/to/manifest.log --source-dir /path/to/files [--allow-missing]" >&2
        echo "  ./run.sh batch --manifest /path/to/manifest.log --archive /path/to/images.zip" >&2
        exit 1
    fi

    exec python -u main.py batch "$@"
fi

# -------------------------------------------------
# Single-observation mode
# -------------------------------------------------
TARGET="$1"
FILTER="${2:-UVW1}"
OUTPUT_IMG_NAME="${3:-data/processed/uvot_${TARGET}_${FILTER}.jpg}"

if [ -z "$TARGET" ]; then
    echo "Usage: ./run.sh <obsid> [filter] [output.jpg]" >&2
    echo "   or: ./run.sh batch --manifest ... --source-dir ..." >&2
    exit 1
fi

DATA_DIR="$PROJECT_DIR/data/processed/${TARGET}_${FILTER}"
echo "Project dir : $PROJECT_DIR"
echo "Output dir  : $DATA_DIR"
cd "$PROJECT_DIR"

echo "Running: python -u main.py $TARGET $FILTER"
python -u main.py "$TARGET" "$FILTER"

echo "Plotting with ds9"

input_img="$DATA_DIR/ObsCrop.fits"
ref_img="$DATA_DIR/RefCrop.fits"
diff_img="$DATA_DIR/imsum_crop.fits"
validsrc_file="$DATA_DIR/uvotDetect.reg"

for file in "$input_img" "$ref_img" "$diff_img" "$validsrc_file"; do
    if [ ! -s "$file" ]; then
        echo "Required pipeline output is missing or empty: $file" >&2
        exit 1
    fi
done

# Unset LD_LIBRARY_PATH so ds9 does not pick up HEASoft libraries
# that can conflict with its own.
env -u LD_LIBRARY_PATH ds9 \
    "$diff_img" -log -scale limits 1.5 400 \
    "$input_img" -log -scale limits 1.5 400 \
    "$ref_img" -log -scale limits 1.5 400 \
    -region load all "$validsrc_file" \
    -tile mode column \
    -saveimage jpeg "$OUTPUT_IMG_NAME"