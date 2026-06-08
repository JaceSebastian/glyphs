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



    #override
    def _getBinaryArray(self, word):
        '''need to be able to handle 3 elements. Keywords should be formated as:
        "the:House.Loc"
        none of this: Nonsense.Nom
        fire (implied Indef and Nom if unmarked.)
        '''
        self.glossing = ""
        if word in self.glyph_list:
            for feature_name, rotation in self.glyph_list[word]:
                fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
                fencoding = self.rotateGlyph(fencoding, rotation) 
                self.binary_array = np.bitwise_or(self.binary_array, fencoding)
                self.glossing = word
            return self.binary_array
        
         # direct encoding hit — bare feature name, no parsing needed
        if word.lower() in self.encodings:
            fencoding = np.array(self.encodings[word.lower()]).reshape(self.attr_num, self.num)
            self.binary_array = np.bitwise_or(self.binary_array, fencoding)
            self.glossing = word
            return self.binary_array
        

        features = []
        if ':' in word:
            det, word = word.split(':', 1)
            features.append((det.strip().lower() if det.strip() else "Def.SG",0))
        else:
            det = None
            features.append(("null",0))
        if '.' in word:
            word, case = word.split('.', 1)
            case = (case.strip().lower() if case.strip() else "adj",0)
        else:
            case = ("adj",0)
        
        root = word.strip().title()
        if not root:
            raise ValueError(f"No root adjective found in '{word}'")
        if root not in self.glyph_list:
            raise KeyError(f"'{root}' not found in glyph_list")
        for feat, rotation in self.glyph_list[root]:
            features.append((feat, rotation))
        features.append(case)
        self._makeGlossing(det, root, case[0])
        #print(features)
        for feature_name, rotation in features:
            if feature_name not in self.encodings:
                print(f"Warning: '{feature_name}' not found in encodings, skipping.")
                continue
            fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
            fencoding = self.rotateGlyph(fencoding, rotation)  # default rotation
            self.binary_array = np.bitwise_or(self.binary_array, fencoding)
        
        return self.binary_array



    def _makeGlossing(self, det, root, wordclass):
        return_value = ""
        return_value += root.title()

        if wordclass == "adj":
            pass
        elif wordclass == "adverb":
            return_value += "ly"
        elif wordclass == "superlative":
            return_value += "-est"
        elif wordclass == "comparative":
            return_value += "-er"

        self.glossing = return_value
        return return_value




if __name__ == "__main__":
    test_obj = adjGlyph(bases.polygon,base_kwargs=[],line_fn=line_shapes.straight,line_kwargs=[])
    #commands = list(test_obj.glyph_list.keys())[:45]
    commands = test_obj._getSampleCommands()
    commands.append("clear.adverb") #This is not working Todo
    commands.append("Early")
    test_obj.demoprint(commands, cell_size=1)


 



