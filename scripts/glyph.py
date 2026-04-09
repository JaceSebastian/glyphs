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
    """unlike Spells, This is simply going to draw a glyph, given the literal information.
        The base class should never be used, instead the subclasses, with innate none and feature counts, will be implemented


    """
    
    def __init__(self,base_fn:Callable=bases.polygon,
                 line_fn:Callable = line_shapes.straight,
                 txt_file_base:str = r"./attribute_ordering/",
                 override_dict = {},
                 base_kwargs = [],
                 line_kwargs = [],
                 ignore_atts = False):
        self.atts = []
        self.base_fn = base_fn
        self.base_kwargs = base_kwargs
        self.line_fn = line_fn
        self.line_kwargs = line_kwargs
        
        self.class_number = 3
        self.attribute_number = 0

        self.class_name = ""
        self.class_names = ["Relativeizer", "Punctuation", "Recursion", "Deontic", "Logical", "Pronouns", "AFFIXES?", "SUBORDINATORS?","Numbers","Prepositions?","Adjectives/Adverbs?","Verbs","Syllabary","Nouns"]




        """This is where the information for each line is held."""
        #self.binary_array = np.zeros((self.n_att,self.class_number),dtype = int)

    def draw(self,annotate = False,
                show_all_paths = False,
                savename = "output.png",
                output_dpi = 200,
                axs = None,
                dot_color = 'none',
                cmap = 'summer',
                line_color = 'darkred',
                dot_size = 20,
                legend_fontsize = 10,
                legend_anchor = (1,0.75),
                show_name = False, glow=True):
            #print(f"Attribute num {self.attribute_number} shape {self.binary_array.shape[0]}")
            assert self.class_number == self.binary_array.shape[1]
            assert self.attribute_number == self.binary_array.shape[0]
            cmap = plt.get_cmap(cmap)
            x_vals,y_vals = self.base_fn(self.class_number,*self.base_kwargs)

            if axs is None:
                fig,axs = plt.subplots(1,1)
            else:
                fig = plt.gcf()
            axs.set_aspect('equal')
            
            #draw the points
            if annotate:
                dot_color = cmap(.3)
            halos = [
                (dot_size+4, 0.05),
                (dot_size+2, 0.12),
                (dot_size+1, 0.25)
            ]
            for w, a in halos:
                axs.scatter(
                    x_vals,
                    y_vals,
                    s=w,
                    color=dot_color,
                    alpha=a,
                    edgecolors='none',
                    zorder=2
                )

            # draw main dots
            axs.scatter(
                x_vals,
                y_vals,
                s=dot_size,
                color=dot_color,
                zorder=3
            )

            if show_all_paths:
                self.draw_all_paths(x_vals,y_vals,axs)

            for i in range(self.attribute_number):
                k = i + 1
                if annotate:
                    color = cmap(0.8*i/(self.attribute_number))
                    linewidth = 4- 3*i/self.attribute_number
                    dot_color
                else:
                    color = line_color
                    linewidth = 2
                labelled = False
                for j,elem in enumerate(self.binary_array[i]):
                    
                    if elem == 1:
                        #if element is 1
                        P = [x_vals[j],y_vals[j]]
                        Q = [x_vals[(j+k)%self.class_number],y_vals[(j+k)%self.class_number]]
                        line_x,line_y = self.line_fn(P,Q,*self.line_kwargs)
                        
                        if glow:
                
                        # layered halo
                            halos = [
                                (linewidth + 8, 0.05),  # widest, faintest
                                (linewidth + 5, 0.1),
                                (linewidth + 3, 0.2)
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
            #save_figure
            axs.set_axis_off()
            if show_name:
                axs.set_title(self.__name__)
            if savename is not None:
                plt.savefig(savename,dpi = output_dpi,bbox_inches = 'tight', transparent=True)
            elif axs is None:
                plt.show()
    
    def draw_all_paths(self,x_vals,y_vals,axs,all_ls = "--",all_c = 'k',all_alpha = 0.7,all_lw = 0.5):
        #loop for all k
        for k in range(1,self.attribute_number+1):
            for i in range(self.class_number):
                P = [x_vals[i],y_vals[i]]
                Q = [x_vals[(i+k)%self.class_number],y_vals[(i+k)%self.class_number]]
                line_x,line_y = self.line_fn(P,Q,*self.line_kwargs)
                axs.plot(line_x,line_y,
                        ls = all_ls,
                        color = all_c,
                        alpha = all_alpha,
                        lw = all_lw, zorder=4)
