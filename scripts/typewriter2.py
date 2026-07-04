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
from ligatureGlyph import ligatureGlyph

# ── Class index ────────────────────────────────────────────────────────────────
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


def parse_spec(spec: str) -> tuple[str | list[tuple[str, int]], int]:
    spec = spec.strip()
    split_pos = None
    for i, ch in enumerate(spec):
        if ch == ":":
            split_pos = i
    if split_pos is None:
        raise ValueError(f"No class index found in spec '{spec}'.")
    body = spec[:split_pos].strip()
    class_index = int(spec[split_pos + 1:].strip())
    if body.startswith("[") and body.endswith("]"):
        inner = body[1:-1]
        tokens = [t.strip() for t in inner.split(",")]
        features = [parse_feature_token(t) for t in tokens if t]
        return features, class_index
    return body, class_index


def parse_ligature(spec: str) -> list[str]:
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
    specs = []
    with open("PreparedTexts/" + filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            specs.append(line)
    return specs


# ── Geometry helpers ───────────────────────────────────────────────────────────

def _get_world_points(obj, x_off: float, y_off: float, scale: float = 1.0):
    """Local polygon points scaled and translated into world space."""
    x_vals, y_vals = obj.base_fn(obj.num, *obj.base_kwargs)
    return (x_vals * scale) + x_off, (y_vals * scale) + y_off


def _right_anchor_world(obj, x_off: float, y_off: float,
                        scale: float = 1.0) -> tuple[float, float]:
    """Rightmost polygon point in world space."""
    x_vals, y_vals = _get_world_points(obj, x_off, y_off, scale)
    idx = np.argmax(x_vals)
    return float(x_vals[idx]), float(y_vals[idx])


def _left_anchor_local(obj, scale: float = 1.0) -> tuple[float, float]:
    """Leftmost polygon point in local space, respecting scale."""
    x_vals, y_vals = obj.base_fn(obj.num, *obj.base_kwargs)
    x_vals = x_vals * scale
    y_vals = y_vals * scale
    idx = np.argmin(x_vals)
    return float(x_vals[idx]), float(y_vals[idx])


# ── Drawing ────────────────────────────────────────────────────────────────────

def _draw_glyph(obj, ax, x_off: float, y_off: float,
                scale:      float = 1.0,
                line_color: str   = 'maroon',
                dot_color:  str   = 'maroon',
                dot_size:   float = 30,
                linewidth:  float = 2):
    """Render one glyph's points and chords directly onto ax."""
    x_vals, y_vals = _get_world_points(obj, x_off, y_off, scale)

    ax.scatter(x_vals, y_vals,
               s=dot_size, color=dot_color, zorder=2)

    for i in range(obj.attr_num):
        k = i + 1
        for j, elem in enumerate(obj.binary_array[i]):
            if elem == 1:
                P = [x_vals[j],                y_vals[j]]
                Q = [x_vals[(j + k) % obj.num], y_vals[(j + k) % obj.num]]
                line_x, line_y = obj.line_fn(P, Q, *obj.line_kwargs)
                ax.plot(line_x, line_y,
                        ls='-', lw=linewidth,
                        color=line_color, zorder=0)

    draw_all_paths(obj, x_vals, y_vals, ax)


def draw_all_paths(obj, x_vals, y_vals, axs,
                   all_ls='--', all_c='k', all_alpha=0.7, all_lw=0.5):
    for k in range(1, obj.attr_num + 1):
        for i in range(obj.num):
            P = [x_vals[i],               y_vals[i]]
            Q = [x_vals[(i + k) % obj.num], y_vals[(i + k) % obj.num]]
            line_x, line_y = obj.line_fn(P, Q, *obj.line_kwargs)
            axs.plot(line_x, line_y,
                     ls=all_ls, color=all_c,
                     alpha=all_alpha, lw=all_lw, zorder=4)


# ── Token ──────────────────────────────────────────────────────────────────────

class GlyphToken:
    __slots__ = ('obj', 'gloss', 'x_off', 'y_off', 'class_index')

    def __init__(self, obj, gloss: str,
                 x_off: float, y_off: float, class_index: int):
        self.obj         = obj
        self.gloss       = gloss
        self.x_off       = x_off
        self.y_off       = y_off
        self.class_index = class_index


# ── Layout ─────────────────────────────────────────────────────────────────────


def resolve_glyph(spec_str: str):
    """Build and return a ready-to-draw glyph object from a spec string."""
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


def build_tokens(spec_strings: list[str],
                 word_gap: float = 0.5,
                 scale:    float = 1.0) -> list[GlyphToken]:
    tokens:    list[GlyphToken] = []
    prev_tok   = None

    for spec_str in spec_strings:
        try:
            obj = resolve_glyph(spec_str)
        except (ValueError, KeyError) as e:
            print(f"Skipping '{spec_str}': {e}")
            continue

        gloss = obj.glossing

        if prev_tok is None:
            x_off, y_off = 0.0, 0.0
        else:
            rx, _ = _right_anchor_world(prev_tok.obj, prev_tok.x_off, prev_tok.y_off, scale)
            lx, _ = _left_anchor_local(obj, scale)
            x_off = rx + word_gap - lx
            y_off = 0.0

        tokens.append(GlyphToken(obj, gloss, x_off, y_off, 0))
        prev_tok = tokens[-1]

    return tokens




# ── Renderer ───────────────────────────────────────────────────────────────────

def render_typewriter(
    spec_strings : list[str],
    max_width    : float = 40.0,
    word_gap     : float = 0.5,
    line_height  : float = 3.5,
    gloss_offset : float = 1.8,
    gloss_size   : float = 7,
    scale        : float = 1.0,
    line_color   : str   = 'maroon',
    dot_color    : str   = 'maroon',
    dot_size     : float = 20,
    linewidth    : float = 2,
):
    # scale spatial parameters proportionally to glyph size
    scaled_gap          = word_gap    * scale
    scaled_line_height  = line_height * scale
    scaled_gloss_offset = gloss_offset * scale

    tokens = build_tokens(spec_strings, word_gap=scaled_gap, scale=scale)

    # ── Line-break pass ───────────────────────────────────────────────────────
    lines        : list[list[GlyphToken]] = []
    current_line : list[GlyphToken]       = []
    line_x_origin = 0.0

    for tok in tokens:
        rx, _ = _right_anchor_world(tok.obj, tok.x_off, tok.y_off, scale)
        extent = rx - line_x_origin

        if current_line and extent > max_width:
            lines.append(current_line)
            line_x_origin = tok.x_off
            current_line  = [tok]
        else:
            if not current_line:
                line_x_origin = tok.x_off
            current_line.append(tok)

    if current_line:
        lines.append(current_line)

    # ── Draw ──────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(
        1, 1,
        figsize=(max_width, scaled_line_height * len(lines))
    )
    ax.set_aspect('equal')
    ax.set_axis_off()

    for line_idx, line_tokens in enumerate(lines):
        y_shift = -line_idx * scaled_line_height
        x_shift = -line_tokens[0].x_off

        for tok in line_tokens:
            x_world = tok.x_off + x_shift
            y_world = tok.y_off + y_shift

            _draw_glyph(tok.obj, ax, x_world, y_world,
                        scale=scale,
                        line_color=line_color,
                        dot_color=dot_color,
                        dot_size=dot_size,
                        linewidth=linewidth)

            x_vals, _ = _get_world_points(tok.obj, x_world, y_world, scale)
            cx = (float(x_vals.min()) + float(x_vals.max())) / 2.0

            ax.text(cx, y_world - scaled_gloss_offset, tok.gloss,
                    ha='center', va='top',
                    fontsize=gloss_size, clip_on=False)

    plt.tight_layout()
    plt.show()


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Typewriter: render conlang glyphs as flowing text with ligatures."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--words", nargs="+", metavar="SPEC",
        help="One or more specs, e.g.  PA:11  '[p, long a]:11'  'PA:11+PB:11'"
    )
    source.add_argument(
        "--file", metavar="PATH",
        help="Path to a .txt file with one spec per line"
    )
    parser.add_argument("--n",            type=int,   default=None)
    parser.add_argument("--max-width",    type=float, default=22.0)
    parser.add_argument("--word-gap",     type=float, default=0.50)
    parser.add_argument("--line-height",  type=float, default=3.5)
    parser.add_argument("--gloss-offset", type=float, default=1.8)
    parser.add_argument("--gloss-size",   type=float, default=6.0)
    parser.add_argument("--scale",        type=float, default=0.5,
                        help="Uniform scale factor for glyph size (default: 1.0)")
    parser.add_argument("--line-color",   type=str,   default='maroon')
    parser.add_argument("--dot-color",    type=str,   default='maroon')
    parser.add_argument("--dot-size",     type=float, default=20.0)
    parser.add_argument("--linewidth",    type=float, default=2.0)
    parser.add_argument("--savename",     type=str,   default=None)

    args = parser.parse_args()

    specs = parse_file(args.file) if args.file else args.words
    if args.n:
        specs = specs[:args.n]

    render_typewriter(
        specs,
        max_width    = args.max_width,
        word_gap     = args.word_gap,
        line_height  = args.line_height,
        gloss_offset = args.gloss_offset,
        gloss_size   = args.gloss_size,
        scale        = args.scale,
        line_color   = args.line_color,
        dot_color    = args.dot_color,
        dot_size     = args.dot_size,
        linewidth    = args.linewidth,
    )


if __name__ == "__main__":
    main()