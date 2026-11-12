#!/usr/bin/env bash
# The repository's one check script: its own steps, on the gate machinery
# every neoteletext repository shares (scripts/gate.sh, copied from
# neoteletext-common; DEVELOPMENT.md section 9 there). Every step passes or
# fails the run: nothing is skipped, and a missing tool is a failure.
#   scripts/check.sh commit   formatting and Clippy, on what is staged
#   scripts/check.sh push     the tests: a push of livedevelopment
#   scripts/check.sh full     release tests, documentation, and the oracle
#                             reproducing the rosetta_stone screenshots
#                             with PP3: a push to main
# This repository is developed on chunko, a Linux machine, so the full gate
# has no separate Linux stage.
set -euo pipefail
cd "$(dirname "$0")/.."

# Unused: the full gate has no linux_steps. gate.sh reads it only there.
linux_host="${TELETEXT_LINUX_HOST:-chunko}"
# What the gates read.
readonly CHECKED_PATHS=(crates scripts .githooks Cargo.toml Cargo.lock rust-toolchain.toml clippy.toml rustfmt.toml)

. scripts/gate.sh

# The crates that read input from outside their process, each with the
# same no-panic lint list at its root (DEVELOPMENT.md section 6). Every
# crate root must be listed.
readonly NO_PANIC_ROOTS=(crates/naplps-oracle/src/lib.rs crates/naplps-oracle/src/main.rs crates/naplps/src/lib.rs crates/naplps-render/src/main.rs)

check_no_panic_lists() {
    step "the no-panic lint list is the same in every crate root"
    local first="" root list
    for root in crates/*/src/lib.rs crates/*/src/main.rs crates/*/src/bin/*.rs; do
        [[ -f "$root" ]] || continue
        [[ " ${NO_PANIC_ROOTS[*]} " == *" $root "* ]] || fail "$root is a crate root missing from NO_PANIC_ROOTS"
    done
    for root in "${NO_PANIC_ROOTS[@]}"; do
        [[ -f "$root" ]] || fail "$root is listed in NO_PANIC_ROOTS but does not exist"
        list="$(sed -n '/^#!\[deny(/,/^)\]/p' "$root")"
        [[ -n "$list" ]] || fail "$root has no #![deny(...)] list"
        if [[ -z "$first" ]]; then
            first="$list"
        elif [[ "$list" != "$first" ]]; then
            fail "$root's #![deny(...)] list differs from ${NO_PANIC_ROOTS[0]}'s"
        fi
    done
}

commit_steps() {
    step "lockfile up to date"
    cargo metadata --quiet --locked --format-version 1 >/dev/null
    step "formatting"
    cargo fmt --check
    check_no_panic_lists
    step "Clippy, warnings as errors"
    cargo clippy --quiet --workspace --all-targets -- -D warnings
}

push_steps() {
    step "tests (the ignored ones need PP3 and run in the full gate)"
    cargo test --quiet --workspace
}

full_steps() {
    step "documentation builds, warnings as errors"
    RUSTDOCFLAGS="-D warnings" cargo doc --quiet --workspace --no-deps
    step "release tests"
    cargo test --quiet --workspace --release
    step "3,000 random pages in a debug build, where arithmetic overflow panics (about seven minutes)"
    cargo test --quiet -p naplps --test random_input -- --ignored
    step "the oracle and the renderer against PP3, and the whole collection (about three minutes)"
    local tool
    for tool in dosbox Xvfb socat xdotool ffmpeg ffprobe sha256sum; do
        need_tool "$tool" "the oracle runs PP3 in DOSBox on Xvfb (sudo apt-get install dosbox xvfb socat xdotool ffmpeg)"
    done
    cargo test --quiet --workspace --release -- --ignored
}

gate_main "$@"
