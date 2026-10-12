import importlib.util
from pathlib import Path
import unittest
import sys
import torch

ROOT = Path(__file__).resolve().parents[1]


class GridSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('director_tools', ROOT / 'director_tools.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.node = module.DirectorToolsGridSplit()

    def test_package_registration(self):
        spec = importlib.util.spec_from_file_location('director_package_test', ROOT / '__init__.py',
                                                      submodule_search_locations=[str(ROOT)])
        package = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = package
        spec.loader.exec_module(package)
        self.assertIn('DirectorToolsPanoramaViewer', package.NODE_CLASS_MAPPINGS)
        node_class = package.NODE_CLASS_MAPPINGS['DirectorToolsGridSplit']
        self.assertEqual(node_class.RETURN_TYPES, ('IMAGE', 'IMAGE', 'INT'))
        self.assertEqual(node_class.RETURN_NAMES, ('selected_image', 'all_cells', 'selected_index'))
        self.assertEqual(package.WEB_DIRECTORY, './web')
        image = torch.rand(1, 3, 3, 3)
        self.assertEqual(getattr(node_class(), node_class.FUNCTION)(image, 3, 3, 5)[2], 4)

    def test_nine_shots_row_major(self):
        image = torch.arange(36).reshape(1, 6, 6, 1).repeat(1, 1, 1, 3).float()
        for shot in range(1, 10):
            selected, cells, index = self.node.split_grid(image, 3, 3, shot)
            row, col = divmod(shot - 1, 3)
            expected = image[:, row*2:row*2+2, col*2:col*2+2, :]
            self.assertTrue(torch.equal(selected, expected))
            self.assertTrue(torch.equal(cells[index:index+1], expected))
            self.assertEqual(index, shot - 1)

    def test_nondivisible_covers_every_pixel_and_pads_edges(self):
        image = torch.arange(77).reshape(1, 7, 11, 1).double()
        restored = torch.empty_like(image)
        for shot, (y0, y1, x0, x1) in enumerate([
            (0, 2, 0, 3), (0, 2, 3, 7), (0, 2, 7, 11),
            (2, 4, 0, 3), (2, 4, 3, 7), (2, 4, 7, 11),
            (4, 7, 0, 3), (4, 7, 3, 7), (4, 7, 7, 11)], 1):
            selected, cells, _ = self.node.split_grid(image, 3, 3, shot)
            self.assertTrue(torch.equal(selected, image[:, y0:y1, x0:x1]))
            restored[:, y0:y1, x0:x1] = selected
            padded = cells[shot-1:shot]
            self.assertEqual(tuple(cells.shape), (9, 3, 4, 1))
            self.assertEqual(padded[0, -1, -1, 0], selected[0, -1, -1, 0])
            self.assertEqual(cells.dtype, image.dtype)
            self.assertEqual(cells.device, image.device)
        self.assertTrue(torch.equal(restored, image))

    def test_multiple_sources_source_major_batch(self):
        image = torch.arange(24).reshape(2, 3, 4, 1).float()
        selected, cells, index = self.node.split_grid(image, 1, 2, 2)
        self.assertEqual(index, 1)
        self.assertTrue(torch.equal(selected, image[:, :, 2:]))
        self.assertTrue(torch.equal(cells[0], image[0, :, :2]))
        self.assertTrue(torch.equal(cells[3], image[1, :, 2:]))

    def test_source_unchanged(self):
        image = torch.rand(1, 7, 11, 3)
        before = image.clone()
        self.node.split_grid(image, 3, 3, 5)
        self.assertTrue(torch.equal(image, before))

    def test_one_cell(self):
        image = torch.rand(2, 3, 7, 4)
        selected, cells, index = self.node.split_grid(image, 1, 1, 1)
        self.assertTrue(torch.equal(selected, image))
        self.assertTrue(torch.equal(cells, image))
        self.assertEqual(index, 0)

    def test_separator_excludes_only_internal_bands(self):
        image = torch.full((2, 8, 11, 3), -1.0)
        # Two rows of height 3, three columns of width 2/2/3, gaps of 2.
        bounds = [(0, 3, 0, 2), (0, 3, 4, 6), (0, 3, 8, 11),
                  (5, 8, 0, 2), (5, 8, 4, 6), (5, 8, 8, 11)]
        for shot, (y0, y1, x0, x1) in enumerate(bounds, 1):
            image[0, y0:y1, x0:x1] = shot
            image[1, y0:y1, x0:x1] = shot + 10
        before = image.clone()
        for shot, (y0, y1, x0, x1) in enumerate(bounds, 1):
            selected, cells, index = self.node.split_grid(image, 2, 3, shot, separator_px=2)
            self.assertTrue(torch.equal(selected, image[:, y0:y1, x0:x1]))
            self.assertEqual(index, shot - 1)
            self.assertEqual(tuple(cells.shape), (12, 3, 3, 3))
            self.assertFalse(bool((cells == -1).any()))
            for source in range(2):
                self.assertTrue(bool((cells[source * 6 + index] == shot + source * 10).all()))
        self.assertTrue(torch.equal(before, image))

    def test_separator_nondivisible_vertical_sizes(self):
        image = torch.arange(14 * 3).reshape(1, 14, 3, 1).double()
        for shot, (y0, y1) in enumerate([(0, 3), (5, 8), (10, 14)], 1):
            selected, cells, _ = self.node.split_grid(image, 3, 1, shot, separator_px=2)
            self.assertTrue(torch.equal(selected, image[:, y0:y1]))
            self.assertEqual(tuple(cells.shape), (3, 4, 3, 1))
            self.assertEqual(cells.dtype, image.dtype)

    def test_separator_zero_and_single_cell_compatibility(self):
        image = torch.rand(1, 7, 11, 4)
        original = self.node.split_grid(image, 3, 3, 5)
        zero = self.node.split_grid(image, 3, 3, 5, separator_px=0)
        for a, b in zip(original[:2], zero[:2]):
            self.assertTrue(torch.equal(a, b))
        selected, cells, index = self.node.split_grid(image, 1, 1, 1, separator_px=4096)
        self.assertTrue(torch.equal(selected, image))
        self.assertTrue(torch.equal(cells, image))
        self.assertEqual(index, 0)

    def test_separator_validation(self):
        image = torch.zeros(1, 5, 5, 3)
        for separator in [-1, 4097, True, 1.5, '2', None]:
            with self.subTest(separator=separator), self.assertRaises(ValueError):
                self.node.split_grid(image, 2, 2, 1, separator_px=separator)
        for rows, cols, separator in [(2, 2, 4), (3, 1, 2), (1, 3, 2)]:
            with self.subTest(grid=(rows, cols, separator)), self.assertRaises(ValueError):
                self.node.split_grid(image, rows, cols, 1, separator_px=separator)
        selected, cells, _ = self.node.split_grid(image, 2, 2, 4, separator_px=3)
        self.assertEqual(tuple(selected.shape), (1, 1, 1, 3))
        self.assertEqual(tuple(cells.shape), (4, 1, 1, 3))

    def test_invalid_inputs(self):
        image = torch.zeros(1, 3, 3, 3)
        for rows, cols, shot in [(0, 3, 1), (3, -1, 1), (65, 1, 1),
                                 (4, 1, 1), (1, 4, 1), (3, 3, 0),
                                 (3, 3, 10), (True, 1, 1), (1, 1, 1.5)]:
            with self.subTest(values=(rows, cols, shot)), self.assertRaises(ValueError):
                self.node.split_grid(image, rows, cols, shot)
        for bad in [None, torch.zeros(3, 3, 3), torch.zeros(0, 3, 3, 3),
                    torch.zeros(1, 0, 3, 3), torch.zeros(1, 3, 3, 2),
                    torch.zeros(1, 3, 3, 3, dtype=torch.int64)]:
            with self.subTest(shape=getattr(bad, 'shape', None)), self.assertRaises(ValueError):
                self.node.split_grid(bad, 1, 1, 1)


if __name__ == '__main__':
    unittest.main()
