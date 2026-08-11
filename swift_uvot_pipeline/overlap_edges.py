def edgeDetect(obs, obsInd, ref, refInd):
    import numpy as np
    import subprocess
    from astropy.io import fits
    from astropy.wcs.utils import skycoord_to_pixel
    from astropy.wcs.utils import pixel_to_skycoord
    from astropy.coordinates import SkyCoord
    from astropy.wcs import WCS
    from astropy.visualization import ZScaleInterval
    import matplotlib.pyplot as plt
    import astropy.units as u
    from astropy.coordinates import Angle
        
    #%%
    #ref = "Data/sw00031752016uuu_sk.img.gz" 
    
    #refInd = 1;
    
        
    hdulR = fits.open(ref)
    hdulR.info()
      
    hdrR = hdulR[refInd].header
    
    RA =  hdulR[refInd].header['RA_PNT']
    DEC =  hdulR[refInd].header['DEC_PNT']
    ASP = hdulR[refInd].header['ASPCORR']
    TGID = hdulR[refInd].header['TARG_ID']
    exposure = hdulR[refInd].header['EXPOSURE']
    PA_PNT = hdulR[refInd].header['PA_PNT']
    N1 = hdulR[refInd].header['NAXIS1']
    N2 = hdulR[refInd].header['NAXIS2']
    
    rot_angle = PA_PNT + 118.8 + 0.4 ;
    dataR1 = hdulR[refInd].data;
    xr, yr = np.shape(dataR1)
    
    x = np.arange(N1)
    y = np.arange(N2)
    X, Y = np.meshgrid(x, y)
    skCoordRef= pixel_to_skycoord(X, Y, WCS(hdrR))
    raR = skCoordRef.ra 
    decR = skCoordRef.dec 
        
            
    hdulO = fits.open(obs)
    hdulO.info()
      
    hdrO = hdulO[obsInd].header
    
    RA =  hdulO[obsInd].header['RA_PNT']
    DEC =  hdulO[obsInd].header['DEC_PNT']
    ASP = hdulO[obsInd].header['ASPCORR']
    TGID = hdulO[obsInd].header['TARG_ID']
    exposure = hdulO[obsInd].header['EXPOSURE']
    PA_PNT = hdulO[obsInd].header['PA_PNT']
    N1 = hdulO[obsInd].header['NAXIS1']
    N2 = hdulO[obsInd].header['NAXIS2']
    
    rot_angle = PA_PNT + 118.8 + 0.4 ;
    dataO1 = hdulO[obsInd].data;
    xo, yo = np.shape(dataO1)
    
    x2 = np.arange(N1)
    y2 = np.arange(N2)
    X2, Y2 = np.meshgrid(x2, y2)
    skCoordObs = pixel_to_skycoord(X2, Y2, WCS(hdrO))
    raO = skCoordObs.ra 
    decO = skCoordObs.dec 
    
    #%%
    if np.min(raR) > np.min(raO):
        RaValidMin = np.min(raR);
    else:
        RaValidMin =np.min(raO);
        
    if np.min(decR) > np.min(decO):
        DecValidMin = np.min(decR);
    else:
        DecValidMin = np.min(decO);
        
    if np.max(raR) < np.max(raO):
        RaValidMax = np.max(raR);
    else:
        RaValidMax =np.max(raO);
        
    if np.max(decR) < np.max(decO):
        DecValidMax = np.max(decR);
    else:
        DecValidMax = np.max(decO);
    
    skMin= SkyCoord(RaValidMin, DecValidMin)
    skMax= SkyCoord(RaValidMax, DecValidMax)
    
    pixRx1, pixRy1 = skycoord_to_pixel(skMin, WCS(hdrR)); 
    pixOx1, pixOy1 = skycoord_to_pixel(skMin, WCS(hdrO)); 
    
    pixRx2, pixRy2 = skycoord_to_pixel(skMax, WCS(hdrR)); 
    pixOx2, pixOy2 = skycoord_to_pixel(skMax, WCS(hdrO)); 
    
    xLimObs = [None]* 2
    yLimObs = [None]* 2
    xLimRef= [None]* 2
    yLimRef = [None]* 2
    
    cut = 100;
    
    xLimObs[0]= int(pixOx2)+cut
    xLimObs[1]= int(pixOx1)-cut
    yLimObs[0]= int(pixOy1)+cut
    yLimObs[1]= int(pixOy2)-cut
    
    xLimRef[0]= int(pixRx2)+cut
    xLimRef[1]= int(pixRx1)-cut
    yLimRef[0]= int(pixRy1)+cut
    yLimRef[1]= int(pixRy2)-cut
    
       
    return  xLimObs , yLimObs, xLimRef, yLimRef