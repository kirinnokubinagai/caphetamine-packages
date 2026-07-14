#!/usr/bin/env python3

import argparse
import base64
import hashlib
import json
from pathlib import Path


REQUIRED_ASSETS = (
    "Caphetamine-macos-universal.zip",
    "Caphetamine-macos-universal.dmg",
    "caphetamine-linux-x86_64.tar.gz",
    "caphetamine-linux-aarch64.tar.gz",
    "caphetamine-linux-x86_64-musl.tar.gz",
    "caphetamine-linux-aarch64-musl.tar.gz",
)


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Caphetamine release manifest")
    parser.add_argument("--version", required=True)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    missing = [name for name in REQUIRED_ASSETS if not (args.assets / name).is_file()]
    if missing:
        raise SystemExit(f"missing required assets: {', '.join(missing)}")

    assets = {}
    # Generated native packages and this manifest are uploaded to the same Release.
    # Only the immutable base archives belong here, otherwise every rerun changes
    # the manifest by hashing the previous run's generated artifacts.
    for name in REQUIRED_ASSETS:
        path = args.assets / name
        sha256 = digest(path, "sha256")
        assets[path.name] = {
            "size": path.stat().st_size,
            "sha256": sha256,
            "sha256_sri": "sha256-" + base64.b64encode(bytes.fromhex(sha256)).decode(),
            "sha512": digest(path, "sha512"),
            "blake2s": digest(path, "blake2s"),
            "blake2b": digest(path, "blake2b"),
        }

    manifest = {
        "schema": 1,
        "version": args.version.removeprefix("v"),
        "tag": f"v{args.version.removeprefix('v')}",
        "repository": "kirinnokubinagai/caphetamine-packages",
        "assets": assets,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
