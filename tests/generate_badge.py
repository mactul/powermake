import sys
import math

def coverage_color(pct: float) -> str:
    k = 0.04
    center = 90

    s = 1 / (1 + math.exp(-k * (pct - center)))

    s_min = 1 / (1 + math.exp(-k * (0   - center)))
    s_max = 1 / (1 + math.exp(-k * (100 - center)))
    t = (s - s_min) / (s_max - s_min)

    hue = t * 120  # red -> green
    return f"hsl({hue:.1f}, 100%, 40%)"

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <coverage_number 0-100>")
    exit(1)

coverage = int(sys.argv[1])

color = coverage_color(coverage)

svg = f"""
<svg width="96.3" height="20" viewBox="0 0 963 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="coverage: {coverage}%">
<title>coverage: {coverage}%</title>
<linearGradient id="zxDZo" x2="0" y2="100%">
    <stop offset="0" stop-opacity=".1" stop-color="#EEE"/>
    <stop offset="1" stop-opacity=".1"/>
</linearGradient>
<mask id="zPoWN"><rect width="963" height="200" rx="30" fill="#FFF"/></mask>
<g mask="url(#zPoWN)">
    <rect width="603" height="200" fill="#555"/>
    <rect width="360" height="200" fill="{color}" x="603"/>
    <rect width="963" height="200" fill="url(#zxDZo)"/>
</g>
<g aria-hidden="true" fill="#fff" text-anchor="start" font-family="Verdana,DejaVu Sans,sans-serif" font-size="110">
    <text x="60" y="148" textLength="503" fill="#000" opacity="0.25">coverage</text>
    <text x="50" y="138" textLength="503">coverage</text>
    <text x="658" y="148" textLength="260" fill="#000" opacity="0.25">{coverage}%</text>
    <text x="648" y="138" textLength="260">{coverage}%</text>
</g>
</svg>
"""

with open("../coverage.svg", "w") as file:
        file.write(svg)