"""Goal here is to make a script that can take in the spell attributes
on the command line and output a png as required. Also useful if it can
return a spell class
"""
from spells import spell
import argparse
import line_shapes
import bases


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    #necessary ones

    parser.add_argument("-lvl","--level",help = "necessary input: level of the spell",
                        required = True)
    parser.add_argument("-sch","--school",help = "necessary input: school of the spell",
                        required = True)
    parser.add_argument("-dmg","--damagetype",help = "necessary input: damage type of spell",
                        required = True)
    parser.add_argument("-a","--aoe",help = "necessary input: AoE of the spell, format is `<shape> (<size>)` e.g. `cube (30)` CHECK THE TXT FILES IF YOU CAN'T FIND WHAT YOU'RE LOOKING FOR. ADD TO THE FILES IF WHAT YOU WANT ISN'T THERE (e.g. a new damage type, or a mix of the two)",
                        required = True)
    parser.add_argument("-ran","--range",help = "necessary input: range of the spell, format is `<size> <units>` e.g. `30 feet`. Also inlcudes one word versions like `Self`.",
                        required = True)
    parser.add_argument("-dur","--duration",help = "necessary input: duration of the spell, format is `<n> <units>` e.g. `1 hour`. Also inlcludes the `Up to...`",
                        required = True)
    
    #concentration and ritual
    parser.add_argument("-r","--ritual",help = "include if spell is ritual",action = "store_true")
    parser.add_argument("-c","--concentration",help = "include if spell is ritual",action = "store_true")

    #plot variables
    parser.add_argument("-spell_name",help = "Spell Name for Title",default = "Test")
    parser.add_argument("--savename",help = "Savename of plot",default = "output.png")
    parser.add_argument("--annotate",help = "Whether to annotate the spell dir",action = "store_true")
    parser.add_argument("--show_all_paths",help = "Whether to show all possible paths",action = "store_true")
    parser.add_argument("--save_dpi",help = "DPI to save image at",default = 200)
    parser.add_argument("--cmap",help = "Colour map to use for annotating",default = "summer")
    parser.add_argument("--dot_color",help = "Colour of the dots in the drawing",default = 'k')
    parser.add_argument("--line_color",help = "Colour of the lines (if not annotating)",default = 'darkred')


    #output options
    parser.add_argument("--format",choices=["svg", "png"],default="svg",help="output format is svg by default")
    
    
    args = parser.parse_args()
    spell_obj = spell(args)
    spell_obj.draw(args.annotate,
                   show_all_paths=args.show_all_paths,
                   savename = args.savename,output_dpi=int(args.save_dpi),
                   line_color = args.line_color,
                   dot_color = args.dot_color,
                   cmap = args.cmap,
                   show_name = True)


    
