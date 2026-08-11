#!/usr1/local/anaconda3/ana310/bin/python
#/usr1/local/python3/miniforge3/bin/python
# -*- coding: utf-8 -*-


###uvot tdrsss - runs uvot data

"""
Created on Tue Mar  5 13:30:27 2024

@author: akordepa
"""

from heasoft_uvot_detect_func_uvot_tdrss import transient_detect 
from checkValidTransients_uvot_tdrss import checkValidTransients
from pandas import *
import numpy as np
import subprocess
import csv
from astropy.io import fits
from datetime import datetime
import os
import shutil
   
print('import statements working')
print('get data')
data = read_csv('/mnt/c/Users/jacob/research/spring_2026/image_subtraction_pipeline_to_process/to_process.log',
                sep='|', header=None)
print(data)

InputImg = data.iloc[:,0]
ExtName = data.iloc[:,2]
arcSecRadius = 4;
thresh_sigma = 5;
criteriaArr = [1,2,3,4,6,7,8]
numRows = len(InputImg);
print('num rows=', numRows)
# DataFiles_Loc = '/Users/jacob/research/spring_2026/image_subtraction_pipeline_to_process/'
# OutputFiles_Loc = '/Users/jacob/research/spring_2026/image_subtraction_pipeline/' 


DataFiles_Loc = '/mnt/c/Users/jacob/research/spring_2026/image_subtraction_pipeline_to_process/'
OutputFiles_Loc = '/mnt/c/Users/jacob/research/spring_2026/image_subtraction_pipeline/'


LogName = '/mnt/c/Users/jacob/research/spring_2026/image_subtraction_pipeline_to_process/Processing_log.csv'
TransientList = '/mnt/c/Users/jacob/research/spring_2026/image_subtraction_pipeline/DetectedTransients_log.txt'
SpuriousTransientList = '/mnt/c/Users/jacob/research/spring_2026/image_subtraction_pipeline/SpuriousTransients_log.txt'

# LogName = DataFiles_Loc + 'Processing_log.csv'
#tells what happens to each image file
#swift has only looked at ~12% of the sky in u-band filter - if you put in a random coordinate, will likley have no data
#every time that swift finds a transient and goes through all track -> adds to file
# TransientList = OutputFiles_Loc + 'DetectedTransients_log.txt'
# SpuriousTransientList =  OutputFiles_Loc + 'SpuriousTransients_log.txt'

#when pipeline runs, it will start printing stuff into terminal
print('\n\n\n##### NEW RUN AT ' + str(datetime.now()))  # Noel - for log file readability

