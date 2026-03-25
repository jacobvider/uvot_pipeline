# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 11:24:14 2023

@author: akordepa
"""
#------------------------------------------------------------------------------------------
# checkValidTransients
# Functionality: Uses uvotDetect.fits to obtain the ra and dec values detected from the
#                from the differenced image to determine which of the detected transients
#                pass through the criteria list
# Inputs: 
# 1. Reference image: path of reference file location
# 2. Ref image index: index of the reference image snapshot
# 3. Input image: path of input file location
# 4. Input image index: index of the input image snapshot
# 5. criteria: criteria list array (described below)
#    Criteria List Array: 
# =============================================================================
#     1.  Check if detected transient is within differenced image boundary sum of 2 pixel radius != 0
# 2. Check source ellipse properties:
#     1. (prof_major <= 4.0)  & (prof_minor >= 0.3) & ((prof_major/prof_minor) < 4
# 3. check significant detection
# 4. check if transient exists in reference image and input image- eliminate if in both
# 5. check if source is an already known source (simbad)
# 6. check for uvotdetect flags
# 7. Sum of flux around the center != 0, sum of flux around a pixel radius(1 pix radius) != 0 in reference and input image
# 8. Eliminate Sources within 0.005 degrees of reference image sources > 10 counts 

# =============================================================================
# Output: returns a list of transients which passed through each of the criteria
#         Writes the final list of transients which passed through all the given criteria 
#         to a .txt file and a .csv file with other decriptors  
#------------------------------------------------------------------------------------------
def checkValidTransients(ref, refInd, obs, obsInd, obsID, criteria, thresh,  arcsec_rad, LogFile, DataLoc):
    from astropy.table import Table
    from astropy.io import fits
    import numpy as np
    from astropy.wcs.utils import skycoord_to_pixel
    from astropy.wcs.utils import pixel_to_skycoord
    from astropy.coordinates import SkyCoord
    from astropy.wcs import WCS
    import astropy.units as u
    import heasoftpy as hsp
    import matplotlib.pyplot as plt
    
    
    hduld = fits.open(DataLoc + "output/"+ str(obsID)  + "_" + str(obsInd) +  '_imsum_crop.fits')
    hduld.info()
    print("check valid open imsum file:", hduld.info())
    hdrDiff = hduld[1].header
    dataDiff = hduld[1].data;
    
    hdul_det = fits.open(DataLoc + "output/"+ str(obsID) + "_" + str(obsInd) + "_uvotDetect.fits")
    hdul_det.info()
        
    evt_data = Table(hdul_det[1].data)
    
    dec_val = evt_data['DEC']
    ra_val  = evt_data['RA']
    prof_major = evt_data['PROF_MAJOR']
    prof_minor = evt_data['PROF_MINOR']
    flags = evt_data['FLAGS']
    rate = evt_data['RATE']
    rate_err= evt_data['RATE_ERR']

    ##ref image
    hdulR = fits.open(ref)
    hdulR.info()
    
          
    hdrR = hdulR[refInd].header
    N1R = hdulR[refInd].header['NAXIS1']
    N2R = hdulR[refInd].header['NAXIS2']
    dataR = hdulR[refInd].data; 
    
    ## input image
    hdulO = fits.open(obs)
    hdulO.info()
    
  
    hdrO = hdulO[obsInd].header
    N1O = hdulO[obsInd].header['NAXIS1']
    N2O = hdulO[obsInd].header['NAXIS2']
    dataO = hdulO[obsInd].data;
    
    sk= SkyCoord(ra_val*u.deg, dec_val*u.deg, unit = 'deg', frame = 'fk5') #transients in differenced image
    
    xo, yo = skycoord_to_pixel(sk, WCS(hdrO)); 
    xr, yr = skycoord_to_pixel(sk, WCS(hdrR)); 
    xd, yd = skycoord_to_pixel(sk, WCS(hdrDiff)); 
    
    if np.any(np.isnan(xo)) or  np.any(np.isnan(yo)) or  np.any(np.isnan(xr)) or  np.any(np.isnan(yr)) or  np.any(np.isnan(xd)) or  np.any(np.isnan(yd)):
        LogFile.write('Transient location not found in input or reference or differenced image|')
        return None, None,None,None,None,None,None,None,None
    
    arcsec_pix_conv = 1.04
   

    #%% CRITERIA 1
    #check for criteria 1 Check if it is within differenced image boundarysum of 2 pixel radius != 0
 
    validSrc1 = [];
    validSrc1Ind = [];
    if (1 in criteria):
        
        radius = 2;
        for i in range(np.size(xo)):
            
            if (0 < int(xo[i]) < N1O)and (0 < int(yo[i]) < N2O) and (0 < int(xr[i]) < N1R)and (0 < int(yr[i]) < N2R):
                if (np.sum(dataO[int(xo[i])-radius: int(xo[i]) + radius, int(yo[i])-radius :  int(yo[i])+radius]) != 0) and (np.sum(dataR[int(xr[i])-radius: int(xr[i]) +radius, int(yr[i])-radius:  int(yr[i])+radius]) != 0):
                   validSrc1.append(sk[i])
                   validSrc1Ind.append(i); #add in the indices
       
  
    
    #%% CRITERIA 2
     #   Check source ellipse properties:
    # 1. (prof_major <= 4.0)  & (prof_minor >= 0.3) & ((prof_major/prof_minor) < 4
 

    validSrc2 = [];
    validSrc2Ind = [];
    if (2 in criteria):
            
        indValidList = [];
        
        ##check for sum of pixels around center of each source
        
        indValidList.append(((prof_major <= 4.0 ) & (prof_minor >= 0.3) & ((prof_major/prof_minor) < 4)).nonzero())
        indEllipse = indValidList[0][0];
        
        for p in range(len(indEllipse)):
            validSrc2.append(sk[int(indEllipse[p])]);
            validSrc2Ind.append(int(indEllipse[p]));
         
       
       
#%%   ## CRITERIA 3
#check significant detection

    validSrc3 = [];
    validSrc3Ind = [];
    sigDet = [];
    if (3 in criteria):
        rate = evt_data['RATE']
        
        rate_err= evt_data['RATE_ERR']
        
        rate_ratio= rate/rate_err;
       
        
        sigDet.append((rate_ratio > 4.0).nonzero())
        sigDetList = sigDet[0][0];
   
        for p in range(len(sigDetList)):
            validSrc3.append(sk[int(sigDetList[p])])
            validSrc3Ind.append(int(sigDetList[p]));
       
  #%%    CRITERIA 4
  ##check if transient exists in reference image and input image

      
    validSrc4 = []; 
    validSrc4Ind = [];
    roundArrRa = [];
    roundArrDec = [];
    sameRefObs = [];
  
    if (4 in criteria):
     
            
        ## ref image 
        refDetect = str(ref) + '+' + str(refInd);
        
        uvotdetect= hsp.HSPTask('uvotdetect')
        uvotDetectOut = uvotdetect (infile= refDetect, outfile=DataLoc + "output/" + 'uvotDetect_ref.fits',regfile = DataLoc + "output/"+ 'uvotDetectRef_reg.reg', sexargs= '-BACK_TYPE AUTO -BACK_SIZE 32,32', expfile='NONE', zerobkg=2, plotsrc = 'no', threshold=thresh, chatter = 5, noprompt='True')
        print('\r\n')
        hdul_detRef = fits.open(DataLoc + "output/" +"uvotDetect_ref.fits")
        hdul_detRef.info()
            
        evt_data_Ref = Table(hdul_detRef[1].data)
        dec_val_Ref = evt_data_Ref['DEC']
        ra_val_Ref  = evt_data_Ref['RA']
        
        
      
        obsDetect = str(obs) + '+' + str(obsInd);##input image ind is 1
        
        #obsDetect = "Data/ObsCrop.fits" # use cropped images
        uvotdetect= hsp.HSPTask('uvotdetect')
        uvotDetectOut = uvotdetect (infile= obsDetect, outfile=DataLoc + "output/" +'uvotDetect_obs.fits',regfile = DataLoc + "output/"+ 'uvotDetectObs_reg.reg', sexargs= '-BACK_TYPE AUTO -BACK_SIZE 32,32', expfile='NONE', zerobkg=2, plotsrc = 'no', threshold=thresh, chatter = 5, noprompt='True')
        print('\r\n')
        hdul_detObs = fits.open(DataLoc + "output/" +"uvotDetect_obs.fits")
        hdul_detObs.info()
            
        evt_data_Obs = Table(hdul_detObs[1].data)
        dec_val_Obs = evt_data_Obs['DEC']
        ra_val_Obs  = evt_data_Obs['RA']
        flags_Obs = evt_data_Obs['FLAGS']
        mag_Obs = evt_data_Obs['MAG']
        mag_err_Obs = evt_data_Obs['MAG_ERR']
        #indflagObs = np.squeeze((flags_Obs != 0).nonzero())
        indflagObs = np.where(flags_Obs!=0)[0];
        
        
        for t in range(len(sk)): #for each source in differenced image, check if there is a detected object in ref and obs image
            validSrc4.append(sk[t]);
            validSrc4Ind.append(t);
        # Create SkyCoord objects for the input coordinates
            coord1Diff = SkyCoord(ra=sk[t].ra.deg*u.deg, dec=sk[t].dec.deg*u.deg, frame='fk5')
            coord2Ref= SkyCoord(ra=ra_val_Ref*u.deg, dec=dec_val_Ref*u.deg, frame='fk5') #coords list for Ref images
            coord2Obs= SkyCoord(ra=ra_val_Obs*u.deg, dec=dec_val_Obs*u.deg, frame='fk5') #coords list for Ref images
            # Calculate the angular separation
            angular_offset_arcsec_Ref = coord1Diff.separation(coord2Ref).arcsec
            angular_offset_arcsec_Obs = coord1Diff.separation(coord2Obs).arcsec
            
            
            # check if it is detected in input image (Transient must exist in input and differenced image)
            # if does not exist in input image, OR exists in both input and reference image remove from list 
            
            if ((any(angular_offset_arcsec_Obs < arcsec_rad) == False) or (any(angular_offset_arcsec_Ref < arcsec_rad) and any(angular_offset_arcsec_Obs < arcsec_rad))):
                validSrc4.remove(sk[t])
                validSrc4Ind.remove(t)
                                
            #else:
                #print(sk[t])
              
           
       
          
        
    #%% CRITERIA 5
    #check if source is an already known source
    from astroquery.simbad import Simbad
    
    validSrc5 = [];
    validSrc5Ind = [];
    if (5 in criteria):
      
        for p in range(len(sk)):
            validSrc5.append(sk[p])
            validSrc5Ind.append(p)
        
        for m in range(len(sk)):
            result_table = Simbad.query_region(sk[m], radius=7 * u.arcsec)
         
            if (result_table is None) :
                print('no source found:', sk[m])
            else:
               #print('source found:, m', sk[m], m) 
               validSrc5.remove(sk[m])
               validSrc5Ind.remove(m)
            
#%% CRITERIA 6 uvotdetect flags
    validSrc6 = [];
    validSrc6Ind = [];

    if ( 6 in criteria):
        validSrcInd6F = [];
       
       #validSrcInd6F = np.squeeze((flags == 0).nonzero())
        validSrcInd6F = np.where(flags == 0)[0]
        
       
        for p in range(len(validSrcInd6F)):
          
            validSrc6.append(sk[validSrcInd6F[p]])
            validSrc6Ind.append([validSrcInd6F[p]])
        
        # for r in range(len(validSrcInd6F2)):
        #     validSrc6.append(sk[validSrcInd6F2[r]])
        #     validSrc6Ind.append([validSrcInd6F2[r]])
        
        
         
#%% CRITERIA 7   Sum of flux around the center is not 0
## sum of flux around a pixel radius != 0 in reference and input image
    
    sumFlux = [];
    sumFluxArr = [];
    ind7 = [];
   
    intprof_major = (np.ceil(prof_major * arcsec_pix_conv)).astype(int);
    validSrc7 = [];
    validSrc7Ind = [];
    #switch x, y coords
    intyd = xd.astype(int)
    intxd = yd.astype(int)
    intyo = xo.astype(int)
    intxo = yo.astype(int)
    intyr = xr.astype(int)
    intxr = yr.astype(int)
    intprof_minor = prof_minor.astype(int)
    pixRad = 1;
      
    if (7 in criteria):
        for q in range(np.size(prof_major)):

           if (np.sum(dataDiff[intxd[q]-intprof_major[q]: intxd[q]+ intprof_major[q], intyd[q]- intprof_major[q]: intyd[q]+ intprof_major[q]]) != 0.0):
               so = np.sum(dataO[intxo[q]-pixRad: intxo[q]+ pixRad, intyo[q]- pixRad: intyo[q]+ pixRad]);
               sr = np.sum(dataR[intxr[q]-pixRad: intxr[q]+ pixRad, intyr[q]- pixRad: intyr[q]+ pixRad]);
              
               if (so  != 0.0 and sr != 0.0):
                        ind7.append(q)
                        
      
       
        for p in range(len(ind7)):
            validSrc7.append(sk[int(ind7[p])])
            validSrc7Ind.append([int(ind7[p])])

#%% CRITERIA 8 Remove sources around transients which are too brightin the ref image
    degRadius = 0.005;
    raDiff = [];
    decDiff = [];
    skBrightSrcDiff = [];

    if (8 in criteria):
        validSrc8 = [];
        validSrc8Ind = [];
        for p in range(len(sk)):
          validSrc8.append(sk[p])
          validSrc8Ind.append(p);
          raDiff.append(round(sk[p].ra.deg,5))
          decDiff.append(round(sk[p].dec.deg,5))
        
         ## ref image 
        refDetect = str(ref) + '+' + str(refInd);
        uvotdetect= hsp.HSPTask('uvotdetect')
        uvotDetectOut = uvotdetect (infile= refDetect, outfile=DataLoc + "output/" +'uvotDetect_ref.fits',regfile = 'uvotDetectRef_reg.reg', sexargs= '-BACK_TYPE AUTO -BACK_SIZE 32,32', expfile='NONE', zerobkg=2, plotsrc = 'no', threshold=thresh, chatter = 5, noprompt='True')
        print('\r\n')
        hdul_detRef = fits.open(DataLoc + "output/" +"uvotDetect_ref.fits")
        hdul_detRef.info()
            
        evt_data_Ref = Table(hdul_detRef[1].data)
        dec_val_Ref = evt_data_Ref['DEC']
        ra_val_Ref  = evt_data_Ref['RA']
        rateRef = evt_data_Ref['RATE']
        
               
        chkSrc= (rateRef > 10).nonzero()
        src = chkSrc[0];
       
       
        raSrc = np.round(np.asarray(ra_val_Ref[src]),5);
        decSrc = np.round(np.asarray(dec_val_Ref[src]),5);
        
        
        
        for k in range(len(raSrc)):  #check if this source is in diff image as well
            ind = [];
          
            coord1Diff = SkyCoord(ra=sk.ra.deg*u.deg, dec=sk.dec.deg*u.deg, frame='fk5')
            coord2Ref= SkyCoord(ra=raSrc[k]*u.deg, dec=decSrc[k]*u.deg, frame='fk5') #coords list for Ref images
            # Calculate the angular separation
            angular_offset_arcsec_Ref = coord1Diff.separation(coord2Ref).arcsec
            ind = np.where(angular_offset_arcsec_Ref < arcsec_rad)[0]
         
           
            for j in range(len(ind)):
                skBrightSrcDiff.append(sk[ind[j]]);
        
            
            for h in range(min(len(skBrightSrcDiff), len(src))): #for each bright source check surrounding transients
                for y in range(len(raDiff)):
                    
                    if (y != src[h]):
                        if ((raDiff[y] >  (skBrightSrcDiff[h].ra.deg - degRadius)) & (raDiff[y] <  (skBrightSrcDiff[h].ra.deg + degRadius)) & (decDiff[y] > (skBrightSrcDiff[h].dec.deg - degRadius)) & (decDiff[y] <  (skBrightSrcDiff[h].dec.deg + degRadius))):#0.001 deg ~ 3.6 arcsec
                            
                            if (sk[y] in validSrc8):  #if the source is not previously removed
                                validSrc8.remove(sk[y])
                                validSrc8Ind.remove(y);
 #%% if all criteria need to be met
    validSrcArr = [];
    validSrcArrInd = [];
    arr0 = [];
    arr0Ind = [];
    arrCmp = np.zeros((len(criteria), ))
    
    src1 = False;
    src2 = False;
    src3 = False;
    src4 = False;
    src5 = False;
    src6 = False;
    src7 = False;
    
    if criteria[0] == 1:
        arr0 = validSrc1.copy();
        arr0Ind = validSrc1Ind.copy();
    if criteria[0] == 2:
        arr0 = validSrc2.copy();
        arr0Ind = validSrc2Ind.copy();
    if criteria[0] == 3:
        arr0 = validSrc3.copy();
        arr0Ind = validSrc3Ind.copy();
    if criteria[0] == 4:
        arr0 = validSrc4.copy();
        arr0Ind = validSrc4Ind.copy();
    if criteria[0] == 5:
        arr0 = validSrc5.copy();
        arr0Ind = validSrc5Ind.copy();
    if criteria[0] == 6:
        arr0 = validSrc6.copy();
        arr0Ind = validSrc6Ind.copy();
    if criteria[0] == 7:
        arr0 = validSrc7.copy();
        arr0Ind = validSrc7Ind.copy();
    if criteria[0] == 8:
        arr0 = validSrc8.copy();
        arr0Ind = validSrc8Ind.copy();
        
      
    for p in range(np.size(arr0)):
        cnt = 0;
       
        sk0 = arr0[p];
        sk0Ind = arr0Ind[p];
        
        for i in range(len(criteria)):
            #print('i=', i )
            if criteria[i] == 1:
                arrCmp = validSrc1.copy();
                src1 = True
            if criteria[i] == 2:
                arrCmp = validSrc2.copy();
                src2 = True
            if criteria[i] == 3:
                arrCmp= validSrc3.copy();
                src3 = True
            if criteria[i] == 4:
                arrCmp = validSrc4.copy();
                src4 = True
            if criteria[i] == 5:
                arrCmp = validSrc5.copy();
                src5 = True
            if criteria[i] == 6:
                arrCmp = validSrc6.copy();
                src6 = True
            if criteria[i] == 7:
                arrCmp = validSrc7.copy();
                src7 = True
            if criteria[i] == 8:
                arrCmp = validSrc8.copy();
                src8 = True
            
              
       
        if (src1 == True and np.size(validSrc1) > 0): 
            for m in range(len(validSrc1)):
                if (sk0.ra.deg == validSrc1[m].ra.deg and sk0.dec.deg == validSrc1[m].dec.deg ):
                    cnt = cnt + 1;
                    
        
        if (src2 == True and np.size(validSrc2) > 0):
            for m in range(len(validSrc2)):
                if( sk0.ra.deg == validSrc2[m].ra.deg and sk0.dec.deg == validSrc2[m].dec.deg ):
                    cnt = cnt + 1;
                    
                    
        if (src3 == True and np.size(validSrc3) > 0):
            for m in range(len(validSrc3)):
                if( sk0.ra.deg == validSrc3[m].ra.deg and sk0.dec.deg == validSrc3[m].dec.deg ):
                    cnt = cnt + 1;
                    
                
        if (src4 == True and np.size(validSrc4) > 0):
            for m in range(len(validSrc4)):
                if( sk0.ra.deg == validSrc4[m].ra.deg and sk0.dec.deg == validSrc4[m].dec.deg ):
                    cnt = cnt + 1;
                    
                    
        if (src5 == True and np.size(validSrc5) > 0):
            for m in range(len(validSrc5)):
                if (sk0.ra.deg == validSrc5[m].ra.deg and sk0.dec.deg == validSrc5[m].dec.deg ):
                    cnt = cnt + 1;
                    
                    
        if (src6 == True and np.size(validSrc6) > 0):
            for m in range(len(validSrc6)):
                if(sk0.ra.deg == validSrc6[m].ra.deg and sk0.dec.deg == validSrc6[m].dec.deg ):
                    cnt = cnt + 1;
                    
                    
        if (src7 == True and np.size(validSrc7) > 0):
            for m in range(len(validSrc7)):
                if(sk0.ra.deg == validSrc7[m].ra.deg and sk0.dec.deg == validSrc7[m].dec.deg ):
                    cnt = cnt + 1;
                    
                    
        if (src8 == True and np.size(validSrc8) > 0):
            for m in range(len(validSrc8)):
                if(sk0.ra.deg == validSrc8[m].ra.deg and sk0.dec.deg == validSrc8[m].dec.deg ):
                    cnt = cnt + 1;         
                   
                    
       
        if (cnt == len(criteria)):
            validSrcArr.append(sk0)
            validSrcArrInd.append(sk0Ind)
        

                  
      #%% write to regions file
    from regions import CircleSkyRegion
    from regions import Regions    
 
    region_valid = [];
    
    for j in range(len(validSrcArr)):
        #src = CircleSkyRegion(validSrc3[j], radius=0.01 * u.deg)
        src = CircleSkyRegion(validSrcArr[j], radius=0.005 * u.deg)
        src.visual.valid_keys[0]= 'yellow'  
        region_valid.append(src)
    
    regs = Regions(region_valid);
    regs.write(DataLoc +"output/"+ str(obsID) + "_" + str(obsInd) +'validSrc.reg', format='ds9', overwrite = True)  
    
  
#%% get magnitude and magnitude error of the valid transient sources from input file
    mag_obs_arr = [];
    mag_obs_err_arr = [];
    for n in range(len(validSrcArr)):
        coordTransients = SkyCoord(ra=validSrcArr[n].ra.deg*u.deg, dec=validSrcArr[n].dec.deg*u.deg, frame='fk5')
        angular_offset_arcsec_Transients = coordTransients.separation(coord2Obs).arcsec
        indTransient = np.where((angular_offset_arcsec_Transients < arcsec_rad) == True)
        mag_obs_arr.append(mag_Obs[indTransient[0][0]]) #assume only 1 index is found where ra,dec of transient is within ra,dec of input 
        mag_obs_err_arr.append(mag_err_Obs[indTransient[0][0]])
    #%% write to a file
    
    eliminationList = open(DataLoc +"output/"+ "TransientEliminationLists_" + obsID + "_" + str(obsInd) + ".txt", "w")
    eliminationList.write('Passed Criteria 1\n')
    eliminationList.write(str(validSrc1))
    eliminationList.write('\n')
    
    eliminationList.write('Passed Criteria 2\n')
    eliminationList.write(str(validSrc2))
    eliminationList.write('\n')
    
    eliminationList.write('Passed Criteria 3  \n')
    eliminationList.write(str(validSrc3))
    eliminationList.write('\n')
    
    eliminationList.write('Passed Criteria 4\n')
    eliminationList.write(str(validSrc4))
    eliminationList.write('\n')
    
    eliminationList.write('Passed Criteria 5 \n')
    eliminationList.write(str(validSrc5))
    eliminationList.write('\n')
    
    eliminationList.write('Passed Criteria 6 \n')
    eliminationList.write(str(validSrc6))
    eliminationList.write('\n')
    
    eliminationList.write('Passed Criteria 7 \n')
    eliminationList.write(str(validSrc7))
    eliminationList.write('\n')
    
    eliminationList.write('Passed Criteria 8\n')
    eliminationList.write(str(validSrc8))
    eliminationList.write('\n')
    
    eliminationList.write('Passed all criteria \n')
    eliminationList.write(str(validSrcArr))
    eliminationList.write('\n')
    
    eliminationList.close()
   
    #%% Write a table to file
    
    from tabulate import tabulate
    
    #'input image', 'input image exp ID', 'reference image', 'ref image exp ID', 'object target', 
    headers = ['ra', 'dec', 'rate', 'rate error', 'major axis', 'minor axis', 'flags']
    table = zip(ra_val[validSrcArrInd], dec_val[validSrcArrInd], rate[validSrcArrInd], rate_err[validSrcArrInd], prof_major[validSrcArrInd], prof_minor[validSrcArrInd], flags[validSrcArrInd])
    tb = tabulate(table, headers=headers, floatfmt=".4f")
       
    
    summaryChart = open(DataLoc + "output/"+ 'TransientSourceSummary.txt', 'a') #write text file
    summaryChart.write('Input Image:')
    summaryChart.write(str(obs))
    summaryChart.write(', ')
    summaryChart.write(str(hdulO[obsInd].name))
    summaryChart.write('\n')
    summaryChart.write('Input Image Exposure Time:')
    summaryChart.write(str(hdulO[obsInd].header['EXPOSURE']))
    summaryChart.write('\n')
    summaryChart.write('Reference Image:') 
    summaryChart.write(str(ref))
    summaryChart.write(', ')
    summaryChart.write(str(hdulR[refInd].name))
    summaryChart.write('\n')
    summaryChart.write('Reference Image Exposure Time:')
    summaryChart.write(str(hdulR[refInd].header['EXPOSURE']))
    summaryChart.write('\n')
    summaryChart.write('Object:' )
    summaryChart.write(str(hdulO[obsInd].header['OBJECT']))
    summaryChart.write('\n')
    summaryChart.write('\n')
    summaryChart.write(tb);
    summaryChart.write('\n')
    summaryChart.write('\n')
    summaryChart.write('\n')
    summaryChart.close();
    
    #%%
    import csv
    lenValid = len(validSrcArrInd)
    raValid = ra_val[validSrcArrInd];
    decValid = dec_val[validSrcArrInd];
    
    with open(DataLoc + "output/"+ 'TransientSourceSummary.csv', 'a', newline='') as csvfile:
        summaryChart = csv.writer(csvfile, delimiter=',')
        summaryChart.writerow(['Input Image:', str(obs ), str(hdulO[obsInd].name)])
        summaryChart.writerow(['Reference Image:', str(ref), str(hdulR[refInd].name), str(hdulR[refInd].name)])
        summaryChart.writerow(['Object:', str(hdulO[obsInd].header['OBJECT'])])
        summaryChart.writerow(['Target ID:', str(hdulO[obsInd].header['TARG_ID'])])
        summaryChart.writerow(['Input Image Exposure Time:', str(hdulO[obsInd].header['EXPOSURE'])])
        summaryChart.writerow(['Reference Image Exposure Time:',  str(hdulR[refInd].header['EXPOSURE'])])
        summaryChart.writerow(['RA', 'DEC', 'Rate', 'Rate Error', 'Major Axis', 'Minor Axis', 'Flags'])
        for i in range(lenValid):
           
            summaryChart.writerow([raValid[i], decValid[i], rate[i],rate_err[i], prof_major[i], prof_minor[i], flags[i] ])
    
            ## write number of transients detected for each obs id
    with open(DataLoc +"output/"+ 'TransientsDetected.csv', 'a', newline='') as csvfile2:
        summaryChart = csv.writer(csvfile2, delimiter=',')
        #summaryChart.writerow(['Object', 'Number of Transients Detected'])
        summaryChart.writerow([str(hdulO[obsInd].header['OBJECT']), str(lenValid)])
    #%%
    # print('valid src1:', validSrc1)
    # print('valid src2:', validSrc2)
    # print('valid src3:', validSrc3)
    # print('valid src4:', validSrc4)
    # print('valid src5:', validSrc5)
    # print('valid src6:', validSrc6)
    # print('valid src7:', validSrc7)
    # print('valid src8:', validSrc8)
    # print('valid src all:', validSrcArr)
    
    return validSrc1, validSrc2, validSrc3, validSrc4, validSrc5, validSrc6, validSrc7, validSrc8, validSrcArr, mag_obs_arr, mag_obs_err_arr
    
    
    