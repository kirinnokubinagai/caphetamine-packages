cask "caphetamine" do
  version "1.0.1"
  sha256 "cc3c083e7245d473f56f8ce40d9fa5573af79b0ee5beeca27176e03ee79949b9"

  url "https://github.com/kirinnokubinagai/caphetamine-packages/releases/download/v1.0.1/Caphetamine-macos-universal.dmg"
  name "Caphetamine"
  desc "Prevent sleep while Caps Lock is on"
  homepage "https://github.com/kirinnokubinagai/caphetamine-packages"

  depends_on macos: :ventura

  app "Caphetamine.app"

  zap trash: [
    "~/Library/Preferences/com.kirinnokubinagaiyo.caphetamine.plist",
    "~/Library/Saved Application State/com.kirinnokubinagaiyo.caphetamine.savedState",
  ]
end
