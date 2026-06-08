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
class verbGlyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.num = 10
        self.attr_num = 5
        self.real_attr_num = 3
        self.binary_array = np.zeros((self.attr_num,self.num),dtype = int)#recreate array
        self.text_file = self.text_file_base +"class10.csv"

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
                for j in range(1, self.real_attr_num + 1):
                    feature = row[f'feature{j}'].strip()
                    rotation = int(row[f'rotation{j}'].strip())
                    features.append((feature, rotation))
                self.glyph_list[word] = features


     #override
    def _getBinaryArray(self, word):
        '''need to be able to handle feature list, not tested. TODO
            should take in a word like Cross.Inf and generate glyph encoding and gloss for "to Cross"
        
        '''
        self.glossing = "Glossing error found."
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
            word, conjugation = word.split('.', 1)
            conj = (conjugation.strip() if conjugation.strip() else "Inf",0)
        else:
            conjugation = "Inf"
            conj = ("Inf",0)
        
        root = word.strip().title()
        if not root:
            raise ValueError(f"No root noun found in '{word}'")
        if root not in self.glyph_list: #eventaully, this should be capable of making glyphs from features? maybe?
            raise KeyError(f"'{root}' not found in glyph_list")
        # get word features
        for feat, rotation in self.glyph_list[root]:
            features.append((feat, rotation))
        features.append(conj)
        for feature_name, rotation in features:
            if feature_name not in self.encodings:
                print(f"Warning: '{feature_name}' not found in encodings, skipping.")
                continue
            fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
            fencoding = self.rotateGlyph(fencoding, rotation)  # default rotation
            self.binary_array = np.bitwise_or(self.binary_array, fencoding)

        self._makeGlossing(root, conjugation)
        return self.binary_array
    
    def _makeGlossing(self, root, conj):
        '''Note that this is a temp fix until I find a conjugation package I like that keeps the archaic feel
        LemmInflect seems good for past participles and irregulars'''
        self.glossing = ""
        if (conj == "Inf"):
            self.glossing += "to "
        elif (conj == "Passive"):
            self.glossing += "be "
        elif(conj == "Gerundive"):
             self.glossing += "(the) "
        elif(conj in ["Continuous", "Present Perfect"]):
            self.glossing += "is "
        elif(conj == "Passive Perfect"):
            self.glossing += "had been "
        elif(conj =="Past Perfect"):
            self.glossing += "was "

        self.glossing += root

        if(conj =="Pres"):
            self.glossing += "s"
        elif(conj in ["Gerundive", "Participle", "Continuous"]):
            self.glossing += "ing "
        elif(conj in ["Past","Past Participle", "Passive","Passive Perfect", "Past Perfect", "Present Perfect"]):
            self.glossing += "ed " if (root[-1] != 'e') else "d "
        
    
        return self.glossing
    




if __name__ == "__main__":
    test_obj = verbGlyph(
                     bases.polygon,
                     base_kwargs=[],
                     line_fn=line_shapes.straight,
                     line_kwargs=[])

    commands = test_obj._getSampleCommands()
    test_obj.demoprint(commands, 5)




