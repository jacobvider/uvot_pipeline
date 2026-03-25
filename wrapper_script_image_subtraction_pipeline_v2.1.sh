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
# Choose display number unlikely to be used
setenv DISPLAY :420
set xvfb_pid = "" #virtal frame buffer

# Check whether DISPLAY is already usable
/bin/xdpyinfo -display $DISPLAY >& /dev/null
if ( $status == 0 ) then
    echo "Reusing existing, working Xvfb on $DISPLAY"
else
    echo "No usable Xvfb on $DISPLAY — starting fresh one"

    # Clean up stale socket/lock if present
    if ( -e /tmp/.X11-unix/X420 ) then
        rm -f /tmp/.X11-unix/X420
    endif
    if ( -e /tmp/.X420-lock ) then
        rm -f /tmp/.X420-lock
    endif

    Xvfb $DISPLAY -screen 0 1920x1080x24 &
    set xvfb_pid = $!
    sleep 2

    # Verify Xvfb actually works
    /bin/xdpyinfo -display $DISPLAY >& /dev/null
    if ( $status != 0 ) then
        echo "ERROR: Xvfb failed to start correctly"
        if ( "$xvfb_pid" != "" ) then
            kill $xvfb_pid >& /dev/null
        endif
        exit 1
    endif
endif



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


### --- Cleanup ---
if ( "$xvfb_pid" != "" ) then
    echo "Stopping Xvfb (PID $xvfb_pid)"
    kill $xvfb_pid
endif

exit $python_exit
