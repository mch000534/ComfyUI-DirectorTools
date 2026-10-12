import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('asset_prompt_test', ROOT / '__init__.py', submodule_search_locations=[str(ROOT)])
package = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = package
spec.loader.exec_module(package)


class AssetPromptTests(unittest.TestCase):
    def node(self):
        self.assertIn('DirectorToolsAssetPrompt', package.NODE_CLASS_MAPPINGS)
        return package.NODE_CLASS_MAPPINGS['DirectorToolsAssetPrompt']()

    def test_default_is_english_three_views_and_preserves_description(self):
        node = self.node()
        result = node.build_prompt(custom_prompt='銀髮少女\nred coat')
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith('銀髮少女\nred coat\n\n'))
        self.assertIn('front, side and back', result[0])
        self.assertNotIn('equirectangular', result[0])
        self.assertEqual(node.RETURN_TYPES, ('STRING',))

    def test_panorama_wrap_projection_and_character_options_do_not_leak(self):
        prompt = self.node().build_prompt(asset_type='Panorama', background='White', expression='Happy', environment='Indoor', time_of_day='Night', lighting='Soft light')[0]
        for text in ['2:1', 'equirectangular', '360', '180', 'left and right', 'indoor', 'night', 'soft']:
            self.assertIn(text, prompt)
        for text in ['front, side and back', 'white background', 'happy expression']:
            self.assertNotIn(text, prompt)

    def test_character_layouts_and_no_panorama_option_leak(self):
        node = self.node()
        single = node.build_prompt(character_layout='Single full body', environment='Outdoor', time_of_day='Night')[0]
        self.assertIn('one full-body', single)
        self.assertNotIn('front, side and back', single)
        self.assertNotIn('night', single)
        closeup = node.build_prompt(character_layout='Three views + face close-up')[0]
        self.assertIn('front, side and back', closeup)
        self.assertIn('face close-up', closeup)

    def test_chinese_both_modes_options_and_original_text(self):
        node = self.node()
        character = node.build_prompt(custom_prompt='woman in blue', language='繁體中文', style='Photorealistic', background='White', expression='Neutral')[0]
        for text in ['woman in blue', '正面', '側面', '背面', '寫實', '白色背景', '中性表情']:
            self.assertIn(text, character)
        panorama = node.build_prompt(language='繁體中文', asset_type='Panorama', environment='Outdoor', time_of_day='Sunset', lighting='Natural light')[0]
        for text in ['等距柱狀', '2:1', '左右', '室外', '日落', '自然光']:
            self.assertIn(text, panorama)
        self.assertNotIn('正面', panorama)

    def test_empty_description_has_no_empty_sections_and_invalid_values_fail(self):
        node = self.node()
        self.assertFalse(node.build_prompt(custom_prompt='   ')[0].startswith('\n'))
        for kwargs in [{'asset_type': 'Unknown'}, {'language': 'French'}, {'style': 'Unknown'}, {'custom_prompt': None}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                node.build_prompt(**kwargs)

    def test_nine_grid_covers_each_asset_in_both_languages_without_panorama_rules(self):
        node = self.node()
        for language in ['English', '繁體中文']:
            for asset in ['Character', 'Scene', 'Prop']:
                with self.subTest(language=language, asset=asset):
                    prompt = node.build_prompt(custom_prompt='指定的資產\noriginal description', asset_type='Nine-grid asset · 九宮格資產', language=language, grid_asset_type=asset)[0]
                    self.assertTrue(prompt.startswith('指定的資產\noriginal description\n\n'))
                    self.assertIn('3', prompt)
                    self.assertNotIn('equirectangular', prompt)
                    self.assertNotIn('2:1', prompt)
                    if language == 'English':
                        self.assertIn('3x3', prompt)
                        self.assertIn('nine equal-sized', prompt)
                        self.assertIn('9.', prompt)
                        self.assertEqual(sum(line[:2] in [f'{i}.' for i in range(1, 10)] for line in prompt.splitlines()), 9)
                    else:
                        self.assertIn('九個等大', prompt)
                        self.assertIn('9.', prompt)

    def test_grid_asset_specific_options_and_consistency(self):
        node = self.node()
        mode = 'Nine-grid asset · 九宮格資產'
        character = node.build_prompt(asset_type=mode, grid_asset_type='Character', background='White', expression='Happy', environment='Indoor', time_of_day='Night')[0]
        self.assertIn('facial features', character)
        self.assertIn('white background', character)
        self.assertNotIn('indoor', character)
        scene = node.build_prompt(asset_type=mode, grid_asset_type='Scene', background='White', expression='Happy', environment='Indoor', time_of_day='Night')[0]
        self.assertIn('same location', scene)
        self.assertIn('indoor', scene)
        self.assertIn('night', scene)
        self.assertNotIn('white background', scene)
        prop = node.build_prompt(asset_type=mode, grid_asset_type='Prop', background='White', lighting='Soft light', time_of_day='Night')[0]
        self.assertIn('same prop', prop)
        self.assertIn('white background', prop)
        self.assertIn('soft light', prop)
        self.assertNotIn('night', prop)
        with self.assertRaises(ValueError):
            node.build_prompt(asset_type=mode, grid_asset_type='Unknown')

    def test_aspect_ratio_applies_to_character_and_whole_grid_with_matching_cells(self):
        node = self.node()
        for language in ['English', '繁體中文']:
            character = node.build_prompt(language=language, aspect_ratio='9:16')[0]
            self.assertIn('9:16', character)
            grid = node.build_prompt(asset_type='Nine-grid asset · 九宮格資產', language=language, aspect_ratio='16:9')[0]
            self.assertIn('16:9', grid)
            self.assertNotIn('square', grid)
            self.assertNotIn('正方形', grid)
            auto = node.build_prompt(asset_type='Nine-grid asset · 九宮格資產', language=language)[0]
            self.assertIn('1:1', auto)
        panorama = node.build_prompt(asset_type='Panorama', aspect_ratio='9:16')[0]
        self.assertIn('2:1', panorama)
        self.assertNotIn('9:16', panorama)
        with self.assertRaises(ValueError):
            node.build_prompt(aspect_ratio='Unknown')

    def test_scene_grid_fixed_positions_and_plan_projection(self):
        node = self.node()
        for language in ['English', '繁體中文']:
            prompt = node.build_prompt(asset_type='Nine-grid asset · 九宮格資產', grid_asset_type='Scene', language=language, aspect_ratio='16:9')[0]
            rows = [line for line in prompt.splitlines() if line[:2] in [f'{i}.' for i in range(1, 10)]]
            self.assertEqual(len(rows), 9)
            if language == 'English':
                for index, text in [(0, 'top-left'), (1, 'north'), (2, '45-degree'), (3, 'west'), (4, 'orthographic'), (5, 'east'), (6, 'main focal'), (7, 'south'), (8, 'detail')]:
                    self.assertIn(text, rows[index])
                self.assertIn('same camera anchor', prompt)
                self.assertIn('top=north, bottom=south, left=west', prompt)
                self.assertIn('right=east', prompt)
                self.assertNotIn('Use ordinary perspective views for the nine panels.', prompt)
            else:
                for index, text in [(0, '左上'), (1, '朝北'), (2, '45 度'), (3, '朝西'), (4, '頂視平面圖'), (5, '朝東'), (6, '主要焦點'), (7, '朝南'), (8, '細節')]:
                    self.assertIn(text, rows[index])
                self.assertIn('正投影', prompt)
                self.assertIn('上北、下南、左西、右東', prompt)
                self.assertNotIn('九格各使用普通透視視圖', prompt)
            self.assertIn('16:9', prompt)

    def test_every_declared_choice_is_executable(self):
        node = self.node()
        schema = node.INPUT_TYPES()
        inputs = {**schema['required'], **schema.get('optional', {})}
        self.assertEqual(inputs['language'][1]['default'], 'English')
        self.assertEqual(inputs['character_layout'][1]['default'], 'Three views')
        for mode in ['Character', 'Panorama']:
            for key, (kind, settings) in inputs.items():
                if isinstance(kind, list):
                    for choice in kind:
                        kwargs = {'asset_type': mode, key: choice}
                        with self.subTest(kwargs=kwargs):
                            self.assertTrue(node.build_prompt(**kwargs)[0].strip())


if __name__ == '__main__':
    unittest.main()
