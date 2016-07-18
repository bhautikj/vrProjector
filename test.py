# imports
from PIL import Image
import abc
import math

from multiprocessing.dummy import Pool as ThreadPool

class AbstractProjection:
  __metaclass__ = abc.ABCMeta

  def __init__(self):
    self.use_bilinear = False
    pass

  def set_use_bilinear(self, val):
    self.use_bilinear = val

  def get_pixel_from_uv(self, u, v, image):
    x = int(self.imsize[0]*u)
    y = int(self.imsize[1]*v)
    x = min(x,self.imsize[0]-1)
    y = min(y,self.imsize[1]-1)
    try:
      pix = image.getpixel((x,y))
      return pix
    except:
      print x,y, self.imsize[0], self.imsize[1]

  def loadImage(self, imageFile):
    self.image = Image.open(imageFile)
    self.imsize = self.image.size
    self.set_angular_resolution()

  def initImage(self, width, height):
    self.imsize = (width*2, height*2)
    self.image = Image.new("RGB", self.imsize)
    self.set_angular_resolution()

  def downsample(self, image):
    resized = image.resize((self.imsize[0]/2, self.imsize[1]/2), Image.ANTIALIAS)
    return resized

  def saveImage(self, destFile):
    self.downsample(self.image).save(destFile)

  # this isn't any faster because of the GIL on the image object
  def reprojectToThisThreaded(self, sourceProjection, numThreads):
    uvList = []
    fx = float(self.imsize[0])
    fy = float(self.imsize[1])

    angleList = [self.angular_position((float(i)/fx,float(j)/fy)) for i in range(self.imsize[0]) for j in range(self.imsize[1])]

    poolAngles = ThreadPool(numThreads)
    image = poolAngles.map(sourceProjection.pixel_value, angleList)
    poolAngles.close()
    poolAngles.join()

    idx = 0
    for x in range(self.imsize[0]):
      for y in range(self.imsize[1]):
        pixel = image[idx]
        if pixel is None:
          print x,y
        else:
          self.image.putpixel((x,y),pixel)
        idx = idx + 1


  def reprojectToThis(self, sourceProjection):
    for x in range(self.imsize[0]):
      for y in range(self.imsize[1]):
        u = float(x)/float(self.imsize[0])
        v = float(y)/float(self.imsize[1])
        theta, phi = self.angular_position((u,v))
        if theta is None or phi is None:
          pixel = (0,0,0)
        else:
          pixel = sourceProjection.pixel_value((theta, phi))
        self.image.putpixel((x,y),pixel)

  def point_on_sphere(self, theta, phi):
    r = math.cos(phi)
    return (r*math.cos(theta), r*math.sin(theta), math.sin(phi))

  def pixel_value(self, angle):
    if self.use_bilinear:
      return self._pixel_value_bilinear_interpolated(angle)
    else:
      return self._pixel_value(angle)

  @abc.abstractmethod
  def _pixel_value(self, angle):
    return None

  @abc.abstractmethod
  def angular_position(self, texcoord):
    return None

  @abc.abstractmethod
  def set_angular_resolution(self):
    return None

  @staticmethod
  def bilinear_interpolation(x, y, points):
      '''Interpolate (x,y) from values associated with four points.

      The four points are a list of four triplets:  (x, y, value).
      The four points can be in any order.  They should form a rectangle.

          >>> bilinear_interpolation(12, 5.5,
          ...                        [(10, 4, 100),
          ...                         (20, 4, 200),
          ...                         (10, 6, 150),
          ...                         (20, 6, 300)])
          165.0

      '''
      # See formula at:  http://en.wikipedia.org/wiki/Bilinear_interpolation

      points = sorted(points)               # order points by x, then by y
      (x1, y1, q11), (_x1, y2, q12), (x2, _y1, q21), (_x2, _y2, q22) = points

      if x1 != _x1 or x2 != _x2 or y1 != _y1 or y2 != _y2:
          raise ValueError('points do not form a rectangle')
      if not x1 <= x <= x2 or not y1 <= y <= y2:
          raise ValueError('(x, y) not within the rectangle')

      return (q11 * (x2 - x) * (y2 - y) +
              q21 * (x - x1) * (y2 - y) +
              q12 * (x2 - x) * (y - y1) +
              q22 * (x - x1) * (y - y1)
             ) / ((x2 - x1) * (y2 - y1) + 0.0)

  def _pixel_value_bilinear_interpolated(self, angle):
    angleeps = self.angular_resolution/8.0
    pixelA = self._pixel_value((angle[0]-angleeps, angle[1]-angleeps))
    pixelB = self._pixel_value((angle[0]-angleeps, angle[1]+angleeps))
    pixelC = self._pixel_value((angle[0]+angleeps, angle[1]-angleeps))
    pixelD = self._pixel_value((angle[0]+angleeps, angle[1]+angleeps))

    pixelR = self.bilinear_interpolation(0,0, [(-1,-1, pixelA[0]), (-1,1, pixelB[0]), (1,-1, pixelC[0]), (1,1, pixelD[0])])
    pixelG = self.bilinear_interpolation(0,0, [(-1,-1, pixelA[1]), (-1,1, pixelB[1]), (1,-1, pixelC[1]), (1,1, pixelD[1])])
    pixelB = self.bilinear_interpolation(0,0, [(-1,-1, pixelA[2]), (-1,1, pixelB[2]), (1,-1, pixelC[2]), (1,1, pixelD[2])])

    return (int(pixelR), int(pixelG), int(pixelB))

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

