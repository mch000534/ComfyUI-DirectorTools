import math
import unittest

from geometry import camera_angles, spherical_uv, pan_sphere


class SphericalGeometryTests(unittest.TestCase):
    def test_cardinal_centers_and_horizontal_periodicity(self):
        for u in [0, .25, .5, .75, 1]:
            actual = spherical_uv(0, 0, 16 / 9, u, .5, 1)
            self.assertAlmostEqual(actual[0], u % 1, places=8)
            self.assertAlmostEqual(actual[1], .5, places=8)
        self.assertEqual(camera_angles(0, .5, 1), camera_angles(1, .5, 1))

    def test_vertical_fov_and_pitch_direction(self):
        self.assertAlmostEqual(spherical_uv(0, -1, 1, .5, .5, 1)[1], .5 - 37.5 / 180)
        self.assertAlmostEqual(spherical_uv(0, 1, 1, .5, .5, 1)[1], .5 + 37.5 / 180)
        self.assertAlmostEqual(spherical_uv(0, 0, 1, .5, .25, 1)[1], .25)
        self.assertAlmostEqual(spherical_uv(0, 0, 1, .5, .75, 1)[1], .75)

    def test_horizontal_fov_and_focal_zoom(self):
        expected = .5 + math.atan(math.tan(math.radians(37.5)) * 16 / 9) / math.tau
        self.assertAlmostEqual(spherical_uv(1, 0, 16 / 9, .5, .5, 1)[0], expected)
        self.assertLess(spherical_uv(1, 0, 16 / 9, .5, .5, 2)[0], expected)

    def test_height_translates_origin_in_world_up_direction(self):
        for h in [-.8, -.4, 0, .4, .8]:
            u, v = spherical_uv(0, 0, 1, .5, .5, 1, camera_height=h)
            self.assertAlmostEqual(u, .5)
            self.assertAlmostEqual(v, .5 - math.asin(h) / math.pi)
        # Looking straight upward/downward still reaches the poles.
        for cy in [0, 1]:
            u, v = spherical_uv(.6, -.4, 2.39, .01, cy, 1, camera_height=.8)
            self.assertTrue(0 <= u < 1 and 0 <= v <= 1)
        self.assertEqual(spherical_uv(.3, -.2, 1.7, .8, .4, 2),
                         spherical_uv(.3, -.2, 1.7, .8, .4, 2, camera_height=0))
        self.assertEqual(spherical_uv(.1, .2, 1, 0, .4, 1, camera_height=-.8),
                         spherical_uv(.1, .2, 1, 1, .4, 1, camera_height=-.8))

    def test_elevated_hit_projects_back_to_original_world_ray(self):
        for cx, cy, h in [(.2,.3,.8),(.95,.7,-.8),(.5,.1,.4)]:
            for sx, sy in [(.6,-.4),(-.8,.7),(0,0)]:
                u,v = spherical_uv(sx,sy,1.7,cx,cy,1.5,camera_height=h)
                lon,lat = (u-.5)*math.tau,(.5-v)*math.pi
                hit = [math.sin(lon)*math.cos(lat),math.sin(lat),math.cos(lon)*math.cos(lat)]
                self.assertAlmostEqual(sum(a*a for a in hit),1)
                ray = [hit[0],hit[1]-h,hit[2]]
                norm = math.sqrt(sum(a*a for a in ray))
                yaw,pitch,tan = camera_angles(cx,cy,1.5)
                x,y = sx*tan*1.7,-sy*tan
                z = -y*math.sin(pitch)+math.cos(pitch)
                expected = [x*math.cos(yaw)+z*math.sin(yaw),y*math.cos(pitch)+math.sin(pitch),-x*math.sin(yaw)+z*math.cos(yaw)]
                en = math.sqrt(sum(a*a for a in expected))
                for a,b in zip(ray,expected):
                    self.assertAlmostEqual(a/norm,b/en,places=8)

    def test_pan_wraps_repeatedly_and_clamps_pitch(self):
        cx, cy = pan_sphere(.01, .5, 1, 100, 0, 400, 400, 1)
        self.assertGreater(cx, .9)
        for _ in range(30):
            cx, cy = pan_sphere(cx, cy, 1, 500, 0, 400, 400, 1)
            self.assertTrue(0 <= cx < 1)
        self.assertGreater(pan_sphere(.5, .5, 1, 0, 10000, 400, 400, 1)[1], 0)
        self.assertLess(pan_sphere(.5, .5, 1, 0, -10000, 400, 400, 1)[1], 1)


if __name__ == '__main__':
    unittest.main()
