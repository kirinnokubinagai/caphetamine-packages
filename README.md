# Caphetamine Packages

Caphetamineの公開バイナリ、署名、checksum、全パッケージマネージャーの定義を管理する単一リポジトリです。本体のソースコードはprivateリポジトリに置き、公開配布に必要なものだけをここへ公開します。

> [!NOTE]
> 現在は配布基盤の準備中です。最初のReleaseが公開されるまで、以下のインストールコマンドはまだ成功しません。

## 対応範囲

| OS・ディストリビューション | 導入経路 | 配布形式 |
| --- | --- | --- |
| macOS | Homebrew Cask、Nix、MacPorts、直接導入 | Universal 2 DMG / ZIP |
| Debian / Ubuntu | APT、直接導入 | deb |
| Fedora / RHEL / Rocky / Alma | DNF / YUM | rpm |
| openSUSE / SLES | Zypper | rpm |
| Arch / Manjaro | pacman | pkg.tar.zst |
| Alpine | apk | apk（musl） |
| NixOS / Linux / nix-darwin | Nix Flake | 固定hashのバイナリパッケージ |
| Void Linux | XBPS template | glibc / musl |
| Gentoo | Portage overlay | ebuild |
| Linux | pkgsrc | pkgsrc定義 |
| その他のmacOS / Linux | curl、GitHub Releases | DMG / ZIP / tar.gz |

deb・rpm・apk・Archパッケージは、同じnFPM定義から生成します。すべての定義は`manifests/latest.json`のバージョン、asset URL、SHA-256を参照して生成されるため、パッケージごとの手動バージョンずれを作りません。

## 簡単インストール

Linuxでは使用中のパッケージマネージャーを自動判定し、署名鍵とrepositoryを登録できます。

```sh
curl -fsSL https://raw.githubusercontent.com/kirinnokubinagai/caphetamine-packages/main/scripts/setup_repository.sh | sh
```

## Homebrew

Homebrewの規約上、`homebrew-`で始まらないGitHubリポジトリはURLを明示してtapします。パッケージを分散させず、このリポジトリをそのまま使います。

```sh
brew tap kirinnokubinagai/caphetamine \
  https://github.com/kirinnokubinagai/caphetamine-packages
brew trust kirinnokubinagai/caphetamine

# macOS
brew install --cask caphetamine

# Linux
brew install caphetamine
```

## Nix / NixOS / nix-darwin

```sh
nix profile install github:kirinnokubinagai/caphetamine-packages#caphetamine
nix run github:kirinnokubinagai/caphetamine-packages
```

Flakeは`aarch64-darwin`、`x86_64-darwin`、`aarch64-linux`、`x86_64-linux`を提供します。

## APT（Debian / Ubuntu）

repositoryは専用OpenPGP鍵で署名し、`Signed-By`によってCaphetamine repositoryだけに信頼範囲を限定します。

```sh
curl -fsSL https://kirinnokubinagai.github.io/caphetamine-packages/keys/caphetamine-archive-keyring.gpg |
  sudo tee /usr/share/keyrings/caphetamine-archive-keyring.gpg >/dev/null

curl -fsSL https://kirinnokubinagai.github.io/caphetamine-packages/apt/caphetamine.sources |
  sudo tee /etc/apt/sources.list.d/caphetamine.sources >/dev/null

sudo apt update
sudo apt install caphetamine
```

## DNF / YUM / Zypper（RPM系）

rpm本体と`repodata/repomd.xml`の両方を署名します。

```sh
# Fedora / RHEL系
sudo curl -fsSL \
  https://kirinnokubinagai.github.io/caphetamine-packages/rpm/caphetamine.repo \
  -o /etc/yum.repos.d/caphetamine.repo
sudo dnf install caphetamine

# openSUSE / SLES
sudo curl -fsSL \
  https://kirinnokubinagai.github.io/caphetamine-packages/rpm/caphetamine.repo \
  -o /etc/zypp/repos.d/caphetamine.repo
sudo zypper --gpg-auto-import-keys refresh
sudo zypper install caphetamine
```

## pacman（Arch / Manjaro）

パッケージとrepository databaseの両方に署名します。鍵登録を含む`setup_repository.sh`の使用を推奨します。

```ini
[caphetamine]
SigLevel = Required DatabaseRequired
Server = https://kirinnokubinagai.github.io/caphetamine-packages/arch/$arch
```

登録後は通常のpacman操作で導入・更新できます。

```sh
sudo pacman -Syu caphetamine
```

## apk（Alpine）

Alpine向けにはglibcバイナリを流用せず、muslターゲットを別にビルドします。

```sh
sudo curl -fsSL \
  https://kirinnokubinagai.github.io/caphetamine-packages/keys/caphetamine.rsa.pub \
  -o /etc/apk/keys/caphetamine.rsa.pub
echo "https://kirinnokubinagai.github.io/caphetamine-packages/alpine/$(apk --print-arch)" |
  sudo tee -a /etc/apk/repositories
sudo apk update
sudo apk add caphetamine
```

## その他

- MacPorts：`packaging/macports/Portfile`
- Void Linux：`packaging/void/template`
- Gentoo：`packaging/gentoo/`
- pkgsrc（Linuxのみ）：`packaging/pkgsrc/`
- GitHub Releases：DMG、ZIP、glibc/musl tar.gz、deb、rpm、apk、pkg.tar.zst

直接インストールする場合は、同じReleaseにある`SHA256SUMS`を検証します。

```sh
curl -fsSL https://raw.githubusercontent.com/kirinnokubinagai/caphetamine-packages/main/scripts/install.sh | sh
```

FlatpakとSnapは、Caps Lock LEDの`/sys/class/leds`読み取りとlogind inhibitorに広いsandbox権限が必要になるため、動作を弱めたパッケージを先に公開せず別途検証します。

## リリース処理

1. private本体リポジトリがmacOS、Linux glibc、Linux muslの基礎assetをこのリポジトリのGitHub Releaseへ送る
2. Releaseイベントからdeb、rpm、apk、Archパッケージを生成する
3. `manifests/latest.json`からHomebrew、Nix、MacPorts、Void、Gentoo、pkgsrc定義を生成する
4. APT、RPM、pacman、apkのindexとnative signatureを生成する
5. GitHub Pagesへrepositoryを公開する
6. 生成定義をPRとしてmainへ反映する

必要なGitHub Actions secretsは次の通りです。

| Secret | 用途 |
| --- | --- |
| `PACKAGE_GPG_PRIVATE_KEY_B64` | APT、RPM、pacman署名用OpenPGP秘密鍵 |
| `PACKAGE_GPG_KEY_ID` | 署名鍵のfingerprint |
| `PACKAGE_GPG_PASSPHRASE` | OpenPGP秘密鍵のpassphrase |
| `PACKAGE_APK_PRIVATE_KEY_B64` | apk署名用のpassphraseなしRSA秘密鍵 |

## 開発・検証

```sh
python3 -m unittest discover -s tests -v
shellcheck scripts/*.sh
actionlint .github/workflows/*.yml
```
