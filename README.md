This is a modification of Gorilla of Destiny's repo for DnD spell writing, used for my own constructed language project centered around a theoretical language for demon summoning and binding contracts.

The conceit here is that demon summoning is possible, and the glyphs outlined in this project can be used to dictate a contract with a summoned demon. Noteably, demons are adversarial readers, who, much like Genies, will seek out loopholes to their summoner's detriment.

For now, to see all possible glyphs for a class, cd to glyphs folder, and run code like so
'''
$ python3 ./scripts/deonticGlyph.py
'''

For the stylus:
```
# defaults — clean output
python stylus.py --words NOM:5 ACC:5

python3 ./scripts/stylus.py --file ./stylusinput.txt  --savename stylusoutput.png --cell-size 1 --show-all-paths


# annotated, all paths shown, wider cells
python stylus.py --words NOM:5 ACC:5 --annotate --show-all-paths --cell-size 2.5

# save to file, 3 columns
python stylus.py --file input.txt  --cols 3
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


    