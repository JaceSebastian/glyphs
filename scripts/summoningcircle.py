import argparse
import math
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import numpy as np

from scripts.Classes.punctuationGlyph import punctuationGlyph
from scripts.Classes.appositionGlyph import appositionGlyph
from scripts.Classes.logicalGlyph import logicalGlyph
from scripts.Classes.deonticGlyph import deonticGlyph
from scripts.Classes.pronounGlyph import PronounGlyph
from scripts.Classes.sequiGlyph import sequiGlyph
from scripts.Classes.NumeralGlyph import NumeralGlyph
from scripts.Classes.adjGlyph import adjGlyph
from scripts.Classes.verbGlyph import verbGlyph
from scripts.Classes.syllabaryGlyph import syllableGlyph
from scripts.Classes.nounGlyph import nounGlyph
from scripts.Classes.morphemeGlyph import morphemeGlyph


# ── Hardcoded class index ──────────────────────────────────────────────────────
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
    depth = 0
    split_pos = None
    for i, ch in enumerate(spec):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif ch == ":" and depth == 0:
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
    else:
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


# ── Rendering ──────────────────────────────────────────────────────────────────

def resolve_and_draw(spec_str: str, ax, draw_kwargs: dict):
    parts = parse_ligature(spec_str)
    label_parts = []
    prev_obj = None
    x_offset = 0.0

    for i, part in enumerate(parts):
        lookup, class_index = parse_spec(part)
        if class_index not in CLASS_MAP:
            raise ValueError(f"Class index {class_index} not in CLASS_MAP.")

        obj = CLASS_MAP[class_index]()

        if (prev_obj is None) or type(obj) != type(prev_obj):
            x_offset = 0.0
            y_offset = 0.0
        else:
            rx, ry = prev_obj.right_anchor(parity=(i - 1) % 2)
            lx, ly = obj.left_anchor(parity=i % 2)
            x_offset = rx - lx

        original_base_fn = obj.base_fn
        obj.base_fn = lambda n, *args, _fn=original_base_fn, _x=x_offset, _y=y_offset: (
            _fn(n, *args)[0] + _x,
            _fn(n, *args)[1] + _y
        )

        obj._getBinaryArray(lookup)
        obj.draw(axs=ax, **draw_kwargs)
        label_parts.append(obj.glossing)
        obj._clear_binary()

        prev_obj = obj

    return ' '.join(label_parts)


# ── Summoning Circle Layout ────────────────────────────────────────────────────

def _collect_new_artists(ax, before_lines, before_patches, before_collections):
    """
    Return all artists added to ax since the before-snapshots were taken.
    Covers Line2D, Patch, and Collection — the three types glyph draw() methods
    are most likely to produce.
    """
    new_artists = []
    new_artists += [a for a in ax.lines       if a not in before_lines]
    new_artists += [a for a in ax.patches     if a not in before_patches]
    new_artists += [a for a in ax.collections if a not in before_collections]
    return new_artists


def _apply_transform_to_artists(artists, angle_rad: float, cx: float, cy: float,
                                 glyph_scale: float, orient: bool, ax):
    """
    For each artist, prepend an Affine2D that:
      1. Scales the glyph uniformly around the origin.
      2. Optionally rotates it so its 'up' direction points away from the
         ring centre (orient=True), or leaves it upright (orient=False).
      3. Translates it to (cx, cy) in data coordinates.

    The artist's existing transform is kept as the *outer* transform so that
    the data → display mapping still works correctly.
    """
    rotation_deg = math.degrees(angle_rad) if orient else 0.0

    affine = (
        mtransforms.Affine2D()
        .scale(glyph_scale)
        .rotate_deg(rotation_deg)
        .translate(cx, cy)
    )

    for artist in artists:
        # Prepend our affine to whatever transform the artist already has.
        # For most matplotlib artists the base transform is ax.transData.
        existing = artist.get_transform()
        artist.set_transform(affine + existing)


