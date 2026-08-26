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
# echo "Run archive.py"
# python uvot_io/archive.py
# echo "Run processing.py"
# python processing.py
echo "Run main.py"
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

# input_img="$DATA_DIR/$1"
# echo $1
# #i think its ObsCrop.fits = input image
# ref_img="$DATA_DIR/$2"
# echo $2
# ##i think its RefCrop.fits = reference image
# diff_img="$DATA_DIR/$3"
# echo $3
# # imsum_crop.fits: combined ObsCrop and RefCrop output from uvotimsum
# transient_loc=$4
# echo $4
# #transient sky coordinate (ra,dec)
# output_img_name="$DATA_DIR/$5"
# echo $5
# #name of output jpg image (eg. output.jpg)
# validsrc_file="$DATA_DIR/$6"
# echo $6
# echo "$validsrc_file"
# #uvotDetect.reg i think?


set -x
# env -u LD_LIBRARY_PATH ds9 "$diff_img" -log -scale limits 1.5 400 wcs fk5 -invert \
#     "$input_img" -log -scale limits 1.5 400 -invert -pan to $transient_loc wcs fk5\
#     # -zoom to 2 -pan to $transient_loc wcs fk5 \
#     "$ref_img" -log -scale limits 1.5 400 -invert \
#     -grid grid color black \
#     -grid numlab color red \
#     -grid axes color red \
#     -grid tick color red \
#     -grid skyformat degrees \
#     -grid yes \
#     -frame prev \
#     -match frame wcs \
#     -region load all "$validsrc_file" \
#     -tile mode column \
#     -saveimage jpeg "$output_img_name" \
#     # -exit

env -u LD_LIBRARY_PATH ds9 \
    "$diff_img" -log -scale limits 1.5 400 -invert \
    "$input_img" -log -scale limits 1.5 400 -invert \
    "$ref_img" -log -scale limits 1.5 400 -invert \
    -region load all "$validsrc_file" \
    -tile mode column \
    -saveimage jpeg "$output_img_name"