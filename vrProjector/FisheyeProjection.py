# Copyright 2020 Bhautik J Joshi
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from .AbstractProjection import AbstractProjection
import math

class FisheyeProjection(AbstractProjection):
  def __init__(self):
    AbstractProjection.__init__(self)

  def set_angular_resolution(self):
    self.angular_resolution = math.pi/self.imsize[1]

  def _pixel_value(self, angle):
    FOV = math.pi
    
    theta = angle[0] * 0.5
    phi = angle[1]
    if theta is None or phi is None:
      return (0,0,0)

    
    # phi: -pi/2..pi/2 
    # theta: -pi..pi

    # using convention from http://paulbourke.net/dome/fish2/
    pt = self.point_on_sphere(theta, phi)
    p_y = pt[0]
    p_x = pt[1]
    p_z = pt[2]

    theta_l = math.atan2(p_z,p_x);
    phi_l = math.atan2(math.sqrt(p_x*p_x+p_z*p_z),p_y);
    r = phi_l / FOV;

    u = 0.5 + r * math.cos(theta_l);
    v = 0.5 + r * math.sin(theta_l);    
    
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
