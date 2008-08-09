import logging
logger = logging.getLogger('neveredit.ui')

import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math,sys
glutInit(sys.argv)      # must be initialized once and only once

from sets import Set

from neveredit.util import Utils
from neveredit.util import Preferences

Numeric = Utils.getNumPy()
LinearAlgebra = Utils.getLinAlg()
import time

class GLWindow(glcanvas.GLCanvas):
    def __init__(self,parent):
        glcanvas.GLCanvas.__init__(self, parent, -1)
        self.init = False
        self.width = 0
        self.height = 0

        self.zoom = 50.0
        self.minZoom = 5.0
        self.maxZoom = 400.0
        self.lookingAtX = 0
        self.lookingAtY = 0
        self.lookingAtZ = 0
        self.viewAngleSky = 50.0
        self.viewAngleFloor = 90.0
        self.angleSpeed = 3.0

        self.viewX = 0
        self.viewY = 0
        self.viewZ = 0
        
        self.point = Numeric.zeros((1,4),typecode=Numeric.Float)
        
        self.clearCache()

        self.frustum = []
        self.viewMatrixInv = Numeric.identity(4,Numeric.Float)
        self.modelMatrix = None
        self.currentModelView = None

        self.redrawRequested = False
        self.preprocessed = False
        self.preprocessing = False
        
        wx.EVT_ERASE_BACKGROUND(self, self.OnEraseBackground)
        wx.EVT_SIZE(self, self.OnSize)
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_LEFT_DOWN(self, self.OnMouseDown)
        wx.EVT_LEFT_UP(self, self.OnMouseUp)
        wx.EVT_MOTION(self, self.OnMouseMotion)
        wx.EVT_MOUSEWHEEL(self, self.OnMouseWheel)
        wx.EVT_KEY_DOWN(self, self.OnKeyDown)
	wx.EVT_KEY_UP(self,self.OnKeyUp)

    def OnEraseBackground(self, event):
        pass

    def OnSize(self, event):
        size = self.GetClientSize()
        if self.GetContext():
            self.SetCurrent()
            self.ReSizeGLScene(size.width,size.height)
        event.Skip()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        #dc.ResetBoundingBox()
        self.SetCurrent()
        if not self.init:
            self.InitGL(self.GetClientSize().width,self.GetClientSize().height)
            self.init = True
        self.DrawGLScene()

    def OnMouseDown(self, evt):
        pass #self.CaptureMouse()
    
    def OnMouseUp(self, evt):
        pass #self.ReleaseMouse()

    def OnKeyUp(self,evt):
	pass

    def OnKeyDown(self,evt):
        if self.preprocessing:
            return
        if evt.GetKeyCode() == wx.WXK_UP:
            self.adjustZoom(2.0)
        if evt.GetKeyCode() == wx.WXK_DOWN:
            self.adjustZoom(-2.0)
        if unichr(evt.GetUnicodeKey()) == Preferences.getPreferences()['GLW_UP']:
            self.adjustPos(1,0)
        if unichr(evt.GetUnicodeKey()) == Preferences.getPreferences()['GLW_DOWN']:
            self.adjustPos(-1,0)
        if unichr(evt.GetUnicodeKey()) == Preferences.getPreferences()['GLW_RIGHT']:
            self.adjustPos(0,-1)
        if unichr(evt.GetUnicodeKey()) == Preferences.getPreferences()['GLW_LEFT']:
            self.adjustPos(0,1)
        if evt.GetKeyCode() == wx.WXK_LEFT:
            self.adjustViewAngle(self.angleSpeed,0.0)
        if evt.GetKeyCode() == wx.WXK_RIGHT:
            self.adjustViewAngle(-self.angleSpeed,0.0)
        if evt.GetKeyCode() in (312,368): #pgdown
            self.adjustViewAngle(0.0,self.angleSpeed)
        if evt.GetKeyCode() in (313,369): #pgup
            self.adjustViewAngle(0.0,-self.angleSpeed)
        
    def OnMouseWheel(self,evt):
        if self.preprocessing:
            return
        rotation = float(evt.GetWheelRotation())
        if sys.platform == 'linux2':
            rotation /= 20.0
        self.adjustZoom(rotation)

    def OnMouseMotion(self,evt):
        pass
    
    def adjustViewAngle(self,floorAdjust, skyAdjust):
        self.viewAngleFloor += floorAdjust
        if self.viewAngleFloor > 360:
            self.viewAngleFloor -= 360
        elif self.viewAngleFloor < 0:
            self.viewAngleFloor += 360
        self.viewAngleSky += skyAdjust
        if self.viewAngleSky > 90:
            self.viewAngleSky = 89.9999
        elif self.viewAngleSky < 10:
            self.viewAngleSky = 10
        #self.SetupProjection()
        self.recomputeCamera()
        #self.Refresh(False)
        self.requestRedraw()

    def getBaseWidth(self):
        return 5.0

    def getBaseHeight(self):
        return 5.0
    
    def adjustPos(self,forwardBackward,sideways):
        w = self.getBaseWidth()
        h = self.getBaseHeight()
        dx = forwardBackward * math.cos((self.viewAngleFloor)*math.pi/180.0)
        dy = forwardBackward * math.sin((self.viewAngleFloor)*math.pi/180.0)
        dx += sideways * math.cos((self.viewAngleFloor+90.0)*math.pi/180.0)
        dy += sideways * math.sin((self.viewAngleFloor+90.0)*math.pi/180.0)
        adjust = True
        testX = self.lookingAtX + dx
        if testX > w:
            self.lookingAtX = w
            adjust = False
        elif testX < 0:
            self.lookingAtX = 0
            adjust = False        
        testY = self.lookingAtY + dy        
        if testY > h:
            self.lookingAtY = h
            adjust = False
        elif testY < 0:
            self.lookingAtY = 0
            adjust = False
        if adjust:
            self.lookingAtX = testX
            self.lookingAtY = testY
        #self.SetupProjection()
        self.recomputeCamera()
        #self.Refresh(False)
        self.requestRedraw()
        
    def adjustZoom(self,adjustment):
        self.zoom += float(adjustment)
        if self.zoom <= self.minZoom:
            self.zoom = self.minZoom
        elif self.zoom > self.maxZoom:
            self.zoom = self.maxZoom
        self.SetupProjection()
        self.recomputeCamera()
        #self.Refresh(False)
        self.requestRedraw()

    def doSelection(self,x,y):
        glSelectBuffer(100)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glMatrixMode(GL_MODELVIEW)
        glRenderMode(GL_SELECT)
        self.SetupProjection(True,x,y)
        self.DrawGLScene()
        buf = glRenderMode(GL_RENDER)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        return buf

    def output_text(self,x, y, text):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0.0, self.width, 0.0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glRasterPos2f(float(x), float(y))
        for c in text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_10, ord(c))
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def clearCache(self):
        self.preprocessedNodes = Set()
        self.textureStore = {}
    
    def preprocessNodes(self,model,tag,bbox=False):
        #if model.getPreprocessed():
        #    logger.warning("asked to preprocess already preprocessed model " +
        #                   model.getName())
        #    import traceback
        #    traceback.print_stack()
        self.preprocessNodesHelper(model.getRootNode(),tag,0)
        if bbox and not model.validBoundingBox:
            root = model.getRootNode()
            model.boundingBox = self.calculateNodeTreeBoundingBox(root)
            model.boundingSphere = [[0,0,0],0]
            model.boundingSphere[0] = (model.boundingBox[1]
                                       + model.boundingBox[0])/2.0
            r0 = model.boundingBox[0] - model.boundingSphere[0]
            r1 = model.boundingBox[1] - model.boundingSphere[0]        
            r = max(Numeric.dot(r0,r0),Numeric.dot(r1,r1))
            model.boundingSphere[1] = math.sqrt(r)
            model.validBoundingBox = True
        #model.setPreprocessed(True)
        
    def preprocessNodesHelper(self,node,tag,level):
        node.controllerDisplayList = glGenLists(1)
        glNewList(node.controllerDisplayList,GL_COMPILE)
        self.processControllers(node)
        glEndList()
        if node.isTriMesh():
            node.colourDisplayList = glGenLists(1)
            glNewList(node.colourDisplayList,GL_COMPILE)
            self.processColours(node)
            glEndList()
            if node.texture0:
                if not node.texture0name in self.textureStore:
                    node.glTexture0Name = glGenTextures(1)
                    glBindTexture (GL_TEXTURE_2D, node.glTexture0Name);
                    glTexParameteri (GL_TEXTURE_2D,
                                     GL_TEXTURE_WRAP_S, GL_REPEAT);
                    glTexParameteri (GL_TEXTURE_2D,
                                     GL_TEXTURE_WRAP_T, GL_REPEAT);
                    glTexParameteri (GL_TEXTURE_2D,
                                     GL_TEXTURE_MAG_FILTER, GL_LINEAR);
                    glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                                     GL_LINEAR_MIPMAP_LINEAR);
                    try:
                        w,h,image = node.texture0.size[0],\
                                    node.texture0.size[1],\
                                    node.texture0.tostring("raw","RGBA",0,-1)
                    except SystemError:
                        try:
                            w,h,image = node.texture0.size[0],\
                                        node.texture0.size[1],\
                                        node.texture0.tostring("raw","RGBX",0,-1)
                        except SystemError:
                            node.texture0 = node.texture0.convert('RGBA')
                            w,h,image = node.texture0.size[0],\
                                        node.texture0.size[1],\
                                        node.texture0.tostring("raw","RGBA",0,-1)
                            
                    assert w*h*4 == len(image)
                    gluBuild2DMipmaps(GL_TEXTURE_2D,GL_RGBA,w,h,GL_RGBA,
                                      GL_UNSIGNED_BYTE,image)
                    self.textureStore[node.texture0name] = node.glTexture0Name
                else:
                    node.glTexture0Name = self.textureStore[node.texture0name]
                    
        for c in node.children:
            self.preprocessNodesHelper(c,tag,level+1)

    def mergeBoxes(self,boxResult,boxAdd):
        for i in range(3):
            boxResult[0][i] = min(boxResult[0][i],boxAdd[0][i])
            boxResult[1][i] = max(boxResult[1][i],boxAdd[1][i])
        return boxResult
    
    def calculateNodeTreeBoundingBoxHelper(self,node,bb):
        glPushMatrix()
        #first, position transform to this node's space
        glCallList(node.controllerDisplayList)
        #calculcate this node's world space bounding box
        mybb = Numeric.array([3*[float(sys.maxint)],
                               3*[-float(sys.maxint)]])
        if node.isTriMesh() and node.vertices:
            for v in node.boundingBox:
                v = Numeric.transpose(self.transformPointModel(v))
                for i in range(3):
                    if v[i,0] < mybb[0][i]:
                        mybb[0][i] = v[i,0]
                    if v[i,0] > mybb[1][i]:
                        mybb[1][i] = v[i,0]
        else:
            mybb = Numeric.array([3*[0.0],3*[0.0]])
        #calculate the children's bboxes and merge them into ours
        for c in node.children:
            childbb = Numeric.array([3*[float(sys.maxint)],
                                      3*[float(-sys.maxint)]])
            self.calculateNodeTreeBoundingBoxHelper(c,childbb)
            self.mergeBoxes(mybb,childbb)
        #set the calculated bbox and calculate the bounding sphere
