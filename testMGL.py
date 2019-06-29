import vrProjector
from PIL import Image
import math
from pyrr import Matrix44

FRAGPROG='''
#version 330

in vec2 uv;
out vec3 f_color;

void main() {
    f_color = vec3(uv.x, uv.y, 0.0);
}'''

FRAGPROGTEX='''
#version 330
#define PI 3.141592653589793
precision highp float;

void UVAtEuler(in vec3 euler, out vec2 uv) {
  float fixedPhi = PI*0.5 - euler.y;
  uv.x = 0.5 + (euler.x/(2.0*PI));
  uv.y = 1.0 - (0.5 + (fixedPhi/PI));
}

void EulerAtUV(in vec2 uv, out vec3 euler) {
  euler.x = 2.0*PI*(uv.x - 0.5);
  euler.y = PI*(uv.y);
  euler.z = 0.0;
}

void EulerToCartesian(in vec3 euler, out vec4 cartesian) {
  cartesian.x = sin(euler.y) * cos(euler.x);
  cartesian.y = sin(euler.y) * sin(euler.x);
  cartesian.z = cos(euler.y);
  cartesian.w = 1.0;
}

void CartesianToEuler(in vec4 cartesian, out vec3 euler) {
  float r = length(cartesian.xyz);
  euler.y = acos(cartesian.z/r);
  euler.x = atan(cartesian.y, cartesian.x);
  euler.z = 0.0;
}

uniform sampler2D Texture;
uniform mat4 transform;

in vec2 uv;
out vec4 f_color;

void main() {
  vec3 euler = vec3(0.0,0.0,0.0);
  vec2 uvOut = vec2(0.0, 0.0);
  vec4 cartesian = vec4(0.0,0.0,0.0,1.0);
  
  EulerAtUV(uv, euler);
  EulerToCartesian(euler, cartesian);
  cartesian *= transform;
  CartesianToEuler(cartesian, euler);  
  UVAtEuler(euler, uvOut);
  
  f_color = vec4(texture(Texture, uvOut).rgb, 1.0);
}'''

def main():
  wrapper = vrProjector.ModernGLWrapper(fragProg=FRAGPROGTEX, outWidth=1024, outHeight=768, texture="images/equirectangular.png")

  transform = wrapper.prog['transform']
  rots = [0,math.pi*0.25,0]
  trfX = Matrix44.from_x_rotation(rots[0])
  trfY = Matrix44.from_y_rotation(rots[1])
  trfZ = Matrix44.from_z_rotation(rots[2])
  transform.write((trfZ*trfY*trfX).astype('f4').tobytes())
  im = wrapper.render()
  im.save('test.png')  
  
if __name__== "__main__":
  main()

