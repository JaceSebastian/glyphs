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

class deonticglyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.is_deontic = True
        self.num = 3
        self.attribute_num = 1
        
        self.class_name = "Deontic"
        self.atributes = {}
        self.glyph_list= ["Obligatory", "Permissable", "Forbidden", "Omissible"]



    def _getBinaryArray(self, word,orientation = "North"):
        if(word not in self.glyph_list):
            KeyError("Not a Valid Glyph")
        
        match(word):
            case "Obligatory":
                return np.array([[0,1,1]])
            case "Permissable":
                return np.array([[0,0,1]])
            case "Forbidden":
                return np.array([[1,1,1]])
            case "Omissible":
                return np.array([[0,0,0]])
       
        return np.array([[0,0,0]])
    





if __name__ == "__main__":
    glyph_list= ["Obligatory", "Permissable", "Forbidden", "Omissible"]
    n = len(glyph_list)

    fig, axes = plt.subplots(2, 2, figsize=(6, 6))  # adjust grid to taste
    axes = axes.flatten()

    for i, word in enumerate(glyph_list):
        test_obj = deonticglyph(
                         bases.polygon,
                         base_kwargs = [],
                         line_fn = line_shapes.straight,
                         line_kwargs = [])
        test_obj.attribute_number = 1
        test_obj.binary_array = test_obj._getBinaryArray(word)

        test_obj.draw(savename=None, show_all_paths=True, annotate=True,
                      show_name=False, axs=axes[i])
        axes[i].set_title(word)


    plt.tight_layout()
    plt.show()



