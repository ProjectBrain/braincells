import json
import random
import ctypes
import numpy as np
import zmq

from pyopengles import *

egl = EGL()

WIDTH=egl.width
HEIGHT=egl.height

glscreensize = eglfloats([WIDTH.value, HEIGHT.value])

print("screen width", WIDTH, "height", HEIGHT)


def catcherror(location):
    e=opengles.glGetError()
    if e:
        print("error", hex(e), "at", location)
        raise ValueError


def showlog(shader):
    """Prints the compile log for a shader"""
    N=1024
    log=(ctypes.c_char*N)()
    loglen=ctypes.c_int()
    opengles.glGetShaderInfoLog(shader,N,ctypes.byref(loglen),ctypes.byref(log))
    print(log.value)

def showprogramlog(shader):
    """Prints the compile log for a program"""
    N=1024
    log=(ctypes.c_char*N)()
    loglen=ctypes.c_int()
    opengles.glGetProgramInfoLog(shader,N,ctypes.byref(loglen),ctypes.byref(log))
    print(log.value)

opengles.glGetString.restype = ctypes.c_char_p
print(opengles.glGetString(GL_EXTENSIONS))

opengles.glClearColor(eglfloat(0.0), eglfloat(0.0), eglfloat(0.0), eglfloat(1.0));
opengles.glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);

points = np.array([
  [-1, -1, 1],
  [1, -1, 1],
  [1, 1, 1],
  [-1, 1, 1]
], dtype="float32")

# Top-down
lightpositions = eglfloats([
    0.4, 0.7225, #AF3
    0.5675, 0.725, #AF4
    0.22, 0.6975, #F7
    0.7475, 0.6975, #F8
    0.3475, 0.6225, #F3
    0.615, 0.6225, #F4
    0.245, 0.5675, #FC5
    0.7225, 0.57, #FC6
    0.145, 0.49, #T7
    0.825, 0.485, #T8
    0.2075, 0.3, #P7
    0.76, 0.3, #P8
    0.3475, 0.1725, #O1
    0.6175, 0.1725, #O2
])

