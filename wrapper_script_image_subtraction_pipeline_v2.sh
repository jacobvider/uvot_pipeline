#!/bin/tcsh

### --- Cron Diagnostics ---
#echo "pwd: `pwd`"
#echo "Home is: $HOME "
#echo "User is: `whoami`"
#echo " "
#echo "ENV: "
#env
#echo " "



### --- Set TMPDIR to a directory on the same filesystem as /data/uvot ---
setenv TMPDIR /data/uvot/tmp



### --- Change working directory to the pipeline directory ---
cd /data/uvot/image_subtraction_pipeline_to_process/Python_Code
#echo "pwd after cd: `pwd`"



### --- Start private Xvfb virtual display (for ds9 -saveimage calls)
# Choose display number unlike to be used
setenv DISPLAY :420

# Check if the display socket is in use
if ( -e /tmp/.X11-unix/X420 ) then
    echo "ERROR: Display $DISPLAY is already in use."
    exit 1
endif

# Check if Xvfb is already running on this display
set Xvfb_running = `ps -ef | grep "Xvfb $DISPLAY" | grep -v grep | wc -l`
if ($Xvfb_running > 0) then
    echo "ERROR: Xvfb already running on $DISPLAY"
    exit 1
endif

# Start Xvfb
echo "Starting Xvfb on DISPLAY $DISPLAY..."
#Xvfb $DISPLAY -screen 0 1920x1080x24 >& /tmp/xvfb_image_subtraction.log &
Xvfb $DISPLAY -screen 0 1920x1080x24 &
set xvfb_pid = $!


# Small delay to ensure Xvfb is ready
sleep 1
echo "Started Xvfb on DISPLAY $DISPLAY ."

### --- Initialize HEASoft environment ---
#source /software/lheasoft/release6.34/x86_64-pc-linux-gnu-libc2.28/headas-init.csh
source /software/lheasoft/release/x86_64-pc-linux-gnu-libc2.28/headas-init.csh
echo "Sourced HEASoft."

### --- Ensure Python sees uvot_tdrss2's packages ---
setenv PYTHONPATH /Home/eud/uvot_tdrss2/.local/lib/python3.10/site-packages:$PYTHONPATH
echo "setenv'ed PYTHONPATH."

### --- Run the pipeline ---
#/usr1/local/anaconda3/ana310/bin/python /data/uvot/image_subtraction_pipeline_to_process/Python_Code/run_transient_detect_LiveList_uvot_tdrss.py
echo "starting python wrapper script..."
/usr1/local/anaconda3/ana310/bin/python run_transient_detect_LiveList_uvot_tdrss.py
set python_exit = $status
echo "finished python wrapper script."


### --- Shut down Xvfb after Python finishes ---
if ( $xvfb_pid > 0 ) then
    echo "Stopping Xvfb (PID $xvfb_pid)"
    kill $xvfb_pid
endif

exit $python_exit
