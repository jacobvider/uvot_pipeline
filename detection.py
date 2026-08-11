
from pathlib import Path
import heasoftpy as hsp
from astropy.table import Table


def detect_sources(
    difference_image,          # Input difference image (FITS)
    output_dir="data/processed",  # Directory where outputs will be written
    threshold=5,               # Detection threshold in sigma
):
    """
    Run HEASoft uvotdetect on a difference image.

    Parameters
    ----------
    difference_image : str or Path
        Difference image produced by uvotimsum.

    output_dir : str or Path
        Directory for output products.

    threshold : float
        Detection threshold (sigma).
    """

    # Convert the input filename into a Path object
    difference_image = Path(difference_image)

    # Convert the output directory into a Path object
    output_dir = Path(output_dir)

    # Create the output directory if it does not already exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Output FITS catalog containing detected sources
    output_fits = output_dir / "uvotDetect.fits"

    # DS9 region file showing detected source locations
    output_region = output_dir / "uvotDetect.reg"

    # ---------------------------------------------------------
    # Remove outputs from a previous run so uvotdetect starts
    # with a clean directory.
    # ---------------------------------------------------------

    # Delete the previous source catalog if it exists
    if output_fits.exists():
        output_fits.unlink()

    # Delete the previous DS9 region file if it exists
    if output_region.exists():
        output_region.unlink()

    # Print progress information
    print("Running source detection...")
    print(f"Input: {difference_image}")

    # Create a Python wrapper around the HEASoft uvotdetect task
    uvotdetect = hsp.HSPTask("uvotdetect")

    # ---------------------------------------------------------
    # Run uvotdetect
    # ---------------------------------------------------------

    result = uvotdetect(

        # Input difference image
        infile=str(difference_image),

        # Output FITS source catalog
        outfile=str(output_fits),

        # Output DS9 region file
        regfile=str(output_region),

        # Additional SExtractor options
        # Estimate the background automatically using
        # 32×32 pixel background meshes.
        sexargs="-BACK_TYPE AUTO -BACK_SIZE 32,32",

        # No separate exposure map supplied
        expfile="NONE",

        # Treat zero-valued pixels as background
        zerobkg=2,

        # Do not create diagnostic plots
        plotsrc="no",

        # Detection significance threshold (sigma)
        threshold=threshold,

        # Verbosity level
        chatter=5,

        # Run non-interactively
        noprompt="True",

        # Overwrite existing output files
        clobber="yes",
    )

    # Print the full HEASoft execution result
    print(result)

    if result.returncode != 0:
        print(f"WARNING: uvotdetect failed (return code {result.returncode})")
        print(result.stdout)
        return None, None

    if not output_fits.exists():
        print(f"WARNING: {output_fits} was not created.")
        return None, None

    if not output_region.exists():
        print(f"WARNING: {output_region} was not created.")
        return None, None

    # Occasionally uvotdetect exits without creating its outputs.
    # Check that the expected files actually exist.
    if not output_fits.exists():
        print(
            f"WARNING: uvotdetect did not create {output_fits}. "
            "Skipping this observation."
        )
        return None, None

    if not output_region.exists():
        print(
            f"WARNING: uvotdetect did not create {output_region}. "
            "Skipping this observation."
        )
        return None, None

    # Inform the user that source detection finished successfully
    print("Detection complete.")

    # Print the location of the output FITS catalog
    print(f"Catalog : {output_fits}")

    # Print the location of the DS9 region file
    print(f"Regions : {output_region}")

    # Return both output filenames so the next stage of the
    # pipeline can use them

    catalog = Table.read(output_fits)

    return catalog, output_region
# def detect_sources(difference_image):
#     """
#     Detect sources in a difference image.
#     """

#     print("Running source detection...")
#     print(f"Input: {difference_image}")

#     # TODO: run uvotdetect

#     return None

# # -*- coding: utf-8 -*-
# """
# Created on Thu Mar  2 12:21:58 2023

# @author: akordepa
# """

