"""Screenshot HTML files at exact dimensions using Playwright.

Usage:
    python3 screenshot.py /tmp/chart.html /tmp/chart.png [width] [height] [scale]

Defaults to 1800x1800 (a generic square). Pass explicit width/height to match
whatever canvas your chart's HTML/CSS was actually designed for (e.g. 1200 627
for the LinkedIn 1.91:1 canvas this skill's brand system uses).
Scale factor multiplies output resolution (e.g., scale=2 -> 3600x3600 output).
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def screenshot(html_path: str, output_path: str, width: int = 1800, height: int = 1800, scale: float = 1.0) -> None:
    html_path = str(Path(html_path).resolve())
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=scale,
        )
        page.goto(f"file://{html_path}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)  # Google Fonts rendering
        page.screenshot(path=output_path)
        browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 screenshot.py <html_path> <output_path> [width] [height] [scale]")
        sys.exit(1)

    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1800
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 1800
    s = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    screenshot(sys.argv[1], sys.argv[2], w, h, s)
    out_w, out_h = int(w * s), int(h * s)
    print(f"Saved: {sys.argv[2]} ({out_w}x{out_h})")
