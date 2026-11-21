"""Shared start of every set 15 generator."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from encoder import (Plate, xy, Y_SCALE, measure, arc_points, star_points,  # noqa: E402,F401
                     unit_rel, px_rel)


def save(script, build):
    out = ROOT / 'out' / (Path(script).stem + '.nap')
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(build().stream())
    print(out.name, out.stat().st_size, 'bytes')
