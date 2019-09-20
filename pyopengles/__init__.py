#
# Copyright (c) 2012 Peter de Rivaz
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted.
#
# Raspberry Pi 3d demo using OpenGLES 2.0 via Python
#
# Version 0.1 (Draws a rectangle using vertex and fragment shaders)
# Version 0.2 (Draws a Julia set on top of a Mandelbrot controlled by the mouse.  Mandelbrot rendered to texture in advance.

import ctypes
import time
import math
# Pick up our constants extracted from the header files with prepare_constants.py
from .egl import *
from .gl2 import *
from .gl2ext import *

# Define verbose=True to get debug messages
verbose = True

# Define some extra constants that the automatic extraction misses
EGL_DEFAULT_DISPLAY = 0
EGL_NO_CONTEXT = 0
EGL_NO_DISPLAY = 0
EGL_NO_SURFACE = 0
DISPMANX_PROTECTION_NONE = 0

# Open the libraries
bcm = ctypes.CDLL('libbcm_host.so')
opengles = ctypes.CDLL('libbrcmGLESv2.so')
openegl = ctypes.CDLL('libbrcmEGL.so')

eglint = ctypes.c_int

eglshort = ctypes.c_short

def eglints(L):
    """Converts a tuple to an array of eglints (would a pointer return be better?)"""
    return (eglint*len(L))(*L)

eglfloat = ctypes.c_float

def eglfloats(L):
    return (eglfloat*len(L))(*L)

def check(e):
    """Checks that error is zero"""
    if e==0: return
    if verbose:
        print('Error code',hex(e&0xffffffff))
    raise ValueError

class EGL(object):

    def __init__(self,depthbuffer=False):
        """Opens up the OpenGL library and prepares a window for display"""
        b = bcm.bcm_host_init()
        assert b==0
        self.display = openegl.eglGetDisplay(EGL_DEFAULT_DISPLAY)
        assert self.display
        r = openegl.eglInitialize(self.display,0,0)
        assert r
        if depthbuffer:
            attribute_list = eglints(     (EGL_RED_SIZE, 8,
                                      EGL_GREEN_SIZE, 8,
                                      EGL_BLUE_SIZE, 8,
                                      EGL_ALPHA_SIZE, 8,
                                      EGL_SURFACE_TYPE, EGL_WINDOW_BIT,
                                      EGL_DEPTH_SIZE, 16,
                                      EGL_NONE) )
        else:
            attribute_list = eglints(     (EGL_RED_SIZE, 8,
                                      EGL_GREEN_SIZE, 8,
                                      EGL_BLUE_SIZE, 8,
                                      EGL_ALPHA_SIZE, 8,
                                      EGL_SURFACE_TYPE, EGL_WINDOW_BIT,
                                      EGL_NONE) )
        # EGL_SAMPLE_BUFFERS,  1,
        # EGL_RENDERABLE_TYPE, EGL_OPENGL_ES2_BIT,

        numconfig = eglint()
        config = ctypes.c_void_p()
        r = openegl.eglChooseConfig(self.display,
                                     ctypes.byref(attribute_list),
                                     ctypes.byref(config), 1,
                                     ctypes.byref(numconfig));
        assert r
        r = openegl.eglBindAPI(EGL_OPENGL_ES_API)
        assert r
        if verbose:
            print('numconfig=',numconfig)
        context_attribs = eglints( (EGL_CONTEXT_CLIENT_VERSION, 2, EGL_NONE) )
        self.context = openegl.eglCreateContext(self.display, config,
                                        EGL_NO_CONTEXT,
                                        ctypes.byref(context_attribs))
        assert self.context != EGL_NO_CONTEXT
        width = eglint()
        height = eglint()
        s = bcm.graphics_get_display_size(0,ctypes.byref(width),ctypes.byref(height))
        self.width = width
        self.height = height
        assert s>=0
        dispman_display = bcm.vc_dispmanx_display_open(0)
        dispman_update = bcm.vc_dispmanx_update_start( 0 )
        dst_rect = eglints( (0,0,width.value,height.value) )
        src_rect = eglints( (0,0,width.value<<16, height.value<<16) )
        assert dispman_update
        assert dispman_display
        dispman_element = bcm.vc_dispmanx_element_add ( dispman_update, dispman_display,
                                  0, ctypes.byref(dst_rect), 0,
                                  ctypes.byref(src_rect),
                                  DISPMANX_PROTECTION_NONE,
                                  0 , 0, 0)
        bcm.vc_dispmanx_update_submit_sync( dispman_update )
        nativewindow = eglints((dispman_element,width,height));
        nw_p = ctypes.pointer(nativewindow)
        self.nw_p = nw_p
        self.surface = openegl.eglCreateWindowSurface( self.display, config, nw_p,
            eglints((EGL_RENDER_BUFFER, EGL_SINGLE_BUFFER, EGL_NONE)) )
        assert self.surface != EGL_NO_SURFACE
        r = openegl.eglMakeCurrent(self.display, self.surface, self.surface, self.context)
        assert r


