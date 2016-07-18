from AbstractProjection import AbstractProjection
import math

class EquirectangularProjection(AbstractProjection):
  def __init__(self):
    AbstractProjection.__init__(self)

  def set_angular_resolution(self):
    self.angular_resolution = math.pi/self.imsize[1]

  def _pixel_value(self, angle):
    theta = angle[0]
    phi = angle[1]
    if theta is None or phi is None:
      return (0,0,0)
    # theta: -pi..pi -> u: 0..1
    u = 0.5+0.5*(theta/math.pi)
    # phi: -pi/2..pi/2 -> v: 0..1
    v = 0.5+(phi/math.pi)
    return self.get_pixel_from_uv(u,v, self.image)

  @staticmethod
  def angular_position(texcoord):
    u = texcoord[0]
    v = texcoord[1]
    # theta: u: 0..1 -> -pi..pi
    theta = math.pi*2.0*(u-0.5)
    # phi: v: 0..1 - > -pi/2..pi/2
    phi = math.pi*(v-0.5)
    return (theta,phi)
