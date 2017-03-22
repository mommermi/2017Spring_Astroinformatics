FITS Image Registration and Co-Adding
=====================================

This tutorial was taught as part of Prof. Trujillo's Astroinformatics
(Spring 2017) class at NAU.


The easiest way to get all the files of this tutorial is to clone this
repository:

    > git clone https://github.com/mommermi/2017Spring_Astroinformatics.git

Sample data can be found in the ``/data`` directory, auxiliary scripts
are located in ``/scripts``, and all the parameter and configuration
files are located in ``/setup``.

Motivation
----------

Image registration allows for a direct translation between image
coordinates and sky coordinates. This translation is defined using the
`FITS World Coordinates System`_ (WCS) information that is stored in
the header of FITS files; software like `SAO DS9`_, `astropy.wcs`_, or
`Aladin`_ can use WCS information to provide the translation.
Although being incredibly useful for image analysis purposes, most
observatories do not provide WCS by default.


Image Registration
------------------

Deriving accurate WCS information is a complicated process, which
involves matching a source catalog of the image with an
astrometrically calibrated star catalog. There are two open-source
tools that we will use as part of this course to register FITS Images.


Astrometry.net
~~~~~~~~~~~~~~

Astrometry.net is a widely used and extremely successful tools that
does not require any information except the image file itself to
perform the image registration. You can upload your image file to the
website and download the registered image, or have a local
installation of the software on your system. You can upload images on
this `website`_.

The disadvantage of astrometry.net is that it more or less represents
a black box. It is fully automated and uses a tailored star catalog,
the uncertainties of which are not fully known, which becomes a
problem if accurate positions (e.g., asteroid astrometry) are
required.

If you just require a decent astrometric calibration and have few
image files, uploading images to astrometry.net might be the easiest
way to go.


SCAMP
~~~~~

The `SCAMP software`_ provides more flexibility in the registration
process by allowing the user to select a calibration catalog and other
settings. This document provides a quick introduction on how to use
SCAMP, using the sample data provided with this repository.

Image Preparation
.................

SCAMP requires some rough WCS information for each image, specifically
the field center coordinates (in both pixel and sky coordinates) and
the pixel scale. The sample data already have some WCS information,
which are not very accurate: there is an offset of about 11
arcminutes. Let's discuss the required FITS header keyqords quickly
for one of the sample images:

* ``CTYPE1`` and ``CTYPE2``: the projection type in RA (axis 1) and
  Dec (axis 2); we use gnomonic projection, hence: ``CTYPE1 =
  RA---TAN`` and ``CTYPE2 = DEC--TAN``
* ``CRPIX1`` and ``CRPIX2``: the image coordinates of the reference
  point (usually the center of the field; for the sample data: (1015,
  1015))
* ``CRVAL1`` and ``CRVAL2``: the sky coordinates of the reference
  point (we can use the ``RA`` and ``DEC`` values in the header
  converted into degrees: (120.676375, 56.50191666666667))
* ``CDX_Y``: the `CD matrix`_, defining image scale and rotation; in
  the case of the sample data, we assume no image rotation use:

  - ``CD1_1 = -0.0001042``: moving one pixel to the right in the
    image reduces RA by 0.375 arcsec (in degrees; moves westward)
  - ``CD1_2 = 0``: moving one pixel to the right does not change Dec
  - ``CD2_1 = 0``: moving one pixel up does not change RA
  - ``CD2_2 = 0.0001042``: moving one pixel up increases Dec by 0.375 arcsec
    
In case these information were not present in the FITS header, you
would have to implant them, e.g., using the ``scripts/implant_wcs.py``
script.


Source Catalog Creation
.......................

Before we can use SCAMP, we have to create a source catalog using
`Source Extractor`_ with a specific set of settings in Source
Extractor's configuration and parameter files. Create a configuration
file with

    > sextractor -d > config.sex

and a parameter file with

    > sextractor -dp > default.param

The following fields have to be activated (uncommented) in the
parameter file (``default.param``):

* ``XWIN_IMAGE``, ``YWIN_IMAGE``: use windowed centroid for target
  image position
* ``ERRAWIN_IMAGE``, ``ERRBWIN_IMAGE``, ``ERRTHETAWIN_IMAGE``: use
  windowed error ellipse information
* ``FLUX_AUTO``, ``FLUXERR_AUTO``: use Kron-like photometry
* ``FLAGS``: diagnostic field (optional)

(or use the files provided in the ``/ setup`` directory of this repository.)

