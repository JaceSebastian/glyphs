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
import re
import inflect


class nounGlyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.num = 12
        self.attr_num = 6
        self.binary_array = np.zeros((self.attr_num,self.num),dtype = int)#recreate array
        self.text_file = self.text_file_base +"class12.csv"
        self.sample_list = ["DefSG:year.Nom", "fire","Any:fire.Loc"]
        self.inflector = inflect.engine()

        with open(self.text_file, newline="") as f:
            featurereader = csv.DictReader((line for line in f if line.strip() and not line.lstrip().startswith("#")), skipinitialspace=True)
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
                #unlike others, should be just the root nouns (with semantic field),
                #and getBinaryArray is changed to handle count and case features, might want to add glossing?.
                i = 1
                #TODO add glossing, so input is purely year.PL not separate roots for year/years.
                # ie, remove count feature, and only make in _getBinaryArray().
                for attribute in ['root', 'field']:
                    feat = row[f'{attribute}'].strip()
                    rotation = int(row[f'rotation{i}'].strip())
                    features.append((feat, rotation))
                    i+=1
                self.glyph_list[word] = features

    #override
    def _getBinaryArray(self, word):
        '''need to be able to handle 3 elements. Keywords should be formated as:
        "the:House.Loc"
        none of this: Nonsense.Nom
        fire (implied Indef and Nom if unmarked.)

        
        '''
        self.glossing = "Glossing not showing up."
        if word in self.glyph_list:
            for feature_name, rotation in self.glyph_list[word]:
                fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
                fencoding = self.rotateGlyph(fencoding, rotation) 
                self.binary_array = np.bitwise_or(self.binary_array, fencoding)
                self.glossing = word
            return self.binary_array
        features = []
        if ':' in word:
            det, word = word.split(':', 1)
            features.append((det.strip() if det.strip() else "Def.SG",0))
        else:
            det = None
            features.append(("Mass",0))
        if '.' in word:
            word, case = word.split('.', 1)
            case_feature = (case.strip() if case.strip() else "Nom",0)
        else:
            case = "Nom"
            case_feature = ("Nom",0)
        
        root = word.strip()
        if not root:
            raise ValueError(f"No root noun found in '{word}'")
        if root not in self.glyph_list:
            raise KeyError(f"'{root}' not found in glyph_list")
        # get root and field features from glyph_list, ignore determinant slot
        for feat, rotation in self.glyph_list[root]:
            features.append((feat, rotation))
        features.append(case_feature)

        self._makeGlossing(det, root, case)
        #print(features)
        for feature_name, rotation in features:
            if feature_name not in self.encodings:
                print(f"Warning: '{feature_name}' not found in encodings, skipping.")
                continue
            fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
            fencoding = self.rotateGlyph(fencoding, rotation)  # default rotation
            self.binary_array = np.bitwise_or(self.binary_array, fencoding)
        
        return self.binary_array


    def _makeGlossing(self, det, root, case):
        return_value = ""
        if case == "Gen":
            return_value += "of "
        elif case == "Loc":
            return_value += "to/from "
        elif case == "Dat":
            return_value += "to "
        elif case == "Inst":
            return_value += "by/with "
        else: #case == "Nom" or case == "Acc":
            case = None

        if det:
            if det in ["PL","ThePL", "Some", "All"]: #hardcoded BAD
                root = self.inflector.plural(root)
            if det == "ThePL":
                return_value += "The "
            elif det != "PL":
                return_value += det + " "
        
        return_value += root.title()
        self.glossing = return_value
        return return_value

if __name__ == "__main__":
    
    test_obj = nounGlyph(
                     bases.polygon,
                     base_kwargs=[],
                     line_fn=line_shapes.straight,
                     line_kwargs=[])

    commands = list(test_obj.glyph_list.keys())
   # print("running sample_list, not glyph_list")
    #commands = test_obj.sample_list
    test_obj.demoprint(commands,cell_size=2)




