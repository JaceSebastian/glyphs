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


class punctuationGlyph(glyph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # subclass-specific initialization
        self.num = 1
        self.attr_num = 1
        self.base_fn = bases.line
        self.binary_array = np.zeros((self.attr_num,self.num),dtype = int)#recreate array
        self.text_file = self.text_file_base +"class1.csv"

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
                for j in range(1, self.attr_num + 1):
                    feature = row[f'feature{j}'].strip()
                    rotation = int(row[f'rotation{j}'].strip())
                    features.append((feature, rotation))
                self.glyph_list[word] = features




    # def draw(self,glow = False,
    #             show_all_paths = False,
    #             savename = "output.png",
    #             output_dpi = 200,
    #             axs = None,
    #             dot_color = 'maroon',
    #             cmap = 'summer',
    #             line_color = 'maroon',
    #             dot_size = 30,
    #             legend_fontsize = 8,
    #             legend_anchor = (1,0.75),
    #             show_name = False):
    #         #print(f"Attribute num {self.attr_num} shape {self.binary_array.shape[0]}")
    #         assert self.num == self.binary_array.shape[1]
    #         assert self.attr_num== self.binary_array.shape[0]
    #         cmap = plt.get_cmap(cmap)
    #         if self.num:
    #             dot_size = max(dot_size/(self.num/4), 6)
    #         x_vals,y_vals = self.base_fn(self.num,*self.base_kwargs)

    #         if axs is None:
    #             fig,axs = plt.subplots(1,1)
    #         else:
    #             fig = plt.gcf()
    #         axs.set_aspect('equal')
    #         axs.margins(0.1)
            
    #         #draw the points
    #         if glow:
    #             dot_color = cmap(.3)
                
    #             halos = [
    #                 (dot_size+3, 0.05),
    #                 (dot_size+2, 0.12),
    #                 (dot_size+1, 0.25)
    #             ]
    #             for w, a in halos:
    #                 axs.scatter(
    #                     x_vals,
    #                     y_vals,
    #                     s=w,
    #                     color=dot_color,
    #                     alpha=a,
    #                     edgecolors='none',
    #                     zorder=2
    #                 )

    #         # draw main dots
    #         axs.scatter(
    #             x_vals,
    #             y_vals,
    #             s=dot_size,
    #             color=dot_color,
    #             zorder=2
    #         )

    #         for i in range(self.attr_num):
    #             k = i+1
    #             if glow:
    #                 color = cmap(0.8*i/(self.attr_num))
    #                 linewidth = 4- 3*i/self.attr_num
    #                 dot_color
    #             else:
    #                 color = line_color
    #                 linewidth = 2
    #             labelled = False
    #             for j,elem in enumerate(self.binary_array[i]):
                    
    #                 if elem == 1:
    #                     #if element is 1
    #                     P = [x_vals[j],y_vals[j]]
    #                     Q = [x_vals[(j+k)%self.num],y_vals[(j+k)%self.num]]
    #                     line_x,line_y = self.line_fn(P,Q,*self.line_kwargs)
                        
    #                     if glow:
    #                     # layered halo
    #                         halos = [
    #                             (linewidth + 5, 0.05),  # widest, faintest
    #                             (linewidth + 3, 0.1),
    #                             (linewidth + 1, 0.2)
    #                         ]

    #                         line, = axs.plot(line_x, line_y, lw=linewidth, color=color, zorder=1)

    #                         line.set_path_effects([
    #                             pe.Stroke(linewidth=w, foreground=color, alpha=a)
    #                             for w, a in halos
    #                         ] + [pe.Normal()])
    #                     else:
    #                         axs.plot(
    #                         line_x, line_y,
    #                         ls="-",
    #                         lw=linewidth,
    #                         color=color,
    #                         label=self.att_strs[i] if (labelled is False) and glow else None,
    #                         zorder=0
    #                         )
    #                     labelled = True
    #         #save_figure
    #         axs.set_axis_off()
    #         if show_name:
    #             axs.set_title(self.__name__)
    #         if savename is not None:
    #             plt.savefig(savename,dpi = output_dpi,bbox_inches = 'tight', pad_inches=0.5, transparent=True)
    #         elif axs is None:
    #             plt.show(transparent=True, pad_inches=0.5,)


if __name__ == "__main__":
    test_obj = punctuationGlyph(
                     bases.circle,
                     base_kwargs=[],
                     line_fn=line_shapes.straight,
                     line_kwargs=[])

    commands = list(test_obj.glyph_list.keys())
    test_obj.demoprint(commands, 2,2)





