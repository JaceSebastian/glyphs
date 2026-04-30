from glyph import glyph
import matplotlib.pyplot as plt #There's almost certainly a better way than matplotlib but oh well
import numpy as np
import matplotlib.patheffects as pe
from collections.abc import Callable
from necklaces import default_generation
#from svg2tikz import convert_svg
import os
import bases
import line_shapes
import csv
import math
import ast

class adjGlyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
  # subclass-specific initialization
        self.num = 9
        self.attr_num = 4   
        self.binary_array = np.zeros((self.attr_num,self.num),dtype = int)
        self.text_file = self.text_file_base +"class9.csv"

        with open(self.text_file, newline="") as f:
            featurereader = csv.DictReader(f, skipinitialspace=True)
            for row in featurereader:
                if row["feature"] == "Glyphs":  # sentinel keyword
                    break
                word = row["feature"].strip()
                  
                encoding = ast.literal_eval(row["encoding"].strip())
                self.attributes.append(word)
                self.encodings[word] = encoding
            glyphreader = csv.DictReader((line for line in f if line.strip() and not line.lstrip().startswith("#")), skipinitialspace=True)
            for row in glyphreader:
                word = row['command'].strip()
                features = []
                for j in range(1, self.attr_num ): #NOT +1 since only 1dimension used.
                    feature = row[f'feature{j}'].strip()
                    rotation = int(row[f'rotation{j}'].strip())
                    features.append((feature, rotation))
                self.glyph_list[word] = features



if __name__ == "__main__":
    test_obj = adjGlyph(bases.polygon,base_kwargs=[],line_fn=line_shapes.straight,line_kwargs=[])
    commands = list(test_obj.glyph_list.keys())
    test_obj.demoprint(commands)


 