# #----------------------------------------------------------------------------------------------------------------------------------------------------------
# # transient_detect
# # Functionality: Detects transients using image differencing, given an input and reference image
# #                If a reference image needs to be queried, a parameter input is required to enable querying
# #                The longest snapshot of the given reference image is used
# # Inputs: 
# #    1. Input image name: path location of name
# #    2. Input image snapshot index : integer index
# #    3. Reference image name: path location of name
# #    4. Reference image querying: 1- enabled querying, 0- disable querying
# #    5. Reference image query period: minimum number of days before/after an input image to query reference image
# #    6. plot: 'yes' or 'no': turn on/off matplot lib plotting
# #    7. thresh: integer threshold for uvotdetect
# #    8. filtSigma: sigma for gaussian filtering of cropped image, if '0': no filtering 
# # Output: returns the queried image with the snapshot index or if querying is not enabled, returns the given reference image with the snapshot index
# #--------------------------------------------------------------------------------------------------------------------------------------------------------
# # import matplotlib.pyplot as plt
# import numpy as np
# from astropy.io import fits
# # import wget 
# from astropy.wcs import WCS
# # import astropy.wcs
# # from astropy.visualization import ZScaleInterval
# # import heasoftpy as hsp
# # from astroquery.heasarc import Heasarc
# from astropy.coordinates import SkyCoord
# import astropy.units as u
# # from astropy.time import Time
# #from find_overlap3 import findOverlap
# from overlap_edges import edgeDetect
# import os
# from scipy.ndimage import gaussian_filter
# from astropy.table import Table
 


# def load_input_image(obsName, DataLoc):

#     FilePath = DataLoc + "output/"
#     # Assume same image file location as working directly
#     # delete any pre-existing files
 
#     if (os.path.isfile(DataLoc + "Data/Obs.fits")):
#         os.remove(DataLoc + "Data/Obs.fits")  ##remove pre-existing file
#     if (os.path.isfile(DataLoc+ "Data/Obs1.fits")):

#         os.remove(DataLoc + "Data/Obs1.fits") 

#     if (os.path.isfile(FilePath+ "Data/ObsCrop.fits")):
#         os.remove(FilePath + "Data/ObsCrop.fits")  
        
#     if (os.path.isfile(DataLoc +"Data/Ref.fits")):
#         os.remove(DataLoc +"Data/Ref.fits")  ##remove pre-existing file
#     if (os.path.isfile(DataLoc +"Data/Ref1.fits")):
#         os.remove(DataLoc +"Data/Ref1.fits") 
#     if (os.path.isfile(FilePath +"Data/RefCrop.fits")):
#         os.remove(FilePath +"Data/RefCrop.fits")  
    
#     if (os.path.isfile(FilePath +"imsum_crop.fits")):
#         os.remove(FilePath +"imsum_crop.fits")   
        
#     if (os.path.isfile(FilePath +"uvotDetect.fits")):
#         os.remove(FilePath +"uvotDetect.fits") 
#     if (os.path.isfile(FilePath +"uvotDetect_ref.fits")):
#         os.remove(FilePath +"uvotDetect_ref.fits")
#     if (os.path.isfile(FilePath +"uvotDetect_obs.fits")):
#         os.remove(FilePath +"uvotDetect_obs.fits")
  
#     if (os.path.isfile(FilePath +"uvotDetect_reg.reg")):
#         os.remove(FilePath +"uvotDetect_reg.reg")
#     if (os.path.isfile(FilePath +"uvotDetectObs_reg.reg")):
#         os.remove(FilePath +"uvotDetectObs_reg.reg")
#     if (os.path.isfile(FilePath +"uvotDetectRef_reg.reg")):
#         os.remove(FilePath +"uvotDetectRef_reg.reg")
#     # open input image
       
#     hdulO = fits.open(obsName)
#     # hdulO.info()
    
