import matplotlib.pyplot as plt #There's almost certainly a better way than matplotlib but oh well
import numpy as np
import matplotlib.patheffects as pe
from collections.abc import Callable
from necklaces import default_generation
#from svg2tikz import convert_svg
import os
import bases
import line_shapes

class glyph():
    def __init__(self):
        self.class_number = 0
        self.class_names = ["Relativeizer", "Punctuation", "Recursion", "Deontic", "Logical", "Pronouns", "AFFIXES?", "SUBORDINATORS?","Numbers","Prepositions?","Adjectives/Adverbs?","Verbs","Syllabary","Nouns"]
        self.vertices = []
        self.atributes = {}
        self.is_ambiguous = True
        self.unique_binary_strings = 0


    def draw(self):
        #TODO copy form spells.
        return
