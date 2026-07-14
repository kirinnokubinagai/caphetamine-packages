{
  description = "Unified Caphetamine binary packages";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs }:
    let
      systems = [ "aarch64-darwin" "x86_64-darwin" "aarch64-linux" "x86_64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      sources = {
        "aarch64-darwin" = { url = "https://github.com/kirinnokubinagai/caphetamine-packages/releases/download/v1.0.0/Caphetamine-macos-universal.zip"; hash = "sha256-bcn7BIQr8oQCx4McmtVc0FcPTfAAV6TAAZwLgEl5qAc="; kind = "darwin"; };
"x86_64-darwin" = { url = "https://github.com/kirinnokubinagai/caphetamine-packages/releases/download/v1.0.0/Caphetamine-macos-universal.zip"; hash = "sha256-bcn7BIQr8oQCx4McmtVc0FcPTfAAV6TAAZwLgEl5qAc="; kind = "darwin"; };
"aarch64-linux" = { url = "https://github.com/kirinnokubinagai/caphetamine-packages/releases/download/v1.0.0/caphetamine-linux-aarch64.tar.gz"; hash = "sha256-PAsfmx4knKz2JoA533hTUgVLhLEXydz0bVY/ugdi8rM="; kind = "linux"; };
"x86_64-linux" = { url = "https://github.com/kirinnokubinagai/caphetamine-packages/releases/download/v1.0.0/caphetamine-linux-x86_64.tar.gz"; hash = "sha256-17mGzjj5Fedk4ZOR6I/R1aJlg1wsRNyw1wvHAKHr/6k="; kind = "linux"; };
      };
    in {
      packages = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          source = sources.${system};
          archive = pkgs.fetchzip { inherit (source) url hash; stripRoot = false; };
        in {
          default = pkgs.stdenvNoCC.mkDerivation {
            pname = "caphetamine";
            version = "1.0.0";
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
              substituteInPlace "$out/share/applications/caphetamine.desktop" \
                --replace-fail 'Exec=caphetamine' "Exec=$out/bin/caphetamine"
            '';
            meta.mainProgram = "caphetamine";
          };
        });
      apps = forAllSystems (system: {
        default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/caphetamine";
          meta.description = "Run Caphetamine";
        };
      });
    };
}
