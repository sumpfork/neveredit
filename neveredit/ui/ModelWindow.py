'''
A class to display a single NWN 3D model.
'''
import sys

import wx
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from neveredit.ui.GLWindow import GLWindow
from neveredit.file import MDLFile
from neveredit.game.ChangeNotification import VisualChangeListener
from neveredit.util import neverglobals

class ModelWindow(GLWindow, VisualChangeListener):
    __doc__ = globals()['__doc__']
    def __init__(self,parent):
        GLWindow.__init__(self, parent)
        self.model = None
        self.lookingAtZ = 1.5
        neverglobals.getResourceManager().addVisualChangeListener(self)

    def visualChanged(self,v):
        self.setModel(v.getModel(copy=True))
        
    def setModel(self,m):
        self.model = m
        self.clearCache()
        if not m:
            return
        self.lookingAtX = self.getBaseWidth()/2.0
        self.lookingAtY = self.getBaseHeight()/2.0
        self.lookingAtZ = self.model.getRootNode().boundingBox[1][2]/2.0
        self.preprocessed = False
        self.requestRedraw()
        
    def DrawGLScene(self):
        GLWindow.DrawGLScene(self)
        self.SetCurrent()
        if not self.model or not self.preprocessed:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.SwapBuffers()
            return
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.setupCamera()
            glLightfv(GL_LIGHT0,GL_AMBIENT,[1.0,1.0,1.0,1.0])
            glLightfv(GL_LIGHT0,GL_DIFFUSE,[1.0,1.0,1.0,1.0])
            glLightfv(GL_LIGHT0,GL_SPECULAR,[1.0,1.0,1.0,1.0])
            glLightfv(GL_LIGHT0,GL_POSITION,[self.viewX,self.viewY,self.viewZ,1.0])
            glTranslate(self.getBaseWidth()/2.0,self.getBaseHeight()/2.0,0)
            self.handleNode(self.model.getRootNode(),boxOnly=False,
                            frustumCull=False,selected=False)
            self.SwapBuffers()
            
        except KeyboardInterrupt:
            print 'shutting down'
            sys.exit()

    def preprocess(self):        
        if self.model:
            self.SetCurrent()
            self.preprocessNodes(self.model,'modelviewer',bbox=True)
            self.lookingAtZ = (self.model.boundingBox[1][2] -
                               self.model.boundingBox[0][2])/2.0
            self.preprocessed = True
            self.recomputeCamera()
            
    def Destroy(self):
        neverglobals.getResourceManager().removeVisualChangeListener(self)
        GLWindow.Destroy(self)
        
    def get_standalone(cls, modelfile):
        win = None
        class MyApp(wx.App):
            def OnInit(self):
                m = MDLFile.MDLFile()
                m.fromFile(open(modelfile))
                frame = wx.Frame(None, -1, "Model " + modelfile, wx.DefaultPosition, wx.Size(400,400))
                sizer = wx.BoxSizer(wx.VERTICAL)
                sizer.Add((100,100))
                b = wx.Button(frame,-1,"test")
                sizer.Add(b,True,wx.EXPAND)
                win = ModelWindow(frame)
                frame.SetSizer(sizer)
                win.SetSize((200,200))
                sizer.Add(win,False,wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT)
                win.setModel(m.getModel())
                frame.Show(True)
                self.SetTopWindow(frame)
                return True
        cls.app = MyApp(0)
        return win
    get_standalone = classmethod(get_standalone)

    def start_standalone(cls):
        cls.app.MainLoop()
    start_standalone = classmethod(start_standalone)
    

def run(args):
    ModelWindow.get_standalone(args[0])
    ModelWindow.start_standalone()
    
# Print message to console, and kick off the main to get it rolling.
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'usage: ' + sys.argv[0] + ' <modelfile>'
        sys.exit(1)
    run(sys.argv[1:])
