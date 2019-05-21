from unittest import TestCase
import vrProjector
import os
import tempfile

class TestBase(TestCase):
  def test_test(self):
    self.assertTrue(True == True)

  def test_equi_to_cube(self):    
    with tempfile.TemporaryDirectory() as tmpdir:
      eq = vrProjector.EquirectangularProjection()
      eq.loadImage("images/equirectangular.png")
      # eq.set_use_bilinear(True)
      cb = vrProjector.CubemapProjection()
      cb.initImages(8,8)
      cb.reprojectToThis(eq)
      cb.saveImages(os.path.join(tmpdir,"front.png"), 
                    os.path.join(tmpdir,"right.png"), 
                    os.path.join(tmpdir,"back.png"), 
                    os.path.join(tmpdir,"left.png"), 
                    os.path.join(tmpdir,"top.png"), 
                    os.path.join(tmpdir,"bottom.png"))
      self.assertTrue(os.path.exists(os.path.join(tmpdir,"front.png")))
      self.assertTrue(os.path.exists(os.path.join(tmpdir,"right.png")))
      self.assertTrue(os.path.exists(os.path.join(tmpdir,"back.png")))
      self.assertTrue(os.path.exists(os.path.join(tmpdir,"left.png")))
      self.assertTrue(os.path.exists(os.path.join(tmpdir,"top.png")))
      self.assertTrue(os.path.exists(os.path.join(tmpdir,"bottom.png")))
      
  def test_ModernGLWrapper(self):
    mglWrapper = vrProjector.ModernGLWrapper()
    im = mglWrapper.render()
    #im.show()
    