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
                for j in range(1, self.attr_num + 1):
                    feature = row[f'feature{j}'].strip()
                    rotation = int(row[f'rotation{j}'].strip())
                    features.append((feature, rotation))
                self.glyph_list[word] = features
        
    def _getCompositeBinaryArray(self,syllable):
        # Parse dot-separated feature string: fone4.ftwo1.fthree
        self.features = []
        if ':' in syllable:
            style, syllable = syllable.split(':', 1)
            if style in ["v", "V", "vowel"]: style = "vowel"
            self.features.append((style.strip() if style.strip() else "",0))
            
        else:
            style = "CV" 
        if '.' in syllable:
                    syllable, vowel = syllable.split('.', 1)
                    vowel_feature = vowel.strip().lower() if vowel.strip() else "null"
        else:
            vowel_feature = "null"
        if syllable != "null":
                root = syllable.strip()
        else: root = "null"
        if root not in self.glyph_list and root != "null":
            raise KeyError(f"'{root}' not found in C5 glyph_list")
        # get root and field features from glyph_list, ignore determinant slot
        for feat, rotation in self.glyph_list[root]:
                self.features.append((feat, rotation))
                self.features.append((vowel_feature, 0))
        self._makeGlossing(consonant=syllable, vowel=vowel_feature, style=style)
        for feature_name, rotation in self.features:
            fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
            fencoding = self.rotateGlyph(fencoding, rotation) 
            self.binary_array = np.bitwise_or(self.binary_array, fencoding)
        return self.binary_array
        
    def _getBinaryArray(self, syllable):
        self.glossing = syllable
        self.features = []
        #Set Phrase ie Bindings, no declensions.
        if syllable in self.glyph_list:
            for feature_name, rotation in self.glyph_list[syllable]:
                fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
                fencoding = self.rotateGlyph(fencoding, rotation) 
                self.binary_array = np.bitwise_or(self.binary_array, fencoding)
                self.glossing = syllable
            return self.binary_array
        # direct encoding hit — bare feature name, no parsing needed
        if syllable in self.encodings:
            fencoding = np.array(self.encodings[syllable]).reshape(self.attr_num, self.num)
            self.binary_array = np.bitwise_or(self.binary_array, fencoding)
            self.glossing = syllable
            return self.binary_array
        else:
            self._getCompositeBinaryArray(syllable)     
            return self.binary_array     

    def _makeGlossing(self, consonant, vowel=None, style="CV", features=None):
        return_value = ""
        if consonant == "null": consonant = ""
        if vowel == "null":vowel =""
        #todo implement vowel features
        match style:
            case "CV":
                return_value = consonant + vowel
            case "VC":
                return_value = vowel +consonant
            case "vowel":
                return_value = consonant #note this is becaue of ordering
            case "c coda":
                return_value = "-"+consonant
            case "v coda":
                return_value = "-"+consonant#note this is becaue of ordering
            case _:
                return_value = consonant + vowel
        #return_value += consonant.title()
        self.glossing = return_value
        return self.glossing  

if __name__ == "__main__":
    test_obj = syllableGlyph(
                     bases.polygon,
                     base_kwargs=[],
                     line_fn=line_shapes.straight,
                     line_kwargs=[])

    #commands = ["p.a", "v coda:a.long vowel"]
    
   # commands = list(test_obj.glyph_list.keys())
    commands = list(test_obj.encodings.keys())
    test_obj.demoprint(commands, 8)




