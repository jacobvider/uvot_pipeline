#!/bin/bash

# ----------------------------------
# Activate conda environment
# ----------------------------------
source ~/miniconda3/etc/profile.d/conda.sh
conda activate venv

# ----------------------------------
# Configure HEASoft
# ----------------------------------
export HEADAS=/mnt/c/Users/jacob/heasoft-6.36/x86_64-pc-linux-gnu-libc2.39
source $HEADAS/headas-init.sh

# ----------------------------------
# Go to your project
# ----------------------------------
cd /mnt/c/Users/jacob/research

echo "Environment ready!"
echo "Conda environment: $(conda info --envs | awk '/\*/ {print $1}')"
echo "HEADAS: $HEADAS"
echo "ftcopy: $(which ftcopy)"
echo "heasoftpy: $(python -c 'import heasoftpy; print(heasoftpy.__file__)')"

# Uncomment to automatically launch your pipeline
# python -m uvot_pipeline.main