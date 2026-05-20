import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
 
# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
 
_MAROON = (0.502, 0.0, 0.0, 1.0)
 
_SCHEMES = {
    "ember":   ("cmap", "gist_heat"),
    "summer":  ("cmap", "summer"),
    "viridis": ("cmap", "viridis"),
    "plasma":  ("cmap", "plasma"),
    "cool":    ("cmap", "cool"),
    "twilight":("cmap", "twilight"),
    "fire":    ("gradient", (0.8,  0.05, 0.0,  1.0), (1.0, 0.9,  0.1,  1.0)),  # deep red → yellow
    "ice":     ("gradient", (0.05, 0.1,  0.6,  1.0), (0.7, 0.95, 1.0,  1.0)),  # navy → icy cyan
    "violet":  ("gradient", (0.3,  0.0,  0.5,  1.0), (1.0, 0.6,  1.0,  1.0)),  # purple → lavender
    "dusk":    ("gradient", (0.1,  0.0,  0.2,  1.0), (1.0, 0.4,  0.2,  1.0)),  # midnight → burnt orange
    "forest":  ("gradient", (0.0,  0.2,  0.05, 1.0), (0.4, 0.9,  0.2,  1.0)),  # dark green → lime
    "mono":    ("gradient", (0.15, 0.15, 0.15, 1.0), (0.85,0.85, 0.85, 1.0)),  # dark → light grey
}
 
def get_palette(annotate, n: int, scheme: str = "maroon") -> list[tuple]:
    """Return n RGBA tuples evenly sampled from a named scheme.
    'maroon' returns n copies of the same color (flat default, no gradient).
    Pass scheme name to get_palette; use list_schemes() to see all options."""
    if n <= 0: return []
    if not annotate: return [_MAROON] * n
    if scheme not in _SCHEMES:
        raise ValueError(f"Unknown scheme '{scheme}'. Available: {list_schemes()}")
    kind, *spec = _SCHEMES[scheme]
    positions = [0.5] if n == 1 else [i / (n - 1) for i in range(n)]
    if kind == "cmap":
        cmap = plt.get_cmap(spec[0])
        return [cmap(t) for t in positions]
    start, end = np.array(spec[0]), np.array(spec[1])
    return [tuple((1 - t) * start + t * end) for t in positions]
 
def list_schemes() -> list[str]:
    return ["maroon"] + sorted(_SCHEMES.keys())
 
 

######################################3


class GlyphDrawer:
    def __init__(self, glyph):
        self.g = glyph

    def draw(
        self,
        annotate=False,
        show_all_paths=False,
        savename="output.png",
        output_dpi=200,
        axs=None,
        dot_color="maroon",
        line_color="maroon",
        dot_size=30,
        legend_fontsize=8,
        legend_anchor=(1, 0.75),
        show_name=False,
        vertex_num = 13,
    ):
        g = self.g
        assert g.num == g.binary_array.shape[1]
        assert g.attr_num == g.binary_array.shape[0]

        colors = get_palette(annotate, vertex_num, line_color)

        #cmap = plt.get_cmap(cmap)
        if g.num:
            dot_size = max(dot_size / (g.num / 6), 6)
            dot_size = min(dot_size, 40)

        x_vals, y_vals = g.base_fn(g.num, *g.base_kwargs)

        if axs is None:
            fig, axs = plt.subplots(1, 1)
        else:
            fig = plt.gcf()

        axs.set_aspect("equal")
        axs.margins(0.1)

        # draw the points
        if annotate:
            dot_color = colors[0] #cmap(0.3)
            halos = [(dot_size + 3, 0.05), (dot_size + 2, 0.12), (dot_size + 1, 0.25)]
            for w, a in halos:
                axs.scatter(x_vals, y_vals, s=w, color=dot_color, alpha=a, edgecolors="none", zorder=2)

        axs.scatter(x_vals, y_vals, s=dot_size, color=dot_color, zorder=2)

        if show_all_paths:
            self.draw_all_paths(x_vals, y_vals, axs)

        for i in range(g.attr_num):
            k = i + 1
            if annotate:
                color = colors[i] #cmap(0.5 * i / g.attr_num + 0.1)
                linewidth = 3
            else:
                color = line_color
                linewidth = 2

            labelled = False
            for j, elem in enumerate(g.binary_array[i]):
                if elem == 1:
                    P = [x_vals[j], y_vals[j]]
                    Q = [x_vals[(j + k) % g.num], y_vals[(j + k) % g.num]]
                    line_x, line_y = g.line_fn(P, Q, *g.line_kwargs)

                    if annotate:
                        halos = [
                            (linewidth + 5, 0.05),
                            (linewidth + 2, 0.1),
                            (linewidth + 0.5, 0.3),
                        ]
                        (line,) = axs.plot(line_x, line_y, lw=linewidth, color=color, zorder=1)
                        line.set_path_effects(
                            [pe.Stroke(linewidth=w, foreground=color, alpha=a) for w, a in halos]
                            + [pe.Normal()]
                        )
                    else:
                        axs.plot(
                            line_x,
                            line_y,
                            ls="-",
                            lw=linewidth,
                            color=color,
                            label=g.att_strs[i] if (labelled is False) and annotate else None,
                            zorder=0,
                        )
                    labelled = True

        axs.set_axis_off()
        if show_name:
            axs.set_title(g.__name__)
        if savename is not None:
            plt.savefig(savename, dpi=output_dpi, bbox_inches="tight", pad_inches=0.5, transparent=True)
        elif axs is None:
            plt.show(transparent=True, pad_inches=0.5)

    def draw_all_paths(self, x_vals, y_vals, axs, all_ls="--", all_c="k", all_alpha=0.7, all_lw=0.5):
        g = self.g
        for k in range(1, g.attr_num + 1):
            for i in range(g.num):
                P = [x_vals[i], y_vals[i]]
                Q = [x_vals[(i + k) % g.num], y_vals[(i + k) % g.num]]
                line_x, line_y = g.line_fn(P, Q, *g.line_kwargs)
                axs.plot(line_x, line_y, ls=all_ls, color=all_c, alpha=all_alpha, lw=all_lw, zorder=4)