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
  wrapper = vrProjector.ModernGLWrapper(FRAGPROGTEX, 1024, 768)
  textureSrc = Image.open("testTex-1024_768.png").transpose(Image.FLIP_TOP_BOTTOM).convert('RGB')
  texture = wrapper.ctx.texture(textureSrc.size, 3, textureSrc.tobytes())
  texture.build_mipmaps()
  texture.use()
          
  im = wrapper.render()
  im.save('test.png')  
  
  

if __name__== "__main__":
  main()

