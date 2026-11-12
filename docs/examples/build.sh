#!/usr/bin/env bash
# Regenerates the example pages and renders each to docs/images/. Run from the repository root.
set -euo pipefail
here=docs/examples
font=${NAPLPS_FONT:-$HOME/devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes}
cargo build --quiet --release -p naplps-render
python3 "$here/examples.py" "$here/pages"
mkdir -p docs/images
for page in "$here"/pages/*.nap; do
    name=$(basename "$page" .nap)
    target/release/naplps-render --font "$font" "$page" "docs/images/$name.ppm"
    ffmpeg -loglevel error -y -i "docs/images/$name.ppm" "docs/images/$name.png"
    rm "docs/images/$name.ppm"
done
# The animation again, half a second on: BLINK changes the colour map, not the picture.
target/release/naplps-render --font "$font" --tenths 5 "$here/pages/11-animation.nap" docs/images/11-animation-5.ppm
ffmpeg -loglevel error -y -i docs/images/11-animation-5.ppm docs/images/11-animation-5.png
rm docs/images/11-animation-5.ppm
