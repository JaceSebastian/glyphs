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
            #print(self.glyph_list)
    
    def _getBinaryArray(self, word):
        self.glossing = word
        self.features = []
        if(word in self.glyph_list):
            self.features = self.glyph_list[word]
            self._makeGlossing(det = "", root = word, case = "Nom")
        else:
            self.features = []
            if ':' in word:
                det, word = word.split(':', 1)
                self.features.append((det.strip() if det.strip() else "Def.SG",0))
            else:
                det = "The "
            if '.' in word:
                word, case = word.split('.', 1)
                case_feature = case.strip() if case.strip() else "Nom"
            else:
                case = "Nom"
                case_feature = "Nom"
            self.features.append((word,0))
            self.features.append((case_feature,0))
            self._makeGlossing(root=word, case=case_feature)
        for feature_name, rotation in self.features:
            fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
            fencoding = self.rotateGlyph(fencoding, rotation) 
            self.binary_array = np.bitwise_or(self.binary_array, fencoding)
        return self.binary_array


    def _makeGlossing(self,det="The ", root="_", case="Nom"):
        return_value = ""
        if case == "Gen":
            return_value += "of "
        elif case == "Loc":
            return_value += "to/from "
        elif case == "Dat":
            return_value += "to "
        elif case == "Instr":
            return_value += "by/with "
        else: #case == "Nom" or case == "Acc":
            case = None

        return_value += det
        return_value += root.title()
        self.glossing = return_value
        return return_value


if __name__ == "__main__":
    test_obj = PronounGlyph(bases.polygon,base_kwargs=[],line_fn=line_shapes.straight,line_kwargs=[])
    printList = list(test_obj.glyph_list.keys())[:12] #to avoid redundancies
    test_obj.demoprint(printList, 4)




