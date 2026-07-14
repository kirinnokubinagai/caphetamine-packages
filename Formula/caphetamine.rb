class Caphetamine < Formula
  desc "Prevent Linux sleep while Caps Lock is on"
  homepage "https://github.com/kirinnokubinagai/caphetamine-packages"
  version "1.0.1"
  depends_on :linux

  if Hardware::CPU.arm?
    url "https://github.com/kirinnokubinagai/caphetamine-packages/releases/download/v1.0.1/caphetamine-linux-aarch64.tar.gz"
    sha256 "1990091e74ef2d52a6d9e3867911abde1961cd43608a1f016277fa59f359761b"
  else
    url "https://github.com/kirinnokubinagai/caphetamine-packages/releases/download/v1.0.1/caphetamine-linux-x86_64.tar.gz"
    sha256 "6bef25674d9422da359f62d84c41de9b0e1fdc8b2ae2fcc050d8d7485c1eb762"
  end

  def install
    bin.install Dir["*/bin/caphetamine"].first
    desktop = Dir["*/share/applications/caphetamine.desktop"].first
    icon = Dir["*/share/icons/hicolor/scalable/apps/caphetamine.svg"].first
    inreplace desktop, "Exec=caphetamine", "Exec=#{bin}/caphetamine"
    share.install desktop => "applications/caphetamine.desktop"
    (share/"icons/hicolor/scalable/apps").install icon
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/caphetamine --version")
  end
end
