#!/bin/sh

set -eu

REPOSITORY="${CAPETHAMINE_REPOSITORY:-kirinnokubinagai/caphetamine-packages}"
BASE_URL="${CAPETHAMINE_RELEASE_URL:-https://github.com/$REPOSITORY/releases/latest/download}"
TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT HUP INT TERM

download() {
    curl --fail --location --silent --show-error "$BASE_URL/$1" --output "$TEMP_DIR/$1"
}

verify() {
    asset="$1"
    expected="$(awk -v name="$asset" '{ file = $2; sub(/^\*/, "", file); if (file == name) { print $1; exit } }' "$TEMP_DIR/SHA256SUMS")"
    test -n "$expected" || { echo "No checksum found for $asset" >&2; exit 1; }
    if command -v sha256sum >/dev/null 2>&1; then
        actual="$(sha256sum "$TEMP_DIR/$asset" | awk '{print $1}')"
    else
        actual="$(shasum -a 256 "$TEMP_DIR/$asset" | awk '{print $1}')"
    fi
    test "$actual" = "$expected" || { echo "Checksum verification failed for $asset" >&2; exit 1; }
}

download SHA256SUMS

case "$(uname -s)" in
    Darwin)
        asset="Caphetamine-macos-universal.zip"
        download "$asset"
        verify "$asset"
        ditto -x -k "$TEMP_DIR/$asset" "$TEMP_DIR/unpacked"
        destination="${CAPETHAMINE_INSTALL_PATH:-/Applications/Caphetamine.app}"
        if test -w "$(dirname "$destination")"; then
            rm -rf "$destination"
            ditto "$TEMP_DIR/unpacked/Caphetamine.app" "$destination"
        else
            sudo rm -rf "$destination"
            sudo ditto "$TEMP_DIR/unpacked/Caphetamine.app" "$destination"
        fi
        open "$destination"
        ;;
    Linux)
        case "$(uname -m)" in
            x86_64|amd64) arch=x86_64 ;;
            aarch64|arm64) arch=aarch64 ;;
            *) echo "Unsupported Linux architecture: $(uname -m)" >&2; exit 1 ;;
        esac
        libc_suffix=""
        if ldd --version 2>&1 | grep -qi musl; then
            libc_suffix="-musl"
        fi
        asset="caphetamine-linux-$arch$libc_suffix.tar.gz"
        download "$asset"
        verify "$asset"
        tar -xzf "$TEMP_DIR/$asset" -C "$TEMP_DIR"
        root="$(find "$TEMP_DIR" -maxdepth 1 -type d -name 'caphetamine-*-linux-*' | head -n 1)"
        prefix="${CAPETHAMINE_PREFIX:-$HOME/.local}"
        mkdir -p "$prefix/bin" "$prefix/share/applications" "$prefix/share/icons/hicolor/scalable/apps"
        cp "$root/bin/caphetamine" "$prefix/bin/caphetamine"
        cp "$root/share/applications/caphetamine.desktop" "$prefix/share/applications/caphetamine.desktop"
        cp "$root/share/icons/hicolor/scalable/apps/caphetamine.svg" "$prefix/share/icons/hicolor/scalable/apps/caphetamine.svg"
        chmod 0755 "$prefix/bin/caphetamine"
        chmod 0644 "$prefix/share/applications/caphetamine.desktop"
        chmod 0644 "$prefix/share/icons/hicolor/scalable/apps/caphetamine.svg"
        "$prefix/bin/caphetamine" --install-autostart
        nohup "$prefix/bin/caphetamine" >/dev/null 2>&1 &
        ;;
    *)
        echo "Caphetamine supports macOS and Linux." >&2
        exit 1
        ;;
esac
