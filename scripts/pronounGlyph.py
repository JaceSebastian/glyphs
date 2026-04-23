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

class PronounGlyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.num = 5
        self.attr_num = 2
        self.binary_array = np.zeros((self.attr_num,self.num),dtype = int)#recreate array
        self.text_file = self.text_file_base +"class5.csv"

        with open(self.text_file, newline="") as f:
            featurereader = csv.DictReader(f, skipinitialspace=True)
            for row in featurereader:
                if row["feature"] == "Glyphs":  # sentinel keyword
                    break
                word = row["feature"].strip()
                #call = row["call"].strip()   
                encoding = ast.literal_eval(row["encoding"].strip())
                self.attributes.append(word)
                self.encodings[word] = encoding
            glyphreader = csv.DictReader(f, skipinitialspace=True)
            for row in glyphreader:
                word = row['command'].strip()
                features = []
                for j in range(1, self.attr_num + 1):
                    feature = row[f'feature{j}'].strip()
                    rotation = int(row[f'rotation{j}'].strip())
                    features.append((feature, rotation))
                self.glyph_list[word] = features
            #print(self.glyph_list)


if __name__ == "__main__":
    test_obj = PronounGlyph(
                     bases.polygon,
                     base_kwargs=[],
                     line_fn=line_shapes.straight,
                     line_kwargs=[])

    commands = list(test_obj.glyph_list.keys())
    n = len(commands)
    cols = 5 #Hard coded number of cases + null, bad.
    rows = math.ceil(n / cols)

    cell_size = 1.5  # inches per cell, adjust to taste
    fig, axes = plt.subplots(rows, cols, figsize=(cols * cell_size, rows * cell_size))

    axes = axes.flatten()

    for i, word in enumerate(commands):
        test_obj.binary_array = test_obj._getBinaryArray(word)

        test_obj.draw(savename=None, show_all_paths=True, annotate=False,
                      show_name=False, axs=axes[i])
        axes[i].set_title(word.capitalize(), pad=-6, y=-0.1) 
        #reset binary array
        test_obj._clear_binary()

    # hide any unused subplots
    for j in range(n, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.show()
    #plt.savefig("pronounlist.png", transparent=True)