def plot_glyphs_circle(
    spec_strings: list[str],
    rings: list[int],
    *,
    ring_radii: list[float] | None = None,
    ring_spacing: float = 2.5,
    glyph_scale: float = 0.8,
    orient: bool = True,
    draw_decorative_rings: bool = True,
    show_glossing: bool = False,
    gloss_offset: float = 0.4,
    gloss_fontsize: float = 7.0,
    draw_kwargs: dict = {},
    figsize: float = 10.0,
):
    """
    Render glyphs arranged on concentric rings (a summoning circle).

    Parameters
    ----------
    spec_strings      : flat list of glyph specs, filled ring-by-ring inward→outward.
    rings             : list of ints, number of glyphs on each ring (index 0 = innermost).
                        e.g. [1, 6, 12]
    ring_radii        : explicit radii for each ring; if None, spaced by ring_spacing.
    ring_spacing      : distance between successive rings when radii are auto-computed.
    glyph_scale       : uniform scale applied to every glyph before placement.
    orient            : if True, rotate each glyph so it faces outward from the centre.
    draw_decorative_rings : if True, draw faint circles tracing each ring.
    show_glossing     : if True, draw the gloss label near each glyph.
    gloss_offset      : how far beyond the glyph centre the label is placed, in data units.
    gloss_fontsize    : font size for gloss labels.
    draw_kwargs       : forwarded to resolve_and_draw / obj.draw().
    figsize           : figure side length in inches (figure is square).
    """

    # ── 1. Validate / build radii ──────────────────────────────────────────────
    if ring_radii is not None:
        if len(ring_radii) != len(rings):
            raise ValueError("ring_radii must have the same length as rings.")
        radii = ring_radii
    else:
        # innermost ring gets radius ring_spacing; each subsequent ring adds ring_spacing
        radii = [(i + 1) * ring_spacing for i in range(len(rings))]

    # ── 2. Figure / axes setup ─────────────────────────────────────────────────
    max_r = max(radii) + ring_spacing          # a little breathing room at the edge
    fig, ax = plt.subplots(figsize=(figsize, figsize))
    ax.set_aspect("equal")
    ax.set_xlim(-max_r, max_r)
    ax.set_ylim(-max_r, max_r)
    ax.axis("off")

    # ── 3. Optional decorative ring circles ───────────────────────────────────
    if draw_decorative_rings:
        for r in radii:
            circle = plt.Circle(
                (0, 0), r,
                color="gray", fill=False, linewidth=0.6, linestyle="--", alpha=0.4,
                transform=ax.transData, zorder=0,
            )
            ax.add_patch(circle)

    # ── 4. Place glyphs ───────────────────────────────────────────────────────
    spec_iter = iter(spec_strings)
    labels = []

    for ring_idx, (n_glyphs, radius) in enumerate(zip(rings, radii)):
        for glyph_idx in range(n_glyphs):
            spec_str = next(spec_iter, None)
            if spec_str is None:
                break                          # fewer specs than ring slots — stop

            # Angle: distribute evenly; offset alternate rings by half a step
            # so glyphs don't stack radially.
            offset = (math.pi / n_glyphs) if (ring_idx % 2 == 1) else 0.0
            theta = (2 * math.pi * glyph_idx / n_glyphs) + offset

            cx = radius * math.cos(theta)
            cy = radius * math.sin(theta)

            # Snapshot existing artists before drawing
            before_lines       = list(ax.lines)
            before_patches     = list(ax.patches)
            before_collections = list(ax.collections)

            try:
                # Draw the glyph at the origin in local coordinates
                label = resolve_and_draw(spec_str, ax, draw_kwargs)
                labels.append(label)
            except (ValueError, KeyError) as e:
                print(f"Skipping '{spec_str}': {e}")
                continue

            # Collect everything that was just added
            new_artists = _collect_new_artists(
                ax, before_lines, before_patches, before_collections
            )

            # Shift + rotate those artists into their ring position
            # angle for orient: theta points outward from centre, so glyph
            # 'up' should align with theta; add 90° so the glyph top faces out.
            orient_angle = theta + math.pi / 2 if orient else 0.0

            _apply_transform_to_artists(
                new_artists, orient_angle, cx, cy, glyph_scale, orient, ax
            )

            # ── Gloss label ───────────────────────────────────────────────────
            # Place the label radially outward from the glyph centre.
            # For the innermost position (radius == 0) just place it below.
            if show_glossing and label:
                if radius == 0:
                    lx, ly = 0.0, -gloss_offset
                else:
                    lx = cx + gloss_offset * math.cos(theta)
                    ly = cy + gloss_offset * math.sin(theta)
                ax.text(
                    lx, ly,
                    label.title(),
                    fontsize=gloss_fontsize,
                    ha="center", va="center",
                    color="black",
                    zorder=10,
                )

    plt.tight_layout()
    plt.show()
    return labels


