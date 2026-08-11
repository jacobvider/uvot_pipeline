#!/bin/tcsh

echo "Home is: $HOME"
echo "User is: `whoami`"
echo "ENV:"
env

echo "pwd before cd: "
pwd

### --- Set TMPDIR to a directory on the same filesystem as /data/uvot ---
setenv TMPDIR /data/uvot/tmp

### --- Change working directory to the pipeline directory ---
cd /data/uvot/image_subtraction_pipeline_to_process/Python_Code
echo "pwd after cd: "
pwd

### --- Initialize HEASoft environment ---
source /software/lheasoft/release/x86_64-pc-linux-gnu-libc2.28/headas-init.csh
#source /software/lheasoft/release6.34/x86_64-pc-linux-gnu-libc2.28/headas-init.csh

### --- Ensure Python sees uvot_tdrss2's packages ---
setenv PYTHONPATH /Home/eud/uvot_tdrss2/.local/lib/python3.10/site-packages:$PYTHONPATH

### --- Run the pipeline ---
#/usr1/local/anaconda3/ana310/bin/python /data/uvot/image_subtraction_pipeline_to_process/Python_Code/run_transient_detect_LiveList_uvot_tdrss.py
/usr1/local/anaconda3/ana310/bin/python run_transient_detect_LiveList_uvot_tdrss.py