#     hdrO = hdulO[obsInd].header
#     RA =  hdulO[obsInd].header['RA_PNT']
#     DEC =  hdulO[obsInd].header['DEC_PNT']
#     #ASP = hdulO[obsInd].header['ASPCORR']
#     TGID = hdulO[obsInd].header['TARG_ID']
#     exposure = hdulO[obsInd].header['exposure']
#     obsImg_obsID = hdulO[obsInd].header['OBS_ID']
#     print(obsImg_obsID)
#     obsID_extName = hdulO[obsInd].header['extname']
    
#     tstart = hdrO['TSTART']
#     tstop = hdrO['TSTOP']
#     MJDREFI = hdrO['MJDREFI']
#     MJDREFF = hdrO['MJDREFF']



#     expO = exposure;
#     #gets image data
#     dataO1 = hdulO[obsInd].data; 
     
#     #gets image size
#     [dx, dy] = np.shape(dataO1);
   
#     #computes central region
#     xLim = [int(dx/2 - dx/3), int(dx/2 + dx/3)] 
#     yLim = [int(dy/2 - dy/3), int(dy/2 + dy/3)] 
    
#     #gets obs time
#     startTimeInputStr = hdrO['DATE-OBS']
#     ExposureInputStr = str(round(exposure, 1)) + "s";

#     #creates sky coordinate
#     obj_skcoord_Input = SkyCoord(ra=RA*u.deg, dec=DEC*u.deg, frame='fk5')
#     #builds a list
#     Input_Info_List = [startTimeInputStr, obsImg_obsID, obsInd, ExposureInputStr, obj_skcoord_Input]
#     return Input_Info_List
    
# def detect_transients(obsInd, refName, refQuery, refQueryPeriod, plot, thresh, filtSigma, LogFile, DataLoc):


#     #%% reference image querying
    
#     if (refQuery == 'yes'): # 0: reference image is given, 1: query for a reference image
#         #%% query for a good reference image
#         heasarc = Heasarc()
        
#         mission = 'swiftuvlog'   # you can change this (or undefine it) to search other missions/tables/logs
        
       
#         coords = SkyCoord(RA*u.deg,DEC*u.deg, frame='icrs')
#         try:
#             table = heasarc.query_region(coords, mission=mission, radius='6 arcmin', fields=' OBSID,RA,DEC, START_TIME,EXPOSURE, ASP_CORR, EXTNAME, FILTER',  sortvar='exposure')
     
#         except:
#             table = Table() #if no table found, create an empty table
           
#         #%%
        
#         if len(table) > 0:
#             print("COLUMNS:", table.colnames)
#             # obsNumList = table['OBSID']
#             # Exposure = table['exposure']
#             # Asp = table['asp_corr'] # aspect correction
#             # filt_band =  table['filter']
#             # refExtName = table['extname']
#             obsNumList = table['obsid']
#             Exposure = table['exposure']
#             Asp = table['asp_corr']
#             filt_band = table['filter']
#             refExtName = table['extname']
            
#             tabRow = np.where(obsNumList == obsImg_obsID);
          
#             tstartRef = table['start_time']

#             # tstartRef = table['start_time']
#             tstartObs = MJDREFI + MJDREFF + (tstart/86400)
           
#             table.colnames
#             tableRows =len(table)
            
#     ####double-check observation filtering algorithm - print table before and after filtering?
#     #may have rejected images in they were too close in time 
#     #make sure pipeline doesnt reject things just because they were recent
            
#             if (tableRows > 0):
#                 tableInd = tableRows -1;
                
