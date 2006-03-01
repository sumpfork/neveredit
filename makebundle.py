'''used to make application bundles on Mac OS X'''

import sys
import bundlebuilder
import os.path

wxPyPath = '/usr/local/lib/'
wxPyName = 'wxPython'
wxPyMajorVersion = '2.5.2'
wxPyMinorVersion = '8'
wxPyVersion = wxPyMajorVersion + '.' + wxPyMinorVersion
wxPy = wxPyPath + wxPyName + '-' + wxPyVersion
libExt = wxPyMajorVersion + '.' + 'dylib'

def neveredit_setup(app):
    app.mainprogram = "NeverEditMainApp.py"

    app.includePackages.append('numarray')
    app.includePackages.append('PIL')
    app.includeModules.append('_imaging')

    app.name = "neveredit"
    app.libs.append(wxPy + "/lib/libwx_macd_gl-" + libExt)
    app.libs.append("/sw/lib/libjpeg.62.dylib")

    app.resources.append("neveredit.jpg")
    app.resources.append("neveredit_logo.jpg")
    app.resources.append("neveredit_logo_init.jpg")
    app.resources.append("paint_icon.png")
    app.resources.append("rotate_icon.png")
    app.resources.append("select_icon.png")
    app.resources.append("paint_icon_sel.png")
    app.resources.append("rotate_icon_sel.png")
    app.resources.append("select_icon_sel.png")

def neverscript_setup(app):
    app.mainprogram = "ScriptEditor.py"
    app.name = "neverscript"
    
def common_setup():
    app = bundlebuilder.AppBuilder(verbosity=1)

    if len(sys.argv) > 1:    
        app.version = sys.argv[1]

    app.includeModules.append('encodings.ascii')
    app.includeModules.append('encodings.utf_8')
    app.includeModules.append('encodings.latin_1')

    app.excludeModules.append('wx._ogl')
    app.excludeModules.append('wx._xrc')
    app.excludeModules.append('wx._wizard')

    app.iconfile = "neveredit.icns"
    #app.standalone = True
    app.semi_standalone = True
    app.strip = True

    app.libs.append(wxPy + "/lib/libwx_macd-" + libExt)
    app.libs.append(wxPy + "/lib/libwx_macd_stc-" + libExt)
    app.libs.append(wxPy + "/lib/libwx_macd-" + wxPyMajorVersion + ".rsrc")

    app.resources.append("help_nwnlexicon.zip")

    app.argv_emulation = True
    
    return app

def make(app):
    app.setup()
    app.build()

if __name__ == '__main__':
    app = common_setup()
    if len(sys.argv) > 2 and sys.argv[2] == 'neverscript':
        print 'bundling neverscript'
        neverscript_setup(app)
    else:
        print 'bundling neveredit'
        neveredit_setup(app)
    make(app)
    
