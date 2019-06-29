#
# Bhautik Joshi bjoshi@gmail.com 2019
# render to fullscreen quad with modernGL
# passes vertex position via vert_pos from the vertex
# shader to the fragment_shader; is normalized to [0,1]
# with (0,0) in the bottom-left corner
#

import moderngl
import numpy as np

from PIL import Image
import math
import abc
import numpy as np

from multiprocessing.dummy import Pool as ThreadPool

QUADVSPROG = '''
#version 330

in vec2 in_vert;
out vec2 uv;

void main() {
    // boilerplate - normalize vert position from [-1,1] to [0,1]
    uv = 0.5*(in_vert + 1.0);
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
'''

SAMPLEFSPROG='''
#version 330

in vec2 uv;
out vec3 f_color;

void main() {
    f_color = vec3(uv.x, uv.y, 0.0);
}
'''

VERTICES = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0])

class ModernGLWrapper:
  __metaclass__ = abc.ABCMeta

  def __init__(self, fragProg=SAMPLEFSPROG, outWidth=512, outHeight=512, texture=None):
    self.ctx = moderngl.create_standalone_context()

    ##
    ## add 
    ## uniform sampler2D Texture;
    ## to your fragment shader to access the texture
    ##
    if texture != None:
      textureSrc = Image.open(texture).transpose(Image.FLIP_TOP_BOTTOM).convert('RGB')
      self.texture = self.ctx.texture(textureSrc.size, 3, textureSrc.tobytes())
      #self.texture.filter = (moderngl.moderngl.LINEAR. moderngl.moderngl.LINEAR)
      #self.texture.build_mipmaps() - don't do this! converts sampling mode to mipmaps, expensive
      self.texture.use()
    
    self.quadVsProg = QUADVSPROG
    self.quadFsProg = fragProg
    self.vertices = VERTICES
    self.outWidth = outWidth
    self.outHeight = outHeight
    self.prog = self.ctx.program(vertex_shader = self.quadVsProg, fragment_shader=self.quadFsProg)
    self.vbo = self.ctx.buffer(self.vertices.astype('f4').tobytes())
    self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')
    self.fbo = self.ctx.simple_framebuffer((self.outWidth, self.outHeight))
    self.fbo.use()
    
  def render(self):
    self.fbo.clear(0.0, 0.0, 0.0, 1.0)
    self.vao.render(moderngl.TRIANGLE_STRIP)
    im = Image.frombytes('RGB', self.fbo.size, self.fbo.read(), 'raw', 'RGB', 0, -1)
    return im
