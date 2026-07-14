#!/bin/sh

set -eu

BASE_URL="${CAPETHAMINE_PACKAGES_URL:-https://kirinnokubinagai.github.io/caphetamine-packages}"
TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT HUP INT TERM

as_root() {
    if [ "$(id -u)" -eq 0 ]; then
        "$@"
    elif command -v sudo >/dev/null 2>&1; then
        sudo "$@"
    elif command -v doas >/dev/null 2>&1; then
        doas "$@"
    else
        echo "Root privileges are required; install sudo/doas or run this script as root." >&2
        exit 1
    fi
}

install_url() {
    url="$1"
    destination="$2"
    temporary="$TEMP_DIR/$(basename "$destination")"
    curl -fsSL "$url" -o "$temporary"
    as_root mkdir -p "$(dirname "$destination")"
    as_root cp "$temporary" "$destination"
    as_root chmod 0644 "$destination"
}

if command -v apt-get >/dev/null 2>&1; then
    install_url "$BASE_URL/keys/caphetamine-archive-keyring.gpg" \
        /usr/share/keyrings/caphetamine-archive-keyring.gpg
    install_url "$BASE_URL/apt/caphetamine.sources" \
        /etc/apt/sources.list.d/caphetamine.sources
    as_root apt-get update
    as_root apt-get install caphetamine
elif command -v dnf >/dev/null 2>&1; then
    install_url "$BASE_URL/rpm/caphetamine.repo" /etc/yum.repos.d/caphetamine.repo
    as_root dnf install caphetamine
elif command -v yum >/dev/null 2>&1; then
    install_url "$BASE_URL/rpm/caphetamine.repo" /etc/yum.repos.d/caphetamine.repo
    as_root yum install caphetamine
elif command -v zypper >/dev/null 2>&1; then
    install_url "$BASE_URL/rpm/caphetamine.repo" /etc/zypp/repos.d/caphetamine.repo
    as_root zypper --gpg-auto-import-keys refresh
    as_root zypper install caphetamine
elif command -v pacman >/dev/null 2>&1; then
    curl -fsSL "$BASE_URL/keys/caphetamine-archive-keyring.asc" -o "$TEMP_DIR/key.asc"
    fingerprint="$(gpg --show-keys --with-colons "$TEMP_DIR/key.asc" | awk -F: '$1 == "fpr" { print $10; exit }')"
    as_root pacman-key --add "$TEMP_DIR/key.asc"
    as_root pacman-key --lsign-key "$fingerprint"
    if ! grep -q '^\[caphetamine\]$' /etc/pacman.conf; then
        # shellcheck disable=SC2016 # pacman expands $arch from its own configuration.
        printf '\n[caphetamine]\nSigLevel = Required DatabaseRequired\nServer = %s/arch/$arch\n' "$BASE_URL" > "$TEMP_DIR/pacman.conf"
        as_root tee -a /etc/pacman.conf < "$TEMP_DIR/pacman.conf" >/dev/null
    fi
    as_root pacman -Syu caphetamine
elif command -v apk >/dev/null 2>&1; then
    install_url "$BASE_URL/keys/caphetamine.rsa.pub" /etc/apk/keys/caphetamine.rsa.pub
    repository="$BASE_URL/alpine/$(apk --print-arch)"
    if ! grep -qxF "$repository" /etc/apk/repositories; then
        printf '%s\n' "$repository" > "$TEMP_DIR/apk-repository"
        as_root tee -a /etc/apk/repositories < "$TEMP_DIR/apk-repository" >/dev/null
    fi
    as_root apk update
    as_root apk add caphetamine
else
    echo "Supported repository managers were not found; using the direct installer." >&2
    curl -fsSL https://raw.githubusercontent.com/kirinnokubinagai/caphetamine-packages/main/scripts/install.sh | sh
fi
