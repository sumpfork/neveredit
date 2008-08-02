'''Some common (non-wx related) util functions'''
import sys

import Image,ImageEnhance

use_numeric = True

def iAmOnMac():
    return sys.platform == 'darwin'

def iAmOnLinux():
    return 'linux' in sys.platform

#for the below, you also need to change setup.py to exclude the correct package
#if you're building mac bundles

def getNumPy():
    if use_numeric:
        import Numeric
        return Numeric
    else:
        import numarray
        return numarray

def getLinAlg():
    if use_numeric:
        import LinearAlgebra
        return LinearAlgebra
    else:
        import numarray.linear_algebra
        return numarray.linear_algebra

def resizeSquareImage(image,size):
    image = image.resize((size,size),Image.ANTIALIAS)
    e = ImageEnhance.Sharpness(image)
    image = e.enhance(13)
    return image

