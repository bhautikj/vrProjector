# imports
from PIL import Image
import abc
import math

class AbstractProjection:
  __metaclass__ = abc.ABCMeta

  def __init__(self):
    pass

  def get_pixel_from_uv(self, u, v):
    x = int(self.imsize[0]*u)
    y = int(self.imsize[1]*v)
    x = min(x,self.imsize[0]-1)
    y = min(y,self.imsize[1]-1)
    try:
      pix = self.image.getpixel((x,y))
      return pix
    except:
      print x,y

  def loadImage(self, imageFile):
    self.image = Image.open(imageFile)
    self.imsize = self.image.size

  def initImage(self, width, height):
    self.imsize = (width*2, height*2)
    self.image = Image.new("RGB", self.imsize)

  def saveImage(self, destFile):
    resized = self.image.resize((self.imsize[0]/2, self.imsize[1]/2), Image.ANTIALIAS)
    resized.save(destFile)

  def reprojectToThis(self, sourceProjection):
    for x in range(self.imsize[0]):
      for y in range(self.imsize[1]):
        u = float(x)/float(self.imsize[0])
        v = float(y)/float(self.imsize[1])
        theta, phi = self.angular_position(u,v)
        if theta is None or phi is None:
          pixel = (0,0,0)
        else:
          pixel = sourceProjection.pixel_value(theta, phi)
        self.image.putpixel((x,y),pixel)

  @abc.abstractmethod
  def pixel_value(self, theta, phi):
    return None

  @abc.abstractmethod
  def angular_position(self, u, v):
    return None

class EquirectangularProjection(AbstractProjection):
  def __init__(self):
    AbstractProjection.__init__(self)

  def pixel_value(self, theta, phi):
    # theta: -pi..pi -> u: 0..1
    u = 0.5+0.5*(theta/math.pi)
    # phi: -pi/2..pi/2 -> v: 0..1
    v = 0.5+(phi/math.pi)
    return self.get_pixel_from_uv(u,v)

  def angular_position(self, u, v):
    # theta: u: 0..1 -> -pi..pi
    theta = math.pi*2.0*(u-0.5)
    # phi: v: 0..1 - > -pi/2..pi/2
    phi = math.pi*(v-0.5)
    return (theta,phi)

class SideBySideFisheyeProjection(AbstractProjection):
  def __init__(self):
    AbstractProjection.__init__(self)

  def pixel_value(self, theta, phi):
    r = math.cos(phi)
    # z is elevation in this case
    sphere_pnt = (r*math.cos(theta), r*math.sin(theta), math.sin(phi))

    # sphere_pnt.x: [-1..1]
    u = 0.5+(sphere_pnt[0]*-0.5)
    if theta>=0:
      u = u*0.5 + 0.5
    else:
      u = (1.0-u)*0.5

    #sphere_pnt.z: -1..1 -> v: 0..1
    v = 0.5+(sphere_pnt[2]*0.5)

    return self.get_pixel_from_uv(u,v)

  def angular_position(self, up, v):
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

eq = EquirectangularProjection()
eq.loadImage("vrsi.jpg")

sbs = SideBySideFisheyeProjection()
sbs.initImage(2048, 1024)
sbs.reprojectToThis(eq)
sbs.saveImage("foo.png")

sbs2 = SideBySideFisheyeProjection()
sbs2.loadImage("foo.png")

eq2 = EquirectangularProjection()
eq2.initImage(2048,1024)
eq2.reprojectToThis(sbs2)
eq2.saveImage("foo2.png")
