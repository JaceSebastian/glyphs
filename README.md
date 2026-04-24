This is a modification of Gorilla of Destiny's repo for DnD spell writing, used for my own constructed language project centered around a theoretical language for demon summoning and binding contracts.

For now, to see all possible glyphs for a class, cd to glyphs folder, and run code like so
'''
$ python3 ./scripts/deonticGlyph.py
'''

For the stylus:
```
# defaults — clean output
python stylus.py --words NOM:5 ACC:5

# annotated, all paths shown, wider cells
python stylus.py --words NOM:5 ACC:5 --annotate --show-all-paths --cell-size 2.5

# save to file, 3 columns
python stylus.py --file input.txt --savename output.png --cols 3
```

A rough correspondence for glyphs:
 Classes -> Shape
    Cartouche -> Circle (used to partion off spelled out proper names)
    Punctuation -> Dot 
    Recursion -> Line/brackets
    Deontic Logic -> Triangle
    Logical Operators -> Square
    Pronouns -> Pentagon
    Prepositions? -> Hexagon
    Suordinating? -> Septagon
    Numerals -> Octogon
    Morphemes/affixes -> Nonagon
    AdjP -> Decagon
    Syllabary -> Hendecagon
    Verb -> Dodecagon   
    Nouns/Determiner Phrases-> Triskaidecagon