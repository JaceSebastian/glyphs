# Writing Spells in D&D

The goal of this is to make a more robust package for my spellwriting system (detailed [here](https://www.drivethrurpg.com/en/product/429711/the-spell-writing-guide), though it has updated now)

There are a few main files worth exploring. I'll add a quick explainer for how to write spells easily here then more detail about the files involved after this. I'm aware that this might attract a few people that have never used coding before so I'll try add some more information about the basics than I normally might.


## Python Setup
In order to use this you need a working python installation on the machine you want to run this (I've never had a good experience installing python but [This guide](https://realpython.com/installing-python/) is pretty comprehensive). You will also need a few python packages installed (I recommend pip ([guide](https://packaging.python.org/en/latest/tutorials/installing-packages/)))

With that you can install the required files by running in the same place you have installed this git repo.

```
pip install -r requirements.txt
```

Though if I'm being totally honest, you really only need matplotlib and nump, tqdm can be removed if you want, I just like a loading bar.

## Writing Spells (scripts/quill.py)

The current most usable part of the repo is `quill.py`. This is a python file that will allow you to write spells using the attributes found in `attribute_ordering/`.

To use, you simply type the following (with the actual values you want replacing something like "<input_value>"):

`python .\scripts\quill.py -lvl <level> -sch <school> -dmg <damage type> -a "<area of effect>" -ran "<range>" -dur "<duration>"`

adding a `-c` for a concentration spell, and `r` for a ritual spell. The reason for the inverted commas is because a lot of things (e.g. the spell range and AoE) tend to have a space which confuses the running in terminal. By enclosing it within inverted commas, it understands even if there is a space.

`python .\scripts\quill.py -h` to see the full list of arguments.

## The Spell Object(scripts/spells.py)

For a few projects of mine it might be useful to have a spell object that I can reference for all the info I need. `spells.py` contains the real workhorse stuff that I need (and so is the class that will likely update the most as time goes on).

The `spell` object takes another object as input which has all the spell attributes (e.g. level, dtype, aoe, etc.). From this, it can then derive the binary information required and then be used for plotting. In future I want it to be able to return things like the "aspects" of later theories, dictionaries for use, and a more complex array that can be useful in some plotting schemes. For now though, it's relatively bare bones. An example of how it might be used is shown at the end of spells.py with a custom spell input object. This is especially useful if (like me) you have all the spell data downloaded and so instead of hard-coding things, you can use this in your other programmes.

```python

test_inp = custom_spell_input(3,"evocation",
                                "fire","sphere (20)",
                                "150 feet","Instantaneous")
test_obj = spell(test_inp,
                    bases.polygon,
                    base_kwargs = [],
                    line_fn = line_shapes.straight,
                    line_kwargs = [])
test_obj.draw(savename = None,show_all_paths=True,annotate=False,
                show_name=True)
```

## Drawing Modules (bases.py and line_shapes.py)

In `bases.py` and `line_shapes.py` you can find the fundamental functions for drawing our spells. 

The "bases" are the arangment of our dots, the "lines" are the lines connecting said dots. See the individual functions for their use.

## Deriving Rotationally Asymmetric Binary Numbers

Thanks to Ernesti from the Theory of Magic discord server we now have an ultra-fast method to generate these binary numbers so all credit to them. The code for this can be found in `necklaces.py` alongside some of my own experiments. If you ever have to touch that file I recommend just using the `default_generation` function as that just calls whatever the current best is. Consider it an open challenge for the especially nerdy to improve upon what is shown.


# TODO

There's a few things I want to add to this that should make life easier

- [ ] add base and line changing to quill.py argparse
- [ ] add a dict returner to spell class
- [ ] a spell json so that the attributes can be loaded (i.e. you could run `writer.py -<spell_name>` and get the output)

- [ ] Functions for outputting the two parsable methods, one is the connections array and the other is the more standard binary string method
    - I will add some detail about these but basically the connections array is a NxN array that has elements $N_{i,j}$. If points $i$ and $j$ are connected then element $N_{i,j}$ is 1, if not its 0. This is really useful for some things like encription and graph making so it's a useful form of the spell.
- [ ] Compatibility with non-wizard systems too, or at least indications on how to use it