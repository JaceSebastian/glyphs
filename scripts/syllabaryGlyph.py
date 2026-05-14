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

class syllableGlyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.num = 11
        self.attr_num = 5
        self.binary_array = np.zeros((self.attr_num,self.num),dtype = int)#recreate array
        self.text_file = self.text_file_base +"class11.csv"
        self.glossing = "NONE"

        with open(self.text_file, newline="", encoding="utf-8") as f:
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
                for j in range(1, self.attr_num + 1):
                    feature = row[f'feature{j}'].strip()
                    rotation = int(row[f'rotation{j}'].strip())
                    features.append((feature, rotation))
                self.glyph_list[word] = features
        
    def _getCompositeBinaryArray(self,word):
        # Parse dot-separated feature string: fone4.ftwo1.fthree
        features = []
        for part in word.split('.'):
            if(part in self.glyph_list):
               self._getBinaryArray(part)
            elif(part in self.encodings):
                rotation = 0 #temporary fix TODO
                fencoding = np.array(self.encodings[part.lower()]).reshape(self.attr_num, self.num)
                fencoding = self.rotateGlyph(fencoding, rotation) 
                self.binary_array = np.bitwise_or(self.binary_array, fencoding)
                
            else:
                print(part)
                raise KeyError(f"Invalid input {part} in Syllabary.")
            
        return features
    
    def _getBinaryArray(self, word):
        if(self.glossing == "NONE"):
            self.glossing = word
        else:
            self.glossing += word
        if(word not in self.glyph_list):
            self._getCompositeBinaryArray(word)
            return self.binary_array
        else:
            feats = self.glyph_list[word]
        for feature_name, rotation in feats:
            if(feature_name not in self.encodings):
                  print(f"Warning: '{feature_name}' not found encodings for class {self.num}, skipping.")
            fencoding = np.array(self.encodings[feature_name.lower()]).reshape(self.attr_num, self.num)
            fencoding = self.rotateGlyph(fencoding, rotation) 
            self.binary_array = np.bitwise_or(self.binary_array, fencoding)
        return self.binary_array


if __name__ == "__main__":
    test_obj = syllableGlyph(
                     bases.polygon,
                     base_kwargs=[],
                     line_fn=line_shapes.straight,
                     line_kwargs=[])

    commands = ["p.a", "unvoiced plosive.bilabial", "a.long vowel"]
    
    #list(test_obj.glyph_list.keys())
    test_obj.demoprint(commands, 8)




