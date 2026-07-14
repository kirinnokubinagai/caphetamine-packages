cask "caphetamine" do
  version "1.0.0"
  sha256 "4191be8d97060ae8232298f61565309a41df7ef054f0207d26ea792bce989229"

  url "https://github.com/kirinnokubinagai/caphetamine-packages/releases/download/v1.0.0/Caphetamine-macos-universal.dmg"
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
