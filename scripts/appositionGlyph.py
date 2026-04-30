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
import ast
import math


class appositionGlyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.num = 2
        self.attr_num = 1
        self.base_fn = bases.line
        self.binary_array = np.zeros((self.attr_num,self.num),dtype = int)#recreate array
        self.text_file = self.text_file_base +"class2.csv"

        with open(self.text_file, newline="") as f:
            featurereader = csv.DictReader(f, skipinitialspace=True)
            for row in featurereader:
                if row["feature"] == "Glyphs":  # sentinel keyword
                    break
                word = row["feature"].strip()
                #call = row["call"].strip()   
                encoding = ast.literal_eval(row["encoding"].strip())
                self.attributes.append(word)
                self.encodings[word] = encoding
            glyphreader = csv.DictReader(f, skipinitialspace=True)
            for row in glyphreader:
                word = row['command'].strip()
                features = []
                for j in range(1, self.attr_num + 1):
                    feature = row[f'feature{j}'].strip()
                    rotation = int(row[f'rotation{j}'].strip())
                    features.append((feature, rotation))
                self.glyph_list[word] = features

    def draw(self, annotate=True,
            show_all_paths=False,
            savename="output.png",
            output_dpi=200,
            axs=None,
            dot_color='maroon',
            cmap='summer',
            line_color='maroon',
            dot_size=30,
            dot_range=20,
            legend_fontsize=10,
            legend_anchor=(1, 0.75),
            show_name=False):

        assert self.num == self.binary_array.shape[1]
        assert self.attr_num == self.binary_array.shape[0]
        cmap = plt.get_cmap(cmap)

        # For a line, base_fn should return just 2 points: start and end
        x_vals, y_vals = self.base_fn(self.num, *self.base_kwargs)

        # compute distance between the two endpoints
        dist = np.sqrt((x_vals[1] - x_vals[0])**2 + (y_vals[1] - y_vals[0])**2)
        dot_size = dist * (dot_size+dot_range)       # dot_size now a scale factor, e.g. 5
        dot_range = dist * dot_size     # dot_range now a scale factor, e.g. 3

        if axs is None:
            fig, axs = plt.subplots(1, 1)
        else:
            fig = plt.gcf()
        #axs.set_aspect('equal')
        axs.margins(0.3)

        sizes = [dot_size+dot_range if self.binary_array[0][j] == 1 else dot_size
                for j in range(self.num)]
        shrink = .01 #to keep dots from looking too offcenter.
        if annotate:
            dot_color = cmap(.3)
            halos = [
                (dot_size+dot_range + 3, 0.05),
                (dot_size+dot_range + 2, 0.12),
                (dot_size+dot_range + 1, 0.25)
            ]
            
            for w, a in halos:
                axs.scatter(x_vals + (x_vals.mean() - x_vals) * shrink,
                            y_vals + (y_vals.mean() - y_vals) * shrink,
                            s=[s + w for s in sizes], color=dot_color,
                            alpha=a, edgecolors='none', zorder=2)
            
        axs.scatter(x_vals + (x_vals.mean() - x_vals) * shrink,
            y_vals + (y_vals.mean() - y_vals) * shrink,
            s=sizes, color=dot_color, zorder=3)

        for i in range(self.attr_num):
            k = i + 1
            if annotate:
                color = cmap(0.8 * i / self.attr_num)
                linewidth = 4 - 3 * i / self.attr_num
            else:
                color = line_color
                linewidth = 2
            labelled = False
            for j, elem in enumerate(self.binary_array[i]):
                if elem == 1:
                    P = [x_vals[j], y_vals[j]]
                    Q = [x_vals[(j + k) % self.num], y_vals[(j + k) % self.num]]
                    line_x, line_y = self.line_fn(P, Q, *self.line_kwargs)

                    if annotate:
                        halos = [
                            (linewidth + 5, 0.05),
                            (linewidth + 3, 0.1),
                            (linewidth + 1, 0.2)
                        ]
                        line, = axs.plot(line_x, line_y, lw=linewidth, color=color, zorder=1)
                        line.set_path_effects([
                            pe.Stroke(linewidth=w, foreground=color, alpha=a)
                            for w, a in halos
                        ] + [pe.Normal()])
                    else:
                        axs.plot(
                            line_x, line_y,
                            ls="-",
                            lw=linewidth,
                            color=color,
                            label=self.att_strs[i] if (labelled is False) and annotate else None,
                            zorder=0
                        )
                    labelled = True

        axs.set_axis_off()
        if show_name:
            axs.set_title(self.__name__)
        if savename is not None:
            plt.savefig(savename, dpi=output_dpi,  pad_inches=0.5, transparent=True)
        elif axs is None:
            plt.show( pad_inches=0.5, transparent=True)


if __name__ == "__main__":
    test_obj = appositionGlyph(
                     bases.line,
                     base_kwargs=[],
                     line_fn=line_shapes.straight,
                     line_kwargs=[])

    commands = list(test_obj.glyph_list.keys())
    test_obj.demoprint(commands, 2,2)
    # n = len(commands)
    # cols = math.ceil(math.sqrt(n))
    # rows = math.ceil(n / cols)

    # cell_size = 2  # inches per cell, adjust to taste
    # fig, axes = plt.subplots(rows, cols, figsize=(cols * cell_size, rows * cell_size))

    # axes = axes.flatten()

    # for i, word in enumerate(commands):
    #     test_obj.binary_array = test_obj._getBinaryArray(word)

    #     test_obj.draw(savename=None, show_all_paths=True, annotate=False,
    #                   show_name=False, axs=axes[i])
    #     axes[i].set_title(word.capitalize(), pad=-6, y=-0.1) 
    #     #clear binary array for next keyword
    #     test_obj._clear_binary()

    # # hide any unused subplots
    # for j in range(n, len(axes)):
    #     axes[j].set_visible(False)

    # plt.tight_layout()
    # plt.show()




