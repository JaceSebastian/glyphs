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

class NounGlyph(glyph):
    ''' Nouns/Nominals can be singular, plural, or mass, with case and head versus modifier marking.
        I want to adjust the determiners to include this/that/all/none/each/some/any
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization  
        self.is_number = True
        self.class_number = 13
        self.class_name = "Numbers"
        self.attribute_num = 6
        self.attr_names = ["Case", "Number", "Determiner"]
        self.attributes = ["Nominative", "Accusative", "Genitive", "Dative", "Instrumental","This", "That", "These", "Those", "A", "Some"]
        attr_masks = {"singular": np.array([1, 0, 0, 0, 0]),
                      "a":   np.array([0, 1, 0, 0, 0]),
                      "b":  np.array([0, 0, 1, 0, 0]),
                    }

    def orient_array(arr, orientation="North"):
        assert arr is np.array()
        if(orientation == "North"):
            return arr
        #todo 
        return arr
    


    def _getBinaryArray(self, features,orientation = "North"):
        '''at some point, this will be able to smart orient rotation for each attribute'''
        result = np.zeros((self.attribute_num, self.class_number))
        for feat in features:
            if(feat not in self.attributes):
                raise KeyError("Not a Valid Glyph")
            findex = self.attributes.index(feat)
            result[findex] = result[findex] | np.array([0,0,0,0,0,0,0,0,0,0,0,0,0])

        return result





if __name__ == "__main__":
    #todo, consider adding EXPR in attritbute 1 for things like +3 as different from +, 3?
    glyph_list= []
    n = len(glyph_list)
    print("This class hasn't been implemented yet, bozo.")

    fig, axes = plt.subplots(4,6, figsize=(7,5))  # adjust grid to taste
    axes = axes.flatten()

    for i, word in enumerate(glyph_list):
        test_obj = NounGlyph(
                         bases.polygon,
                         base_kwargs = [],
                         line_fn = line_shapes.straight,
                         line_kwargs = [])
        test_obj.class_number = 8
        test_obj.attribute_number = 4
        test_obj.binary_array = test_obj._getBinaryArray(word)

        test_obj.draw(savename=None, show_all_paths=True, annotate=True,
                      show_name=False, axs=axes[i])
        axes[i].set_title(word)


    plt.tight_layout()
    #plt.show()
    plt.savefig("Numberlist.png", transparent=True)




