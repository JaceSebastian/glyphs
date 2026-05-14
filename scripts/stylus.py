import argparse
import math
import ast
import matplotlib.pyplot as plt
from punctuationGlyph import punctuationGlyph
from appositionGlyph import appositionGlyph
from logicalGlyph import logicalGlyph
from deonticGlyph import deonticGlyph
from pronounGlyph import PronounGlyph
from sequiGlyph import sequiGlyph
from NumeralGlyph import NumeralGlyph
from adjGlyph import adjGlyph
from verbGlyph import verbGlyph
from syllabaryGlyph import syllableGlyph
from nounGlyph import nounGlyph
from morphemeGlyph import morphemeGlyph
from glyph import ligatureGlyph



# ── Hardcoded class index ──────────────────────────────────────────────────────
# Each entry: index → (GlyphClass, base_fn, base_kwargs, line_fn, line_kwargs)
CLASS_MAP = {
    1: punctuationGlyph,
    2: appositionGlyph,
    3: deonticGlyph,
    4: logicalGlyph,
    5: PronounGlyph,
    6: sequiGlyph,
    7: morphemeGlyph,
    8: NumeralGlyph,
    9: adjGlyph,
    10: verbGlyph,
    11: syllableGlyph,
    12: nounGlyph,
    #If I want to make non circular, should probably do something here? like 11l for line? 12: (PronounGlyph, bases.polygon, [], line_shapes.straight, []),
}


# ── Parsing ────────────────────────────────────────────────────────────────────

def parse_feature_token(token: str) -> tuple[str, int]:
    """
    Parse a single feature token into (feature, rotation).
    'long a'  → ('long a', 0)
    'p:1'     → ('p', 1)
    'long a:90' → ('long a', 90)
    """
    token = token.strip()
    if ":" in token:
        feat, rot = token.rsplit(":", 1)
        return feat.strip(), int(rot.strip())
    return token, 0


def parse_spec(spec: str) -> tuple[str | list[tuple[str, int]], int]:
    """
    Parse a single spec string into (lookup, class_index).

    Keyword:  'PA:11'            → ('PA', 11)
    Features: '[p, long a]:11'   → ([('p',0), ('long a',0)], 11)
    Mixed:    '[p:1, long a]:11' → ([('p',1), ('long a',0)], 11)
    """
    spec = spec.strip()

    # Split off the class index — always the last ':INT' not inside brackets
    # Find the last colon that's outside brackets
    depth = 0
    split_pos = None
    for i, ch in enumerate(spec):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif ch == ":" and depth == 0:
            split_pos = i  # keep updating — we want the LAST one

    if split_pos is None:
        raise ValueError(f"No class index found in spec '{spec}'. Expected format: 'LABEL:INT' or '[feat]:INT'")

    body = spec[:split_pos].strip()
    class_index = int(spec[split_pos + 1:].strip())

    if body.startswith("[") and body.endswith("]"):
        # Feature list
        inner = body[1:-1]  # strip brackets
        tokens = [t.strip() for t in inner.split(",")]
        features = [parse_feature_token(t) for t in tokens if t]
        return features, class_index
    else:
        # Keyword
        return body, class_index
    
def parse_ligature(spec: str) -> list[str]:
    """Split a ligature spec on '+' outside brackets."""
    parts = []
    depth = 0
    current = []
    for ch in spec:
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
        elif ch == '+' and depth == 0:
            parts.append(''.join(current).strip())
            current = []
            continue
        current.append(ch)
    parts.append(''.join(current).strip())
    return parts


def parse_file(filepath: str) -> list[str]:
    """Read a .txt file and return a list of spec strings, one per non-comment line."""
    specs = []
    with open("PreparedTexts/" +filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            specs.append(line)
    return specs


# ── Rendering ──────────────────────────────────────────────────────────────────

#def resolve_and_draw(spec_str: str, ax, draw_kwargs: dict, gap: float = 0.2):
def resolve_and_draw(spec_str: str, ax, draw_kwargs: dict):
    if '+' in spec_str:
        sub_specs = [parse_spec(s) for s in parse_ligature(spec_str)]
        obj = ligatureGlyph(sub_specs, CLASS_MAP)
        obj.build()
    else:
        lookup, class_index = parse_spec(spec_str)
        if class_index not in CLASS_MAP:
            raise ValueError(f"Class index {class_index} not in CLASS_MAP.")
        obj = CLASS_MAP[class_index]()
        obj._getBinaryArray(lookup)

    obj.draw(axs=ax, **draw_kwargs)
    glossing = obj.glossing
    obj._clear_binary()
    return glossing


def plot_glyphs(spec_strings: list[str], n: int | None = None,
                cols: int = 5, cell_size: float = 2.25, draw_kwargs: dict = {}):
    if n is not None:
        spec_strings = spec_strings[:n]

    count = len(spec_strings)
    cols = min(cols, count)
    rows = math.ceil(count / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(cols * cell_size, rows * cell_size))
    axes = axes.flatten() if count > 1 else [axes]

    for i, spec_str in enumerate(spec_strings):
        try:
            label = resolve_and_draw(spec_str, axes[i], draw_kwargs)
            fig_width_inches = fig.get_size_inches()[0]
            ax_width_inches = axes[i].get_position().width * fig_width_inches
            fontsize = ax_width_inches * 10
            fontsize = max(fontsize, 8)  # minimum font size of 8
            axes[i].set_title(label, pad=-6, y=-0.1, fontsize=fontsize)
        except (ValueError, KeyError) as e:
            print(f"Skipping '{spec_str}': {e} because of {spec_str}.")
            axes[i].set_visible(False)

    for j in range(count, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.show()

# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Typewriter: render conlang glyphs from labels or feature lists."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--words", nargs="+", metavar="SPEC",
        help="One or more specs, e.g.  PA:11  '[p, long a]:11'  '[p:1, long a]:11'"
    )
    source.add_argument(
        "--file", metavar="PATH",
        help="Path to a .txt file with one spec per line"
    )
    parser.add_argument(
        "--n", type=int, default=None,
        help="Max number of glyphs to render"
    )

        # draw() passthrough args
    parser.add_argument("--annotate",       action="store_true", default=False)
    parser.add_argument("--show-all-paths", action="store_true", default=True)
    parser.add_argument("--show-name",      action="store_true", default=False)
    parser.add_argument("--savename",       type=str,            default=None)
    parser.add_argument("--cell-size",      type=float,          default=1.25)
    parser.add_argument("--cols",           type=int,            default=7)

    args = parser.parse_args()

    draw_kwargs = {
        "annotate":       args.annotate,
        "show_all_paths": args.show_all_paths,
        "show_name":      args.show_name,
        "savename":       args.savename,
    }


    if args.file:
        specs = parse_file(args.file)
    else:
        specs = args.words

    plot_glyphs(specs, n=args.n, cols=args.cols,
                cell_size=args.cell_size, draw_kwargs=draw_kwargs)


if __name__ == "__main__":
    main()