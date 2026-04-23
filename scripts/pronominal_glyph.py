from glyph import glyph
import matplotlib.pyplot as plt #There's almost certainly a better way than matplotlib but oh well
import numpy as np
import matplotlib.patheffects as pe
from collections.abc import Callable
from necklaces import default_generation
import os
import bases
import line_shapes

class PronounGlyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.is_pronoun = True
        self.num = 5
        self.class_name = "Pronoun-ish"
        self.attribute_num = 1
        self.atributes = {"Subject", "Case"}
        self.glyph_list= ["Summoner", "Demon", "Nominative", "Accusative", "Genitive", "Dative", "Instrumental"]



    def _getBinaryArray(self, word,orientation = "North"):
        if(word not in self.glyph_list):
            KeyError("Not a Valid Glyph")

        #at some point, this will be able to smart orient rotation for each attribute
        # todo, throw error if trying to add two features for one attribute. ie summoner && demon.
        match(word): #on pentagram order is [right top, right bottom, left bottom, right top, top]
            case "Summoner":
                return np.array([[0,0,0,0,0],[0,0,1,1,1]])
            case "Demon":
                return np.array([[0,0,0,0,0],[1,0,1,0,0]])
            case "Nominative": #No markings
                return np.array([[0,0,0,0,0],[0,0,0,0,0]])
            case "Accusative":
                return np.array([[0,1,0,0,0],[0,0,0,0,0]])
            case "Genitive":
                return np.array([[1,0,1,0,0],[0,0,0,0,0]])
            case "Dative":
                return np.array([[0,0,0,1,1],[0,0,0,0,0]])
            case "Instrumental":
                return np.array([[0,0,1,1,1],[0,0,0,0,0]])
            case "Summoner's":
                return np.array([[1,0,1,0,0],[0,0,1,1,1]])
            case "to the Demon":
                return np.array([[0,1,1,0,0],[1,0,1,0,0]])


        return np.array([[0,0,0,0,0],[0,0,0,0,0]])
    





if __name__ == "__main__":
    glyph_list= ["Summoner", "Demon", "Nominative", "Accusative", "Genitive", "Dative", "Instrumental", "Summoner's", "to the Demon"]
    n = len(glyph_list)

    fig, axes = plt.subplots(3,3, figsize=(7, 7))  # adjust grid to taste
    axes = axes.flatten()

    for i, word in enumerate(glyph_list):
        test_obj = PronounGlyph(
                         bases.polygon,
                         base_kwargs = [],
                         line_fn = line_shapes.straight,
                         line_kwargs = [])
        test_obj.num = 5
        test_obj.attribute_number = 2
        test_obj.binary_array = test_obj._getBinaryArray(word)

        test_obj.draw(savename=None, show_all_paths=True, annotate=False,
                      show_name=False, axs=axes[i])
        axes[i].set_title(word)


    plt.tight_layout()
    #plt.show()
    plt.savefig("pronounlist.png", transparent=True)

 
    # test_obj = PronounGlyph(
    #                  bases.polygon,
    #                  base_kwargs = [],
    #                  line_fn = line_shapes.straight,
    #                  line_kwargs = [])
    # test_obj.class_number = 4
    # test_obj.attribute_number =2

    
    # test_obj.binary_array = test_obj._getBinaryArray("OR")

    # test_obj.draw(savename = None,show_all_paths=True,annotate=True,
    #               show_name=False)


