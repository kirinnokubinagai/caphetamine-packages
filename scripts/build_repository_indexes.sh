#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "usage: $0 PACKAGE_DIRECTORY PUBLIC_DIRECTORY" >&2
    exit 2
fi

PACKAGES="$(cd "$1" && pwd)"
PUBLIC="$(mkdir -p "$2" && cd "$2" && pwd)"
PAGES_URL="${CAPETHAMINE_PAGES_URL:-https://kirinnokubinagai.github.io/caphetamine-packages}"

for command in apt-ftparchive createrepo_c dpkg-scanpackages gpg; do
    command -v "$command" >/dev/null || {
        echo "required command is missing: $command" >&2
        exit 1
    }
done

if [[ -z "${GPG_KEY_ID:-}" ]]; then
    echo "GPG_KEY_ID is required for repository metadata signing" >&2
    exit 1
fi

GPG_SIGN_ARGS=(--batch --yes --pinentry-mode loopback --local-user "$GPG_KEY_ID")
if [[ -n "${GPG_PASSPHRASE:-}" ]]; then
    GPG_SIGN_ARGS+=(--passphrase "$GPG_PASSPHRASE")
fi

APT_ROOT="$PUBLIC/apt"
mkdir -p "$APT_ROOT/pool/main/c/caphetamine"
cp "$PACKAGES"/*.deb "$APT_ROOT/pool/main/c/caphetamine/"
for arch in amd64 arm64; do
    index="$APT_ROOT/dists/stable/main/binary-$arch"
    mkdir -p "$index"
    (
        cd "$APT_ROOT"
        dpkg-scanpackages --arch "$arch" pool /dev/null > "$index/Packages"
    )
    gzip -9 -c "$index/Packages" > "$index/Packages.gz"
done
mkdir -p "$APT_ROOT/dists/stable"
(
    cd "$APT_ROOT"
    apt-ftparchive \
        -o APT::FTPArchive::Release::Origin=Caphetamine \
        -o APT::FTPArchive::Release::Label=Caphetamine \
        -o APT::FTPArchive::Release::Suite=stable \
        -o APT::FTPArchive::Release::Codename=stable \
        -o APT::FTPArchive::Release::Architectures="amd64 arm64" \
        -o APT::FTPArchive::Release::Components=main \
        release dists/stable > dists/stable/Release
)
gpg "${GPG_SIGN_ARGS[@]}" --armor --detach-sign \
    --output "$APT_ROOT/dists/stable/Release.gpg" "$APT_ROOT/dists/stable/Release"
gpg "${GPG_SIGN_ARGS[@]}" --armor --clearsign \
    --output "$APT_ROOT/dists/stable/InRelease" "$APT_ROOT/dists/stable/Release"

mkdir -p "$PUBLIC/keys"
gpg --batch --yes --export "$GPG_KEY_ID" > "$PUBLIC/keys/caphetamine-archive-keyring.gpg"
gpg --batch --yes --armor --export "$GPG_KEY_ID" > "$PUBLIC/keys/caphetamine-archive-keyring.asc"

RPM_ROOT="$PUBLIC/rpm"
for arch in x86_64 aarch64; do
    mkdir -p "$RPM_ROOT/$arch"
    find "$PACKAGES" -maxdepth 1 -type f -name "*.$arch.rpm" -exec cp {} "$RPM_ROOT/$arch/" \;
    createrepo_c "$RPM_ROOT/$arch" >/dev/null
    gpg "${GPG_SIGN_ARGS[@]}" --armor --detach-sign \
        --output "$RPM_ROOT/$arch/repodata/repomd.xml.asc" \
        "$RPM_ROOT/$arch/repodata/repomd.xml"
done
cat > "$RPM_ROOT/caphetamine.repo" <<EOF
[caphetamine]
name=Caphetamine
baseurl=$PAGES_URL/rpm/\$basearch
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=$PAGES_URL/keys/caphetamine-archive-keyring.asc
EOF

cat > "$APT_ROOT/caphetamine.sources" <<EOF
Types: deb
URIs: $PAGES_URL/apt
Suites: stable
Components: main
Signed-By: /usr/share/keyrings/caphetamine-archive-keyring.gpg
EOF
