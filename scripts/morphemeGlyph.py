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

class morphemeGlyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.num = 7
        self.attr_num = 3
        self.binary_array = np.zeros((self.attr_num,self.num),dtype = int)#recreate array
        self.text_file = self.text_file_base +"class7.csv"

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
 
#override
    def _getBinaryArray(self, word):
        '''Needs to be able to handle case/conjugation and root
        '''
        self.glossing = "Glossing not showing up."
        if word in self.glyph_list:
            for feature_name, rotation in self.glyph_list[word]:
                fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
                fencoding = self.rotateGlyph(fencoding, rotation) 
                self.binary_array = np.bitwise_or(self.binary_array, fencoding)
                self.glossing = word
            return self.binary_array
        
         # direct encoding hit — bare feature name, no parsing needed
        if word in self.encodings:
            fencoding = np.array(self.encodings[word]).reshape(self.attr_num, self.num)
            self.binary_array = np.bitwise_or(self.binary_array, fencoding)
            self.glossing = word
            return self.binary_array
        features = []
        if '.' in word:
            word, case = word.split('.', 1)
            features.append((case.strip().lower(), 0))

        root = word.strip()
        if not root:
            raise ValueError(f"No root morpheme found in '{word}'")
        if root not in self.glyph_list:
            raise KeyError(f"'{root}' not found in C9 glyph_list")
        # get root and field features from glyph_list, ignore determinant slot
        for feat, rotation in self.glyph_list[root]:
            features.append((feat, rotation))

        self._makeGlossing(root, case)
        #print(features)
        for feature_name, rotation in features:
            if feature_name not in self.encodings:
                print(f"Warning: '{feature_name}' not found in encodings, skipping.")
                continue
            fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
            fencoding = self.rotateGlyph(fencoding, rotation)  # default rotation
            self.binary_array = np.bitwise_or(self.binary_array, fencoding)
        
        return self.binary_array


    def _makeGlossing(self, root, case):
        '''Note that thisis copied from noun, and not adapted.'''
        return_value = self.getDeclension(case, "")
        return_value += root.title()
        self.glossing = return_value
        return return_value

if __name__ == "__main__":
    test_obj = morphemeGlyph(
                     bases.polygon,
                     base_kwargs=[],
                     line_fn=line_shapes.straight,
                     line_kwargs=[])

    commands = test_obj._getSampleCommands()
    test_obj.demoprint(commands)




