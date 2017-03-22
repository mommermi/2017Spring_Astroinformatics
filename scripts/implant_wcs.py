"""implant wcs information into image header

adjust values below accordingly and the script will implant this
information into all FITS files in the same directory

michael.mommert@nau.edu, Mar 21, 2017
"""

import os
from astropy.io import fits

for filename in os.listdir('.'):
    if not '.fits' in filename:
        continue

    print(filename)
    
    hdu = fits.open(filename, mode='update')
    header = hdu[0].header

    header['CRTYPE1'] = 'RA---TAN'
    header['CRTYPE2'] = 'DEC--TAN'    
    header['CRPIX1'] = 1016 # use center of field x axis
    header['CRPIX2'] = 1016 # use center of field y axis
    header['CRVAL1'] = 120.676375 # use RA of center of field
    header['CRVAL2'] = 56.50191666666667 # use Dec of center of field
    header['CD1_1'] = -0.00010416 # pixel scale (arcsec/px) / 3600
    header['CD1_2'] = 0 # 0 if no field rotation
    header['CD2_1'] = 0 # 0 if no field rotation   
    header['CD2_2'] = 0.00010416 # pixel scale (arcsec/px) / 3600

    hdu.flush()