#                 # beginTimemjd = table[tableInd]['start_time']
#                 beginTimemjd = table[tableInd]['start_time']

                
#                 c = True; ## default true, if it goes in the while loop- it is true
#                 while ([((np.abs(tstartObs - float(beginTimemjd)) < refQueryPeriod) or Asp[tableInd] == 'N' or (60140 < float(beginTimemjd) < 60402) or Exposure[tableInd] < 60 or refExtName[tableInd] == obsID_extName or filt_band[tableInd].strip() != 'U')]):#1. if time between input and ref images is less than refquery period or 2. asp corr is not true or 3. 15th july 2023 < ref image start time < 2 april 2024, eliminate row or exposure < 60
#                             print('table ind:', tableInd)        
#                             # if all((np.abs(tstartObs - float(beginTimemjd)) > refQueryPeriod) and  Asp[tableInd] == 'Y' and not(60140 < float(beginTimemjd) < 60402) and Exposure[tableInd] > 60 and refExtName != obsID_extName and filt_band[tableInd] == 'U'):
#                             #     break;
#                             # else:
#                             if c == False:
#                                 break;
#                             if (tableInd > 0) :   
#                                 tableInd -= 1;
#                                 # beginTimemjd = table[tableInd]['start_time']
#                                 beginTimemjd = table[tableInd]['start_time']
#                                 c1 = (np.abs(tstartObs - float(beginTimemjd)) < refQueryPeriod) 
#                                 c2 =  Asp[tableInd] == 'N' 
#                                 c3 =  (60140 < float(beginTimemjd) < 60402) 
#                                 c4 = Exposure[tableInd] < 60 
#                                 c5 = refExtName[tableInd] == obsID_extName 
#                                 c6 = filt_band[tableInd].strip() != 'U'
#                                 c = c1 or c2 or c3 or c4 or c5 or c6
#                                 #print('filt band:', filt_band[tableInd].strip())
                                
#                             else:
#                               LogFile.write('Archival image does not satisfy requirements |')
#                               return None, None, None, None, None, None
                         
                    
                    
#                 t = Time(beginTimemjd, format='mjd')
#                 beginTime = t.to_value('datetime')
#                 year = beginTime.year
#                 month = beginTime.month
#                 dayRef = beginTime.day;
              
               
#                 obsNum =  table[tableInd]['obsid']
#                 #print('table len:' , len(table))
#                 print('table Ind:', tableInd)
#             ## difference in time start and ref image > 1 or 2 week converterd seconds 
           
#                 if month < 10:
#                    mth = "0"+ str(month)
#                 else:
#                    mth = str(month)
        
        
#                 #%% download the queried image
#                 site_url = "https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/"+ str(year)+ "_"+  mth + "/"  + str(obsNum) + "/uvot/image/sw" + str(obsNum)+ "uuu_sk.img.gz";
#                 print("Archival Image URL:", site_url)
#                 #wget -q -nH --no-check-certificate --cut-dirs=5 -r -l0 -c -N -np -R 'index*' -erobots=off --retr-symlinks imgLink
#                 import os
#                 if (os.path.isfile(DataLoc + "Data/"+ "sw" +str(obsNum)+ "uuu_sk.img.gz")):
#                     refImgExp = "sw" + str(obsNum)+ "uuu_sk.img.gz";
#                     #os.rename(refImgExp, DataLoc + "Data/"+ refImgExp)
#                     queryRef = DataLoc + "Data/"+ refImgExp;
#                 else:
#                     try:
#                         refImgExp  = wget.download(site_url, out = DataLoc + "Data/")
#                         #os.rename(refImgExp, DataLoc + "Data/"+ refImgExp)
#                         queryRef = refImgExp;
#                     except:
#                         LogFile.write("Could not download archival image |")
#                         return None, None, None, None, None, None;
#             else:
#                 print("Query results = None")
#                 LogFile.write('Could not find archival image |')
#                 return None, None, None, None, None, None #if there is no reference image,exit this function
#         else:
#             print("Query results = None")
#             LogFile.write('Could not find archival image |')
#             return None, None, None, None, None, None
# #%%
#     if (refQuery == 'yes'):
#         refImg = queryRef;
#     else:
#         refImg= refName;
#     #%% open reference image and find a snapshot with the longest exposure
#     print("ref Name:", queryRef)
#     hdul = fits.open(refImg)
#     hdul.info()
#     #Find snapshot in refImgExp with the given exposure
#     expArr =np.zeros(len(hdul)-1)
#     for entry in range(1, len(hdul)):
#         expArr[entry-1] = hdul[entry].header['exposure']
        
        
#     [maxExpRef] = np.where(expArr == np.max(expArr))
#     indRef = int(maxExpRef[0])+1
     
