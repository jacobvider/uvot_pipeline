@author: Jacob Vider, jacobisaacvider@gmail.com
Date:   Wed Aug 26 2026

./test_script.sh "ra dec" filename.jpg
Useage: ./test_script.sh "ra dec" filename.jpg
"""

#sudo apt update
#sudo apt install saods9
#sudo apt install tcllib

set -e
TARGET="${1:-30010013}"
FILTER="${2:-UVW1}"
OUTPUT_IMG_NAME="${3:-data/processed/uvot_detection.jpg}"

# assign project directory
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

#is conda iunstalled? check
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate uvot
PROJECT_DIR="/mnt/c/Users/jacob/research/uvot_pipeline"
echo $PROJECT_DIR
cd "$PROJECT_DIR"
# python uvot_io/archive.py
# python processing.py

#is ds9 installed? 
command -v ds9 >/dev/null || {
    echo "DS9 is not installed or not in PATH."
    exit 1
}

python -u main.py "$TARGET" "$FILTER"

#runs all scripts that main.py depends on
#code is commented out, unless this is the first run
: <<'COMMENT'
for script in uvot_io/archive.py uvot_io/fits.py processing.py detection.py registration.py subtraction.py; do
    python "$script" &
done
wait
COMMENT


echo "Run main.py <target> <filter>"
python -u main.py 30010013 "UVW1"
python -u main.py "$TARGET" "$FILTER"

echo "main.py outputs to main.log"
echo "Plotting with ds9"

#image files are in data/processed
DATA_DIR="data/processed"
OUTPUT_IMG_NAME="${3:-data/processed/uvot_detection_{TARGET}.jpg}"

input_img="$DATA_DIR/ObsCrop.fits"
ref_img="$DATA_DIR/RefCrop.fits"
