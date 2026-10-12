import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import torch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('director_shots_test', ROOT/'__init__.py', submodule_search_locations=[str(ROOT)])
package = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = package
spec.loader.exec_module(package)

SHOT = dict(shot_id='SH010', name='Door', source_id='room_A', yaw=35, pitch=-4,
            vertical_fov=58, width=32, height=18, aspect_ratio='16:9', camera_height=0)
def document(shots):
    return json.dumps(dict(schema_version=1, shots=shots))

class ShotTests(unittest.TestCase):
    def test_conversion_and_validation(self):
        from director_shots_test.shots import parse_presets, degree_framing, framing_degrees
        for cx, cy, zoom in [(.5,.5,.5),(.5,.5,1),(.73,.4,2.7),(0,.1,32)]:
            angles = framing_degrees(cx,cy,zoom)
            actual = degree_framing(**angles)
            for a,b in zip(actual,(cx,cy,zoom)):
                self.assertAlmostEqual(a,b)
        self.assertEqual(parse_presets(document([SHOT]))['shots'],[SHOT])
        for shots in [[],[SHOT,SHOT],[SHOT,dict(SHOT,shot_id='sh010')],[dict(SHOT,vertical_fov=120)],[dict(SHOT,width=30)],[dict(SHOT,yaw=True)]]:
            with self.subTest(shots=shots), self.assertRaises(ValueError):
                parse_presets(document(shots))

    def test_manifest_named_shot_retains_its_sidecar(self):
        node = package.NODE_CLASS_MAPPINGS['DirectorToolsBatchPanorama']()
        with tempfile.TemporaryDirectory() as tmp, patch.dict(sys.modules, {'folder_paths':types.SimpleNamespace(get_output_directory=lambda:tmp)}):
            node.render(torch.ones(1,8,16,3),document([dict(SHOT,shot_id='camera_presets')]),2,64,True)
            png = next(Path(tmp).rglob('*.png'))
            self.assertEqual(json.loads(png.with_suffix('.json').read_text())['shot']['shot_id'],'camera_presets')

    def test_batch_tensor_pixels_order_and_sidecars(self):
        from director_shots_test.shots import degree_framing
        node = package.NODE_CLASS_MAPPINGS['DirectorToolsBatchPanorama']()
        source = torch.rand(1,16,32,3)
        second = dict(SHOT,shot_id='SH020',yaw=-120,camera_height=.3)
        with tempfile.TemporaryDirectory() as tmp, patch.dict(sys.modules, {'folder_paths':types.SimpleNamespace(get_output_directory=lambda:tmp)}):
            images,sheet,metadata = node.render(source,document([SHOT,second]),2,64,True)['result']
            self.assertIsInstance(images,torch.Tensor)
            self.assertEqual(tuple(images.shape),(2,18,32,3))
            self.assertEqual(images.dtype,source.dtype)
            self.assertEqual(images.device,source.device)
            for i,shot in enumerate([SHOT,second]):
                cx,cy,zoom = degree_framing(shot['yaw'],shot['pitch'],shot['vertical_fov'])
                expected = package.nodes.sample_panorama(source,shot['width'],shot['height'],cx,cy,zoom,shot['camera_height'])
                torch.testing.assert_close(images[i:i+1],expected)
            self.assertEqual(sheet.shape[0],1)
            self.assertEqual(json.loads(metadata)['shots'][1]['shot_id'],'SH020')
            files = list(Path(tmp).rglob('*.png'))
            self.assertEqual(len(files),2)
            for path in files:
                data = json.loads(path.with_suffix('.json').read_text())
                self.assertIn(data['shot']['shot_id'],['SH010','SH020'])
                self.assertEqual(data['source_size'],[32,16])
            self.assertEqual(node.OUTPUT_IS_LIST,(False,False,False))
            assembled=package.NODE_CLASS_MAPPINGS['DirectorToolsContactSheet']().assemble(images,2,64,'SH',10)[0]
            torch.testing.assert_close(assembled[:,:36],sheet[:,:36])

    def test_mixed_sizes_fail_before_sampling_or_saving(self):
        node=package.NODE_CLASS_MAPPINGS['DirectorToolsBatchPanorama']()
        for second in [dict(SHOT,shot_id='SH020',width=11,height=11,aspect_ratio='1:1'),dict(SHOT,shot_id='SH020',width=64,height=36)]:
            with tempfile.TemporaryDirectory() as tmp, patch.dict(sys.modules, {'folder_paths':types.SimpleNamespace(get_output_directory=lambda:tmp)}), patch('director_shots_test.shot_nodes.sample_panorama') as sampler:
                with self.assertRaisesRegex(ValueError,'same width and height'):
                    node.render(torch.ones(1,8,16,3),document([SHOT,second]),2,64,True)
                sampler.assert_not_called()
                self.assertEqual(list(Path(tmp).iterdir()),[])

    def test_contact_sheet_does_not_mutate_input_and_labels_have_own_band(self):
        node = package.NODE_CLASS_MAPPINGS['DirectorToolsContactSheet']()
        source = torch.ones(2,8,16,3)
        before = source.clone()
        sheet = node.assemble(source,2,64,'SH',10)[0]
        torch.testing.assert_close(source,before)
        self.assertEqual(tuple(sheet.shape),(1,56,128,3))
        self.assertLess(sheet[0,37].mean().item(),.5)

    def test_contact_sheet_cells_follow_landscape_portrait_and_square_ratios(self):
        node=package.NODE_CLASS_MAPPINGS['DirectorToolsContactSheet']()
        for h,w,tw,th in [(9,16,187,105),(16,9,105,187),(8,8,187,187)]:
            with self.subTest(size=(w,h)):
                images=torch.ones(3,h,w,3)
                sheet=node.assemble(images,2,187,'SH',1)[0]
                self.assertEqual(tuple(sheet.shape),(1,2*(th+24),2*tw,3))
                # No dark letterboxing above or below either populated row.
                for y in [0,th+24]:
                    torch.testing.assert_close(sheet[0,y:y+th,:tw],torch.ones(th,tw,3))

    def test_batch_rejects_multiple_sources_and_over_budget_before_sampling(self):
        node = package.NODE_CLASS_MAPPINGS['DirectorToolsBatchPanorama']()
        oversized=dict(SHOT,width=8192,height=8192,aspect_ratio='1:1')
        for source,shots in [(torch.zeros(2,8,16,3),[SHOT]),(torch.zeros(1,8,16,3),[oversized])]:
            with patch('director_shots_test.shot_nodes.sample_panorama') as sampler:
                with self.assertRaises(ValueError):
                    node.render(source,document(shots),2,64,False)
                sampler.assert_not_called()

    def test_malformed_contract_and_sheet_labels(self):
        from director_shots_test.shots import parse_presets
        for change in [dict(aspect_ratio=['16:9']),dict(source_id=''),dict(shot_id='../bad'),dict(width=True),dict(camera_height=float('nan')),dict(vertical_fov=1)]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                parse_presets(document([dict(SHOT,**change)]))
        with self.assertRaises(ValueError):
            parse_presets(document([SHOT,dict(SHOT,shot_id='SH020',source_id='different_source')]))
        with self.assertRaises(ValueError):
            package.NODE_CLASS_MAPPINGS['DirectorToolsContactSheet']().assemble(torch.ones(2,8,16,3),2,64,'SH\nInvalid',1)

    def test_numbered_labels_prefix_start_and_minimum_three_digits(self):
        from director_shots_test.shot_nodes import numbered_labels
        inputs=package.NODE_CLASS_MAPPINGS['DirectorToolsContactSheet'].INPUT_TYPES()['required']
        self.assertNotIn('labels',inputs)
        self.assertEqual(inputs['prefix'][1]['default'],'SH')
        self.assertEqual(inputs['start_number'][1]['default'],1)
        self.assertEqual(numbered_labels('SH',10,3),['SH010','SH011','SH012'])
        self.assertEqual(numbered_labels('Shot_',998,3),['Shot_998','Shot_999','Shot_1000'])
        self.assertEqual(numbered_labels('',0,2),['000','001'])
        for prefix,start in [('SH',-1),('SH',True),('SH',1.5),('SH','10'),('SH',1000000000),('a'*81,1),('bad\nlabel',1)]:
            with self.subTest(prefix=prefix,start=start),self.assertRaises(ValueError):
                numbered_labels(prefix,start,2)

if __name__ == '__main__': unittest.main()