It is mandatory to write the resulting catalog into LDAC file. This
can be changed in the configuration file (``config.sex``), along with
some other optional things that can be used to control the source
properties for the extraction:

* ``CATALOG_TYPE     FITS_LDAC``: set the output file type to LDAC (mandatory)
* ``FILTER           N``: deactivate detection filtering
* ``DETECT_MINAREA   10``: minimum number of pixels above threshold
* ``DETECT_THRESH    5``: detection threshold
* ``BACKPHOTO_TYPE LOCAL``: use local sky background measurement
  (improves photometry results)

Run Source Extractor on each of the images using:
    > sextractor <filename>.fits -c config.sex -CATALOG_NAME <filename>.ldac

You can have a look at the LDAC catalogs using ``ldactoasc <filename>.ldac``.

Running SCAMP to Register the Images
....................................

SCAMP has to be setup in a similar way as Source Extractor. Generate a
SCAMP configuration file with

    > scamp -d > config.scamp

The most important parameters to change are:

* ``PIXSCALE_MAXERR``: the maximum uncertainty on the image pixel
  scale (remember the CD matrix above)
* ``POSANGLE_MAXERR``: the maximum uncertainty on the image rotation
  angle (as high as 180 degrees)
* ``POSITION_MAXERR``: the maximum uncertainty on the image position
  (remember ``CRVAL``; set this to 15)
* ``MATCH_FLIPPED``: set to ``Y`` if you are really unsure about the
  image rotation
* ``ASTREF_CATALOG``: catalog to use for astrometric calibration (use
  ``2MASS`` for now)

Running SCAMP is then as simple as:

    > scamp \*.ldac -c config.scamp
    
SCAMP actually runs on the LDAC catalogs and not the image files;
you can run it over all catalogs at a time. If SCAMP succeeds
registering the images, it will create a ``.head`` file for each
catalog and a number of diagnostic plots.

You can tell if SCAMP succeeded by checking the numbers displayed on
the screen. Under the section `Astrometric matching`, you find two
contrast numbers (``cont.``). If those numbers are greater than 2.5,
the matching was successful. Also, the `Astrometric stats (external)`
give you some idea of the positional uncertainties of each source
(``dAXIS1`` and ``dAXIS2``).

Finally, we have to merge the information in the ``.head`` files with
our FITS images. You can use the ``scripts/merge_headers.py`` script
to do this.

Once the WCS solution has been implanted, use DS9 to display one of
the images and display the 2MASS catalog excerpt for this field
(``Analysis/Catalogs/Infrared/2MASS Point Sources``). As you can see,
the catalog positions match the locations of the stars in the image
very well.


Image Co-Addition
-----------------

Image Co-addition, or stacking, is used to improve the signal-to-noise
ratio of sources in the image. In an ideal world, combining 30
ten-second integrations has the same depth as a 300-second
integration. Images are combined using average or median operations by
matching pixels that correspond to the same position in the sky.

Once our images are registered, co-adding them is really simple using
`SWARP`_. It uses an interface similar to Source Extractor and SCAMP,
meaning that all settings are done in a configuration file. We create
a configuration file with

    > swarp -d > config.swarp

The most important settings are:

* ``IMAGEOUT_NAME``: the output image name
* ``COMBINE_TYPE``: the operation used in the image combination
* ``CENTER_TYPE``: ``ALL`` only uses that part of the sky that is
  shared by all input images; ``MOST`` uses that part of the sky that
  is sharded by most images

We can use the default configurations (``setup/config.swarp``) to
create a median combine of our sample data:

    > swarp mscience0*fits -c config.swarp

The resulting image, ``coadd.fits``, is signficantly deeper than the
individual frames and - more importantly - the bright asteroid is not
present anymore in the combined image.

Image Co-Addition in a Co-Moving Frame
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TBD...













.. _FITS World Coordinates System: https://fits.gsfc.nasa.gov/fits_wcs.html

.. _SAO DS9: http://ds9.si.edu/site/Home.html
.. _astropy.wcs: http://docs.astropy.org/en/v1.3.1/wcs/index.html
.. _Aladin: http://aladin.u-strasbg.fr/AladinDesktop/

.. _website: http://nova.astrometry.net/
.. _SCAMP software: http://www.astromatic.net/software/scamp

.. _CD matrix: http://www.stsci.edu/hst/HST_overview/documents/multidrizzle/ch44.html

.. _Source Extractor: http://www.astromatic.net/software/sextractor

.. _SWARP: http://www.astromatic.net/software/swarp
