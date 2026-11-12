#!/usr/bin/env bash
# The sample pages through the renderer and through PP3. Run from the repository root:
#   samples/pipeline.sh collect   gather samples/*/out/*.nap into tmp/samples/all/pages
#   samples/pipeline.sh render    each page at the sizes below, and as the oracle shows it to PP3
#   samples/pipeline.sh capture   each page in PP3, a fresh PP3 per page, eight at once (about 20 minutes)
#   samples/pipeline.sh compare   the renderer against PP3 at 640 x 480 (docs/verification.md)
# Everything is written under tmp/samples/all.
set -euo pipefail
export PATH=$HOME/.cargo/bin:$PATH
all=tmp/samples/all
font=$HOME/devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes
render=target/release/naplps-render
oracle=target/release/naplps-oracle
shards=8

case "${1:-}" in
collect)
    rm -rf "$all"
    mkdir -p "$all/pages"
    cp samples/*/out/*.nap "$all/pages/"
    ls "$all/pages" | wc -l
    ;;
render)
    cargo build --quiet --release -p naplps-render -p naplps-oracle
    for size in 256x200 320x200 512x400 480x500 480x462; do
        mkdir -p "$all/$size"
        for page in "$all"/pages/*.nap; do
            name=$(basename "$page" .nap)
            "$render" --width "${size%x*}" --height "${size#*x}" --font "$font" "$page" "$all/$size/$name.ppm"
            ffmpeg -loglevel error -y -i "$all/$size/$name.ppm" "$all/$size/$name.png"
            rm "$all/$size/$name.ppm"
        done
    done
    # As the oracle shows a page to PP3, for the comparison.
    mkdir -p "$all/ours"
    for page in "$all"/pages/*.nap; do
        name=$(basename "$page" .nap)
        "$render" --preamble --dac-bits 6 --font "$font" "$page" "$all/ours/$name.ppm"
    done
    ;;
capture)
    mkdir -p "$all/pp3"
    ls "$all"/pages/*.nap > "$all/list.txt"
    for shard in $(seq 0 $((shards - 1))); do
        awk -v n="$shards" -v s="$shard" 'NR % n == s' "$all/list.txt" > "$all/shard-$shard.txt"
        (
            # shellcheck disable=SC2046 # one argument per page file is intended
            "$oracle" capture --fresh --out "$all/pp3-shard-$shard" --work "$all/work-$shard" $(cat "$all/shard-$shard.txt") > "$all/shard-$shard.log" 2>&1 || echo "shard $shard failed" >> "$all/capture-failures.txt"
        ) &
    done
    wait
    cp "$all"/pp3-shard-*/*.png "$all/pp3/"
    ls "$all/pp3" | wc -l
    cat "$all/capture-failures.txt" 2>/dev/null || true
    ;;
compare)
    # Channel 4 allows one step of a 6-bit colour register: PP3 truncates page-defined colours.
    for channel in 0 4; do
        for displacement in 1 2; do
            "$oracle" compare --channel "$channel" --displacement "$displacement" "$all/pp3" "$all/ours" > "$all/compare-c$channel-d$displacement.txt" || true
        done
    done
    grep -c ": pass" "$all"/compare-c*.txt || true
    ;;
*)
    echo "usage: samples/pipeline.sh collect|render|capture|compare" >&2
    exit 2
    ;;
esac
