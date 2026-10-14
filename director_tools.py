"""Super Director Tools: pixel-exact grid splitting for ComfyUI BHWC images."""

from numbers import Integral

import torch

MAX_GRID_AXIS = 64
MAX_SEPARATOR_PX = 4096


class DirectorToolsGridSplit:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'image': ('IMAGE',),
                'rows': ('INT', {'default': 3, 'min': 1, 'max': MAX_GRID_AXIS}),
                'cols': ('INT', {'default': 3, 'min': 1, 'max': MAX_GRID_AXIS}),
                'shot_number': ('INT', {
                    'default': 1, 'min': 1, 'max': MAX_GRID_AXIS ** 2,
                    'tooltip': '1-based shot: left to right, then top to bottom. Must be <= rows × cols.',
                }),
            },
            'optional': {
                'separator_px': ('INT', {
                    'default': 0, 'min': 0, 'max': MAX_SEPARATOR_PX,
                    'tooltip': 'Width of internal separator bands in pixels; excludes outer border. 0 for no separators.',
                }),
            },
        }

    RETURN_TYPES = ('IMAGE', 'IMAGE', 'INT')
    RETURN_NAMES = ('selected_image', 'all_cells', 'selected_index')
    FUNCTION = 'split_grid'
    CATEGORY = 'image/Super Director Tools'
    DESCRIPTION = (
        'Split a grid into row-major shots, starting at 1. Internal separator bands are excluded. '
        'selected_image is an exact crop. '
        'all_cells pads smaller cells on the right/bottom by repeating their edge pixels. '
        'For multiple source images, all shots from each source are grouped together. '
        'selected_index is the zero-based shot index within each source grid.'
    )

    def split_grid(self, image, rows, cols, shot_number, separator_px=0):
        for name, value, maximum in (
            ('rows', rows, MAX_GRID_AXIS),
            ('cols', cols, MAX_GRID_AXIS),
            ('shot_number', shot_number, MAX_GRID_AXIS ** 2),
        ):
            if isinstance(value, bool) or not isinstance(value, Integral) or not 1 <= value <= maximum:
                raise ValueError(f'{name} must be an integer between 1 and {maximum}.')
        if (isinstance(separator_px, bool) or not isinstance(separator_px, Integral)
                or not 0 <= separator_px <= MAX_SEPARATOR_PX):
            raise ValueError(f'separator_px must be an integer between 0 and {MAX_SEPARATOR_PX}.')
        separator_px = int(separator_px)
        rows, cols, shot_number = int(rows), int(cols), int(shot_number)
        if shot_number > rows * cols:
            raise ValueError(f'shot_number must be between 1 and {rows * cols} for this grid.')
        if not isinstance(image, torch.Tensor) or image.ndim != 4:
            raise ValueError('image must be a ComfyUI IMAGE tensor with shape [batch, height, width, channels].')
        batch, height, width, channels = image.shape
        if min(batch, height, width) < 1 or channels not in (1, 3, 4):
            raise ValueError('image must be nonempty with 1, 3 or 4 channels.')
        if not image.is_floating_point():
            raise ValueError('image must have a floating-point dtype, as required by ComfyUI IMAGE.')
        if rows > height or cols > width:
            raise ValueError('rows cannot exceed image height; cols cannot exceed image width (empty cells).')

        content_w = width - (cols - 1) * separator_px
        content_h = height - (rows - 1) * separator_px
        if content_w < cols or content_h < rows:
            raise ValueError('separator_px is too large: each cell must retain at least one pixel per axis.')

        # Partition content first, then add preceding gaps. Separate starts/ends
        # exclude exactly separator_px pixels between cells, without drift.
        x_starts = [i * content_w // cols + i * separator_px for i in range(cols)]
        x_ends = [(i + 1) * content_w // cols + i * separator_px for i in range(cols)]
        y_starts = [i * content_h // rows + i * separator_px for i in range(rows)]
        y_ends = [(i + 1) * content_h // rows + i * separator_px for i in range(rows)]
        index = shot_number - 1
        selected_row, selected_col = divmod(index, cols)
        selected = image[:, y_starts[selected_row]:y_ends[selected_row],
                         x_starts[selected_col]:x_ends[selected_col], :].contiguous()

        cell_h = (content_h + rows - 1) // rows
        cell_w = (content_w + cols - 1) // cols
        # Preallocate instead of keeping a second list of padded image copies.
        all_cells = image.new_empty((batch * rows * cols, cell_h, cell_w, channels))
        for source in range(batch):
            for row in range(rows):
                for col in range(cols):
                    crop = image[source, y_starts[row]:y_ends[row], x_starts[col]:x_ends[col], :]
                    h, w = crop.shape[:2]
                    target = all_cells[source * rows * cols + row * cols + col]
                    target[:h, :w] = crop
                    if w < cell_w:
                        target[:h, w:] = crop[:, -1:, :]
                    if h < cell_h:
                        target[h:] = target[h - 1:h]
        return selected, all_cells, index
