import numpy as np
class ligatureGlyph:
    """This handles compound words and derivations."""

    def __init__(self, specs: list[tuple], class_map: dict, cell_size: int = 1):
        self.specs = specs
        self.class_map = class_map
        self.components = []
        self.glossing = ""

    def build(self):
        self.components = []
        for lookup, class_index in self.specs:
            obj = self.class_map[class_index]()
            obj._getBinaryArray(lookup)
            self.components.append(obj)
        self.glossing = " ".join(obj.glossing for obj in self.components)


    def left_anchor(self) -> tuple[float, float]:
        all_x = []
        for obj in self.components:
            x_vals, y_vals = obj.base_fn(obj.num, *obj.base_kwargs)
            all_x.append((float(np.min(x_vals)), float(y_vals[np.argmin(x_vals)])))
        return min(all_x, key=lambda p: p[0])

    def right_anchor(self) -> tuple[float, float]:
        all_x = []
        for obj in self.components:
            x_vals, y_vals = obj.base_fn(obj.num, *obj.base_kwargs)
            all_x.append((float(np.max(x_vals)), float(y_vals[np.argmax(x_vals)])))
        return max(all_x, key=lambda p: p[0])

    def draw(self, axs, **draw_kwargs):
        x_cursor = 0.0
        for obj in self.components:
            x_vals, _ = obj.base_fn(obj.num, *obj.base_kwargs)
            x_min = float(np.min(x_vals))
            x_max = float(np.max(x_vals))

            x_offset = x_cursor - x_min
            obj.draw_offset(axs=axs, x_offset=x_offset, **draw_kwargs)
            x_cursor = x_max + x_offset

    def draw_offset(self, axs, x_offset=0.0, y_offset=0.0, rotation=0, **draw_kwargs):
        x_cursor = 0
        y_cursor = 0
        for obj in self.components:
            obj.draw_offset(axs=axs, x_offset=x_offset + x_cursor, y_offset = y_offset+y_cursor, **draw_kwargs)
            incrementx, incrementy = obj.right_anchor()
            x_cursor += incrementx
            y_cursor += incrementy





    def _clear_binary(self):
        for obj in self.components:
            obj._clear_binary()
        self.glossing = ""

    def _makeGlossing(self):
        return self.glossing
        # raise NotImplementedError(f"Ligature glossing not implemented in glyph.py.")