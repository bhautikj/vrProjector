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

ctx = moderngl.create_standalone_context()

prog = ctx.program(
    vertex_shader='''
        #version 330

        in vec2 in_vert;
        out vec2 vert_pos;

        void main() {
            // boilerplate - normalize vert position from [-1,1] to [0,1]
            vert_pos = 0.5*(in_vert + 1.0);
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
    ''',
    fragment_shader='''
        #version 330

        in vec2 vert_pos;
        out vec3 f_color;

        void main() {
            f_color = vec3(vert_pos.x, vert_pos.y, 0.0);
        }
    ''',
)

vertices = np.array([
  1.0,  1.0,
  -1.0,  1.0,
  -1.0, -1.0,
  -1.0, -1.0,
   1.0, -1.0,
   1.0,  1.0
])

vbo = ctx.buffer(vertices.astype('f4').tobytes())
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert')

fbo = ctx.simple_framebuffer((512, 512))
fbo.use()
fbo.clear(0.0, 0.0, 0.0, 1.0)
vao.render(moderngl.TRIANGLE_STRIP) 
        
Image.frombytes('RGB', fbo.size, fbo.read(), 'raw', 'RGB', 0, -1).show()