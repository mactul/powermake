import os
import sys
import json
import math
import argparse
import typing as T
from html import escape

Pair = T.Tuple[str, str]                # (lib, provider)
Combo = T.Tuple[str, str, str, str]      # (host_os, host_arch, target_os, target_arch)

# ---------------------------------------------------------------------------
# Loading & normalizing
# ---------------------------------------------------------------------------


def _normalize_results(raw) -> T.List[T.Tuple[str, str, bool]]:
    """Expects 'results' to be a list of {"lib", "provider", "success"} dicts
    and returns a flat list of (lib, provider, success) triples."""
    return [(item["lib"], item["provider"], bool(item["success"])) for item in raw]


def load_matrix(files: T.List[str]) -> T.Tuple[T.Dict[Pair, T.Dict[Combo, bool]], T.List[Pair], T.List[Combo]]:
    """builds:
    matrix[(lib, provider)][(host_os, host_arch, target_os, target_arch)] = success (bool)
    Also returns sorted lists of the pairs and combos encountered.
    """
    files.sort()

    matrix: T.Dict[Pair, T.Dict[Combo, bool]] = {}
    combos_seen: set[Combo] = set()
    pairs_seen: set[Pair] = set()

    for fp in files:
        try:
            with open(fp, "r") as file:
                data = json.load(file)
        except Exception as e:
            print(f"warning: failed to read/parse {fp}: {e}", file=sys.stderr)
            continue

        try:
            combo: Combo = (data["host_os"], data["host_arch"], data["target_os"], data["target_arch"])
        except KeyError as e:
            print(f"warning: {fp} missing {e} field, skipping", file=sys.stderr)
            continue

        combos_seen.add(combo)

        for lib, provider, success in _normalize_results(data.get("results", [])):
            pair: Pair = (lib, provider)
            pairs_seen.add(pair)
            matrix.setdefault(pair, {})[combo] = success

    pairs = sorted(pairs_seen, key=lambda p: (p[0].lower(), p[1].lower()))
    combos = sorted(combos_seen, key=lambda c: tuple(s.lower() for s in c))
    return matrix, pairs, combos


# ---------------------------------------------------------------------------
# SVG rendering
# ---------------------------------------------------------------------------

FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO_FAMILY = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

COLOR_OK = "#22c55e"       # green
COLOR_OK_BG = "#dcfce7"
COLOR_FAIL = "#ef4444"     # red
COLOR_FAIL_BG = "#fee2e2"
COLOR_MISSING_BG = "#f3f4f6"
COLOR_MISSING_FG = "#9ca3af"
COLOR_GRID = "#e5e7eb"
COLOR_TEXT = "#1f2937"
COLOR_HEADER_BG = "#f9fafb"


def _text_width(s: str, font_size: float) -> float:
    """Rough heuristic for rendered text width (avoids needing a real font
    metrics library / headless browser just for a README badge)."""
    return len(s) * font_size * 0.6


