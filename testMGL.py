import vrProjector
from PIL import Image

FRAGPROG='''
#version 330

in vec2 vert_pos;
out vec3 f_color;

void main() {
    f_color = vec3(vert_pos.x, vert_pos.y, 0.0);
}'''

FRAGPROGTEX='''
#version 330

uniform sampler2D Texture;

in vec2 vert_pos;
out vec4 f_color;

void main() {
    f_color = vec4(texture(Texture, vert_pos).rgb, 1.0);
}'''

def main():
  wrapper = vrProjector.ModernGLWrapper(fragProg=FRAGPROGTEX, outWidth=1024, outHeight=768, texture="tests/testTex-1024_768.png")
  im = wrapper.render()
  im.save('test.png')  
  
if __name__== "__main__":
  main()