#        print 'setting bounding box for',node.name,'to',mybb
        node.boundingBox = Numeric.array(mybb)
        node.boundingSphere = [[0,0,0],0]
        node.boundingSphere[0] = (node.boundingBox[1]
                                  + node.boundingBox[0])/2.0
        r0 = node.boundingBox[0] - node.boundingSphere[0]
        r1 = node.boundingBox[1] - node.boundingSphere[0]        
        r = max(Numeric.dot(r0,r0),Numeric.dot(r1,r1))
        node.boundingSphere[1] = math.sqrt(r)
        #finally, merge our box with the passed in one
        self.mergeBoxes(bb,mybb)
        glPopMatrix()
        
    def calculateNodeTreeBoundingBox(self,node):
        self.modelMatrix = None
        self.viewMatrixInv = Numeric.identity(4)
        boundingBox = Numeric.array([3*[0.0],#float(sys.maxint)],
                                     3*[0.0]])#float(-sys.maxint)]])
        glPushMatrix()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.calculateNodeTreeBoundingBoxHelper(node,boundingBox)
        glPopMatrix()
        self.SetupProjection()
        return boundingBox

    def fixMatrixToNumPy(self,matrix):
	    numpymatrix = Numeric.array(matrix,'d')
	    return numpymatrix

    def processControllers(self,node):
        if node.position != None:
            p = node.position
            glTranslate(p[0],p[1],p[2])
        if node.orientation != None:
	    node.orientation = self.fixMatrixToNumPy(node.orientation)
            glMultMatrixf(node.orientation)
        if node.scale:
            s = node.scale
            glScalef(s,s,s)

    def processColours(self,node):
        if node.shininess:
            glMaterialf(GL_FRONT,GL_SHININESS,node.shininess)
        glMaterialfv(GL_FRONT,GL_AMBIENT,node.ambientColour)
        glMaterialfv(GL_FRONT,GL_DIFFUSE,node.diffuseColour)
        glMaterialfv(GL_FRONT,GL_SPECULAR,node.specularColour)

    def solidColourOn(self):
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        glShadeModel(GL_FLAT)
        glEnable(GL_POLYGON_OFFSET_LINE)
        glPolygonOffset(1.0, 1.0)

    def solidColourOff(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glDisable(GL_POLYGON_OFFSET_LINE)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

    def wireOn(self):
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glBlendFunc(GL_ONE,GL_ONE)
        glShadeModel(GL_FLAT)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glEnable(GL_POLYGON_OFFSET_LINE)
        glPolygonOffset(1.0, 1.0)

    def wireOff(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_POLYGON_OFFSET_LINE)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def transparentColourOn(self):
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_FLAT)
        glEnable(GL_POLYGON_OFFSET_LINE)

    def transparentColourOff(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_POLYGON_OFFSET_LINE)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        
    def glColorf(self,colour):
	    #FIXME: glColorf is not defined, changing to glColor3f
	    glColor3f(colour[0],colour[1],colour[2])

    def renderHighlightBoxOutline(self,box,colour=(0.1,1.0,0.1,0.5),
                                  thickness=3.0):
        self.solidColourOn()
        self.glColorf(colour)
        glLineWidth(thickness)
        self.renderBox(box)
        glLineWidth(1.0)
        self.solidColourOff()

    def renderArrowOutline(self,size,colour=(0.1,1.0,0.1,1.0)):
        self.solidColourOn()
        self.glColorf(colour)
        glLineWidth(3.0)
        self.renderArrow(size)
        glLineWidth(1.0)
        self.solidColourOff()
        
    def renderHighlightBoxTransparent(self,box,colour=(0.1,1.0,0.1,0.5)):
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        self.glColorf(colour)
        glShadeModel(GL_FLAT)
        glEnable(GL_POLYGON_OFFSET_LINE)
        glPolygonOffset(1.0, 1.0)
        self.renderBox(box,fill=True)
        glEnable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_POLYGON_OFFSET_LINE)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)

    def renderSphereTransparent(self,sphere,colour=(0.1,1.0,0.1,0.5)):
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        self.glColorf(colour)
        glShadeModel(GL_FLAT)
        glEnable(GL_POLYGON_OFFSET_LINE)
        glPolygonOffset(1.0, 1.0)
        glPushMatrix()
        glTranslatef(sphere[0][0],
                     sphere[0][1],
                     sphere[0][2])
        glutSolidSphere(sphere[1],20,20)
        glPopMatrix()
        glEnable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_POLYGON_OFFSET_LINE)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)

    def renderArrow(self,size,fill=False):
        type = GL_LINE_STRIP
        if fill:
            type = GL_TRIANGLE_STRIP
        glBegin(type)
        glVertex3f(-size,-size,0)
        glVertex3f(size,-size,0)
        glVertex3f(size,-size,size)
        glVertex3f(-size,-size,size)        
        glVertex3f(-size,-size,0)
        glVertex3f(0,2*size,0)
        glVertex3f(0,2*size,size)
        glVertex3f(-size,-size,size)

        glEnd()

        glBegin(type)
        glVertex3f(0,2*size,0)
        glVertex3f(0,2*size,size)
        glVertex3f(size,-size,size)
        glVertex3f(size,-size,0)
        glEnd()
        
    def renderBox(self,box,fill=False):
        if fill:
            glBegin(GL_QUADS)
        else:
            glBegin(GL_LINE_STRIP)
        glVertex3f(box[0][0],box[0][1],box[0][2])
        glVertex3f(box[0][0],box[0][1],box[1][2])
        glVertex3f(box[0][0],box[1][1],box[1][2])
        glVertex3f(box[0][0],box[1][1],box[0][2])
            
        glVertex3f(box[0][0],box[0][1],box[0][2])
        glVertex3f(box[0][0],box[1][1],box[0][2])
        glVertex3f(box[1][0],box[1][1],box[0][2])
        glVertex3f(box[1][0],box[0][1],box[0][2])

        glVertex3f(box[0][0],box[0][1],box[0][2])
        glVertex3f(box[0][0],box[0][1],box[1][2])
        glVertex3f(box[1][0],box[0][1],box[1][2])
        glVertex3f(box[1][0],box[0][1],box[0][2])
        
        glVertex3f(box[1][0],box[0][1],box[1][2])
        glVertex3f(box[1][0],box[0][1],box[0][2])
        glVertex3f(box[1][0],box[1][1],box[0][2])
        glVertex3f(box[1][0],box[1][1],box[1][2])
            
        glVertex3f(box[1][0],box[1][1],box[1][2])
        glVertex3f(box[1][0],box[0][1],box[1][2])
        glVertex3f(box[0][0],box[0][1],box[1][2])
        glVertex3f(box[0][0],box[1][1],box[1][2])

        glVertex3f(box[1][0],box[1][1],box[1][2])
        glVertex3f(box[1][0],box[1][1],box[0][2])
        glVertex3f(box[0][0],box[1][1],box[0][2])
        glVertex3f(box[0][0],box[1][1],box[1][2])
        glEnd()

    def processTextures(self,node):
        if node.texture0:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D,node.glTexture0Name)
            if hasattr(node,'texture0Vertices') and node.texture0Vertices:
                glTexCoordPointerf(node.texture0Vertices)
                glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            else:
                glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        else:
            glDisable(GL_TEXTURE_2D)
            #print node.name,'does not have texture'
            return False

    def sendVertices(self,node):
        glVertexPointerf(node.vertices)

    def doNormals(self,node):
        if node.normals:
            glNormalPointerf(node.normals)
            glEnableClientState(GL_NORMAL_ARRAY)
        else:
            glDisableClientState(GL_NORMAL_ARRAY)

    def drawVertices(self,l):
        glDrawElementsus(GL_TRIANGLES,l)
        
    def drawVertexLists(self,node):
        for l in node.vertexIndexLists:
            self.drawVertices(l)
        
    def processVertices(self,node):
        self.sendVertices(node)
        self.doNormals(node)
        self.drawVertexLists(node)
        
    def processNode(self,node,boxOnly=False):
        if boxOnly and node.boundingBox[1][0]:
            self.renderBox(node.boundingBox)
            return True
        self.processTextures(node)
        glCallList(node.colourDisplayList)
        self.processVertices(node)
        return True

    def drawBoundingBoxes(self,node):
        if Numeric.alltrue(Numeric.equal(node.boundingBox[1],[0,0,0])):
            return
        self.renderBox(node.boundingBox)
        for c in node.children:
            self.drawBoundingBoxes(c)

    def drawBoundingSpheres(self,node):
        for c in node.children:
            self.drawBoundingSpheresHelper(c)
            
    def drawBoundingSpheresHelper(self,node):
        if Numeric.alltrue(Numeric.equal(node.boundingBox[1],[0,0,0])):
            return
        if self.sphereInFrustum(self.transformPointModel(node.boundingSphere[0]),
                                node.boundingSphere[1]):
            #print 'bounding sphere for',node.name,'is IN frustum'
            glPushMatrix()
            glTranslate(node.boundingSphere[0][0],
                        node.boundingSphere[0][1],
                        node.boundingSphere[0][2])
            glutSolidSphere(node.boundingSphere[1],30,30)
            glPopMatrix()
        for c in node.children:
            self.drawBoundingSpheres(c)

    def handleNode(self,node,
                   frustumCull=False,
                   boxOnly=False,
                   selected=False):
        if frustumCull:
            self.modelMatrix =  Numeric.dot(glGetDoublev(GL_MODELVIEW_MATRIX),
                                             self.viewMatrixInv)
        else:
            self.modelMatrix = None
        drewSomething = self.handleNodeHelper(node,frustumCull,boxOnly,selected)
        if not drewSomething:
            self.renderHighlightBoxOutline(node.boundingBox)
        self.modelMatrix = None
            
    def handleNodeHelper(self,node,
                   frustumCull=False,
                   boxOnly=False,
                   selected=False):
        glPushMatrix()
        glCallList(node.controllerDisplayList)
        if frustumCull and node.boundingBox[1][0]:
            #print node.name,self.transformPointModel(node.boundingSphere[0]),
            #node.boundingSphere[1]
            if self.sphereInFrustum(self.transformPointModel(node.boundingSphere[0]),
                                    node.boundingSphere[1]):
                #print node.name,'is IN the frustum'
                pass
            else:
                #print node.name,'is OUTSIDE the frustum'
                glPopMatrix()
                return True
        drewSomething = False
        if node.isTriMesh() and\
               node.vertices:
            drewSomething = self.processNode(node,boxOnly)
            if selected:
                glPushMatrix()
                glScalef(1.2,1.2,1.2)
                #glBlendFunc(GL_ONE,GL_ONE)
                glColor4f(0.1,0.9,0.1,0.6)
                glDisable(GL_LIGHTING)
                #self.renderBox(self.model.boundingBox)
                self.processNode(node,False)
                glPopMatrix()
                #glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
                glEnable(GL_LIGHTING)            
        for c in node.children:
            drewSomething |= self.handleNodeHelper(c,frustumCull,boxOnly,selected)
        glPopMatrix()
        return drewSomething
            


    def isBoxVisible(self,box):
        return self.boxInFrustum(box)

    def isVisible(self,object):
        if not hasattr(object,'boundingSphere'):
            return True
        return self.isSphereVisible(object.boundingSphere)
    
    def isSphereVisible(self,sphere):
        centre = self.transformPointModelView(sphere[0])
        return self.sphereInFrustum(centre,sphere[1])
    
    def getTotalMatrix(self):
        pm = glGetDoublev(GL_PROJECTION_MATRIX)
        mvm = glGetDoublev(GL_MODELVIEW_MATRIX)
        return Numeric.dot(mvm,pm)

    def transformPointInverseModelView(self,p):
        p = Numeric.resize(p,(1,4))
        p[0,3] = 1.0
        mvm = Numeric.array(glGetDoublev(GL_MODELVIEW_MATRIX),copy=False)
        mvminv = LinearAlgebra.inverse(mvm)
        p = Numeric.dot(p,mvminv)
        p /= p[0,3]
        return p

    def transformPointModel(self,p):
        p = Numeric.resize(p,(1,4))
        p[0,3] = 1.0
        if self.modelMatrix != None:
            p = Numeric.matrixmultiply(p,self.modelMatrix)
        else:
            p = Numeric.dot(p,glGetDoublev(GL_MODELVIEW_MATRIX))
            p = Numeric.dot(p,self.viewMatrixInv)
        p /= p[0,3]
        return p

    def cacheModelView(self):
        self.currentModelView = glGetDoublev(GL_MODELVIEW_MATRIX)

    def clearModelView(self):
        self.currentModelView = None
        
    def transformPointModelView(self,p):
        self.point[0,:3] = p
        self.point[0,3] = 1.0
        #p = Numeric.resize(p,(1,4))
        #p[0,3] = 1.0
        if self.currentModelView == None:
            mvm = glGetDoublev(GL_MODELVIEW_MATRIX,copy=False)
        else:
            mvm = self.currentModelView
        r = Numeric.dot(self.point,mvm)
        r /= r[0,3]
        return r
    
    def transformPoint(self,p):
        p = Numeric.resize(p,(1,4))
        p[0,3] = 1.0
        p = Numeric.dot(p,glGetDoublev(GL_MODELVIEW_MATRIX))
        p = Numeric.dot(p,glGetDoublev(GL_PROJECTION_MATRIX))
        p /= p[0,3]
        return p

    def drawFrustum(self):
        #right-bottom-front
        p1 = -self.triplePlaneIntersect(self.frustum[0],
                                       self.frustum[2],
                                       self.frustum[5])
        #right-bottom-back
        p2 = -self.triplePlaneIntersect(self.frustum[0],
                                       self.frustum[2],
                                       self.frustum[4])
        #right-top-front
        p3 = -self.triplePlaneIntersect(self.frustum[0],
                                       self.frustum[3],
                                       self.frustum[5])
        #right-top-back
        p4 = -self.triplePlaneIntersect(self.frustum[0],
                                       self.frustum[3],
                                       self.frustum[4])
        #left-bottom-front
        p5 = -self.triplePlaneIntersect(self.frustum[1],
                                       self.frustum[2],
                                       self.frustum[5])
        #left-bottom-back
        p6 = -self.triplePlaneIntersect(self.frustum[1],
                                       self.frustum[2],
                                       self.frustum[4])
        #left-top-front        
        p7 = -self.triplePlaneIntersect(self.frustum[1],
                                       self.frustum[3],
                                       self.frustum[5])
        #left-top-back        
        p8 = -self.triplePlaneIntersect(self.frustum[1],
                                       self.frustum[3],
                                       self.frustum[4])

        print p1
        print p3
        print p5
        print p7
        print p2
        print p4
        print p6
        print p8
       
        glBegin(GL_LINE_STRIP)
        glVertexf(p1)
        glVertexf(p2)
        glVertexf(p4)
        glVertexf(p3)
        glVertexf(p1)
        glVertexf(p5)
        glVertexf(p6)
        glVertexf(p8)
        glVertexf(p7)
        glVertexf(p5)
        glEnd()
        glBegin(GL_LINES)
        glVertexf(p7)
        glVertexf(p3)
        glVertexf(p8)
        glVertexf(p4)
        glVertexf(p6)
        glVertexf(p2)
        glEnd()
        glColor3f(1.0,0.0,0.0)
        glBegin(GL_QUADS)
        glVertex(p2)
        glVertex(p4)
        glVertex(p8)
        glVertex(p6)
        glEnd()
