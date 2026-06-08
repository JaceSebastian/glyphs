import argparse
import math
import numpy as np
import matplotlib.pyplot as plt

from scripts.punctuationGlyph import punctuationGlyph
from scripts.appositionGlyph import appositionGlyph
from scripts.logicalGlyph import logicalGlyph
from scripts.deonticGlyph import deonticGlyph
from scripts.pronounGlyph import PronounGlyph
from scripts.sequiGlyph import sequiGlyph
from scripts.morphemeGlyph import morphemeGlyph
from scripts.NumeralGlyph import NumeralGlyph
from scripts.adjGlyph import adjGlyph
from scripts.verbGlyph import verbGlyph
from scripts.syllabaryGlyph import syllableGlyph
from scripts.nounGlyph import nounGlyph
from ligatureGlyph import ligatureGlyph

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

# ── Parsing ────────────────────────────────────────────────────────────────────

def parse_feature_token(token: str) -> tuple[str, int]:
    token = token.strip()
    if ":" in token:
        feat, rot = token.rsplit(":", 1)
        return feat.strip(), int(rot.strip())
    return token, 0


def parse_spec(spec: str) -> tuple:
    spec = spec.strip()
    split_pos = max(i for i, ch in enumerate(spec) if ch == ":")
    body = spec[:split_pos].strip()
    class_index = int(spec[split_pos + 1:].strip())
    if body.startswith("[") and body.endswith("]"):
        tokens = [t.strip() for t in body[1:-1].split(",")]
        return [parse_feature_token(t) for t in tokens if t], class_index
    return body, class_index


def parse_ligature(spec: str) -> list[str]:
    parts, current, depth = [], [], 0
    for ch in spec:
        if ch == '[':   depth += 1
        elif ch == ']': depth -= 1
        elif ch == '+' and depth == 0:
            parts.append(''.join(current).strip())
            current = []
            continue
        current.append(ch)
    parts.append(''.join(current).strip())
    return parts


def parse_file(filepath: str) -> list[str]:
    with open("PreparedTexts/" + filepath) as f:
        return [l.strip() for l in f if l.strip() and not l.lstrip().startswith("#")]


def resolve_glyph(spec_str: str):
    """Build and return a ready-to-draw glyph or ligatureGlyph from a spec string."""
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
    return obj


# ── Rendering ──────────────────────────────────────────────────────────────────

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
    # ── Build glyph objects ───────────────────────────────────────────────────
    glyphs = []
    for spec_str in spec_strings:
        try:
            obj = resolve_glyph(spec_str)
            glyphs.append((obj, obj.glossing))
        except (ValueError, KeyError) as e:
            print(f"Skipping '{spec_str}': {e}")

    # ── Compute x offsets using anchors ───────────────────────────────────────
    positions = []   # (x_off, y_off) per glyph
    x_cursor  = 0.0

    for obj, _ in glyphs:
        lx, _ = obj.left_anchor()
        x_off  = x_cursor - lx * scale
        rx, _  = obj.right_anchor()
        x_cursor = x_off + rx * scale + word_gap
        positions.append((x_off, 0.0))

    # ── Line-break pass ───────────────────────────────────────────────────────
    lines         = []   # list of list of (obj, gloss, x_off, y_off)
    current_line  = []
    line_x_origin = positions[0][0] if positions else 0.0

    for (obj, gloss), (x_off, y_off) in zip(glyphs, positions):
        rx, _ = obj.right_anchor()
        extent = x_off + rx * scale - line_x_origin

        if current_line and extent > max_width:
            lines.append(current_line)
            shift         = x_off
            line_x_origin = x_off
            current_line  = [(obj, gloss, x_off, y_off)]
        else:
            if not current_line:
                line_x_origin = x_off
            current_line.append((obj, gloss, x_off, y_off))

    if current_line:
        lines.append(current_line)

    # ── Draw ──────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(
        1, 1,
        figsize=(max_width, line_height * scale * len(lines))
    )
    ax.set_aspect('equal')
    ax.set_axis_off()

    for line_idx, line_tokens in enumerate(lines):
        y_shift = -line_idx * line_height * scale
        x_shift = -line_tokens[0][2]   # normalise line to start at x=0

        for obj, gloss, x_off, y_off in line_tokens:
            #the line is not properly offsetting by number of glyphs in ligature
            x_world = (x_off + x_shift)
            y_world = y_off + y_shift

            obj.draw_offset(axs=ax,
                     x_offset=x_world, y_offset=y_world,
                     **draw_kwargs)

            lx, _ = obj.left_anchor()
            rx, _ = obj.right_anchor()
            cx = x_world + (lx + rx) / 2 * scale

            ax.text(cx, y_world - gloss_offset * scale, gloss,
                    ha='center', va='top',
                    fontsize=gloss_size, clip_on=False)

            obj._clear_binary()

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