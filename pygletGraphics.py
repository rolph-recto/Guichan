#!/usr/bin/env python

import pyglet
from pyglet.gl import *
import pyglet.graphics
#from pygame.locals import *
#There's two Colors! Error!

from guichan import *
from graphics import Graphics
from pygameImage import PygameImage
from pygameImage import GuichanToPygameColor
from font import Font


def GcnCoord(x,y,height,h):
    return x, height-y+h

def PygletCoord(x,y,height,h):
    return x, height-y+h

class PygletGraphics(Graphics):
    def __init__(self):
        Graphics.__init__(self)
        self.mAlpha=False
        self.mColor=Color(255,255,255,255)
        self.mWidth, self.mHeight=0,0
        self.mBatch=None
        
    def beginDraw(self):
        glPushAttrib(GL_COLOR_BUFFER_BIT |GL_CURRENT_BIT |GL_DEPTH_BUFFER_BIT |GL_ENABLE_BIT |GL_FOG_BIT |GL_LIGHTING_BIT |GL_LINE_BIT |GL_POINT_BIT |GL_POLYGON_BIT |GL_SCISSOR_BIT |GL_STENCIL_BUFFER_BIT |GL_TEXTURE_BIT |GL_TRANSFORM_BIT |GL_POINT_BIT |GL_LINE_BIT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glMatrixMode(GL_TEXTURE);
        glPushMatrix()
        glLoadIdentity()

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
       
        glOrtho(0.0, float(mWidth), float(mHeight), 0.0, -1.0, 1.0)
        glDisable(GL_LIGHTING);
        glDisable(GL_CULL_FACE);
        glDisable(GL_DEPTH_TEST);
        glDisable(GL_TEXTURE_2D);

        glEnable(GL_SCISSOR_TEST);
        glPointSize(1.0);
        glLineWidth(1.0);

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);

        self.pushClipArea( Rectangle(0,0,self.mTarget.get_width(),self.mTarget.get_height()) )
        
        #create Pyglet batch vertex list
        self.mBatch=pyglet.graphics.Batch()
        
    def endDraw(self):
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        glMatrixMode(GL_TEXTURE)
        glPopMatrix()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glPopAttrib()

        self.popClipArea()
        
        self.mBatch.draw()
        self.mBatch=None
        
    def setTargetPlane(self,width,height):
        self.mWidth=width
        self.mHeight=height
        
    def getTargetPlane(self):
        return self.mWidth, self.mHeight
    
    def getTargetWidth(self):
        return self.mWidth
    
    def getTargetHeight(self):
        return self.mHeight
        
    def pushClipArea(self,area):
        result=Graphics.pushClipArea(self,area)
        top=self.mClipStack[-1]
        glScissor(top.x, self.mHeight - top.y - top.height, top.width, top.height)
        return result
    
    def popClipArea(self):
        Graphics.popClipArea(self)
        if len(self.mClipStack) > 0:
            top=self.mClipStack[-1]
            glScissor(top.x, self.mHeight - top.y - top.height, top.width, top.height)
            
    def drawImage(self,image,srcX,srcY,dstX=-1,dstY=-1,width=-1,height=-1):
        if width == -1 or height == -1 or dstX == -1 or dstY == -1:
            self.drawImage(image,0,0,srcX,srcY,image.getWidth(),image.getHeight())
        else:                
            if len(self.mClipStack) == 0:
                raise GCN_EXCEPTION("Clip stack is empty, perhaps you called a draw funtion outside of beginDraw() and endDraw()?")
            if srcX < 0 or srcY < 0:
                raise GCN_EXCEPTION("Source coordinates can't be negative!")
            
            top=ClipRectangle(self.mClipStack[-1])
            src = pygame.Rect(srcX,srcY,width,height)
            dst = pygame.Rect(dstX+top.xOffset,dstY+top.yOffset,0,0)
            
            if isinstance(image,PygameImage) == False:
                raise GCN_EXCEPTION("Trying to draw an image of unknown format, must be a PygameImage.")
            
            self.mTarget.unlock()
                
            self.mTarget.blit(image.getSurface(),dst,src)
            
            self.mTarget.lock()
            
    def fillRectangle(self,rect):
        if len(self.mClipStack) == 0:
            raise GCN_EXCEPTION("Clip stack is empty, perhaps you called a draw funtion outside of beginDraw() and endDraw()?")
        
        top=self.mClipStack[-1]
        area=Rectangle(rect)
        area.x+=top.xOffset
        area.y+=top.yOffset
        
        if area.isIntersecting(top) == False:
            return None
        
        self.mTarget.fill(GuichanToPygameColor(self.mColor), pygame.Rect(area.x,area.y,area.width,area.height) )
        
    def drawPoint(self,x,y):
        if len(self.mClipStack) == 0:
            raise GCN_EXCEPTION("Clip stack is empty, perhaps you called a draw funtion outside of beginDraw() and endDraw()?")
        
        top=self.mClipStack[-1]
        x+=top.xOffset
        y+=top.yOffset
        
        if top.isPointInRect(x,y) == False:
            return None
        
        self.mTarget.set_at( (x,y), GuichanToPygameColor(self.mColor) )
        
    def drawHLine(self,x1,y,x2):
        if len(self.mClipStack) == 0:
            raise GCN_EXCEPTION("Clip stack is empty, perhaps you called a draw funtion outside of beginDraw() and endDraw()?")
        
        top=self.mClipStack[-1]
        x1+=top.xOffset
        y+=top.yOffset
        x2+=top.xOffset
        
        if y < top.y or y >= top.y+top.height:
            return None
        
        #if x1 is bigger, switch values
        if x1 > x2:
           x1^=x2
           x2^=x1
           x1^=x2
           
        if top.x > x1:
            if top.x > x2:
                return None
            
            x1=top.x
            
        if top.x+top.width <= x2:
            if top.x+top.width <= x1:
                return None
            
            x2=top.x+top.width-1
            
        pygame.draw.line(self.mTarget,GuichanToPygameColor(self.mColor),(x1,y),(x2,y))
    
    def drawVLine(self,x,y1,y2):
        if len(self.mClipStack) == 0:
            raise GCN_EXCEPTION("Clip stack is empty, perhaps you called a draw funtion outside of beginDraw() and endDraw()?")
        
        top=self.mClipStack[-1]
        x+=top.xOffset
        y1+=top.yOffset
        y2+=top.yOffset
        
        if x < top.x or x >= top.x+top.width:
            return None
        
        if y1 > y2:
           y1^=y2
           y2^=y1
           y1^=y2
           
        if top.y > y1:
            if top.y > y2:
                return None
            
            y1=top.y
            
        if top.y+top.height <= y2:
            if top.y+top.height <= y1:
                return None
            
            y2=top.y+top.height-1
            
        pygame.draw.line(self.mTarget,GuichanToPygameColor(self.mColor),(x,y1),(x,y2))
        
    def drawRectangle(self,rect):
        x1=rect.x
        x2=rect.x+rect.width-1
        y1=rect.y
        y2=rect.y+rect.height-1
        
        self.drawHLine(x1, y1, x2)
        self.drawHLine(x1, y2, x2)

        self.drawVLine(x1, y1, y2)
        self.drawVLine(x2, y1, y2)
        
    def drawLine(self,x1,y1,x2,y2):
        if len(self.mClipStack) == 0:
            raise GCN_EXCEPTION("Clip stack is empty, perhaps you called a draw funtion outside of beginDraw() and endDraw()?")
        
        top=self.mClipStack[-1]
        x1+=top.xOffset
        y1+=top.yOffset
        x2+=top.xOffset
        y2+=top.yOffset        
        
        pygame.draw.line(self.mTarget,GuichanToPygameColor(self.mColor),(x1,y1),(x2,y2))
        
    def setColor(self,color):
        self.mColor=color
        glColor4ub(color.r, color.g, color.b, color.a)
        self.mAlpha = (False if color.a != 255 else True)
        
        if self.mAlpha == True:
            glEnable(GL_BLEND)
        
    def getColor(self):
        return self.mColor

            
        
        
        
        
    
    