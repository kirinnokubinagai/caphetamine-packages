import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "Caphetamine-macos-universal.zip",
    "Caphetamine-macos-universal.dmg",
    "caphetamine-linux-x86_64.tar.gz",
    "caphetamine-linux-aarch64.tar.gz",
    "caphetamine-linux-x86_64-musl.tar.gz",
    "caphetamine-linux-aarch64-musl.tar.gz",
)


class GenerationTests(unittest.TestCase):
    def test_one_manifest_generates_every_definition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            assets = work / "assets"
            assets.mkdir()
            for name in REQUIRED:
                (assets / name).write_bytes(f"fixture:{name}".encode())
            (assets / "caphetamine_1.2.3_amd64.deb").write_bytes(b"generated package")

            manifest = work / "manifest.json"
            subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/create_manifest.py"),
                    "--version",
                    "1.2.3",
                    "--assets",
                    str(assets),
                    "--output",
                    str(manifest),
                ],
                check=True,
            )
            output = work / "generated"
            subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/generate_definitions.py"),
                    str(manifest),
                    "--output",
                    str(output),
                ],
                check=True,
            )

            data = json.loads(manifest.read_text())
            self.assertEqual(data["version"], "1.2.3")
            self.assertEqual(set(REQUIRED), set(data["assets"]))
            for relative in (
                "Casks/caphetamine.rb",
                "Formula/caphetamine.rb",
                "flake.nix",
                "packaging/macports/Portfile",
                "packaging/void/template",
                "packaging/pkgsrc/Makefile",
                "packaging/gentoo/app-misc/caphetamine-bin/caphetamine-bin-1.2.3.ebuild",
                "manifests/latest.json",
            ):
                self.assertTrue((output / relative).is_file(), relative)

            cask = (output / "Casks/caphetamine.rb").read_text()
            self.assertIn('version "1.2.3"', cask)
            self.assertNotIn(":no_check", cask)

            pkgsrc = (output / "packaging/pkgsrc/Makefile").read_text()
            self.assertIn("ONLY_FOR_PLATFORM= Linux-*-*", pkgsrc)


if __name__ == "__main__":
    unittest.main()
