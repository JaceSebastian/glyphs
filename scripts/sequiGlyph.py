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

class SequiGlyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.is_coordinator = True
        self.num = 6
        self.attr_num = 3
        self.binary_array = np.array([[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]])
        
        self.class_name = "Sequi"
        self.atributes = {"Sequencing", "Sequent", "Consequence"}
        self.glyph_list= []
        self.encondings = None
        self.text_file = self.text_file_base +"class6.csv"

        with open(self.txt_file_base+"class3.csv", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row["Word"].strip()
                call = row[" call"].strip()      # note the leading space in your header
                encoding = ast.literal_eval(row[" encoding"].strip())

                self.glyph_list.append(word)
                self.encodings[word] = encoding



    def _getBinaryArray(self, word,orientation = "North"):
        if(word not in self.glyph_list):
            KeyError("Not a Valid Glyph")
        
        #TODO
    





if __name__ == "__main__":
    glyph_list= ["Obligatory", "Permissable", "Forbidden", "Omissible"]
    n = len(glyph_list)

    fig, axes = plt.subplots(2, 2, figsize=(6, 6))  # adjust grid to taste
    axes = axes.flatten()

    for i, word in enumerate(glyph_list):
        test_obj = sequiGlyph(
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



