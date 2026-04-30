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
        
        self.num = 0
        self.attr_num = 0
        self.text_file_base:str = r"./GlyphTables/"
        """This is where the information for each line is held."""
        self.binary_array = np.zeros((self.attr_num,self.num),dtype = int)
        self.attributes = []#Not sure if this is ever used
        self.glyph_list= {}
        self.feature_list={}
        self.encodings = {}
        self.glossing = "Gloss Default"

    def demoprint(self, printList, cols=None, Flip=False, cell_size=1.5, save=False, 
              savename="demoprint.png", draw_kwargs={}):
        commands = printList
        
        n = len(commands)
        if (cols == None):
            cols = math.ceil(math.sqrt(n))
        else:
            cols = min(cols, n)
        rows = math.ceil(n / cols)

        fig, axes = plt.subplots(rows, cols, figsize=(cols * cell_size, rows * cell_size))
        axes = np.array(axes).flatten() if n > 1 else [axes]

        for i, word in enumerate(commands):
            self.binary_array = self._getBinaryArray(word)

            if Flip:
                r = i % rows
                c = i // rows
                idx = r * cols + c
            else:
                idx = i

            self.draw(savename=None, show_all_paths=True, annotate=False,show_name=False, axs=axes[idx], **draw_kwargs)
            #self.draw(savename=None, show_all_paths=True, annotate=False,show_name=False, axs=axes[i], **draw_kwargs)
            
            fig_width_inches = fig.get_size_inches()[0]
            ax_width_inches = axes[i].get_position().width * fig_width_inches
            fontsize = ax_width_inches * 10
            fontsize = max(fontsize, 8)  # minimum font size of 8
            axes[i].set_title(word, pad=-6, y=-0.1, fontsize=fontsize)
            pos = axes[i].get_position()
            # fig.text(pos.x0 + pos.width/2, pos.y0 - 0.02, 
            #      word.capitalize(),
            #      ha='center', va='top',
            #      fontsize=cell_size * 4)
            self._clear_binary()

        for j in range(n, len(axes)):
            axes[j].set_visible(False)

        plt.tight_layout(rect=[0, 0.05, 1, 1])
        
        if save:
            plt.savefig(savename, dpi=200, bbox_inches='tight', transparent=True)
        else:
            plt.show()
    
    def _clear_binary(self):
        self.glossing = ""
        self.binary_array = np.zeros((self.attr_num,self.num),dtype = int)
    
    def rotateGlyph(self, binary_encoding, rotation):
        if rotation == 0: return binary_encoding
        #encoding is a list of lists
        for i in range(len(binary_encoding)):
            if np.any(binary_encoding[i]):
                binary_encoding[i] = np.roll(binary_encoding[i], rotation)
        return binary_encoding
    
    def _getBinaryArray(self, word):
        self.glossing = word
        if(word not in self.glyph_list):
            raise KeyError("Not a Valid Glyph")
        for feature_name, rotation in self.glyph_list[word]:
                fencoding = np.array(self.encodings[feature_name]).reshape(self.attr_num, self.num)
                fencoding = self.rotateGlyph(fencoding, rotation) 
                self.binary_array = np.bitwise_or(self.binary_array, fencoding)
        return self.binary_array
    
    def _makeGlossing(self, det=None, root="", case=None):
        """This should always be overwritten for glyph class"""
        self.glossing = root
    
    def left_anchor(self, parity=0) -> tuple[float, float]:
        """Point where an incoming glyph connects to me."""
        x_vals, y_vals = self.base_fn(self.num, *self.base_kwargs)
        if len(x_vals) == 0:
            raise ValueError(
                f"{self.__class__.__name__}.right_anchor(): base_fn returned empty arrays"
            )
        
        idx = np.argmin(x_vals)
        return (float(x_vals[idx]), float(y_vals[idx]))

    def right_anchor(self, parity=0) -> tuple[float, float]:
        """Point where I connect to an outgoing glyph."""
        x_vals, y_vals = self.base_fn(self.num, *self.base_kwargs)
    
        if len(x_vals) == 0:
            raise ValueError(
                f"{self.__class__.__name__}.right_anchor(): base_fn returned empty arrays"
            )
        
        idx = np.argmax(x_vals)
        return (float(x_vals[idx]), float(y_vals[idx]))

    def join_to(self, other):
        """Left Side glyph's right anchor attaches to left anchor of other glyph.
        Override to allow for line alinements to avoid confusion or overlap."""

        raise NotImplementedError
      
    
    def draw(self,annotate = False,
                show_all_paths = False,
                savename = "output.png",
                output_dpi = 200,
                axs = None,
                dot_color = 'maroon',
                cmap = 'summer',
                line_color = 'maroon',
                dot_size = 30,
                legend_fontsize = 8,
                legend_anchor = (1,0.75),
                show_name = False):
            #print(f"Attribute num {self.attr_num} shape {self.binary_array.shape[0]}")
            assert self.num == self.binary_array.shape[1]
            assert self.attr_num== self.binary_array.shape[0]
            cmap = plt.get_cmap(cmap)
            if self.num:
                dot_size = max(dot_size/(self.num/4), 10)
            x_vals,y_vals = self.base_fn(self.num,*self.base_kwargs)

            if axs is None:
                fig,axs = plt.subplots(1,1)
            else:
                fig = plt.gcf()
            axs.set_aspect('equal')
            axs.margins(0.1)
            
            #draw the points
            if annotate:
                dot_color = cmap(.3)
                
                halos = [
                    (dot_size+3, 0.05),
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
                zorder=2
            )

            if show_all_paths:
                self.draw_all_paths(x_vals,y_vals,axs)

            for i in range(self.attr_num):
                k = i+1
                if annotate:
                    color = cmap(0.8*i/(self.attr_num))
                    linewidth = 4- 3*i/self.attr_num
                    dot_color
                else:
                    color = line_color
                    linewidth = 2
                labelled = False
                for j,elem in enumerate(self.binary_array[i]):
                    
                    if elem == 1:
                        #if element is 1
                        P = [x_vals[j],y_vals[j]]
                        Q = [x_vals[(j+k)%self.num],y_vals[(j+k)%self.num]]
                        line_x,line_y = self.line_fn(P,Q,*self.line_kwargs)
                        
                        if annotate:
                
                        # layered halo
                            halos = [
                                (linewidth + 5, 0.05),  # widest, faintest
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
            #save_figure
            axs.set_axis_off()
            if show_name:
                axs.set_title(self.__name__)
            if savename is not None:
                plt.savefig(savename,dpi = output_dpi,bbox_inches = 'tight', pad_inches=0.5, transparent=True)
            elif axs is None:
                plt.show(transparent=True, pad_inches=0.5,)
    
    def draw_all_paths(self,x_vals,y_vals,axs,all_ls = "--",all_c = 'k',all_alpha = 0.7,all_lw = 0.5):
        #loop for all k
        for k in range(1,self.attr_num+1):
            for i in range(self.num):
                P = [x_vals[i],y_vals[i]]
                Q = [x_vals[(i+k)%self.num],y_vals[(i+k)%self.num]]
                line_x,line_y = self.line_fn(P,Q,*self.line_kwargs)
                axs.plot(line_x,line_y,
                        ls = all_ls,
                        color = all_c,
                        alpha = all_alpha,
                        lw = all_lw, zorder=4)
