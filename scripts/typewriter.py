import argparse
import math
import numpy as np
import matplotlib.pyplot as plt

from punctuationGlyph import punctuationGlyph
from appositionGlyph import appositionGlyph
from logicalGlyph import logicalGlyph
from deonticGlyph import deonticGlyph
from pronounGlyph import PronounGlyph
from sequiGlyph import sequiGlyph
from morphemeGlyph import morphemeGlyph
from NumeralGlyph import NumeralGlyph
from adjGlyph import adjGlyph
from verbGlyph import verbGlyph
from syllabaryGlyph import syllableGlyph
from nounGlyph import nounGlyph


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
}

LIGATURE_SPACING = 0.075

# ── Parsing ────────────────────────────────────────────────────────────────────

def parse_feature_token(token: str) -> tuple[str, int]:
    token = token.strip()
    if ":" in token:
        feat, rot = token.rsplit(":", 1)
        return feat.strip(), int(rot.strip())
    return token, 0


def OLDparse_spec(spec: str) -> tuple:
    spec = spec.strip()
    split_pos = max(i for i, ch in enumerate(spec) if ch == ":")
    body = spec[:split_pos].strip()
    class_index = int(spec[split_pos + 1:].strip())
    if body.startswith("[") and body.endswith("]"):
        tokens = [t.strip() for t in body[1:-1].split(",")]
        return [parse_feature_token(t) for t in tokens if t], class_index
    return body, class_index

def parse_spec(spec: str) -> tuple:
    spec = spec.strip()
    split_pos = max(i for i, ch in enumerate(spec) if ch == ":")
    body = spec[:split_pos].strip()
    class_index = int(spec[split_pos + 1:].strip())
    if body.startswith("[") and body.endswith("]"):
        tokens = [t.strip() for t in body[1:-1].split(",")]
        return [parse_feature_token(t) for t in tokens if t], class_index
    return body, class_index

def parse_file(filepath: str) -> list[str]:
    with open("PreparedTexts/" + filepath) as f:
        return [l.strip() for l in f if l.strip() and not l.lstrip().startswith("#")]


def resolve_glyph(spec_str: str) -> list:
    """Returns a list of glyph objects: one element for a plain spec,
    multiple for a '+'-joined ligature spec. No depth-aware splitting —
    '+' is always a separator."""
    if '+' in spec_str:
        parts = []
        for s in spec_str.split('+'):
            lookup, class_index = parse_spec(s)
            obj = CLASS_MAP[class_index]()
            obj._getBinaryArray(lookup)
            parts.append(obj)
        return parts
    else:
        lookup, class_index = parse_spec(spec_str)
        obj = CLASS_MAP[class_index]()
        obj._getBinaryArray(lookup)
        return [obj]
    

    

# ── Rendering ──────────────────────────────────────────────────────────────────

def wordWidth(parts, scale):

    width = 0

    for part in parts:

        width += (
            part.getRightAnchor()[0]
            - part.getLeftAnchor()[0]
        ) * scale

    return width

def render_typewriter(
    spec_strings : list[str],
    max_width    : float = 22.0,
    word_gap     : float = 0.5,
    line_height  : float = 3.5,
    gloss_offset : float = 1.8,
    gloss_size   : float = 6.0,
    scale        : float = 0.5,
    draw_kwargs  : dict  = {},
):
# ── Build groups ───────────────────────────────────────────────────────────
    groups = []   # list of (parts, gloss) where parts is a list of glyph objs
    for spec_str in spec_strings:
        try:
            parts = resolve_glyph(spec_str)
            gloss = "+".join(p.glossing for p in parts)
            groups.append((parts, gloss))
        except (ValueError, KeyError) as e:
            print(f"Skipping '{spec_str}': {e}")

    layouts = []

    cursor_x = 0
    cursor_y = 0

    for parts, gloss in groups:

        width = wordWidth(parts, scale)

        if cursor_x > 0 and cursor_x + width > max_width:
            cursor_x = 0
            cursor_y -= line_height * scale

        #word_start = cursor_x
        word_start = cursor_x + parts[0].getLeftAnchor()[0] * scale

        glyph_positions = []

        for i, part in enumerate(parts):

            glyph_positions.append(
                (part, cursor_x, cursor_y)
            )

            advance = (
                part.getRightAnchor()[0]
                - part.getLeftAnchor()[0]
            )

            cursor_x += advance * scale + LIGATURE_SPACING

        word_end = cursor_x

        layouts.append(
            (
                gloss,
                glyph_positions,
                word_start,
                word_end,
                cursor_y
            )
        )

        cursor_x += word_gap * scale

    # ── Draw ──────────────────────────────────────────────────────────────────
    line_ys = sorted({layout[4] for layout in layouts}, reverse=True)
    num_lines = max(1, len(line_ys))
    fig, ax = plt.subplots(
        1, 1,
        figsize=(max_width, line_height * scale * num_lines)
    )
    ax.set_aspect('equal')
    ax.set_axis_off()

    for gloss, glyph_positions, word_start, word_end, baseline_y in layouts:

        for part, x, y in glyph_positions:

            part.draw_offset(
                axs=ax,
                x_offset=x,
                y_offset=y,
                **draw_kwargs
            )

            """This part draws anchor points"""
            # rx, ry = part.getRightAnchor()

            # ax.plot(
            #     x + rx*scale,
            #     y + ry*scale,
            #     'o',
            #     color='blue',
            #     markersize=5
            # )
            # rx, ry = part.getLeftAnchor()

            # ax.plot(
            #     x + rx*scale,
            #     y + ry*scale,
            #     'o',
            #     color='red',
            #     markersize=5
            # )

            part._clear_binary()

        center = (word_start + word_end -word_gap)/2

        ax.text(
            center,
            y - gloss_offset*scale,
            gloss,
            ha='center',
            va='top',
            fontsize=gloss_size
        )

    plt.tight_layout()
    plt.show()


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Typewriter: render conlang glyphs as flowing text with glosses."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--words", nargs="+", metavar="SPEC")
    source.add_argument("--file",  metavar="PATH")

    parser.add_argument("--n",            type=int,   default=None)
    parser.add_argument("--max-width",    type=float, default=15.0)
    parser.add_argument("--word-gap",     type=float, default=0.5)
    parser.add_argument("--line-height",  type=float, default=3.5)
    parser.add_argument("--gloss-offset", type=float, default=1.8)
    parser.add_argument("--gloss-size",   type=float, default=6.0)
    parser.add_argument("--scale",        type=float, default=1.1)
    parser.add_argument("--glow",         action="store_true", default=False)
    parser.add_argument("--show-all-paths", action="store_true", default=True)
    parser.add_argument("--color",        type=str,   default="maroon")
    parser.add_argument("--savename",     type=str,   default=None)

    args = parser.parse_args()

    specs = parse_file(args.file) if args.file else args.words
    if args.n:
        specs = specs[:args.n]

    draw_kwargs = {
        "glow":           args.glow,
        "show_all_paths": args.show_all_paths,
        "line_color":     args.color,
        "savename":       None,
        "scale":          args.scale,
    }

    render_typewriter(
        specs,
        max_width    = args.max_width,
        word_gap     = args.word_gap,
        line_height  = args.line_height,
        gloss_offset = args.gloss_offset,
        gloss_size   = args.gloss_size,
        scale        = args.scale,
        draw_kwargs  = draw_kwargs,
    )


if __name__ == "__main__":
    main()