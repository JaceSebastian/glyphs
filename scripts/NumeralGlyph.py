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

class NumeralGlyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.num = 8
        self.attr_num = 4
        self.binary_array = np.zeros((self.attr_num,self.num),dtype = int)#recreate array
        self.text_file = self.text_file_base +"class8.csv"

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
        '''Handle numeral encoding. Format:
        "LT:Three.Numerator"
        "GT:Five.Percentage"
        bare numerals default to null:NaN.null
        Checks glyph_list first for aliases (1, one, One) and special combinations.
        Format: "boundary:Digit.type"
        '''
        self.glossing = "Glossing not showing up."
        
        # check glyph_list first for aliases and special combinations
        if word in self.glyph_list:
            for feature_name, rotation in self.glyph_list[word]:
                fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
                fencoding = self.rotateGlyph(fencoding, rotation)
                self.binary_array = np.bitwise_or(self.binary_array, fencoding)
                self.glossing = word
            return self.binary_array

        features = []

        # boundary slot
        if ':' in word:
            boundary, word = word.split(':', 1)
            boundary = boundary.strip() if boundary.strip() else None
            if boundary:
                features.append((boundary, 0))
        else:
            boundary = None

        # type slot
        if '.' in word:
            word, numtype = word.split('.', 1)
            numtype = numtype.strip() if numtype.strip() else None
        else:
            numtype = None

        # num slot
        root = word.strip().lower()
        if not root:
            raise ValueError(f"No numeral found in '{word}'")
        
        # check glyph_list for digit aliases (1/one/One -> One encoding)
        if root in self.glyph_list:
            for feat, rotation in self.glyph_list[root]:
                features.append((feat, rotation))
            num_gloss = root
        else:
            # direct encoding lookup
            if root not in self.encodings:
                raise KeyError(f"'{root}' not found in glyph_list or encodings")
            features.append((root, 0))
            num_gloss = root

        # type slot
        if numtype:
            features.append((numtype, 0))

        self._makeGlossing(boundary, num_gloss, numtype)

        for feature_name, rotation in features:
            if feature_name not in self.encodings:
                print(f"Warning: '{feature_name}' not found in encodings, skipping.")
                print(f"Encodings: '{self.encodings}'.")
                continue
            fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
            fencoding = self.rotateGlyph(fencoding, rotation)
            self.binary_array = np.bitwise_or(self.binary_array, fencoding)

        return self.binary_array
    

    def _makeGlossing(self, boundary, num, type):
        return_value = ""
        match(boundary):
            case "LEQ":
                return_value += "⩽"
            case "LT":
                return_value += "<"
            case "GT":
                return_value += ">"
            case "GEQ": 
                return_value += "⩽"
     

        return_value += num.title() if (num.lower() != "nan") else num

        match(type):
            case "percent":
                return_value +="%"
            case "ordinal":
                if(num == "one"  or num == "1"):
                    return_value = "First"
                elif(num == "2"):
                    return_value = "Second"
                else:
                    return_value += "th"
            case "denominator":
                return_value +="^-1"




        self.glossing = return_value
        return return_value



if __name__ == "__main__":
    test_obj = NumeralGlyph(bases.polygon,base_kwargs=[],line_fn=line_shapes.straight,line_kwargs=[])

    commands = list(test_obj.glyph_list.keys())[:24]
    test_obj.demoprint(commands, cols=4)





