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
                if row['command'] == "BREAK":  # sentinel keyword
                    break
                word = row['command'].strip()
                features = []
                for j in range(1, self.attr_num ): #NOT +1 since only 1dimension used.
                    feature = row[f'feature{j}'].strip()
                    rotation = int(row[f'rotation{j}'].strip())
                    features.append((feature, rotation))
                self.glyph_list[word] = features
    
    def _getSampleCommands(self, group: str | None = None) -> list[str]:
        #TODO, see if need to modify to just have in glyph.py
        commands = []
        with open(self.text_file, newline="") as f:
            reader = csv.DictReader(
                (line for line in f if line.strip() and not line.lstrip().startswith("#")),
                skipinitialspace=True
            )
            for row in reader:
                feature = row["feature"].strip()
                if feature.lower() in ("glyphs"):
                    break
                if group is None or row["group"].strip() == group:
                    commands.append(feature)
        if group == "glyphs":
            for word in self.glyph_list:
                commands.append(word)
        return commands



if __name__ == "__main__":
    test_obj = adjGlyph(bases.polygon,base_kwargs=[],line_fn=line_shapes.straight,line_kwargs=[])
    #commands = list(test_obj.glyph_list.keys())[:45]
    commands = test_obj._getSampleCommands()
    commands.append("clear.adverb")
    test_obj.demoprint(commands, cell_size=1)


 



