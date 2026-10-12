import json
import math
from pathlib import Path
import unittest

from geometry import crop_rect, validate_settings, RATIOS


class GeometryTests(unittest.TestCase):
    def test_panorama_center_and_zoom(self):
        self.assertEqual(crop_rect(2000, 1000, 1, .5, .5, 1), (500, 0, 1000, 1000))
        self.assertEqual(crop_rect(2000, 1000, 1, .5, .5, 2), (750, 250, 500, 500))

    def test_bounds_for_every_ratio(self):
        for aspect in [*RATIOS.values(), .1, 10]:
            for zoom in [1, 1.2, 32]:
                for cx, cy in [(0, 0), (1, 1), (.37, .62)]:
                    x, y, w, h = crop_rect(2011, 997, aspect, cx, cy, zoom)
                    self.assertGreaterEqual(x, 0)
                    self.assertGreaterEqual(y, 0)
                    self.assertLessEqual(x + w, 2011 + 1e-8)
                    self.assertLessEqual(y + h, 997 + 1e-8)
                    self.assertAlmostEqual(w / h, aspect)

    def test_rounding_and_free_dimensions(self):
        self.assertEqual(validate_settings('16:9', 1920, 1080, .5, .5, 1), 1920 / 1080)
        validate_settings('2.39:1', 1920, 803, .5, .5, 1)
        validate_settings('9:16', 608, 1080, .5, .5, 1)
        self.assertEqual(validate_settings('Free', 777, 301, .5, .5, 1), 777 / 301)

    def test_minimum_zoom(self):
        self.assertEqual(validate_settings('Free', 100, 100, .5, .5, .5), 1)

    def test_reject_invalid_settings(self):
        for args in [('bad', 100, 100, .5, .5, 1), ('16:9', 100, 100, .5, .5, 1),
                     ('Free', 0, 100, .5, .5, 1), ('Free', 100, 100, math.nan, .5, 1),
                     ('Free', 100, 100, .5, .5, math.inf), ('Free', 100, 100, .5, .5, .49),
                     ('Free', 100.5, 100, .5, .5, 1), ('Free', 100, 100, -.1, .5, 1)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                validate_settings(*args)

    def test_shared_fixture(self):
        cases = json.loads((Path(__file__).parent / 'geometry_cases.json').read_text())
        for case in cases:
            actual = crop_rect(*case['input'])
            for a, b in zip(actual, case['expected']):
                self.assertAlmostEqual(a, b, places=8)


if __name__ == '__main__':
    unittest.main()