# ── Grid layout (unchanged from original) ─────────────────────────────────────

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
            fontsize = max(fontsize, 8)
            axes[i].set_title(label.title(), pad=-6, y=-0.1, fontsize=fontsize)
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
    parser.add_argument("--n",              type=int,   default=None)
    parser.add_argument("--annotate",       action="store_true", default=False)
    parser.add_argument("--show-all-paths", action="store_true", default=True)
    parser.add_argument("--show-name",      action="store_true", default=False)
    parser.add_argument("--savename",       type=str,   default=None)
    parser.add_argument("--cell-size",      type=float, default=1.25)
    parser.add_argument("--cols",           type=int,   default=7)

    # Circle layout args
    parser.add_argument(
        "--circle", action="store_true", default=False,
        help="Use summoning-circle layout instead of grid."
    )
    parser.add_argument(
        "--rings", nargs="+", type=int, default=[1, 6, 12],
        metavar="N",
        help="Number of glyphs per ring, innermost first. e.g. --rings 1 6 12"
    )
    parser.add_argument(
        "--ring-spacing", type=float, default=2.5,
        help="Radial distance between rings (used when --ring-radii not set)."
    )
    parser.add_argument(
        "--ring-radii", nargs="+", type=float, default=None,
        metavar="R",
        help="Explicit radius for each ring. Must match number of --rings entries."
    )
    parser.add_argument(
        "--glyph-scale", type=float, default=0.8,
        help="Uniform scale factor applied to every glyph."
    )
    parser.add_argument(
        "--no-orient", action="store_true", default=False,
        help="Keep glyphs upright instead of rotating them to face outward."
    )
    parser.add_argument(
        "--no-decorative-rings", action="store_true", default=False,
        help="Suppress the faint dashed circles tracing each ring."
    )
    parser.add_argument(
        "--figsize", type=float, default=10.0,
        help="Figure side length in inches (figure is always square)."
    )
    parser.add_argument(
        "--show-glossing", action="store_true", default=False,
        help="Draw gloss labels next to each glyph in the circle layout."
    )
    parser.add_argument(
        "--gloss-offset", type=float, default=0.4,
        help="Radial distance beyond the glyph centre where the gloss label sits."
    )
    parser.add_argument(
        "--gloss-fontsize", type=float, default=7.0,
        help="Font size for gloss labels."
    )

    args = parser.parse_args()

    draw_kwargs = {
        "annotate":       args.annotate,
        "show_all_paths": args.show_all_paths,
        "show_name":      args.show_name,
        "savename":       args.savename,
    }

    specs = parse_file(args.file) if args.file else args.words
    if args.n is not None:
        specs = specs[:args.n]

    if args.circle:
        plot_glyphs_circle(
            specs,
            rings=args.rings,
            ring_radii=args.ring_radii,
            ring_spacing=args.ring_spacing,
            glyph_scale=args.glyph_scale,
            orient=not args.no_orient,
            draw_decorative_rings=not args.no_decorative_rings,
            show_glossing=args.show_glossing,
            gloss_offset=args.gloss_offset,
            gloss_fontsize=args.gloss_fontsize,
            draw_kwargs=draw_kwargs,
            figsize=args.figsize,
        )
    else:
        plot_glyphs(specs, cols=args.cols, cell_size=args.cell_size,
                    draw_kwargs=draw_kwargs)


if __name__ == "__main__":
    main()