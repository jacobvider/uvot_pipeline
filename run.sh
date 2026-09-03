
### @author: Jacob Vider, jacobisaacvider@gmail.com
### Date:   Wed Aug 26 2026
### Usage: ./run.sh target_observed filter output_filename.jpg
### Default batch: ./run.sh batch
### Custom batch: ./run.sh batch --manifest /path/to_process.log --source-dir /path/to/files
### Example: ./run.sh 30010013 UVW1 uvot_30010013_UVW1.jpg


# #check if conda is installed
# source "$(conda info --base)/etc/profile.d/conda.sh"
# conda activate uvot

# #check if ds9 is installed
# command -v ds9 >/dev/null || {
#     echo "DS9 is not installed or not in PATH."
#     exit 1
# }

#stops the script when a command fails
set -e

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
UVOT_ENVIRONMENT="uvot"
DEFAULT_HEADAS="/mnt/c/Users/jacob/heasoft-6.36/x86_64-pc-linux-gnu-libc2.39"

activate_uvot_environment() {
    if ! command -v conda >/dev/null 2>&1; then
        if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
            source "$HOME/miniconda3/etc/profile.d/conda.sh"
        else
            echo "Conda was not found. Start WSL with Miniconda available first." >&2
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
    if [ ! -f "$HEADAS/headas-init.sh" ] && [ -f "$DEFAULT_HEADAS/headas-init.sh" ]; then
        echo "Ignoring invalid HEADAS override: $HEADAS" >&2
        HEADAS="$DEFAULT_HEADAS"
    fi
    if [ ! -f "$HEADAS/headas-init.sh" ]; then
        echo "HEASoft initialization script was not found at: $HEADAS/headas-init.sh" >&2
        echo "Set HEADAS to your HEASoft installation and retry." >&2
        exit 1
    fi
    export HEADAS
    source "$HEADAS/headas-init.sh"
}

activate_uvot_environment
initialize_heasoft

# Batch mode processes every filename|version|EXTNAME entry and deliberately
# skips DS9: opening a window for each of hundreds of entries is not useful.
if [ "$1" = "batch" ]; then
    shift
    cd "$PROJECT_DIR"

    # With no extra arguments, process the files currently supplied to Codex.
    # Supply explicit arguments after ``batch`` to override these defaults.
    if [ "$#" -eq 0 ]; then
        set -- \
            --manifest /mnt/c/Users/jacob/Downloads/to_process.log \
            --source-dir /mnt/c/Users/jacob/AppData/Local/Temp \
            --allow-missing
    fi

    exec python -u main.py batch "$@"
fi

#user inputs the target
TARGET="$1"
#user can input the filter. if input is not specified, the filter will be UVW1
FILTER="${2:-UVW1}"
#user can input the output img file name. if name is not specified, it will be in this format
OUTPUT_IMG_NAME="${3:-data/processed/uvot_${TARGET}_${FILTER}.jpg}"

# find folder containing this code, and move to folder
DATA_DIR="$PROJECT_DIR/data/processed/${TARGET}_${FILTER}"
echo $PROJECT_DIR
echo $DATA_DIR
cd "$PROJECT_DIR"
##if folder already exists - does it create a new one?

#run main.py, with an input target and filter
echo "Run main.py <target> <filter> outputs to main.log"
python -u main.py "$TARGET" "$FILTER" 
echo "Plotting with ds9"

#set paths for input image, reference image, difference image, and region file
input_img="$DATA_DIR/ObsCrop.fits"
ref_img="$DATA_DIR/RefCrop.fits"
diff_img="$DATA_DIR/imsum_crop.fits"
validsrc_file="$DATA_DIR/uvotDetect.reg" #older archival image of the same sky region

for file in "$input_img" "$ref_img" "$diff_img" "$validsrc_file"; do
    if [ ! -s "$file" ]; then
        echo "Required pipeline output is missing or empty: $file"
        exit 1
    fi
done

set -x
env -u LD_LIBRARY_PATH ds9 \
    "$diff_img" -log -scale limits 1.5 400 \
    "$input_img" -log -scale limits 1.5 400 \
    "$ref_img" -log -scale limits 1.5 400 \
    -region load all "$validsrc_file" \
    -tile mode column \
    -saveimage jpeg "$output_img_name"


    #sw00014012162uuu_sk.img.gz|003|uu791523077I
