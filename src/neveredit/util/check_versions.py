import sys,logging

logger = logging.getLogger('neveredit')
logger.info( 'Platform: %s' % sys.platform )
logger.info( 'Python version: %s' % sys.version )
logger.info( 'Python comand: %s' % sys.executable )
logger.info( 'Python path: %s' % sys.path )

from neveredit.util import Utils

failed = False
try:
    import wx
    logger.info( 'wxPython version: %s' % wx.__version__ )
except:
    logger.error( "couldn't import wx package - please install wxPython",
                  exc_info=True )
    failed = True
try:
    import PIL
except:
    logger.error( "couldn't import PIL package - please install the Python Image Lib",
                  exc_info=True)
    failed = True
try:
    Numeric = Utils.getNumPy()
    if Utils.use_numeric:
        logger.info( 'Numeric version: %s' % Numeric.__version__ )
    else:
            logger.info( 'numarray version: %s' % Numeric.__version__ )    
except:
    if Utils.use_numeric:
            logger.error( "couldn't import the Numeric package - please install Numeric", 
                      exc_info = True)
    else:
            logger.error( "couldn't import the numarray package - please install numarray", 
                      exc_info = True)
    failed = True
try:
    import OpenGL
    logger.info( 'pyopengl version: %s' % OpenGL.__version__ )
except:
    logger.error( "couldn't import OpenGL package - please install pyopengl" ,
                  exc_info=True)
    failed = True
if failed:
    logger.error("Please see README for URLs to install missing packages reported" )