lightcolors = eglfloats([math.ceil(random.random()-0.5) for _ in range(0, len(lightpositions)//2*3)])

print("lights", lightcolors)

sources = []

def loadshader(filename, shadertype):
  source = ctypes.c_char_p(open(filename).read().encode('utf-8'))
  sources.append(source)
  shader = opengles.glCreateShader(shadertype)
  opengles.glShaderSource(shader, 1, ctypes.byref(source), 0)
  opengles.glCompileShader(shader)
  print("shader", filename)
  showlog(shader)
  return shader

def createprogram(*args):
  program = opengles.glCreateProgram()
  for shader in args:
    opengles.glAttachShader(program, shader)
  opengles.glLinkProgram(program)

  status = eglint()
  opengles.glGetProgramiv(program, GL_LINK_STATUS, ctypes.byref(status))
  print("ruh roh", status.value == 1)
  showprogramlog(program)
  return program

stepvs = loadshader("shaders/step.vs", GL_VERTEX_SHADER)
stepfs = loadshader("shaders/step.fs", GL_FRAGMENT_SHADER)

stepprogram = createprogram(stepvs, stepfs)

drawvs = loadshader("shaders/draw.vs", GL_VERTEX_SHADER)
drawfs = loadshader("shaders/draw.fs", GL_FRAGMENT_SHADER)

drawprogram = createprogram(drawvs, drawfs)


stepprogram_vertex = opengles.glGetAttribLocation(stepprogram, b"vertex")
stepprogram_tex = opengles.glGetUniformLocation(stepprogram, b"tex")
stepprogram_texsize = opengles.glGetUniformLocation(stepprogram, b"texsize")
catcherror("step: get attributes")

print(stepprogram_tex)
stepprogram_vertex = 0

drawprogram_vertex = opengles.glGetAttribLocation(drawprogram, b"vertex")
drawprogram_tex = opengles.glGetUniformLocation(drawprogram, b"tex")
drawprogram_lightpos = opengles.glGetUniformLocation(drawprogram, b"lightpos")
drawprogram_lightcolor = opengles.glGetUniformLocation(drawprogram, b"lightcolor")
drawprogram_screensize = opengles.glGetUniformLocation(drawprogram, b"screensize")
catcherror("draw: get attributes")

print(drawprogram_tex)
drawprogram_vertex = 0

opengles.glViewport(0, 0, WIDTH, HEIGHT)

opengles.glPointSize(40)
vbuf = eglint()
opengles.glGenBuffers(1, ctypes.byref(vbuf))
opengles.glBindBuffer(GL_ARRAY_BUFFER, vbuf)
#opengles.glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(points), ctypes.byref(points), GL_STATIC_DRAW)
opengles.glBufferData(GL_ARRAY_BUFFER, points.nbytes, points.ctypes.data, GL_STATIC_DRAW)
catcherror("allocate buffers")
#

TEXSCALE = 1.0/32.0 #1.0/1.0
TEXWIDTH = int(WIDTH.value * TEXSCALE)
TEXHEIGHT = int(HEIGHT.value * TEXSCALE)
#gltexsize = eglfloats([float(TEXWIDTH), float(TEXHEIGHT)])

print("tex width", TEXWIDTH, "height", TEXHEIGHT)

print("calculating color range")
predata = np.random.random((TEXWIDTH, TEXHEIGHT, 3))
texdata = (predata*predata*255).astype(np.uint8)
#texdata = np.array([[x/1920.0*255, y/1080.0*255, 255] for x in xrange(1920) for y in xrange(1080)], dtype='uint8')
#texdata = np.array([[255, 255, 255] for x in xrange(1920) for y in xrange(1080)], dtype='uint8')
#texdata = np.zeros((1920, 1080, 3), dtype='uint8')
print("done")
texdata2 = (np.random.random((TEXWIDTH, TEXHEIGHT, 3))*255).astype(np.uint8)
# texdata2 = np.zeros((TEXWIDTH, TEXHEIGHT, 3), dtype='uint8')

tex=eglint()
opengles.glGenTextures(1,ctypes.byref(tex))
opengles.glBindTexture(GL_TEXTURE_2D,tex)
#opengles.glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,1920,1080,0,GL_RGB,GL_UNSIGNED_SHORT_5_6_5, texdata.ctypes.data)
opengles.glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,TEXWIDTH,TEXHEIGHT,0,GL_RGB,GL_UNSIGNED_BYTE, texdata.ctypes.data)
#opengles.glTexImage2D(GL_TEXTURE_2D,0,GL_BGRA_EXT,1920,1080,0,GL_BGRA_EXT,GL_UNSIGNED_BYTE, texdata.ctypes.data)
opengles.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
opengles.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
opengles.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
opengles.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
catcherror("create texture 1")

tex2=eglint()
opengles.glGenTextures(1,ctypes.byref(tex2))
opengles.glBindTexture(GL_TEXTURE_2D,tex2)
#opengles.glTexImage2D(GL_TEXTURE_2D,0,GL_BGRA_EXT,1920,1080,0,GL_BGRA_EXT,GL_UNSIGNED_BYTE, 0)
#opengles.glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,1920,1080,0,GL_RGB,GL_UNSIGNED_SHORT_5_6_5, texdata2.ctypes.data)
opengles.glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,TEXWIDTH,TEXHEIGHT,0,GL_RGB,GL_UNSIGNED_BYTE, 0) #,texdata2.ctypes.data)
#opengles.glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,1920,1080,0,GL_RGB,GL_UNSIGNED_SHORT_5_6_5,0)
opengles.glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, eglfloat(GL_NEAREST))
opengles.glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, eglfloat(GL_NEAREST))
catcherror("create texture 2")

print("screen width", WIDTH, "height", HEIGHT)
print("tex width", TEXWIDTH, "height", TEXHEIGHT)
# print("dims", opengles.glGetIntegerv(GL_MAX_VIEWPORT_DIMS)) ##crash?

fbuf = eglint()
opengles.glGenFramebuffers(1,ctypes.byref(fbuf))
opengles.glBindFramebuffer(GL_FRAMEBUFFER,fbuf)
opengles.glViewport(0, 0, TEXWIDTH, TEXHEIGHT)
opengles.glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,tex2,0)
print("framebuffer status", hex(opengles.glCheckFramebufferStatus(GL_FRAMEBUFFER)))
catcherror("create framebuffer")

#showerror()

def swaptex():
    global tex, tex2
    tex, tex2 = tex2, tex
    opengles.glBindTexture(GL_TEXTURE_2D, tex)
    opengles.glBindFramebuffer(GL_FRAMEBUFFER, fbuf)
    opengles.glViewport(0, 0, TEXWIDTH, TEXHEIGHT)
    opengles.glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,tex2,0)
    #print "framebuffer status", hex(opengles.glCheckFramebufferStatus(GL_FRAMEBUFFER))
    catcherror("swaptex")

