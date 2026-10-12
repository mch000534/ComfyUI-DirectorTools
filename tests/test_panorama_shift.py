import importlib.util
from pathlib import Path
import sys
import unittest
import torch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('panorama_shift_test',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
package=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=package
spec.loader.exec_module(package)

class PanoramaShiftTests(unittest.TestCase):
    def node(self):
        self.assertIn('DirectorToolsPanoramaShift',package.NODE_CLASS_MAPPINGS)
        return package.NODE_CLASS_MAPPINGS['DirectorToolsPanoramaShift']()

    def test_half_shift_brings_original_join_to_center_without_mutating_pixels(self):
        node=self.node()
        image=torch.arange(8).reshape(1,1,8,1).float()
        original=image.clone()
        shifted,prompt=node.shift(image,.5)
        self.assertEqual(shifted.flatten().tolist(),[4,5,6,7,0,1,2,3])
        self.assertTrue(torch.equal(image,original))
        self.assertIn('x=4 pixels',prompt)
        self.assertIn('equirectangular',prompt)
        self.assertIn('narrow vertical neighborhood',prompt)
        self.assertIn('Do not convert',prompt)
        self.assertEqual(node.RETURN_TYPES,('IMAGE','STRING'))
        self.assertEqual(node.RETURN_NAMES,('image','prompt'))

    def test_inverse_and_wrapping_batch_channels_and_dtype(self):
        for channels in [1,3,4]:
            image=torch.arange(2*3*7*channels).reshape(2,3,7,channels).half()
            for shift in [-1,-.5,-.2,0,.2,.5,1]:
                moved,_=self.node().shift(image,shift)
                restored,_=self.node().shift(moved,-shift)
                self.assertTrue(torch.equal(restored,image))
                self.assertEqual(moved.dtype,image.dtype)
                self.assertEqual(moved.device,image.device)
                self.assertEqual(moved.shape,image.shape)

    def test_fractional_rounding_ties_away_from_zero_and_negative_seam_location(self):
        image=torch.arange(5).reshape(1,1,5,1).double()
        self.assertEqual(self.node().shift(image,.5)[0].flatten().tolist(),[2,3,4,0,1])
        moved,prompt=self.node().shift(image,-.5)
        self.assertEqual(moved.flatten().tolist(),[3,4,0,1,2])
        self.assertIn('x=2 pixels',prompt)
        self.assertIn('40.00%',prompt)

    def test_zero_full_turn_and_single_column_seam_stays_at_outer_edges(self):
        for width in [1,8]:
            image=torch.rand(1,4,width,3)
            for shift in [0,1,-1]:
                moved,prompt=self.node().shift(image,shift)
                self.assertTrue(torch.equal(moved,image))
                self.assertIn('outer left and right edges',prompt)

    def test_invalid_shift_and_image_inputs(self):
        node=self.node()
        image=torch.zeros(1,4,8,3)
        for shift in [True,None,'0.5',float('nan'),float('inf'),-1.01,1.01]:
            with self.subTest(shift=shift),self.assertRaises(ValueError):node.shift(image,shift)
        for bad in [None,torch.zeros(4,8,3),torch.zeros(0,4,8,3),torch.zeros(1,0,8,3),torch.zeros(1,4,0,3),torch.zeros(1,4,8,2),torch.zeros(1,4,8,3,dtype=torch.uint8)]:
            with self.subTest(shape=getattr(bad,'shape',None)),self.assertRaises(ValueError):node.shift(bad,.5)

if __name__=='__main__':unittest.main()
