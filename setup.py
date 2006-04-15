# NOTE: you don't need this file to run neveredit. See INSTALL file
"""
A wxPython graphical editor for module files of Bioware's Neverwinter Nights
role-playing game. Includes wxPython-independent classes for reading and
writing NWN files.
"""

import ez_setup
ez_setup.use_setuptools()

#from distutils.core import setup
from setuptools import setup,find_packages
import sys,os,shutil

dependency_links = [
    'http://svn.red-bean.com/bob/py2app/trunk/',
    'http://sourceforge.net/project/showfiles.php?group_id=1369',
    'http://www.pythonware.com/products/pil/'
]

build_dependencies = ['numarray>=1.5','PIL>=1.1.5','pygame>=1.7']
if 'py2app' in sys.argv:
    build_dependencies.append('py2app>=0.3-dev_r551')
extra_dependencies = {'compiler' : ['nwntools>=2.3']}

try:
    import py2app
except:
    print 'py2app not present'
    pass #of course, this will now fail when 'py2app' is given as an arg

sys.path.insert(0,'src')
import neveredit
version = neveredit.__version__
print 'neveredit version',version
    
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
        mainclass = 'src/neveredit/ui/NeverEditMainApp.py'
        resources.append('neveredit.icns')
    elif name == 'neverscript':
        mainclass = 'src/neveredit/ui/ScriptEditor.py'
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

          setup_requires = build_dependencies,
          dependency_links = dependency_links,
          extras_require = extra_dependencies,
          package_dir = {'':'src'},
          packages = find_packages('src',exclude=['ez_setup']),
          scripts = ['run/neveredit','run/neverscript','run/nevercommand',
                   'run/nevererf'],
          entry_points = {
              'gui_scripts' : ['neveredit = neveredit.ui.NevereditMainApp:main']
          },
          include_package_data = True,
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
                       'Copyright 2004-2006, Peter Gorniak'}
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