#     hdrR = hdul[indRef].header
#     RA =  hdul[indRef].header['RA_PNT']
#     DEC =  hdul[indRef].header['DEC_PNT']
#     TGID = hdul[indRef].header['TARG_ID']
#     Exposure_Ref = hdul[indRef].header['exposure']
#     refImg_obsID = hdul[indRef].header['OBS_ID']
#     ref_extension = hdul[indRef].name
    
#     tstart = hdrR['TSTART']
#     tstop = hdrR['TSTOP']
#     expR = Exposure_Ref;
    
#     ra_obj = hdrR['RA_OBJ']
#     dec_obj = hdrR['DEC_OBJ']
    
#     #obj_skcoord = SkyCoord(ra=ra_obj*u.deg, dec=dec_obj*u.deg, frame='fk5')
#     obj_skcoord = SkyCoord(ra=RA*u.deg, dec=DEC*u.deg, frame='fk5')
    
#     startTimeRefStr = hdrR['DATE-OBS']    
#     ExposureRefStr = str(round(Exposure_Ref, 1)) + "s";
#     Ref_Info_List = [startTimeRefStr, refImg_obsID, ref_extension, ExposureRefStr, obj_skcoord ]
#     dataR1 = hdul[indRef].data;
#     [dx, dy] = np.shape(dataR1);
#     xLim = [int(dx/2 - dx/3), int(dx/2 + dx/3)] 
#     yLim = [int(dy/2 - dy/3), int(dy/2 + dy/3)] 
    
#     #find overlap
#     cropImg =  hsp.HSPTask('ftcopy')
   
  
#     xLimO, yLimO, xLimR, yLimR = edgeDetect( obsName, obsInd, refImg, indRef )
    
   
    
#     #crop input image
#     Lim = '[' + str(xLimO[0]) + ':' + str(xLimO[1]) + ',' +  str(yLimO[0]) + ':' + str(yLimO[1]) + ']'
   
#     cropImg(infile = str(obsName) + '[' + str(obsInd) + ']'  + Lim, outfile = DataLoc +'Data/ObsCrop' + '_'+ str(obsImg_obsID) + '_' + str(obsInd) + '.fits')
    
#     ONewPix1 = xLimO[1] - xLimO[0];
#     ONewPix2 = yLimO[1] - yLimO[0];
    
#     ctrPixOX = round(ONewPix1/2)
#     ctrPixOY = round(ONewPix2/2)
#     wo = WCS(hdrO)
#     skyOrig = wo.pixel_to_world(560, 502.5)
#     skyO = wo.pixel_to_world(ctrPixOX, ctrPixOY)
    
   
#     #crop ref image
#     Lim = '[' + str(xLimR[0]) + ':' + str(xLimR[1]) + ',' +  str(yLimR[0]) + ':' + str(yLimR[1]) + ']'
   
#     cropImg(infile = str(refImg) + '[' + str(indRef) + ']' + Lim, outfile = DataLoc +'Data/RefCrop' + '_'+ str(refImg_obsID) + '_' + str(indRef) +'.fits') 

#     RNewPix1 = xLimR[1] - xLimR[0];
#     RNewPix2 = yLimR[1] - yLimR[0];
    
#     ctrPixRX = round(RNewPix1/2)
#     ctrPixRY = round(RNewPix2/2)
    
#     wr = WCS(hdrR)
#     skyR = wr.pixel_to_world(ctrPixRX, ctrPixRY)
    
#     ## update header extension name
#     with fits.open(DataLoc +'Data/ObsCrop' + '_'+ str(obsImg_obsID) + '_' + str(obsInd) +'.fits', mode='update') as hdulOU:
#          hdulOU[1].header['extname'] = hdrO['extname'] + "_Input"
 
        
#     if (filtSigma != 0):
#     # filter the cropped images
#     #input image
#         with fits.open(DataLoc +'Data/ObsCrop' + '_'+ str(obsImg_obsID) + '_' + str(obsInd) + '.fits', mode='update') as hdulOU:
#         # Change something in hdul.
#             dataOC = hdulOU[1].data; 
#             filterData = gaussian_filter(dataOC, sigma=filtSigma)
#             hdulOU[1].data = filterData;
#             hdulOU.flush()  # chanuges are written back to original.fits
            
