#!/usr/bin/env python3

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--arch", choices=("amd64", "arm64"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rpm-key")
    parser.add_argument("--apk-key")
    args = parser.parse_args()

    rpm_signature = " {}"
    if args.rpm_key:
        rpm_signature = f"\n  signature:\n    key_file: {args.rpm_key}\n"
    apk_signature = " {}"
    if args.apk_key:
        apk_signature = f"\n  signature:\n    key_file: {args.apk_key}\n    key_name: caphetamine.rsa.pub\n"

    args.output.write_text(f'''name: caphetamine
arch: {args.arch}
platform: linux
version: {args.version}
release: 1
section: utils
priority: optional
maintainer: Caphetamine <noreply@github.com>
description: Prevent Linux sleep while Caps Lock is on
homepage: https://github.com/kirinnokubinagai/caphetamine-packages
license: Proprietary
contents:
  - src: {args.stage}/bin/caphetamine
    dst: /usr/bin/caphetamine
    file_info:
      mode: 0755
  - src: {args.stage}/share/applications/caphetamine.desktop
    dst: /usr/share/applications/caphetamine.desktop
    file_info:
      mode: 0644
  - src: {args.stage}/share/icons/hicolor/scalable/apps/caphetamine.svg
    dst: /usr/share/icons/hicolor/scalable/apps/caphetamine.svg
    file_info:
      mode: 0644
overrides:
  deb:
    depends:
      - dbus
      - systemd | elogind
  rpm:
    depends:
      - dbus
      - systemd
  apk:
    depends:
      - dbus
      - elogind
  archlinux:
    depends:
      - dbus
      - systemd-libs
rpm:{rpm_signature}
apk:{apk_signature}
''')


if __name__ == "__main__":
    main()
