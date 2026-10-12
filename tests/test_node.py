import importlib.util
import math
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

import torch
# Load lazy comparison dependencies before patch.dict restores sys.modules.
# This prevents re-registering PyTorch distributed operators across tests.
import torch.distributed.tensor
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('director_tools_panorama_test', ROOT / '__init__.py',
                                            submodule_search_locations=[str(ROOT)])
package = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = package
spec.loader.exec_module(package)
DirectorToolsPanoramaViewer = package.NODE_CLASS_MAPPINGS['DirectorToolsPanoramaViewer']


class CameraTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        folder_paths = types.SimpleNamespace(get_temp_directory=lambda: self.tmp.name)
        self.folder_patch = patch.dict(sys.modules, {'folder_paths': folder_paths})
        self.folder_patch.start()
        self.camera = DirectorToolsPanoramaViewer()

    def tearDown(self):
        self.folder_patch.stop()
        self.tmp.cleanup()

    def run_camera(self, image, width, height, cx=.5, cy=.5, zoom=1, ratio='Free'):
        return self.camera.frame(image, ratio, width, height, cx, cy, zoom)

    def test_identity_and_source_unchanged(self):
        source = torch.rand(1, 17, 34, 3)
        original = source.clone()
        result = self.run_camera(source, 34, 17)['result'][0]
        torch.testing.assert_close(result, source, atol=3e-6, rtol=1e-5)
        torch.testing.assert_close(source, original)

    def test_coordinate_ramp_has_correct_pixels_and_zoom(self):
        source = torch.zeros(1, 100, 200, 3)
        source[0, :, :, 0] = (torch.arange(200) + .5)[None, :] / 200
        source[0, :, :, 1] = (torch.arange(100) + .5)[:, None] / 100
        result = self.run_camera(source, 10, 10, .5, .5, 2)['result'][0]
        self.assertEqual(tuple(result.shape), (1, 10, 10, 3))
        self.assertAlmostEqual(result[0, 0, 0, 0].item(), 77.5 / 200, places=6)
        self.assertAlmostEqual(result[0, 0, 0, 1].item(), 27.5 / 100, places=6)
        self.assertAlmostEqual(result[0, -1, -1, 0].item(), 122.5 / 200, places=6)

    def test_edges_no_black_border_and_chunk_boundary(self):
        source = torch.ones(1, 100, 200, 3)
        for cx, cy in [(0, 0), (1, 1)]:
            output = self.run_camera(source, 57, 301, cx, cy, 32)['result'][0]
            self.assertEqual(tuple(output.shape), (1, 301, 57, 3))
            torch.testing.assert_close(output, torch.ones_like(output))

    def test_preview_is_bounded_source_not_cropped_output(self):
        source = torch.zeros(1, 1000, 2000, 3)
        source[..., 0] = 1
        data = self.run_camera(source, 320, 180, ratio='16:9')
        preview = data['ui']['director_tools_panorama'][0]
        self.assertEqual((preview['source_width'], preview['source_height']), (2000, 1000))
        self.assertEqual(preview['type'], 'temp')
        self.assertEqual(preview['subfolder'], '')
        with Image.open(Path(self.tmp.name) / preview['filename']) as img:
            self.assertEqual(img.size, (1536, 768))
            self.assertEqual(img.getpixel((0, 0)), (255, 0, 0))
        self.assertNotIn('images', data['ui'])

    def test_invalid_images_and_settings(self):
        for image in [torch.zeros(2, 10, 10, 3), torch.zeros(1, 0, 10, 3),
                      torch.zeros(10, 10, 3), torch.zeros(1, 10, 10, 4),
                      torch.zeros(1, 10, 10, 3, dtype=torch.uint8)]:
            with self.subTest(shape=image.shape), self.assertRaises(ValueError):
                self.run_camera(image, 10, 10)
        with self.assertRaises(ValueError):
            self.run_camera(torch.zeros(1, 10, 10, 3), 100, 100, ratio='16:9')

    def test_output_dtype_is_preserved(self):
        source = torch.rand(1, 10, 20, 3).half()
        output = self.run_camera(source, 9, 9)['result'][0]
        self.assertEqual(output.dtype, source.dtype)
        self.assertEqual(output.device, source.device)

    def test_registration_and_serializable_input_contract(self):
        self.assertEqual(package.WEB_DIRECTORY, './web')
        self.assertEqual(DirectorToolsPanoramaViewer.RETURN_TYPES, ('IMAGE','STRING','STRING'))
        self.assertEqual(DirectorToolsPanoramaViewer.RETURN_NAMES, ('image','prompt','presets_json'))
        self.assertTrue(DirectorToolsPanoramaViewer.OUTPUT_NODE)
        self.assertEqual(list(DirectorToolsPanoramaViewer.INPUT_TYPES()['required']),
                         ['image', 'aspect_ratio', 'width', 'height', 'center_x', 'center_y', 'zoom'])

    def test_expired_temporary_preview_can_be_regenerated_on_run(self):
        # A constant cache key cannot recover a deleted temp file in a live server.
        self.assertTrue(math.isnan(DirectorToolsPanoramaViewer.IS_CHANGED()))

    def test_refinement_prompt_uses_render_mode_and_preserves_original_image_slot(self):
        source=torch.rand(1,8,16,3)
        for mode in ['Flat','360 Panorama']:
            result=self.camera.frame(source,'Free',11,7,.5,.5,1,projection=mode)['result']
            self.assertEqual(len(result),3)
            self.assertEqual(tuple(result[0].shape),(1,7,11,3))
            self.assertIsInstance(result[1],str)
            self.assertIn('Preserve',result[1])
            self.assertIn('wide-angle',result[1])
            self.assertIn('perspective convergence',result[1])
            self.assertIn('detail',result[1])
            if mode=='360 Panorama':self.assertIn('spherical',result[1])
            else:self.assertNotIn('spherical',result[1])

    def test_refinement_prompt_accounts_for_simulated_height_only_in_panorama_mode(self):
        source=torch.rand(1,8,16,3)
        elevated=self.camera.frame(source,'Free',11,7,.5,.5,1,projection='360 Panorama',camera_height=.4)['result'][1]
        self.assertIn('off-center',elevated)
        flat=self.camera.frame(source,'Free',11,7,.5,.5,1,projection='Flat',camera_height=.4)['result'][1]
        self.assertNotIn('off-center',flat)

    def test_saved_presets_output_selects_current_node_and_round_trips_batch(self):
        import json
        shot=dict(shot_id='SH010',name='Door',source_id='room_A',yaw=35,pitch=-4,vertical_fov=58,width=32,height=18,aspect_ratio='16:9',camera_height=0)
        presets=dict(schema_version=1,shots=[shot])
        extra={'workflow':{'nodes':[{'id':99,'properties':{'director_tools_shots':{'invalid':True}}},{'id':2,'properties':{'director_tools_shots':presets}}]}}
        source=torch.rand(1,8,16,3)
        result=self.camera.frame(source,'Free',11,7,.5,.5,1,projection='360 Panorama',extra_pnginfo=extra,unique_id='2')['result']
        self.assertEqual(json.loads(result[2]),presets)
        images,_,_=package.NODE_CLASS_MAPPINGS['DirectorToolsBatchPanorama']().render(source,result[2],1,64,False)['result']
        self.assertIsInstance(images,torch.Tensor)
        self.assertEqual(tuple(images.shape),(1,18,32,3))

    def test_no_saved_presets_returns_empty_document_and_malformed_presets_fail(self):
        import json
        source=torch.rand(1,8,16,3)
        empty=self.camera.frame(source,'Free',11,7,.5,.5,1)['result'][2]
        self.assertEqual(json.loads(empty),dict(schema_version=1,shots=[]))
        extra={'workflow':{'nodes':[{'id':2,'properties':{'director_tools_shots':{'schema_version':1,'shots':[]}}}]}}
        self.assertEqual(json.loads(self.camera.frame(source,'Free',11,7,.5,.5,1,extra_pnginfo=extra,unique_id=2)['result'][2]),dict(schema_version=1,shots=[]))
        extra['workflow']['nodes'][0]['properties']['director_tools_shots']={'schema_version':2,'shots':[]}
        with self.assertRaises(ValueError):
            self.camera.frame(source,'Free',11,7,.5,.5,1,extra_pnginfo=extra,unique_id='2')
        extra['workflow']['nodes'][0]['properties']['director_tools_shots']={'schema_version':True,'shots':[]}
        with self.assertRaises(ValueError):
            self.camera.frame(source,'Free',11,7,.5,.5,1,extra_pnginfo=extra,unique_id='2')

    def test_spherical_projection_center_samples_and_wrap(self):
        source = torch.zeros(1, 8, 16, 3)
        source[0, :, :, 0] = (torch.arange(16) + .5)[None, :] / 16
        source[0, :, :, 1] = (torch.arange(8) + .5)[:, None] / 8
        for cx, cy in [(.5,.5),(.25,.25),(.75,.75)]:
            output = self.camera.frame(source,'Free',1,1,cx,cy,1,projection='360 Panorama')['result'][0]
            self.assertAlmostEqual(output[0,0,0,0].item(),cx,places=6)
            self.assertAlmostEqual(output[0,0,0,1].item(),cy,places=6)
        a = self.camera.frame(source,'Free',11,7,0,.5,1,projection='360 Panorama')['result'][0]
        b = self.camera.frame(source,'Free',11,7,1,.5,1,projection='360 Panorama')['result'][0]
        torch.testing.assert_close(a,b)
        self.assertAlmostEqual(a[0,3,5,0].item(),.5,places=6)

    def test_spherical_seam_bilinear_and_no_black_border(self):
        source = torch.zeros(1, 8, 16, 3)
        source[...,0,0] = 1
        source[...,-1,2] = 1
        output = self.camera.frame(source,'Free',1,1,0,.5,1,projection='360 Panorama')['result'][0]
        torch.testing.assert_close(output[0,0,0],torch.tensor([.5,0,.5]),atol=2e-6,rtol=1e-5)
        for cx, cy in [(0,0),(1,1),(.75,.02)]:
            output = self.camera.frame(torch.ones(1,8,16,3),'Free',57,301,cx,cy,2,projection='360 Panorama')['result'][0]
            torch.testing.assert_close(output,torch.ones_like(output))

    def test_height_validation_and_flat_compatibility(self):
        source = torch.rand(1, 8, 16, 3)
        for h in [float('nan'), float('inf'), -.81, .81, True, '0']:
            with self.subTest(height=h), self.assertRaises(ValueError):
                self.camera.frame(source,'Free',7,7,.5,.5,1,camera_height=h)
        a = self.run_camera(source,7,7)['result'][0]
        b = self.camera.frame(source,'Free',7,7,.5,.5,1,camera_height=.8)['result'][0]
        torch.testing.assert_close(a,b)
        self.assertEqual(list(DirectorToolsPanoramaViewer.INPUT_TYPES()['optional']),['projection','camera_height'])

    def test_projection_option_and_invalid_projection(self):
        self.assertEqual(DirectorToolsPanoramaViewer.INPUT_TYPES()['optional']['projection'][1]['default'],'360 Panorama')
        with self.assertRaises(ValueError):
            self.camera.frame(torch.ones(1,8,16,3),'Free',1,1,.5,.5,1,projection='Unknown')

    def test_spherical_tensor_matches_reference_rays(self):
        from geometry import spherical_uv
        source = torch.rand(1,15,30,3,generator=torch.Generator().manual_seed(42))
        for cx,cy,zoom,h in [(.5,.5,1,0),(0,.5,1,.8),(1,.5,1,-.8),(.93,.24,2,.4),(.1,.97,1,-.4)]:
            output = self.camera.frame(source,'Free',41,27,cx,cy,zoom,projection='360 Panorama',camera_height=h)['result'][0]
            for px,py in [(0,0),(20,13),(40,26),(11,7),(25,23)]:
                u,v = spherical_uv(2*(px+.5)/41-1,2*(py+.5)/27-1,41/27,cx,cy,zoom,camera_height=h)
                x,y = u*30-.5,v*15-.5
                ix,iy = math.floor(x),math.floor(y)
                fx,fy = x-ix,y-iy
                expected = torch.zeros(3)
                for dy in range(2):
                    for dx in range(2):
                        weight = (fx if dx else 1-fx)*(fy if dy else 1-fy)
                        expected += source[0,min(14,max(0,iy+dy)),(ix+dx)%30,:]*weight
                torch.testing.assert_close(output[0,py,px,:],expected,atol=1e-5,rtol=1e-4)


if __name__ == '__main__':
    unittest.main()
