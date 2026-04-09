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

class Pronounglyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.is_pronoun = True
        self.class_number = 5
        self.class_name = "Pronoun-ish"
        self.attribute_num = 1
        self.atributes = {"Binary", "Unary"}
        self.glyph_list= ["Summoner", "Demon", "Nominative", "Accusative", "Genitive", "Dative"]



    def _getBinaryArray(self, word,orientation = "North"):
        if(word not in self.glyph_list):
            KeyError("Not a Valid Glyph")

        #at some point, this will be able to smart orient rotation for each attribute
        match(word):
            case "Summoner":
                return np.array([[0,0,0,0,0],[0,1,1,1,0]])
            case "Demon":
                return np.array([[0,0,0,0,0],[0,1,0,1,0]])
            case "Nominative": #No markings
                return np.array([[0,0,0,0,0],[0,0,0,0,0]])
            case "Accusative":
                return np.array([[1,0,0,0,0],[0,0,0,0,0]])
            case "Genitive":
                return np.array([[0,1,0,0,1],[0,0,0,0,0]])
            case "Dative":
                return np.array([[0,0,1,1,0],[0,0,0,0,0]])
            case "Summoner's":
                return np.array([[0,1,0,0,1],[0,1,1,1,0]])
            case "to the Demon":
                return np.array([[0,0,1,1,0],[0,1,0,1,0]])


        return np.array([[0,0,0,0,0],[0,0,0,0,0]])
    





if __name__ == "__main__":
    glyph_list= ["Summoner", "Demon", "Nominative", "Accusative", "Genitive", "Dative", "Summoner's", "to the Demon"]
    n = len(glyph_list)

    fig, axes = plt.subplots(4, 2, figsize=(4, 8))  # adjust grid to taste
    axes = axes.flatten()

    for i, word in enumerate(glyph_list):
        test_obj = Pronounglyph(
                         bases.polygon,
                         base_kwargs = [],
                         line_fn = line_shapes.straight,
                         line_kwargs = [])
        test_obj.class_number = 5
        test_obj.attribute_number = 2
        test_obj.binary_array = test_obj._getBinaryArray(word)

        test_obj.draw(savename=None, show_all_paths=True, annotate=True,
                      show_name=False, axs=axes[i])
        axes[i].set_title(word)


    plt.tight_layout()
    #plt.show()
    plt.savefig("pronounlist.png", transparent=True)

 
    # test_obj = Pronounglyph(
    #                  bases.polygon,
    #                  base_kwargs = [],
    #                  line_fn = line_shapes.straight,
    #                  line_kwargs = [])
    # test_obj.class_number = 4
    # test_obj.attribute_number =2

    
    # test_obj.binary_array = test_obj._getBinaryArray("OR")

    # test_obj.draw(savename = None,show_all_paths=True,annotate=True,
    #               show_name=False)