class SideBySideFisheyeProjection(AbstractProjection):
  def __init__(self):
    AbstractProjection.__init__(self)

  def set_angular_resolution(self):
    self.angular_resolution = math.pi/self.imsize[1]

  def _pixel_value(self, angle):
    theta = angle[0]
    phi = angle[1]
    if theta is None or phi is None:
      return (0,0,0)

    r = math.cos(phi)
    # z is elevation in this case
    sphere_pnt = self.point_on_sphere(theta, phi)

    # sphere_pnt.x: [-1..1]
    u = 0.5+(sphere_pnt[0]*-0.5)
    if theta>=0:
      u = u*0.5 + 0.5
    else:
      u = (1.0-u)*0.5

    #sphere_pnt.z: -1..1 -> v: 0..1
    v = 0.5+(sphere_pnt[2]*0.5)

    return self.get_pixel_from_uv(u,v, self.image)

  @staticmethod
  def angular_position(texcoord):
    up = texcoord[0]
    v = texcoord[1]
    # correct for hemisphere
    if up>=0.5:
      u = 2.0*(up-0.5)
    else:
      u = 2.0*up

    # ignore points outside of circles
    if ((u-0.5)*(u-0.5) + (v-0.5)*(v-0.5))>0.25:
      return None, None

    # v: 0..1-> vp: -1..1
    phi = math.asin(2.0*(v-0.5))

    # u = math.cos(phi)*math.cos(theta)
    # u: 0..1 -> upp: -1..1
    u = 1.0-u
    theta = math.acos( 2.0*(u-0.5) / math.cos(phi) )

    if up<0.5:
       theta = theta-math.pi

    return (theta,phi)

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

#
# sbs = SideBySideFisheyeProjection()
# sbs.initImage(2048, 1024)
## sbs.reprojectToThisThreaded(eq, 8)
# sbs.reprojectToThis(eq)
# sbs.saveImage("foo.png")
#
# sbs2 = SideBySideFisheyeProjection()
# sbs2.loadImage("foo.png")
#
# eq2 = EquirectangularProjection()
# eq2.initImage(2048,1024)
# eq2.reprojectToThis(sbs2)
# eq2.saveImage("foo2.png")

eq = EquirectangularProjection()
eq.loadImage("cuber.jpg")
eq.set_use_bilinear(True)
cb = CubemapProjection()
cb.initImages(256,256)
cb.reprojectToThis(eq)
cb.saveImages("front.png", "right.png", "back.png", "left.png", "top.png", "bottom.png")
#

# cb2 = CubemapProjection()
# cb2.loadImages("front.png", "right.png", "back.png", "left.png", "top.png", "bottom.png")
# eq2 = EquirectangularProjection()
# eq2.initImage(2048,1024)
# eq2.reprojectToThis(cb2)
# eq2.saveImage("foo.png")
