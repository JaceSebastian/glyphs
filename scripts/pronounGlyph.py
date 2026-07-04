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
            glyphreader = csv.DictReader((line for line in f if line.strip() and not line.lstrip().startswith("#")), skipinitialspace=True)
            for row in glyphreader:
                word = row['command'].strip()
                features = []
                for j in range(1, self.attr_num + 1):
                    feature = row[f'feature{j}'].strip()
                    rotation = int(row[f'rotation{j}'].strip())
                    features.append((feature, rotation))
                self.glyph_list[word] = features

    
    def _getBinaryArray(self, word):
        self.glossing = word
        self.features = []
        #Set Phrase ie Bindings, no declensions.
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
        else:
            self.features = []
            if ':' in word:
                det, word = word.split(':', 1)
                self.features.append((det.strip() if det.strip() else "",0))
            else:
                det = "The "
            if '.' in word:
                word, case = word.split('.', 1)
                case_feature = case.strip().lower() if case.strip() else "nom"
            else:
                case = "nom"
                case_feature = "nom"
            root = word.strip()
            if not root:
                raise ValueError(f"No root pronoun found in '{word}'")
            if root not in self.glyph_list:
                raise KeyError(f"'{root}' not found in C5 glyph_list")
            # get root and field features from glyph_list, ignore determinant slot
            for feat, rotation in self.glyph_list[root]:
                self.features.append((feat, rotation))
            self.features.append((case_feature, 0))
            self._makeGlossing(root=word, case=case_feature)
        for feature_name, rotation in self.features:
            fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
            fencoding = self.rotateGlyph(fencoding, rotation) 
            self.binary_array = np.bitwise_or(self.binary_array, fencoding)
        return self.binary_array



    def _makeGlossing(self,det="The ", root="_", case="Nom"):
        return_value = self.getDeclension(case, "")
        return_value += det
        return_value += root.title()
        self.glossing = return_value
        return self.glossing


if __name__ == "__main__":
    test_obj = PronounGlyph(bases.polygon,base_kwargs=[],line_fn=line_shapes.straight,line_kwargs=[])
    commands = list(test_obj.glyph_list.keys()) #to avoid redundancies
    #commands = test_obj._getSampleCommands()
    commands.append("Bindings.Loc")
    test_obj.demoprint(commands, 4)




