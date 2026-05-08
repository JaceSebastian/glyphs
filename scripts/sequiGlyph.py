from glyph import glyph
import matplotlib.pyplot as plt #There's almost certainly a better way than matplotlib but oh well
import numpy as np
import matplotlib.patheffects as pe
from collections.abc import Callable
from necklaces import default_generation
import os
import bases
import line_shapes
import csv
import ast
import math

class sequiGlyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.num = 6
        self.attr_num = 3
        self.binary_array = np.zeros((self.attr_num,self.num),dtype = int)#recreate array
        self.text_file = self.text_file_base +"class6.csv"

        with open(self.text_file, newline="") as f:
            featurereader = csv.DictReader((line for line in f if line.strip() and not line.lstrip().startswith("#")), skipinitialspace=True)
            for row in featurereader:
                if row["feature"] == "Glyphs":  # sentinel keyword
                    break
                word = row["feature"].strip()
                #call = row["call"].strip()   
                encoding = ast.literal_eval(row["encoding"].strip())
                self.attributes.append(word)
                self.encodings[word] = encoding
            glyphreader = csv.DictReader((line for line in f if line.strip() and not line.lstrip().startswith("#")), skipinitialspace=True)
            for row in glyphreader:
                word = row['command'].strip()
                features = []
                for j in range(1, self.attr_num + 1):
                    feature = row[f'feature{j}'].strip()
                    rotation = int(row[f'rotation{j}'].strip())
                    features.append((feature, rotation))
                self.glyph_list[word] = features
            #print(self.glyph_list)

    def left_anchor(self, parity: int = 0) -> tuple[float, float]:
        x_vals, y_vals = self.base_fn(self.num, *self.base_kwargs)
        right_candidates = np.where(x_vals == min(x_vals))[0]
        if parity == 0:
            idx = right_candidates[np.argmin(y_vals[right_candidates])]  # lower-left
        else:
            idx = right_candidates[np.argmax(y_vals[right_candidates])]  # upper-left
        return (float(x_vals[idx]), float(y_vals[idx]+80))

    def right_anchor(self, parity: int = 0) -> tuple[float, float]:
        x_vals, y_vals = self.base_fn(self.num, *self.base_kwargs)
        right_candidates = np.where(x_vals == max(x_vals))[0]
        if parity == 0:
            idx = right_candidates[np.argmax(y_vals[right_candidates])]  # upper-right
        else:
            idx = right_candidates[np.argmin(y_vals[right_candidates])]  # lower-right
        return (float(x_vals[idx]), float(y_vals[idx]-30))
    


    def _getSampleCommands(self, group: str | None = None) -> list[str]:
        """
        Returns a list of all renderable specs.
        If group is specified, only features belonging to that group are included.
        - individual features (direct encoding keys, skipping null/sentinel)
        - combined glyphs from glyph_list
        """
        commands = []

        # individual features — filtered by group if specified
        with open(self.text_file, newline="") as f:
            reader = csv.DictReader(
                (line for line in f if line.strip() and not line.lstrip().startswith("#")),
                skipinitialspace=True
            )
            for row in reader:
                if row["feature"] == "Glyphs":  # sentinel keyword
                    break
                feature = row["feature"].strip()
                if group is None or row["group"].strip() == group:
                    commands.append(feature)

        # combined glyphs from glyph_list — no group concept, always included
        if group == "glyphs":
            for word in list(self.glyph_list)[:40]:
                commands.append(word)

        return commands


if __name__ == "__main__":
    test_obj = sequiGlyph(
                     bases.polygon,
                     base_kwargs=[],
                     line_fn=line_shapes.straight,
                     line_kwargs=[])

    #commands = list(test_obj.glyph_list.keys())
    commands = test_obj._getSampleCommands("glyphs")
    test_obj.demoprint(commands, cols=5, cell_size=1)