#        glColor3f(0.0,1.0,0.0)
#        glBegin(GL_QUADS)
#        glVertex(p1)
#        glVertex(p3)
#        glVertex(p7)
#        glVertex(p5)
#        glEnd()
        
    def computeFrustum(self):
        self.frustum = []
        #clip = self.getTotalMatrix()
        clip = Numeric.array(glGetDoublev(GL_PROJECTION_MATRIX),copy=False)
        
        #print 'total',clip        
        self.frustum.append(clip[:,3]-clip[:,0]) # right
        self.frustum.append(clip[:,3]+clip[:,0]) # left
        self.frustum.append(clip[:,3]+clip[:,1]) # bottom        
        self.frustum.append(clip[:,3]-clip[:,1]) # top
        #self.frustum.append(clip[:,3]-clip[:,2]) # back
        #self.frustum.append(clip[:,3]+clip[:,2]) # front
        self.frustum = self.fixMatrixToNumPy(self.frustum)
        #print 'frustum',self.frustum        

        for plane in self.frustum:
            plane /= math.sqrt(Numeric.dot(plane[:3],plane[:3]))
            
    def pointInFrustum(self,p):
        for plane in self.frustum:
            if (Numeric.dot(p,plane)) <= 0:
                return False
        return True

    def sphereInFrustum(self,centre,radius):
        for plane in self.frustum[:4]:
            #print centre[0,:3],plane[3]
            #print centre,plane,Numeric.dot(centre,plane)[0],-radius
            if centre[0,0]*plane[0] + centre[0,1]*plane[1] +\
               centre[0,2]*plane[2] + plane[3] < -radius:
                #Numeric.dot(centre[0,:3],plane[:3]) + plane[3] < -radius:
                #print 'frustum cull failed on plane',i
                return False
        return True
        
    def boxInFrustum(self,box):
        boxMin = box[0]
        boxMax = box[1]
        #print self.pointInFrustum(boxMin)
        #print self.pointInFrustum(boxMax)
        #print self.pointInFrustum([boxMin[0],boxMax[1],boxMax[2]])
        #print self.pointInFrustum([boxMin[0],boxMin[1],boxMax[2]])
        #print self.pointInFrustum([boxMax[0],boxMin[1],boxMin[2]])
        #print self.pointInFrustum([boxMax[0],boxMax[1],boxMin[2]])
        #print self.pointInFrustum([boxMin[0],boxMax[1],boxMin[2]])
        #print self.pointInFrustum([boxMax[0],boxMin[1],boxMax[2]])

        return self.pointInFrustum(boxMin) or\
               self.pointInFrustum(boxMax) or\
               self.pointInFrustum([boxMin[0],boxMax[1],boxMax[2]]) or\
               self.pointInFrustum([boxMin[0],boxMin[1],boxMax[2]]) or\
               self.pointInFrustum([boxMax[0],boxMin[1],boxMin[2]]) or\
               self.pointInFrustum([boxMax[0],boxMax[1],boxMin[2]]) or\
               self.pointInFrustum([boxMin[0],boxMax[1],boxMin[2]]) or\
               self.pointInFrustum([boxMax[0],boxMin[1],boxMax[2]])
               
               
               
    def InitGL(self,Width, Height):
        '''A general OpenGL initialization function.
        Sets all of the initial parameters. '''
        self.width = Width
        self.height = Height
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(True)            # Enables Clearing Of The Depth Buffer
        glDepthFunc(GL_LESS)          # The Type Of Depth Test To Do
        glEnable(GL_DEPTH_TEST)       # Enables Depth Testing
        glShadeModel(GL_SMOOTH)       # Enables Smooth Color Shading
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glEnable(GL_ALPHA_TEST)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnableClientState (GL_VERTEX_ARRAY)
        glEnableClientState (GL_TEXTURE_COORD_ARRAY)
        glDisableClientState (GL_COLOR_ARRAY)
        glDisableClientState (GL_EDGE_FLAG_ARRAY)
        glDisableClientState (GL_INDEX_ARRAY)
        glDisableClientState (GL_NORMAL_ARRAY)
        glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glEnable(GL_TEXTURE_2D)
        glAlphaFunc (GL_GREATER, 0.1)
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(0.1,0)
        glInitNames()

        self.SetupProjection()
	##self.wireOn()
