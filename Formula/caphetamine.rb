class Caphetamine < Formula
  desc "Prevent Linux sleep while Caps Lock is on"
  homepage "https://github.com/kirinnokubinagai/caphetamine-packages"
  version "1.0.0"
  depends_on :linux

  if Hardware::CPU.arm?
    url "https://github.com/kirinnokubinagai/caphetamine-packages/releases/download/v1.0.0/caphetamine-linux-aarch64.tar.gz"
    sha256 "3c0b1f9b1e249cacf6268039df785352054b84b117c9dcf46d563fba0762f2b3"
  else
    url "https://github.com/kirinnokubinagai/caphetamine-packages/releases/download/v1.0.0/caphetamine-linux-x86_64.tar.gz"
    sha256 "d7b986ce38f915e764e19391e88fd1d5a265835c2c44dcb0d70bc700a1ebffa9"
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
