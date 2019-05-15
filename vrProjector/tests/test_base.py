from unittest import TestCase
import vrProjector

class TestBase(TestCase):
  def test_root(self):
    s = vrProjector.DummySpit()
    self.assertTrue(s == "BLARGH")

  def test_base(self):
    s = vrProjector.DummySpitBase()
    self.assertTrue(s == "BLARGH_BASE")