#        self.recomputeCamera()

    # The function called when our window is resized
    def ReSizeGLScene(self,Width, Height):
        self.width = Width
        self.height = Height
        if Height == 0:    # Prevent A Divide By Zero If The Window Is Too Small 
            Height = 1
        # Reset The Current Viewport And Perspective Transformation
        glViewport(0, 0, Width, Height)
        self.SetupProjection()
        
    def SetupProjection(self,pick=False,x=0,y=0):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if pick:
            gluPickMatrix(x,y,5,5,None)
        gluPerspective(45.0, float(self.width)/float(self.height),
                       self.minZoom/2.0, self.maxZoom + 32.0)
        glMatrixMode(GL_MODELVIEW)
        if not pick:
            self.recomputeFrustum = True

    def project(self,x,y,z):
        vm = glGetDoublev(GL_MODELVIEW_MATRIX)
        pm = glGetDoublev(GL_PROJECTION_MATRIX)
        vp = glGetIntegerv(GL_VIEWPORT)
        return gluProject(x,y,z,vm,pm,vp)

    def unproject(self,x,y,z):
        vm = glGetDoublev(GL_MODELVIEW_MATRIX)
        pm = glGetDoublev(GL_PROJECTION_MATRIX)
        vp = glGetIntegerv(GL_VIEWPORT)
        return gluUnProject(x,y,z,vm,pm,vp)

    def linePlaneIntersect(self,plane,linep1,linep2):
        u = Numeric.dot(plane[:3],linep1) + plane[3]
        u /= Numeric.dot(plane[:3],linep1-linep2)
        return linep1 + u * (linep2-linep1)

    def triplePlaneIntersect(self,plane1,plane2,plane3):
        m = Numeric.array([plane1[:3],plane2[:3],plane3[:3]])
        m = LinearAlgebra.inverse(m)
        v = Numeric.array([[plane1[3],plane2[3],plane3[3]]],shape=(3,1))
        return Numeric.dot(m,v)
        
    
    def quadricErrorCallback(self,arg):
        print gluErrorString(arg)
        
    def drawRoundedRect(self,width,height):
        cornersize = 5
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric,GLU_FILL)
        gluQuadricNormals(quadric,GLU_SMOOTH)
        glPushMatrix()
        glTranslatef(cornersize,cornersize,0)
        gluPartialDisk(quadric,0,cornersize,5,5,180,90)
        glTranslatef(width-2*cornersize,0,0)
        gluPartialDisk(quadric,0,cornersize,5,5,90,90)
        glTranslatef(0,height-2*cornersize,0)
        gluPartialDisk(quadric,0,cornersize,5,5,0,90)
        glTranslatef(-width+2*cornersize,0,0)
        gluPartialDisk(quadric,0,cornersize,5,5,270,90)        
        gluDeleteQuadric(quadric)
        glTranslatef(-cornersize,0,0)
        glBegin(GL_QUADS)
        glVertex3f(0,0,0)
        glVertex3f(width,0,0)
        glVertex3f(width,-height+2*cornersize,0)
        glVertex3f(0,-height+2*cornersize,0)
        glVertex3f(cornersize,cornersize,0)
        glVertex3f(width-cornersize,cornersize,0)
        glVertex3f(width-cornersize,0,0)
        glVertex3f(cornersize,0,0)
        glVertex3f(cornersize,-height+2*cornersize,0)
        glVertex3f(width-cornersize,-height+2*cornersize,0)
        glVertex3f(width-cornersize,-height+cornersize,0)
        glVertex3f(cornersize,-height+cornersize,0)
        glEnd()        
        glPopMatrix()

    def recomputeCamera(self):
        self.viewX = self.lookingAtX
        self.viewY = self.lookingAtY
        distance = 400.0/self.zoom
        self.viewZ = math.sin((180.0-self.viewAngleSky)
                              *math.pi/180.0) * distance
        floorDistance = math.cos((180.0-self.viewAngleSky)
                                 *math.pi/180.0) * distance
        self.viewX += math.cos(self.viewAngleFloor
                               *math.pi/180.0) * floorDistance
        self.viewY += math.sin(self.viewAngleFloor
                               *math.pi/180.0) * floorDistance
        self.recomputeFrustum = True
        
    def setupCamera(self):
        glLoadIdentity()           # Reset The View
        gluLookAt(self.viewX,self.viewY,self.viewZ,
                  self.lookingAtX,self.lookingAtY,self.lookingAtZ,
                  0,0,1)
        mvm = Numeric.array(glGetDoublev(GL_MODELVIEW_MATRIX),copy=False)
        self.viewMatrixInv = LinearAlgebra.inverse(mvm)
        if self.recomputeFrustum:
            self.computeFrustum()
            self.recomputeFrustum = False

    def requestRedraw(self):
        if self.redrawRequested:
            return
        else:
            self.redrawRequested = True
            wx.PostEvent(self,wx.PaintEvent(self.GetId()))

    def preprocess(self):
        '''override this routine to do preprocessing on visuals
        with the graphics context active.'''
        raise NotImplementedError('preprocess must be overriden in subclass')
    
    def DrawGLScene(self):
        self.redrawRequested = False
        self.SetCurrent()
        if self.preprocessing:
            return
        if not self.preprocessed:
            self.preprocessing = True
            now = time.time()
            #import profile
            #p = profile.Profile()
            #p.runcall(self.preprocess)
            self.preprocess()
            if self.preprocessed:
                print 'preprocessing took %.2f seconds' % (time.time()-now)
                #p.dump_stats('prep.prof')
                self.recomputeCamera()
            self.preprocessing = False
