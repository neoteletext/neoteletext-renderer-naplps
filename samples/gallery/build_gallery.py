"""Builds the sample-pages gallery as one HTML file with every picture embedded.

Run from the repository root after samples/pipeline.sh has rendered, captured and compared:
    python3 samples/gallery/build_gallery.py tmp/samples/all samples tmp/samples/gallery.html
"""

import base64
import json
import pathlib
import re
import sys

all_dir, manifest_dir, out = (pathlib.Path(a) for a in sys.argv[1:4])
PIXELS = 640 * 480

manifest = {}
for path in sorted(manifest_dir.glob("set-*/out/manifest.json")):
    for row in json.loads(path.read_text()):
        manifest[pathlib.Path(row["file"]).stem] = row
signal = {
    "01-tide-clock": ("Tide Clock", "Harbour scene with animated beam and water", "Flat screen-print bands"),
    "02-botanical": ("Herbarium", "Botanical plate of a fern", "Natural-history engraving"),
    "03-constellation": ("After Dark", "Star chart with staged constellations", "Night atlas"),
    "04-city-block": ("Common Ground", "Isometric city block, day to night", "Isometric illustration"),
    "05-form": ("Form", "Typographic poster", "Swiss typography"),
    "06-two-languages": ("One Bird, Two Languages", "Mosaic and vector comparison", "Teaching diagram"),
    "07-weather": ("Southern Season", "Weather map of Australia", "Banded infographic"),
    "08-kaleidoscope": ("Chromatic", "Macro-built colour-cycling flower", "Abstract pattern"),
    "09-evening-menu": ("Lumiere", "Restaurant menu card", "Art Deco"),
    "10-signal": ("Signal", "Cover and directory of the collection", "1980s videotex welcome page"),
}


def results(name):
    table = {}
    path = all_dir / name
    if not path.exists():
        return table
    for line in path.read_text().splitlines():
        match = re.match(r"^(\S+): (pass|FAIL) (\d+) of \d+ pixels differ; unexplained (\d+) in the candidate, (\d+)", line)
        if match:
            table[match[1]] = (match[2] == "pass", int(match[3]), max(int(match[4]), int(match[5])))
    return table


exact = results("compare-c0-d1.txt")
loose = results("compare-c4-d1.txt")
loose2 = results("compare-c4-d2.txt")


def uri(path):
    if not path.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


pages = []
for page in sorted((all_dir / "pages").glob("*.nap")):
    stem = page.stem
    row = manifest.get(stem)
    if row:
        title, purpose, style = row["title"], row["purpose"], row["style"]
        animated = bool(row.get("animated"))
    else:
        title, purpose, style = signal.get(stem, (stem, "", ""))
        animated = stem in ("01-tide-clock", "03-constellation", "04-city-block", "06-two-languages", "08-kaleidoscope")
    ok0, _, _ = exact.get(stem, (False, 0, PIXELS))
    ok4, _, un4 = loose.get(stem, (False, 0, PIXELS))
    ok42, _, _ = loose2.get(stem, (False, 0, PIXELS))
    pages.append(
        {
            "id": stem,
            "n": stem.split("-")[0],
            "title": title,
            "purpose": purpose[:1].upper() + purpose[1:],
            "style": style[:1].upper() + style[1:],
            "bytes": page.stat().st_size,
            "animated": animated,
            "captured": (all_dir / "pp3" / f"{stem}.png").exists(),
            "exact": ok0,
            "close": ok4,
            "close2": ok42,
            "share": round(100 * un4 / PIXELS, 2),
            "s256": uri(all_dir / "256x200" / f"{stem}.png"),
            "s320": uri(all_dir / "320x200" / f"{stem}.png"),
            "s512": uri(all_dir / "512x400" / f"{stem}.png"),
            "s480": uri(all_dir / "480x500" / f"{stem}.png"),
            "s462": uri(all_dir / "480x462" / f"{stem}.png"),
            "pp3": uri(all_dir / "pp3" / f"{stem}.png"),
            "ours": uri(all_dir / "ours-png" / f"{stem}.png"),
        }
    )

template = (pathlib.Path(__file__).parent / "gallery_template.html").read_text()
out.write_text(template.replace("/*DATA*/[]", json.dumps(pages, separators=(",", ":"))))
print(len(pages), "pages,", out.stat().st_size // 1024, "KB")