#opens log list, processes columns
with open (LogName, 'a') as LogFile, open(TransientList, 'a') as transientMaster, open(SpuriousTransientList, 'a') as SpuriousTransients:
    transientSrcMaster = csv.writer(transientMaster, delimiter=',')  
    SpuriousTransientSrcMaster = csv.writer(SpuriousTransients, delimiter=',')  
    
    for i in range(numRows):
        print('i=', i)
        #open input file to get number of extensions. Run transient detect on all extensions
        try:
            hdul = fits.open(DataFiles_Loc + InputImg[i])
            num_extensions = len(hdul)
        except FileNotFoundError:
            print(f"Error: The file '{InputImg[i]}' was not found.")
            num_extensions = 0;
        except OSError as e:
            # This catches other FITS-related errors, like corrupted files or invalid formats
            print(f"Error opening FITS file '{InputImg[i]}': {e}")
            num_extensions = 0;
        except Exception as e:
            # Catch any other unexpected exceptions
            print(f"An unexpected error occurred: {e}")
            num_extensions = 0;
            
       
        # create a log file 
     
        #for j in range(1, num_extensions): #index 0 is primary so start with 1
        LogFile.write("\n")
        LogFile.write(str(InputImg[i]))
        LogFile.write("|")
        LogFile.write(str(ExtName[i]))
        LogFile.write("|")
        
        
        extension_name = ExtName[i];
        
        if (num_extensions == 0): # file not found
            LogFile.write("File Not Found |")
            continue
        
        
        #get extension number from extension name
        for k, hdu in enumerate(hdul):
                    
            if 'EXTNAME' in hdu.header and hdu.header['EXTNAME'] == extension_name:
                j = k
               
            else:
               if k == num_extensions:
                    LogFile.write("Image Extension Not Found |")
                    exit
                
        filt = hdul[j].header['FILTER']
        exposure = hdul[j].header['EXPOSURE']
        
        if (filt != 'U'):
            LogFile.write("Input Image Invalid Filter |")
            # write to log and exit
            exit
        elif (exposure < 60):
            # write to log and exit
            LogFile.write("Input Image Exposure < 60 |")
            #LogFile.write("\n")
            exit
        else:
            ext_name = hdul[j].name
            print('j=', j)
            print('ext name', ext_name)
           
        
            refImg, refInd, obsID, refID, Input_Info_List, Ref_Info_List = transient_detect(DataFiles_Loc + str(InputImg[i]), j, DataFiles_Loc + str(InputImg[i]),'yes',0, 'no', thresh_sigma, 0, LogFile, DataFiles_Loc) #obsName, obsInd, refName, refQuery, refQueryPeriod, plot, thresh, filtSigma, log file
            
            if (refImg !=None): # if no archival ref image is found, set valid src array to None
                validSrc1, validSrc2, validSrc3, validSrc4, validSrc5, validSrc6, validSrc7, validSrc8, validSrcArr,  mag_obs_arr, mag_obs_err_arr = checkValidTransients(refImg, refInd, DataFiles_Loc + str(InputImg[i]), j, obsID, criteriaArr, thresh_sigma, arcSecRadius, LogFile, DataFiles_Loc ) 
               
                if (validSrcArr != None ):
                    if len(validSrcArr)> 0 :
                        LogFile.write(str(len(validSrcArr)) + ' transients found |')
                        # if transients are found, create an output directory
                        try:
                            os.mkdir(str(OutputFiles_Loc) + str(obsID)+ "_" + ext_name)
                            #create txt file with information of transients for given obs ID and extension
                                 
                        except FileExistsError:
                                print("Directory ", str(OutputFiles_Loc) + str(obsID) + "_" + ext_name, " already exists.")
                    else:
                        LogFile.write('No transients found |')
            # plot for each transient detected
                    if len(validSrcArr)> 0 :
                        with open(str(OutputFiles_Loc)  + str(obsID)+ "_" + ext_name + "/" + str(obsID)+ "_" + ext_name + '.csv', 'a', newline='') as transientSrcInfo:
                            transientSrcCSV = csv.writer(transientSrcInfo, delimiter=',')
                            transientSrcCSV.writerow(['Transient RA', 'Transient DEC', 'Transeint Mag', 'Transeint Mag Error', 'Input Image Obs ID', 'Input Image Extension', 'Input Image Start Time', 'Input Image Exposure Time','Src #', 'Transient RA_DEC distance from Archival Image Object RA_DEC', 'Archival Image Obs ID', 'Archival Image Extension', 'Archival Image Start Time', 'Archival Image Exposure', 'Transient Source Number', 'Run_Time'])
                            for m in range(len(validSrcArr)):   
                                print ('m=', m)
                               	# run bash script for saving images
                                DiffImg = DataFiles_Loc+ "output/" + str(obsID) + "_" + str(j) + "_imsum_crop.fits"
                                TransientLoc = str(validSrcArr[m].ra.deg) + " " + str(validSrcArr[m].dec.deg)
                                ra_str = str(np.round(validSrcArr[m].ra.deg, 3)) + "," + str(np.round(validSrcArr[m].dec.deg, 3))
                                coord1InputObj = Input_Info_List[4];
                                arc_dist = (coord1InputObj.separation(validSrcArr[m]).arcsec) / 60; #arcmin separation
                                Output_Name = str(obsID) + "_" + str(ext_name) + "_" + "transientSrc" + str(m) + ".jpeg"
                                ############ Write transient info to csv file #############
                                cur_datetime = datetime.now()
                                transientSrcCSV.writerow([validSrcArr[m].ra.deg, validSrcArr[m].dec.deg, mag_obs_arr[m], mag_obs_err_arr[m], str(Input_Info_List[1]), str(ext_name), str(Input_Info_List[0]),  str(Input_Info_List[3]), str(m), str(round(arc_dist,2)), str(Ref_Info_List[1]), str(Ref_Info_List[2]), str(Ref_Info_List[0]), str(Ref_Info_List[3]), str(cur_datetime)])
                                
                                if len(validSrcArr) > 15: # if number of transients > 15, write them to a spurious transients file
                                    SpuriousTransientSrcMaster.writerow([validSrcArr[m].ra.deg,validSrcArr[m].dec.deg,  mag_obs_arr[m], mag_obs_err_arr[m], str(Input_Info_List[1]), str(ext_name), str(Input_Info_List[0]),  str(Input_Info_List[3]), str(m), str(round(arc_dist,2)), str(Ref_Info_List[1]), str(Ref_Info_List[2]), str(Ref_Info_List[0]), str(Ref_Info_List[3]), str(cur_datetime)])              
                                else:
                                   transientSrcMaster.writerow([validSrcArr[m].ra.deg,validSrcArr[m].dec.deg,  mag_obs_arr[m], mag_obs_err_arr[m], str(Input_Info_List[1]), str(ext_name), str(Input_Info_List[0]),  str(Input_Info_List[3]), str(m), str(round(arc_dist,2)), str(Ref_Info_List[1]), str(Ref_Info_List[2]), str(Ref_Info_List[0]), str(Ref_Info_List[3]), str(cur_datetime)])              
                                
                                ValidSrc_file = DataFiles_Loc + "output/" + str(obsID) + "_" + str(j) + "validSrc.reg"
                                InputImg_gen = DataFiles_Loc + str(InputImg[i]) + "[" + str(j) + "]";
                                RefImg_gen = str(refImg) + "[" + str(refInd) + "]";
                                args = [InputImg_gen,RefImg_gen,DiffImg,TransientLoc,Output_Name, ValidSrc_file];
                                print ("output name:", Output_Name)
                                subprocess.call(["./create_ds9_img.sh", args[0], args[1], args[2], args[3], args[4], args[5]])
                                 
                                if os.path.exists(str(OutputFiles_Loc) + str(obsID) + "_" + ext_name) and m == 0: #if processing the first transient, and if folder exists remove the folder
                                    shutil.rmtree(str(OutputFiles_Loc) + str(obsID) + "_" + ext_name + "/", ignore_errors=True)
                                 
                                if os.path.exists(Output_Name):
                                    shutil.move(Output_Name, str(OutputFiles_Loc) + str(obsID) + "_" + ext_name + "/")
                                else:
                                    LogFile.write('DS9 did not generate Transient ' + str(m) + ' image|')
                   
            hdul.close()
            #LogFile.write('\n')
