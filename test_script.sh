#!/usr/bin/env bash


#sudo apt update
#sudo apt install saods9
#sudo apt install tcllib

set -e
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate uvot
PROJECT_DIR="/mnt/c/Users/jacob/research/uvot_pipeline"
echo $PROJECT_DIR
cd "$PROJECT_DIR"
echo "Run main.py"
#previous image files tried
# python -u main.py 30009002 "UVW1">> main.log 2>&1
# python -u main.py 30009005 "UVW1"
python -u main.py 30010013 "UVW1"

echo "main.py outputs to main.log"
echo "Plotting with ds9"

#image files are in data/processed
DATA_DIR="data/processed"

input_img="$DATA_DIR/ObsCrop.fits"
ref_img="$DATA_DIR/RefCrop.fits"
diff_img="$DATA_DIR/imsum_crop.fits"
validsrc_file="$DATA_DIR/uvotDetect.reg"

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
