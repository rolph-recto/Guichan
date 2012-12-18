#!/usr/bin/env python

import pyglet
import pyglet.image
import pyglet.sprite
#from pygame.locals import *
#There's two Colors! Error!

from guichan import *
from image import Image

def GuichanToPygameColor(color):
    return (color.r,color.g,color.b,color.a)

class PygletImage(Image):
    def __init__(self,img=None,autoFree=False):
        self.mSprite=pyglet.sprite.Sprite(img)
        self.mAutoFree=autoFree
    
    def __del__(self):
        
        if self.mAutoFree == True:
            self.free()
    
    def getImage(self):
        return self.mImageHandle
    
    def getWidth(self):
        if self.mImageHandle == None:
            raise GCN_EXCEPTION("Trying to get the width of a non loaded image.")
        
        return self.mImageHandle.width
    
    def getHeight(self):
        if self.mImageHandle == None:
            raise GCN_EXCEPTION("Trying to get the height of a non loaded image.")
        
        return self.mImageHandle.height
    
    def getPixel(self,x,y):
        pass
    
    def putPixel(self,x,y,color):
        pass
        
    def setColorkey(self,color):
        pass
        
    def getColorkey(self):
        pass
    
    def setAlpha(self,alpha):
        if (alpha > -1 and alpha < 256) or alpha == None: 
            self.mSurface.set_alpha(alpha)
    
    def getAlpha(self):
        return self.mSurface.get_alpha()

    def convertToDisplayFormat(self):
        pass
        
    def free(self):
        tex=self.mImageHandle.get_texture()
        del self.mImageHandle
        glDeleteTextures(1, tex.id)
        
        