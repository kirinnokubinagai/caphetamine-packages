# Unified package repositories

- [x] 公開配布を`caphetamine-packages`の1リポジトリに統一する
- [x] 1つのmanifestからHomebrew、Nix、MacPorts、Void、Gentoo、pkgsrc定義を生成する
- [x] 1つのnFPM定義からdeb、rpm、Arch、apkパッケージを生成する
- [x] 署名付きAPT、RPM、pacman、Alpine repositoryをGitHub Pagesへ生成する
- [x] root、sudo、doas環境に対応したrepository設定スクリプトを用意する
- [x] private本体リポジトリから配布定義を分離する
- [ ] 両リポジトリのCIを通してpushする
