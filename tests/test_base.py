from unittest import TestCase
import vrProjector

class TestBase(TestCase):
  def test_root(self):
    self.assertTrue(True == True)
    
    
# import vrProjector
#
# eq = vrProjector.EquirectangularProjection()
# eq.loadImage("images/equirectangular.png")
# # eq.set_use_bilinear(True)
# cb = vrProjector.CubemapProjection()
# cb.initImages(256,256)
# cb.reprojectToThis(eq)
# cb.saveImages("front.png", "right.png", "back.png", "left.png", "top.png", "bottom.png")
#
#