#         with fits.open(DataLoc + 'Data/RefCrop' + '_'+ str(refImg_obsID) + '_' + str(indRef) + '.fits', mode='update') as hdulRU:
#         # Change something in hdul.
#             dataRC = hdulRU[1].data; 
#             filterDataR = gaussian_filter(dataRC, sigma=filtSigma)
#             hdulRU[1].data = filterDataR;
#             hdulRU.flush()  # changes are written back to original.fits
# #%% bring both images on the same exposure scale
#     if expO > expR:
#         dataO = dataO1 * (expR/expO)
#         dataR = dataR1;
#         ex = 0;
        
#     else:
#         dataR = dataR1 * (expO/expR)
#         dataO = dataO1;  
#         ex = 1;
    
# #%% Plot reference and observed images

#     if (plot == 'yes'):
#         wcs = WCS(hdrR)
        
#         #plot reference image
#         z = ZScaleInterval()
#         z1,z2 = z.get_limits(dataR1)
#         plt.figure()
#         ax = plt.subplot(projection=wcs)
#         plt.imshow(dataR1, vmin=z1, vmax=z2, origin='lower')
#         plt.grid(color='white', ls='solid')
#         ax = plt.gca()
#         #ax.coords[0].set_ticklabel_position('l')
#         #ax.coords[1].set_ticklabel_position('b')
#         ra = ax.coords[0]
#         dec = ax.coords[1]
#         ax.coords[0].set_axislabel('RA')
#         ax.coords[1].set_axislabel('DEC')
#         plt.xlabel('RA')
#         plt.ylabel('DEC')
#         plt.title('Ref Image')
#         plt.colorbar();
        
#         plt.savefig(FilePath +'Reference_Image.png')
#         #plot input image
#         wcs = WCS(hdrO)
        
#         z = ZScaleInterval()
#         z1,z2 = z.get_limits(dataO1)
        
#         plt.figure()
#         plt.subplot(projection=wcs)
#         plt.imshow(dataO1, vmin=z1, vmax=z2, origin='lower')
#         plt.grid(color='white', ls='solid')
#         ax = plt.gca()
#         #ax.coords[0].set_ticklabel_position('l')
#         #ax.coords[1].set_ticklabel_position('b')
#         ra = ax.coords[0]
#         dec = ax.coords[1]
#         ax.coords[0].set_axislabel('RA')
#         ax.coords[1].set_axislabel('DEC')
#         plt.xlabel('RA')
#         plt.ylabel('DEC')
#         plt.title('Input Image')
#         plt.colorbar();


#         plt.savefig(FilePath +'Input_Image.png')
 
   

#     #%%write weights file
   
#     obsFile = obsName;
#     refFile = refName;
   
#     f = open(FilePath +'uvotimsum_weights.txt', 'w')
#     for ext in range(1, len(hdulO)):
      
#         if (ext == 1): ## assuming extension 1 in obs file is used
#                 if ex == 0:
#                     f.write(hdulO[ext].name + ":" + str(1.0* (expR/expO))  + "\n")
#                 else:
#                     f.write(hdulO[ext].name + ":" + str(1.0) + "\n")
                   
#         else:
#                 f.write(hdulO[ext].name + ":" + str(0.0) + "\n")
                
#     for ext in range(1, len(hdul)):
      
#          if (ext == indRef): ## assuming extension 1 in obs file is used
#              if ex == 1 : 
#                  f.write(hdul[ext].name + ":" + str(-1.0 * (expO/expR)) + "\n")
#              else:
#                  f.write(hdul[ext].name + ":" + str(-1.0) + "\n")
#          else:
#                 f.write(hdul[ext].name + ":" + str(0.0) + "\n")
                
