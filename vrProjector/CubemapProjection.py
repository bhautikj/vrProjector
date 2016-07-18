from AbstractProjection import AbstractProjection
from PIL import Image
import math

class CubemapProjection(AbstractProjection):
  def __init__(self):
    AbstractProjection.__init__(self)

  def set_angular_resolution(self):
    # imsize on a face: covers 90 degrees
    #     |\
    #  0.5| \
    #     |  \
    #     -----
    #     1/self.imsize[0]
    #  angular res ~= arctan(1/self.imsize[0], 0.5)
    self.angular_resolution = math.atan2(1/self.imsize[0], 0.5)

  def loadImages(self, front, right, back, left, top, bottom):
    self.front = Image.open(front)
    self.right = Image.open(right)
    self.back = Image.open(back)
    self.left = Image.open(left)
    self.top = Image.open(top)
    self.bottom = Image.open(bottom)
    self.imsize = self.front.size
    self.set_angular_resolution()

  def initImages(self, width, height):
    self.imsize = (width*2, height*2)
    self.front = Image.new("RGB", self.imsize)
    self.right = Image.new("RGB", self.imsize)
    self.back = Image.new("RGB", self.imsize)
    self.left = Image.new("RGB", self.imsize)
    self.top = Image.new("RGB", self.imsize)
    self.bottom = Image.new("RGB", self.imsize)
    self.set_angular_resolution()

  def saveImages(self, front, right, back, left, top, bottom):
    self.downsample(self.front).save(front)
    self.downsample(self.right).save(right)
    self.downsample(self.back).save(back)
    self.downsample(self.left).save(left)
    self.downsample(self.top).save(top)
    self.downsample(self.bottom).save(bottom)

  def _pixel_value(self, angle):
    theta = angle[0]
    phi = angle[1]
    if theta is None or phi is None:
      return (0,0,0)

    sphere_pnt = self.point_on_sphere(theta, phi)
    x = sphere_pnt[0]
    y = sphere_pnt[1]
    z = sphere_pnt[2]

    eps = 1e-6

    if math.fabs(x)>eps:
      if x>0:
        t = 0.5/x
        u = 0.5+t*y
        v = 0.5+t*z
        if u>=0.0 and u<=1.0 and v>=0.0 and v<=1.0:
          return self.get_pixel_from_uv(u, v, self.front)
      elif x<0:
        t = 0.5/-x
        u = 0.5+t*-y
        v = 0.5+t*z
        if u>=0.0 and u<=1.0 and v>=0.0 and v<=1.0:
          return self.get_pixel_from_uv(u, v, self.back)

    if math.fabs(y)>eps:
      if y>0:
        t = 0.5/y
        u = 0.5+t*-x
        v = 0.5+t*z
        if u>=0.0 and u<=1.0 and v>=0.0 and v<=1.0:
          return self.get_pixel_from_uv(u, v, self.right)
      elif y<0:
        t = 0.5/-y
        u = 0.5+t*x
        v = 0.5+t*z
        if u>=0.0 and u<=1.0 and v>=0.0 and v<=1.0:
          return self.get_pixel_from_uv(u, v, self.left)

    if math.fabs(z)>eps:
      if z>0:
        t = 0.5/z
        u = 0.5+t*y
        v = 0.5+t*-x
        if u>=0.0 and u<=1.0 and v>=0.0 and v<=1.0:
          return self.get_pixel_from_uv(u, v, self.bottom)
      elif z<0:
        t = 0.5/-z
        u = 0.5+t*y
        v = 0.5+t*x
        if u>=0.0 and u<=1.0 and v>=0.0 and v<=1.0:
          return self.get_pixel_from_uv(u, v, self.top)

    return None

  def get_theta_phi(self, _x, _y, _z):
    dv = math.sqrt(_x*_x + _y*_y + _z*_z)
    x = _x/dv
    y = _y/dv
    z = _z/dv
    theta = math.atan2(y, x)
    phi = math.asin(z)
    return theta, phi

  @staticmethod
  def angular_position(texcoord):
    u = texcoord[0]
    v = texcoord[1]
    return None

  def reprojectToThis(self, sourceProjection):
    halfcubeedge = 1.0

    for x in range(self.imsize[0]):
      for y in range(self.imsize[1]):
        u = 2.0*(float(x)/float(self.imsize[0])-0.5)
        v = 2.0*(float(y)/float(self.imsize[1])-0.5)

        # front
        theta, phi = self.get_theta_phi(halfcubeedge, u, v)
        pixel = sourceProjection.pixel_value((theta, phi))
        self.front.putpixel((x,y), pixel)

        # right
        theta, phi = self.get_theta_phi(-u, halfcubeedge, v)
        pixel = sourceProjection.pixel_value((theta, phi))
        self.right.putpixel((x,y), pixel)

        # left
        theta, phi = self.get_theta_phi(u, -halfcubeedge, v)
        pixel = sourceProjection.pixel_value((theta, phi))
        self.left.putpixel((x,y), pixel)

        # back
        theta, phi = self.get_theta_phi(-halfcubeedge, -u, v)
        pixel = sourceProjection.pixel_value((theta, phi))
        self.back.putpixel((x,y), pixel)

        # bottom
        theta, phi = self.get_theta_phi(-v, u, halfcubeedge)
        pixel = sourceProjection.pixel_value((theta, phi))
        self.bottom.putpixel((x,y), pixel)

        # top
        theta, phi = self.get_theta_phi(v, u, -halfcubeedge)
        pixel = sourceProjection.pixel_value((theta, phi))
        self.top.putpixel((x,y), pixel)
