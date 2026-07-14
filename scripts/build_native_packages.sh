#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 3 ]]; then
    echo "usage: $0 VERSION ASSET_DIRECTORY OUTPUT_DIRECTORY" >&2
    exit 2
fi

VERSION="${1#v}"
ASSETS="$(cd "$2" && pwd)"
OUTPUT="$(mkdir -p "$3" && cd "$3" && pwd)"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NFPM="${NFPM:-nfpm}"

for arch in amd64 arm64; do
    case "$arch" in
        amd64) release_arch=x86_64 ;;
        arm64) release_arch=aarch64 ;;
    esac

    work="$(mktemp -d)"
    trap 'rm -rf "$work"' EXIT
    tar -xzf "$ASSETS/caphetamine-linux-$release_arch.tar.gz" -C "$work"
    stage="$(find "$work" -mindepth 1 -maxdepth 1 -type d -print -quit)"
    config="$work/nfpm.yaml"
    if [[ -n "${RPM_SIGNING_KEY:-}" ]]; then
        python3 "$ROOT/scripts/render_nfpm.py" \
            --stage "$stage" --version "$VERSION" --arch "$arch" --output "$config" \
            --rpm-key "$RPM_SIGNING_KEY"
    else
        python3 "$ROOT/scripts/render_nfpm.py" \
            --stage "$stage" --version "$VERSION" --arch "$arch" --output "$config"
    fi
    for format in deb rpm archlinux; do
        "$NFPM" package --config "$config" --packager "$format" --target "$OUTPUT/"
    done
    rm -rf "$work"
    trap - EXIT

    work="$(mktemp -d)"
    trap 'rm -rf "$work"' EXIT
    tar -xzf "$ASSETS/caphetamine-linux-$release_arch-musl.tar.gz" -C "$work"
    stage="$(find "$work" -mindepth 1 -maxdepth 1 -type d -print -quit)"
    config="$work/nfpm.yaml"
    if [[ -n "${APK_SIGNING_KEY:-}" ]]; then
        python3 "$ROOT/scripts/render_nfpm.py" \
            --stage "$stage" --version "$VERSION" --arch "$arch" --output "$config" \
            --apk-key "$APK_SIGNING_KEY"
    else
        python3 "$ROOT/scripts/render_nfpm.py" \
            --stage "$stage" --version "$VERSION" --arch "$arch" --output "$config"
    fi
    "$NFPM" package --config "$config" --packager apk --target "$OUTPUT/"
    rm -rf "$work"
    trap - EXIT
done