def render_svg(matrix: T.Dict[Pair, T.Dict[Combo, bool]], pairs: T.List[Pair], combos: T.List[Combo], title: str = "Package Provider Compatibility Matrix") -> str:
    cell_w = 44
    cell_h = 26
    row_label_font = 12.5
    header_font = 12
    title_font = 15

    row_labels = [f"{lib} ({provider})" for lib, provider in pairs]
    row_label_w = max([_text_width(s, row_label_font) for s in row_labels] + [0]) + 24
    row_label_w = max(row_label_w, 140)

    def _combo_label(combo: Combo) -> str:
        host_os, host_arch, target_os, target_arch = combo
        host = f"{host_os}/{host_arch}"
        target = f"{target_os}/{target_arch}"
        return host if host == target else f"{host} \u2192 {target}"

    col_labels = [_combo_label(combo) for combo in combos]
    # column headers are rotated 40deg, so height depends on label length
    max_col_label_w = max([_text_width(s, header_font) for s in col_labels] + [0])
    header_h = max_col_label_w * 0.72 + 20
    header_h = max(header_h, 70)
    # rotated text starts at each column's anchor and extends further right/up,
    # so the last column needs extra room on the right or its label gets clipped
    right_margin_extra = max_col_label_w * math.cos(math.radians(40))

    n_rows = len(pairs)
    n_cols = len(combos)

    margin = 20
    title_h = 34 if title else 0
    legend_h = 34

    grid_w = cell_w * n_cols
    grid_h = cell_h * n_rows

    width = margin * 2 + row_label_w + grid_w + right_margin_extra
    height = margin * 2 + title_h + header_h + grid_h + legend_h

    x0 = margin + row_label_w
    y0 = margin + title_h + header_h

    parts: T.List[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" font-family="{FONT_FAMILY}">'
    )
    parts.append(f'<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" fill="white"/>')

    # Title
    if title:
        parts.append(
            f'<text x="{margin}" y="{margin + title_h * 0.68:.1f}" '
            f'font-size="{title_font}" font-weight="700" fill="{COLOR_TEXT}">{escape(title)}</text>'
        )

    # Header background band
    parts.append(
        f'<rect x="{x0:.1f}" y="{margin + title_h:.1f}" width="{grid_w:.1f}" height="{header_h:.1f}" '
        f'fill="{COLOR_HEADER_BG}"/>'
    )

    # Column headers (rotated)
    for ci, label in enumerate(col_labels):
        cx = x0 + ci * cell_w + cell_w / 2
        cy = margin + title_h + header_h - 8
        parts.append(
            f'<text x="{cx:.1f}" y="{cy:.1f}" font-size="{header_font}" fill="{COLOR_TEXT}" '
            f'text-anchor="start" transform="rotate(-40 {cx:.1f} {cy:.1f})">{escape(label)}</text>'
        )

    # Row labels + grid + cells
    for ri, (pair, label) in enumerate(zip(pairs, row_labels)):
        ry = y0 + ri * cell_h
        row_bg = "#ffffff" if ri % 2 == 0 else "#fafafa"
        parts.append(
            f'<rect x="{margin:.1f}" y="{ry:.1f}" width="{row_label_w + grid_w:.1f}" height="{cell_h:.1f}" '
            f'fill="{row_bg}"/>'
        )
        parts.append(
            f'<text x="{margin + 8:.1f}" y="{ry + cell_h / 2 + 4:.1f}" font-size="{row_label_font}" '
            f'font-family="{MONO_FAMILY}" fill="{COLOR_TEXT}">{escape(label)}</text>'
        )

        for ci, combo in enumerate(combos):
            cx = x0 + ci * cell_w
            success = matrix.get(pair, {}).get(combo)
            if success is True:
                fg, bg, glyph = COLOR_OK, COLOR_OK_BG, "\u2713"
            elif success is False:
                fg, bg, glyph = COLOR_FAIL, COLOR_FAIL_BG, "\u2717"
            else:
                fg, bg, glyph = COLOR_MISSING_FG, COLOR_MISSING_BG, "\u2013"

            parts.append(
                f'<rect x="{cx + 3:.1f}" y="{ry + 3:.1f}" width="{cell_w - 6:.1f}" height="{cell_h - 6:.1f}" '
                f'rx="4" fill="{bg}"/>'
            )
            parts.append(
                f'<text x="{cx + cell_w / 2:.1f}" y="{ry + cell_h / 2 + 4.5:.1f}" '
                f'font-size="13" text-anchor="middle" fill="{fg}" font-weight="600">{glyph}</text>'
            )

    # Grid lines
    grid_top = y0
    grid_bottom = y0 + grid_h
    for ci in range(n_cols + 1):
        gx = x0 + ci * cell_w
        parts.append(f'<line x1="{gx:.1f}" y1="{grid_top:.1f}" x2="{gx:.1f}" y2="{grid_bottom:.1f}" stroke="{COLOR_GRID}" stroke-width="1"/>')
    for ri in range(n_rows + 1):
        gy = grid_top + ri * cell_h
        parts.append(f'<line x1="{x0:.1f}" y1="{gy:.1f}" x2="{x0 + grid_w:.1f}" y2="{gy:.1f}" stroke="{COLOR_GRID}" stroke-width="1"/>')

    # Legend
    legend_y = height - legend_h + 20
    lx = margin
    for glyph, fg, bg, label in [
        ("\u2713", COLOR_OK, COLOR_OK_BG, "builds"),
        ("\u2717", COLOR_FAIL, COLOR_FAIL_BG, "fails"),
        ("\u2013", COLOR_MISSING_FG, COLOR_MISSING_BG, "not tested"),
    ]:
        parts.append(f'<rect x="{lx:.1f}" y="{legend_y - 12:.1f}" width="16" height="16" rx="3" fill="{bg}"/>')
        parts.append(
            f'<text x="{lx + 8:.1f}" y="{legend_y - 1:.1f}" font-size="12" text-anchor="middle" '
            f'fill="{fg}" font-weight="600">{glyph}</text>'
        )
        parts.append(f'<text x="{lx + 22:.1f}" y="{legend_y:.1f}" font-size="12" fill="{COLOR_TEXT}">{escape(label)}</text>')
        lx += 22 + _text_width(label, 12) + 24

    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("files", nargs="+", default=[], help="list of result files")
parser.add_argument("--output", default="svg_output/compatibility-matrix.svg", help="output SVG path")
parser.add_argument("--title", default="powermake.package - pre-configured libs - tested download/build/install combos", help="chart title (empty string to omit)")
args = parser.parse_args()

matrix, pairs, combos = load_matrix(args.files)

if not pairs or not combos:
    print("error: no data found to render", file=sys.stderr)
    exit(1)

svg = render_svg(matrix, pairs, combos, title=args.title)
os.makedirs(os.path.dirname(args.output), exist_ok=True)
with open(args.output, "w") as file:
    file.write(svg)
print(f"wrote {args.output} ({len(pairs)} lib/provider pairs x {len(combos)} host/target combos)")
