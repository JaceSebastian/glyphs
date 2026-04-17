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

class NumeralGlyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.num = 8
        self.attr_num = 4

        self.class_name = "Numbers"
        self.is_number = True
        self.attributes = ["Boundary","Number", "Type", "Operators"]
        self.glyph_list=[]



    def _getBinaryArray(self, word,orientation = "North"):
        if(word not in self.glyph_list):
            KeyError("Not a Valid Glyph")

        #at some point, this will be able to smart orient rotation for each attribute
        match(word):
            case "Value X":
                return np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "LEQ X":
                return np.array([[1,0,1,0,0,1,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "GEQ X":
                return np.array([[1,1,1,1,1,0,1,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "LT X":
                return np.array([[0,1,1,0,0,1,1,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "GT X":
                return np.array([[1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "NaN":
                return np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "0":
                return np.array([[0,0,0,0,0,0,0,0],[0,1,0,1,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "1":
                return np.array([[0,0,0,0,0,0,0,0],[1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "2":
                return np.array([[0,0,0,0,0,0,0,0],[0,1,1,1,0,0,1,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "3":
                return np.array([[0,0,0,0,0,0,0,0],[0,0,1,0,0,1,0,1],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "4":
                return np.array([[0,0,0,0,0,0,0,0],[1,0,1,0,1,0,1,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "5":
                return np.array([[0,0,0,0,0,0,0,0],[1,1,0,0,1,1,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "6":
                return np.array([[0,0,0,0,0,0,0,0],[1,0,0,0,1,1,0,1],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "7":
                return np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,1,1,1],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "Numerator":
                return np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,1,1,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
            case "Denominator":
                return np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,1,1,1,1],[0,0,0,0,0,0,0,0]])
            case "Percentage":
                return np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,1,1,0,0,1,1,0],[0,0,0,0,0,0,0,0]])
            case "Negative":
                return np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,1,0,1,0,0],[0,0,0,0,0,0,0,0]])     
            case "Add":
                return np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,1,1,0,0,0,0,0]])
            case "Multiply":
                return np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,1,0,1,0]])
            case "Equate":
                return np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[1,1,1,1,0,0,0,0]])
            case "<=1/4":
                return np.array([[0,0,1,0,1,0,0,1],[1,0,1,0,1,0,1,0],[0,0,0,0,1,1,1,1],[0,0,0,0,0,0,0,0]])
            case "<7%": 
                return np.array([[0,0,1,1,0,0,1,1],[0,0,0,0,0,1,1,1],[0,1,1,0,0,1,1,0],[0,0,0,0,0,0,0,0]])
            case "-5":
                return np.array([[0,0,0,0,0,0,0,0],[1,1,0,0,1,1,0,0],[0,0,0,1,0,1,0,0],[0,1,1,0,0,0,0,0]])
            

        return np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
    





if __name__ == "__main__":
    #todo, consider adding EXPR in attritbute 1 for things like +3 as different from +, 3?
    glyph_list= ["Value X", "LEQ X", "GEQ X", "LT X", "GT X", "0", "1", "2", "3", "4", "5", "6","7", "NaN","Numerator", "Denominator", "Negative", "Percentage", "Add", "Multiply", "Equate", "<=1/4", "<7%", "-5"]
    n = len(glyph_list)

    fig, axes = plt.subplots(4,6, figsize=(7,5))  # adjust grid to taste
    axes = axes.flatten()

    for i, word in enumerate(glyph_list):
        test_obj = NumeralGlyph(
                         bases.polygon,
                         base_kwargs = [],
                         line_fn = line_shapes.straight,
                         line_kwargs = [])
        test_obj.num = 8
        test_obj.attribute_number = 4
        test_obj.binary_array = test_obj._getBinaryArray(word)

        test_obj.draw(savename=None, show_all_paths=True, annotate=False,
                      show_name=False, axs=axes[i])
        axes[i].set_title(word)


    plt.tight_layout()
    #plt.show()
    plt.savefig("Numberlist.png", transparent=True)




