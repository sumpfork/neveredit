# NOTE: you don't need this file to run neveredit. See INSTALL file
"""
A wxPython graphical editor for module files of Bioware's Neverwinter Nights
role-playing game. Includes wxPython-independent classes for reading and
writing NWN files.
"""

from distutils.core import setup
import sys,os,shutil

try:
    import py2app
except:
    print 'py2app not present'
    pass #of course, this will now fail when 'py2app' is given as an arg

import __init__
version = __init__.__version__

    
def main():
    name = 'neveredit'
    if 'neveredit' in sys.argv:
        name = 'neveredit'
        sys.argv.remove('neveredit')
    elif 'neverscript' in sys.argv:
        name = 'neverscript'
        sys.argv.remove('neverscript')

    resources = ["neveredit.jpg",
                 "help_nwnlexicon.zip"]
    
    if name == 'neveredit':
        mainclass = 'ui/NeverEditMainApp.py'
        resources.append('neveredit.icns')
    elif name == 'neverscript':
        mainclass = 'ui/ScriptEditor.py'
        resources.append('neverscript.icns')
        
    setup(app = [mainclass],
          name=name,
          version=version,
          description="The neveredit NWN Module Editor",
          long_description=__doc__,
          author="Sumpfork",
          author_email="sumpfork@users.sourceforge.net",
          url="http://neveredit.sourceforge.net",
          download_url="http://prdownloads.sourceforge.net/neveredit/" +\
          name + "-" +\
          version + ".tar.gz?download",
          license="BSD-like, but subject to Bioware's NWN License Agreement",
          platforms=['any'],
          classifiers=
          ['Development Status :: 3 - Alpha',
           'Intended Audience :: Developers',
           'Intended Audience :: End Users/Desktop',
           "License :: Freely Distributable",
           'Programming Language :: Python',
           'Topic :: Games/Entertainment :: Role-Playing'
           ],
          package_dir = {'neveredit':'.'},
          packages=['neveredit','neveredit.openglcontext',
                    'neveredit.util','neveredit.file',
                    'neveredit.game','neveredit.ui',
                    'neveredit.resources',
                    'neveredit.resources.images',
                    'neveredit.resources.xrc'],
          scripts=['run/neveredit','run/neverscript','run/nevercommand',
                   'run/nevererf'],
          
          options=dict(py2app=dict(
                argv_emulation=True,
                compressed=True,
                strip=True,
                semi_standalone=False,
                #next line needs to be changed if Numeric enabled in Utils.py
                excludes=['Numeric','LinearAlgebra'],
                includes=['numarray.libnumarray','numarray._ufuncBool',
                          'numarray._ufuncComplex64','numarray._ufuncInt16',
                          'numarray._ufuncInt8','numarray._ufuncUInt64',
                          'numarray._ufuncBool','numarray._ufuncFloat32',
                          'numarray._ufuncInt32','numarray._ufuncUInt16',
                          'numarray._ufuncUInt8','numarray._ufuncComplex32',
                          'numarray._ufuncFloat64','numarray._ufuncInt64',
                          'numarray._ufuncUInt32'],
                resources=resources,
                plist={'CFBundleIconFile':name+'.icns',
                       'CFBundleName':name,
                       'CFBundleVersion':version,
                       'NSHumanReadableCopyright':
                       'Copyright 2005, Peter Gorniak'}
                )),
    )

    toRemove = [('OpenGL','doc'),
                ('OpenGL','Demo'),
                ('OpenGL','Tk'),
                ('GLU','EXT'),
                ('GLU','SGI')]

    for path,dirs,files in os.walk(os.path.join('dist',name+'.app')):
        for f in files:
            for r in toRemove:
                if os.path.split(path)[-1] == r[0] and\
                   f == r[1] or\
                   f.endswith('.cached'):
                    print 'removing',os.path.join(path,f)
                    os.remove(os.path.join(path,f))                    
                    break
        for f in dirs:
            for r in toRemove:
                if os.path.split(path)[-1] == r[0] and\
                   f == r[1] or\
                   os.path.split(path)[-1] == 'GL' or\
                   os.path.split(path)[-1] == 'numarray' and\
                   f != 'linear_algebra':
                    print 'removing',os.path.join(path,f)
                    shutil.rmtree(os.path.join(path,f))
                    break
                
                        
                      
if __name__ == '__main__':
    main()