#     f.close()
#     #%% do uvot subtraction using heasoft tools
#     import os
#     if (os.path.isfile(FilePath + str(obsImg_obsID) + "_" + str(obsInd) + '_imsum_crop.fits')):
#         os.remove(FilePath + str(obsImg_obsID) + "_" + str(obsInd)  + '_imsum_crop.fits')  ##remove pre-existing file
#     uvotimsum = hsp.HSPTask('uvotimsum')
#     #inDir = obsFile + ',' + refFile
#     inDir = DataLoc +'Data/ObsCrop'  + '_'+ str(obsImg_obsID) + '_' + str(obsInd) + '.fits' + ',' + DataLoc + 'Data/RefCrop'  + '_'+ str(refImg_obsID) + '_' + str(indRef) +'.fits' ## if using cropped images
   
#     result = uvotimsum(infile = inDir, outfile= FilePath + str(obsImg_obsID) + "_" + str(obsInd)  + '_imsum_crop.fits', method = 'GRID', weightfile= FilePath + 'uvotimsum_weights.txt', exclude='NONE', ignoreframetime= 'yes')
#     if (result.returncode != 0):
#         LogFile.write("UVOTIMSUM Error: " + str(result.returncode) +"|")
#         print("\n### Error info here:")
#         print("return code = " + str(result.returncode)) # Noel - for bug fixing
#         print("result.stdout = " + str(result.stdout))	# Noel - for bug fixing
#         print("result.stderr = " + str(result.stderr) + "\n")	# Noel - for bug fixing
#         return None, None, None, None, None, None;
#     else:
#         uvotDetectFile = FilePath + str(obsImg_obsID) + "_" + str(obsInd)  + '_imsum_crop.fits'
    
# #%% plot differenced image

#     if (plot == 'yes'):
#         test = uvotDetectFile
#         hdult = fits.open(test)
#         hdult.info()
#         hdrt = hdult[1].header
        
#         datat = hdult[1].data;
        
#         wcs = WCS(hdrt)
        
#         z = ZScaleInterval()
#         z1,z2 = z.get_limits(datat)
#         plt.figure()
#         ax = plt.subplot(projection=wcs)
#         plt.imshow(datat, vmin=z1, vmax=z2, origin='lower')
#         plt.grid(color='white', ls='solid')
#         ax = plt.gca()
#         #ax.coords[0].set_ticklabel_position('l')
#         #ax.coords[1].set_ticklabel_position('b')
#         ra = ax.coords[0]
#         dec = ax.coords[1]
#         ax.coords[0].set_axislabel('RA')
#         ax.coords[1].set_axislabel('DEC')
#         plt.xlabel('RA')
#         plt.ylabel('DEC')
#         plt.title('uvot differenced')
#         plt.colorbar();

#         plt.savefig(FilePath +'Differenced_Image.png')
#     #%% run uvot detect
#     if (os.path.isfile(FilePath + str(obsImg_obsID) + "_" + str(obsInd) + "_uvotDetect.fits")):
#         os.remove(FilePath + str(obsImg_obsID) + "_" + str(obsInd) + "_uvotDetect.fits")  ##remove pre-existing file
#     if (os.path.isfile(FilePath + str(obsImg_obsID) + "_" + str(obsInd) + "_uvotDetect_reg.reg")):
#         os.remove(FilePath + str(obsImg_obsID) + "_" + str(obsInd) + "_uvotDetect_reg.reg")    
#     uvotdetect= hsp.HSPTask('uvotdetect')
#     uvotDetectOut = uvotdetect (infile= uvotDetectFile, outfile= FilePath + str(obsImg_obsID)+ "_" + str(obsInd) +'_uvotDetect.fits',regfile = FilePath  + str(obsImg_obsID) + '_uvotDetect_reg.reg', sexargs= '-BACK_TYPE AUTO -BACK_SIZE 32,32', expfile='NONE', zerobkg=2, plotsrc = 'no', threshold=thresh, chatter = 5, noprompt='True')
#     print('\r\n')


#     return refImg, indRef, obsImg_obsID, refImg_obsID, Input_Info_List, Ref_Info_List

  
# # def subtract_images()

# # def register_images()
