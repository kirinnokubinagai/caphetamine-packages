EAPI=8
DESCRIPTION="Prevent Linux sleep while Caps Lock is on"
HOMEPAGE="https://github.com/kirinnokubinagai/caphetamine-packages"
SRC_URI="amd64? ( https://github.com/kirinnokubinagai/caphetamine-packages/releases/download/v1.0.1/caphetamine-linux-x86_64.tar.gz ) arm64? ( https://github.com/kirinnokubinagai/caphetamine-packages/releases/download/v1.0.1/caphetamine-linux-aarch64.tar.gz )"
LICENSE="all-rights-reserved"
SLOT="0"
KEYWORDS="~amd64 ~arm64"
IUSE=""

if [[ ${ARCH} == amd64 ]]; then
  S="${WORKDIR}/caphetamine-${PV}-linux-x86_64"
else
  S="${WORKDIR}/caphetamine-${PV}-linux-aarch64"
fi

src_install() {
  dobin bin/caphetamine
  insinto /usr/share/applications
  doins share/applications/caphetamine.desktop
  insinto /usr/share/icons/hicolor/scalable/apps
  doins share/icons/hicolor/scalable/apps/caphetamine.svg
}