LogFile.close()


#%% uncomment for live pipelin
#Remove data folders to save space

current_datetime = datetime.now()
#Data folder
if os.path.exists(DataFiles_Loc + "/Data"):
    shutil.rmtree(DataFiles_Loc + "/Data")
    os.mkdir(DataFiles_Loc + "/Data")
else:
    print("Data folder Not Deleted")
    
#output folder
if os.path.exists(DataFiles_Loc + "/output"):
    # first rename the folder
    shutil.move(DataFiles_Loc + "/output", DataFiles_Loc + "/output" + str(current_datetime) )
    shutil.move(DataFiles_Loc + "/output" + str(current_datetime), DataFiles_Loc + "/done_intermediate-images_to-delete")
    os.mkdir(DataFiles_Loc + "/output")
else:
    print("Output folder Not Moved")
    
# to_process.log

# if os.path.exists(DataFiles_Loc + "/to_process.log"):
#     shutil.move(DataFiles_Loc + "/to_process.log", DataFiles_Loc + "/to_process" + str(current_datetime) + ".log")
# else:
#     print("to_process log Not renamed")

# move all the input files and the log file
for i in range(numRows):
    if os.path.exists(DataFiles_Loc + str(InputImg[i])):
        if os.path.exists(DataFiles_Loc + "done_input-images_to-delete/" + str(InputImg[i])) :
            os.remove(DataFiles_Loc + "done_input-images_to-delete/" + str(InputImg[i]))
        shutil.move(DataFiles_Loc + str(InputImg[i]), DataFiles_Loc + "done_input-images_to-delete")
