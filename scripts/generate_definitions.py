#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path


REQUIRED = (
    "Caphetamine-macos-universal.zip",
    "Caphetamine-macos-universal.dmg",
    "caphetamine-linux-x86_64.tar.gz",
    "caphetamine-linux-aarch64.tar.gz",
    "caphetamine-linux-x86_64-musl.tar.gz",
    "caphetamine-linux-aarch64-musl.tar.gz",
)


def write(root: Path, relative: str, contents: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(contents).lstrip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate every package definition from one manifest")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, default=Path("."))
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    assets = manifest["assets"]
    missing = [name for name in REQUIRED if name not in assets]
    if missing:
        raise SystemExit(f"manifest is missing: {', '.join(missing)}")

    version = manifest["version"]
    tag = manifest["tag"]
    repo = manifest["repository"]
    release = f"https://github.com/{repo}/releases/download/{tag}"
    x64 = "caphetamine-linux-x86_64.tar.gz"
    arm64 = "caphetamine-linux-aarch64.tar.gz"
    dmg = "Caphetamine-macos-universal.dmg"
    zip_name = "Caphetamine-macos-universal.zip"

    write(args.output, "Casks/caphetamine.rb", f'''
        cask "caphetamine" do
          version "{version}"
          sha256 "{assets[dmg]['sha256']}"

          url "{release}/{dmg}"
          name "Caphetamine"
          desc "Prevent sleep while Caps Lock is on"
          homepage "https://github.com/{repo}"

          depends_on macos: :ventura

          app "Caphetamine.app"

          zap trash: [
            "~/Library/Preferences/com.kirinnokubinagaiyo.caphetamine.plist",
            "~/Library/Saved Application State/com.kirinnokubinagaiyo.caphetamine.savedState",
          ]
        end
    ''')

    write(args.output, "Formula/caphetamine.rb", f'''
        class Caphetamine < Formula
          desc "Prevent Linux sleep while Caps Lock is on"
          homepage "https://github.com/{repo}"
          version "{version}"
          depends_on :linux

          if Hardware::CPU.arm?
            url "{release}/{arm64}"
            sha256 "{assets[arm64]['sha256']}"
          else
            url "{release}/{x64}"
            sha256 "{assets[x64]['sha256']}"
          end

          def install
            bin.install Dir["*/bin/caphetamine"].first
            desktop = Dir["*/share/applications/caphetamine.desktop"].first
            icon = Dir["*/share/icons/hicolor/scalable/apps/caphetamine.svg"].first
            inreplace desktop, "Exec=caphetamine", "Exec=#{{bin}}/caphetamine"
            share.install desktop => "applications/caphetamine.desktop"
            (share/"icons/hicolor/scalable/apps").install icon
          end

          test do
            assert_match version.to_s, shell_output("#{{bin}}/caphetamine --version")
          end
        end
    ''')

    systems = {
        "aarch64-darwin": (zip_name, "darwin"),
        "x86_64-darwin": (zip_name, "darwin"),
        "aarch64-linux": (arm64, "linux"),
        "x86_64-linux": (x64, "linux"),
    }
    source_lines = []
    for system, (name, kind) in systems.items():
        source_lines.append(
            f'        "{system}" = {{ url = "{release}/{name}"; '
            f'hash = "{assets[name]["sha256_sri"]}"; kind = "{kind}"; }};'
        )
    write(args.output, "flake.nix", f'''
        {{
          description = "Unified Caphetamine binary packages";
          inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

          outputs = {{ self, nixpkgs }}:
            let
              systems = [ "aarch64-darwin" "x86_64-darwin" "aarch64-linux" "x86_64-linux" ];
              forAllSystems = nixpkgs.lib.genAttrs systems;
              sources = {{
        {chr(10).join(source_lines)}
              }};
            in {{
              packages = forAllSystems (system:
                let
                  pkgs = import nixpkgs {{ inherit system; }};
                  source = sources.${{system}};
                  archive = pkgs.fetchzip {{ inherit (source) url hash; stripRoot = false; }};
                in {{
                  default = pkgs.stdenvNoCC.mkDerivation {{
                    pname = "caphetamine";
                    version = "{version}";
                    dontUnpack = true;
                    installPhase = if source.kind == "darwin" then ''
                      mkdir -p "$out/Applications" "$out/bin"
                      cp -R "$archive/Caphetamine.app" "$out/Applications/"
                      ln -s ../Applications/Caphetamine.app/Contents/MacOS/Caphetamine "$out/bin/caphetamine"
                    '' else ''
                      binary="$(find "$archive" -path '*/bin/caphetamine' -type f -print -quit)"
                      desktop="$(find "$archive" -path '*/share/applications/caphetamine.desktop' -type f -print -quit)"
                      icon="$(find "$archive" -path '*/share/icons/hicolor/scalable/apps/caphetamine.svg' -type f -print -quit)"
                      install -Dm755 "$binary" "$out/bin/caphetamine"
                      install -Dm644 "$desktop" "$out/share/applications/caphetamine.desktop"
                      install -Dm644 "$icon" "$out/share/icons/hicolor/scalable/apps/caphetamine.svg"
                      substituteInPlace "$out/share/applications/caphetamine.desktop" \\
                        --replace-fail 'Exec=caphetamine' "Exec=$out/bin/caphetamine"
                    '';
                    meta.mainProgram = "caphetamine";
                  }};
                }});
              apps = forAllSystems (system: {{
                default = {{
                  type = "app";
                  program = "${{self.packages.${{system}}.default}}/bin/caphetamine";
                  meta.description = "Run Caphetamine";
                }};
              }});
            }};
        }}
    ''')

    write(args.output, "packaging/macports/Portfile", f'''
        PortSystem          1.0
        name                caphetamine
        version             {version}
        categories          aqua sysutils
        platforms           darwin
        license             Restrictive
        maintainers         nomaintainer
        description         Prevent macOS sleep while Caps Lock is on
        homepage            https://github.com/{repo}
        master_sites        {release}
        distname            Caphetamine-macos-universal
        extract.suffix      .zip
        worksrcdir          .
        checksums           sha256 {assets[zip_name]['sha256']} \\
                            size {assets[zip_name]['size']}
        use_configure       no
        build {{}}
        destroot {{
            xinstall -d ${{destroot}}${{applications_dir}}
            copy ${{worksrcpath}}/Caphetamine.app ${{destroot}}${{applications_dir}}/
        }}
    ''')

    x64_musl = "caphetamine-linux-x86_64-musl.tar.gz"
    arm64_musl = "caphetamine-linux-aarch64-musl.tar.gz"
    write(args.output, "packaging/void/template", f'''
        pkgname=caphetamine
        version={version}
        revision=1
        archs="x86_64 aarch64"
        short_desc="Prevent Linux sleep while Caps Lock is on"
        maintainer="Caphetamine <noreply@github.com>"
        license="custom:Proprietary"
        homepage="https://github.com/{repo}"
        case "$XBPS_TARGET_MACHINE" in
          x86_64) _asset="{x64}"; checksum="{assets[x64]['sha256']}" ;;
          x86_64-musl) _asset="{x64_musl}"; checksum="{assets[x64_musl]['sha256']}" ;;
          aarch64) _asset="{arm64}"; checksum="{assets[arm64]['sha256']}" ;;
          aarch64-musl) _asset="{arm64_musl}"; checksum="{assets[arm64_musl]['sha256']}" ;;
        esac
        distfiles="{release}/${{_asset}}"

        do_install() {{
          vbin */bin/caphetamine
          vinstall */share/applications/caphetamine.desktop 644 usr/share/applications
          vinstall */share/icons/hicolor/scalable/apps/caphetamine.svg 644 usr/share/icons/hicolor/scalable/apps
        }}
    ''')

    write(args.output, f"packaging/gentoo/app-misc/caphetamine-bin/caphetamine-bin-{version}.ebuild", f'''
        EAPI=8
        DESCRIPTION="Prevent Linux sleep while Caps Lock is on"
        HOMEPAGE="https://github.com/{repo}"
        SRC_URI="amd64? ( {release}/{x64} ) arm64? ( {release}/{arm64} )"
        LICENSE="all-rights-reserved"
        SLOT="0"
        KEYWORDS="~amd64 ~arm64"
        IUSE=""

        if [[ ${{ARCH}} == amd64 ]]; then
          S="${{WORKDIR}}/caphetamine-${{PV}}-linux-x86_64"
        else
          S="${{WORKDIR}}/caphetamine-${{PV}}-linux-aarch64"
        fi

        src_install() {{
          dobin bin/caphetamine
          insinto /usr/share/applications
          doins share/applications/caphetamine.desktop
          insinto /usr/share/icons/hicolor/scalable/apps
          doins share/icons/hicolor/scalable/apps/caphetamine.svg
        }}
    ''')
    write(args.output, "packaging/gentoo/app-misc/caphetamine-bin/Manifest", f'''
        DIST {x64} {assets[x64]['size']} BLAKE2B {assets[x64]['blake2b']} SHA512 {assets[x64]['sha512']}
        DIST {arm64} {assets[arm64]['size']} BLAKE2B {assets[arm64]['blake2b']} SHA512 {assets[arm64]['sha512']}
    ''')

    write(args.output, "packaging/pkgsrc/Makefile", f'''
        DISTNAME=       caphetamine-{version}
        PKGNAME=        caphetamine-{version}
        CATEGORIES=     sysutils
        MASTER_SITES=   {release}/
        COMMENT=        Prevent Linux sleep while Caps Lock is on
        NO_BUILD=       yes
        ONLY_FOR_PLATFORM= Linux-*-*

        .if ${{MACHINE_ARCH}} == "x86_64"
        DISTFILES=      {x64}
        WRKSRC=         ${{WRKDIR}}/caphetamine-{version}-linux-x86_64
        .elif ${{MACHINE_ARCH}} == "aarch64"
        DISTFILES=      {arm64}
        WRKSRC=         ${{WRKDIR}}/caphetamine-{version}-linux-aarch64
        .else
        PKG_FAIL_REASON+= "Unsupported architecture ${{MACHINE_ARCH}}"
        .endif

        do-install:
        \t${{INSTALL_PROGRAM}} ${{WRKSRC}}/bin/caphetamine ${{DESTDIR}}${{PREFIX}}/bin
        \t${{INSTALL_DATA_DIR}} ${{DESTDIR}}${{PREFIX}}/share/applications
        \t${{INSTALL_DATA}} ${{WRKSRC}}/share/applications/caphetamine.desktop ${{DESTDIR}}${{PREFIX}}/share/applications
        \t${{INSTALL_DATA_DIR}} ${{DESTDIR}}${{PREFIX}}/share/icons/hicolor/scalable/apps
        \t${{INSTALL_DATA}} ${{WRKSRC}}/share/icons/hicolor/scalable/apps/caphetamine.svg ${{DESTDIR}}${{PREFIX}}/share/icons/hicolor/scalable/apps

        .include "../../mk/bsd.pkg.mk"
    ''')
    write(args.output, "packaging/pkgsrc/PLIST", '''
        @comment $NetBSD$
        bin/caphetamine
        share/applications/caphetamine.desktop
        share/icons/hicolor/scalable/apps/caphetamine.svg
    ''')
    distinfo = ["$NetBSD$", ""]
    for name in (x64, arm64):
        distinfo.extend([
            f"BLAKE2s ({name}) = {assets[name]['blake2s']}",
            f"SHA512 ({name}) = {assets[name]['sha512']}",
            f"Size ({name}) = {assets[name]['size']} bytes",
        ])
    write(args.output, "packaging/pkgsrc/distinfo", "\n".join(distinfo) + "\n")

    app_id = "io.github.kirinnokubinagai.Caphetamine"
    metainfo_name = f"{app_id}.metainfo.xml"
    write(args.output, f"packaging/flatpak/{metainfo_name}", f'''
        <?xml version="1.0" encoding="UTF-8"?>
        <component type="desktop-application">
          <id>{app_id}</id>
          <name>Caphetamine</name>
          <summary>Prevent Linux sleep while Caps Lock is on</summary>
          <metadata_license>CC0-1.0</metadata_license>
          <project_license>LicenseRef-proprietary</project_license>
          <description>
            <p>Caphetamine keeps the computer awake while Caps Lock is on and restores the normal power settings as soon as Caps Lock is turned off.</p>
          </description>
          <launchable type="desktop-id">{app_id}.desktop</launchable>
          <provides><binary>caphetamine</binary></provides>
          <url type="homepage">https://github.com/{repo}</url>
          <releases><release version="{version}"/></releases>
        </component>
    ''')

    flatpak_manifest = {
        "app-id": app_id,
        "runtime": "org.freedesktop.Platform",
        "runtime-version": "25.08",
        "sdk": "org.freedesktop.Sdk",
        "command": "caphetamine",
        "finish-args": [
            "--share=ipc",
            "--socket=wayland",
            "--socket=fallback-x11",
            "--system-talk-name=org.freedesktop.login1",
            "--talk-name=org.freedesktop.ScreenSaver",
            "--talk-name=org.kde.StatusNotifierWatcher",
            "--filesystem=xdg-config/autostart:create",
        ],
        "modules": [
            {
                "name": "caphetamine",
                "buildsystem": "simple",
                "build-commands": [
                    "install -Dm755 bin/caphetamine /app/bin/caphetamine",
                    f"install -Dm644 share/applications/caphetamine.desktop /app/share/applications/{app_id}.desktop",
                    f"sed -i 's/^Exec=.*/Exec=caphetamine/' /app/share/applications/{app_id}.desktop",
                    f"install -Dm644 share/icons/hicolor/scalable/apps/caphetamine.svg /app/share/icons/hicolor/scalable/apps/{app_id}.svg",
                    f"sed -i 's/^Icon=.*/Icon={app_id}/' /app/share/applications/{app_id}.desktop",
                    f"install -Dm644 {metainfo_name} /app/share/metainfo/{metainfo_name}",
                ],
                "sources": [
                    {
                        "type": "archive",
                        "url": f"{release}/{x64}",
                        "sha256": assets[x64]["sha256"],
                        "only-arches": ["x86_64"],
                    },
                    {
                        "type": "archive",
                        "url": f"{release}/{arm64}",
                        "sha256": assets[arm64]["sha256"],
                        "only-arches": ["aarch64"],
                    },
                    {"type": "file", "path": metainfo_name},
                ],
            }
        ],
    }
    write(
        args.output,
        f"packaging/flatpak/{app_id}.json",
        json.dumps(flatpak_manifest, ensure_ascii=False, indent=2) + "\n",
    )

    write(args.output, "packaging/snap/snap/snapcraft.yaml", f'''
        name: caphetamine
        base: core24
        version: '{version}'
        summary: Prevent Linux sleep while Caps Lock is on
        description: |
          Caphetamine keeps the computer awake while Caps Lock is on and restores
          the normal power settings as soon as Caps Lock is turned off.
        grade: stable
        confinement: strict

        platforms:
          amd64:
          arm64:

        apps:
          caphetamine:
            command: bin/caphetamine
            desktop: share/applications/caphetamine.desktop
            common-id: {app_id}
            plugs:
              - desktop
              - desktop-legacy
              - wayland
              - x11
              - hardware-observe
              - login-session-control
              - screen-inhibit-control
              - autostart-config

        plugs:
          autostart-config:
            interface: personal-files
            write:
              - $HOME/.config/autostart/caphetamine.desktop

        parts:
          caphetamine:
            plugin: nil
            build-packages:
              - ca-certificates
              - curl
            override-pull: |
              case "$CRAFT_ARCH_BUILD_FOR" in
                amd64)
                  asset='{x64}'
                  checksum='{assets[x64]['sha256']}'
                  ;;
                arm64)
                  asset='{arm64}'
                  checksum='{assets[arm64]['sha256']}'
                  ;;
                *)
                  echo "Unsupported architecture: $CRAFT_ARCH_BUILD_FOR" >&2
                  exit 1
                  ;;
              esac
              curl --fail --location --retry 3 \\
                "{release}/$asset" --output caphetamine.tar.gz
              printf '%s  %s\\n' "$checksum" caphetamine.tar.gz | sha256sum --check -
              tar --extract --gzip --file caphetamine.tar.gz --strip-components=1
            override-build: |
              install -Dm755 bin/caphetamine "$CRAFT_PART_INSTALL/bin/caphetamine"
              install -Dm644 share/applications/caphetamine.desktop \\
                "$CRAFT_PART_INSTALL/share/applications/caphetamine.desktop"
              install -Dm644 share/icons/hicolor/scalable/apps/caphetamine.svg \\
                "$CRAFT_PART_INSTALL/share/icons/hicolor/scalable/apps/caphetamine.svg"
    ''')

    write(args.output, "manifests/latest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
