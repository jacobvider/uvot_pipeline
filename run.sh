
### @author: Jacob Vider, jacobisaacvider@gmail.com
### Date:   Wed Aug 26 2026
### Usage: ./run.sh target_observed filter output_filename.jpg
### Example: ./run.sh 30010013 UVW1 uvot_30010013_UVW1.jpg


#check if conda is installed
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate uvot

#check if ds9 is installed
command -v ds9 >/dev/null || {
    echo "DS9 is not installed or not in PATH."
    exit 1
}

#stops the script when a command fails
set -e
#user inputs the target
TARGET="$1"
#user can input the filter. if input is not specified, the filter will be UVW1
FILTER="${2:-UVW1}"
#user can input the output img file name. if name is not specified, it will be in this format
OUTPUT_IMG_NAME="${3:-data/processed/uvot_${TARGET}_${FILTER}.jpg}"

# find folder containing this code, and move to folder
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$PROJECT_DIR/data/processed/${TARGET}_${FILTER}"
echo $PROJECT_DIR
echo $DATA_DIR
cd "$PROJECT_DIR"

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