def step():
    opengles.glBindFramebuffer(GL_FRAMEBUFFER, fbuf)
    opengles.glViewport(0, 0, TEXWIDTH, TEXHEIGHT)

    opengles.glBindBuffer(GL_ARRAY_BUFFER, vbuf)
    catcherror("step: load vertices 1")
    opengles.glVertexAttribPointer(stepprogram_vertex, 3, GL_FLOAT, 0, 0, 0)
    catcherror("step: load vertices 2")
    opengles.glEnableVertexAttribArray(stepprogram_vertex)
    catcherror("step: load vertices 3")

    opengles.glUseProgram(stepprogram)

    opengles.glBindTexture(GL_TEXTURE_2D, tex)
    opengles.glUniform1i(stepprogram_tex, 0)
    opengles.glUniform2f(stepprogram_texsize, eglfloat(TEXWIDTH), eglfloat(TEXHEIGHT))
    #opengles.glBindTexture(GL_TEXTURE_2D, tex)

    #opengles.glDrawArrays(GL_POINTS, 0, len(points))
    opengles.glDrawArrays(GL_TRIANGLE_FAN, 0, len(points))
    # Send this to make the graphics drawn visible
    catcherror("step: drawArrays")

    #opengles.glFlush()
    #opengles.glFinish()



def draw():
    opengles.glBindFramebuffer(GL_FRAMEBUFFER, 0)
    opengles.glViewport(0, 0, WIDTH, HEIGHT)

    opengles.glBindBuffer(GL_ARRAY_BUFFER, vbuf)
    catcherror("draw: load vertices 1")
    opengles.glVertexAttribPointer(drawprogram_vertex, 3, GL_FLOAT, 0, 0, 0)
    catcherror("draw: load vertices 2")
    opengles.glEnableVertexAttribArray(drawprogram_vertex)
    catcherror("draw: load vertices 3")
    opengles.glUseProgram(drawprogram)

    opengles.glBindTexture(GL_TEXTURE_2D, tex)
    opengles.glUniform1i(drawprogram_tex, 0)
    opengles.glUniform2f(drawprogram_screensize, eglfloat(WIDTH.value), eglfloat(HEIGHT.value))
    opengles.glUniform2fv(drawprogram_lightpos, len(lightpositions), ctypes.byref(lightpositions))
    opengles.glUniform3fv(drawprogram_lightcolor, len(lightcolors), ctypes.byref(lightcolors))
    catcherror("draw: load variables")
    #opengles.glBindTexture(GL_TEXTURE_2D, tex)

    #opengles.glDrawArrays(GL_POINTS, 0, len(points))
    opengles.glDrawArrays(GL_TRIANGLE_FAN, 0, len(points))
    # Send this to make the graphics drawn visible
    catcherror("draw: drawArrays")
    # opengles.glFinish()

    # openegl.eglSwapBuffers(egl.display, egl.surface)
#opengles.glDisableVertexAttribArray(attr_vertex)
print("colors", lightcolors[3])


context = zmq.Context()
# global bands
bands = context.socket(zmq.SUB)
bands.connect('ipc:///var/socks/bands')
bands.setsockopt(zmq.SUBSCRIBE, b'')

FPS = 60.0
STEPRATE = 0.175
# STEPRATE = 1.0
counter = 0
THRESHOLD = 1.0/2.25

global data
data = None
while True:
    t = time.time()
    if round(t % 1, 1) == 0:
        bands.setsockopt(zmq.SUBSCRIBE, b'')
    try:
        data = bands.recv_json(flags=zmq.NOBLOCK)
        # print(data)
    except zmq.ZMQError:
        pass

    if data:
        #time.sleep(1)
        #continue

        for i in range(0, 14):
            beta = data['beta'][i]
            theta = data['theta'][i]
            alpha = data['alpha'][i]
            globl = data['global'][i]
            r = i*3
            g = i*3+1
            b = i*3+2

            if beta > globl*THRESHOLD:
                lightcolors[r] = 1.0
            else:
                # lightcolors[r] = beta / (globl * THRESHOLD)
                lightcolors[r] = 0.0
            if theta > globl*THRESHOLD*1.05:
                lightcolors[g] = 1.0
            else:
                # lightcolors[g] = theta / (globl * THRESHOLD)
                lightcolors[g] = 0.0
            if alpha > globl*THRESHOLD*0.95:
                lightcolors[b] = 1.0
            else:
                # lightcolors[b] = alpha / (globl * THRESHOLD)
                lightcolors[b] = 0.0
    counter += STEPRATE
    # if True:
    opengles.glFlush()
    if counter >= 1:
        step()
        swaptex()
        counter -= 1
    draw()
    opengles.glFinish()

    dt = time.time() - t
    if dt < 1.0/FPS:
        time.sleep(1.0/FPS - dt)
