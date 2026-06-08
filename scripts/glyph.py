import matplotlib.pyplot as plt  # There's almost certainly a better way than matplotlib but oh well
import numpy as np
import matplotlib.patheffects as pe
from collections.abc import Callable
from necklaces import default_generation
from drawer import GlyphDrawer

# from svg2tikz import convert_svg
import os
import bases
import line_shapes
import ligatureGlyph

import csv
import ast
import math




class glyph:
    """The base class should never be used, instead the subclasses, with innate none and feature counts, will be implemented"""

    def __init__(self,base_fn: Callable = bases.polygon,line_fn: Callable = line_shapes.straight,txt_file_base: str = r"./attribute_ordering/",override_dict={},base_kwargs=[],line_kwargs=[],ignore_atts=False,
    ):
        self.atts = []
        self.base_fn = base_fn
        self.base_kwargs = base_kwargs
        self.line_fn = line_fn
        self.line_kwargs = line_kwargs

        self.num = 0
        self.attr_num = 0
        self.text_file_base: str = r"./GlyphTables/"
        """This is where the information for each line is held."""
        self.binary_array = np.zeros((self.attr_num, self.num), dtype=int)
        self.attributes = []  # Not sure if this is ever used
        self.glyph_list = {}
        self.feature_list = {}
        self.encodings = {}
        self.glossing = None

    def demoprint(
        self,
        printList,
        cols=None,
        Flip=False,
        cell_size=1.5,
        save=False,
        savename="demoprint.png",
        draw_kwargs={},
    ):
        commands = printList

        n = len(commands)
        if cols is None:
            cols = math.ceil(math.sqrt(n))
        else:
            cols = min(cols, n)
        rows = math.ceil(n / cols)

        fig, axes = plt.subplots(
            rows, cols, figsize=(cols * cell_size, rows * cell_size)
        )
        axes = np.array(axes).flatten() if n > 1 else [axes]

        for i, word in enumerate(commands):
            self.binary_array = self._getBinaryArray(word)

            if Flip:
                r = i % rows
                c = i // rows
                idx = r * cols + c
            else:
                idx = i

            self.draw(
                savename=None,
                show_all_paths=True,
                glow=True,
                show_name=False,
                axs=axes[idx],
                vertex_num = self.num,
                **draw_kwargs,
            )


            fig_width_inches = fig.get_size_inches()[0]
            ax_width_inches = axes[i].get_position().width * fig_width_inches
            fontsize = ax_width_inches * 10
            fontsize = max(fontsize, 8)  # minimum font size of 8
            axes[i].set_title(word, pad=-6, y=-0.1, fontsize=fontsize)
            pos = axes[i].get_position()
            self._clear_binary()

        for j in range(n, len(axes)):
            axes[j].set_visible(False)

        plt.tight_layout(rect=[0, 0.05, 1, 1])

        if save:
            plt.savefig(savename, dpi=200, bbox_inches="tight", transparent=True)
        else:
            plt.show()

    def _clear_binary(self):
        self.glossing = ""
        self.binary_array = np.zeros((self.attr_num, self.num), dtype=int)

    def rotateGlyph(self, binary_encoding, rotation):
        if rotation == 0:
            return binary_encoding
        # encoding is a list of lists
        for i in range(len(binary_encoding)):
            if np.any(binary_encoding[i]):
                binary_encoding[i] = np.roll(binary_encoding[i], rotation)
        return binary_encoding

    def _readFeatureList(self, word):
        # Parse dot-separated feature string: fone4.ftwo1.fthree
        features = []
        for part in word.split("."):
            if not part:
                continue
            # todo, figure out why regex isn't working here
            i = len(part)
            while i > 1 and part[i - 1].isdigit():
                i -= 1
            feature_name = part[:i]
            rotation = int(part[i:]) if part[i:] else 0
            features.append((feature_name, rotation))
        return features

    def _getBinaryArray(self, word):
        self.glossing = word
        if word in self.glyph_list:
            feats = self.glyph_list[word]
        else:
            feats = self._readFeatureList(word)
        for feature_name, rotation in feats:
            if feature_name not in self.encodings:
                print(
                    f"Warning: '{feature_name}' not found encodings for class {self.num} word {word}, skipping."
                )
            fencoding = np.array(self.encodings[feature_name.lower()]).reshape(
                self.attr_num, self.num
            )
            fencoding = self.rotateGlyph(fencoding, rotation)
            self.binary_array = np.bitwise_or(self.binary_array, fencoding)
        return self.binary_array

    def _makeGlossing(self, det=None, root="", case=None):
        """This should always be overwritten for glyph class"""
        self.glossing = root

    def base_points(self):
        """Return x/y coordinates from the base function."""
        #print(self.base_fn(self.num, *self.base_kwargs))
        return self.base_fn(self.num, *self.base_kwargs)
    
    def left_anchor(self):
        x_vals, y_vals = self.base_points()
        idx = np.argmin(x_vals)
        return x_vals[idx], y_vals[idx]

    def right_anchor(self):
        x_vals, y_vals = self.base_points()
        idx = np.argmax(x_vals)
        return x_vals[idx], y_vals[idx]

    def _getSampleCommands(self, group: str | None = None) -> list[str]:
        """
        Returns a list of all renderable specs.
        If group is specified, only features belonging to that group are included.
        - individual features (direct encoding keys, skipping null/sentinel)
        - combined glyphs from glyph_list
        """
        commands = []

        # individual features — filtered by group if specified
        with open(self.text_file, newline="") as f:
            reader = csv.DictReader(
                (line for line in f if line.strip() and not line.lstrip().startswith("#")),
                skipinitialspace=True
            )
            for row in reader:
                if row["feature"] == "Glyphs":  # sentinel keyword
                    break
                feature = row["feature"].strip()
                if group is None or row["group"].strip() == group:
                    commands.append(feature)

        # combined glyphs from glyph_list — no group concept, always included
        if group == "glyphs":
            for word in list(self.glyph_list)[:40]:
                commands.append(word)

        return commands


    def draw_offset(self, axs, x_offset=0.0, y_offset=0.0, rotation=0, **draw_kwargs):
        original_base_fn = self.base_fn

        def offset_base_fn(n, *args):
            x_vals, y_vals = original_base_fn(n, *args)
            return [x + x_offset for x in x_vals], [y + y_offset for y in y_vals]

        self.base_fn = offset_base_fn
        self.draw(axs=axs, **draw_kwargs)
        self.base_fn = original_base_fn


    def draw(self, **kwargs):
        GlyphDrawer(self).draw(**kwargs)





#####################################################################################################################33



