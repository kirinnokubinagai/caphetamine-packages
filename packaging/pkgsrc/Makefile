DISTNAME=       caphetamine-1.0.1
PKGNAME=        caphetamine-1.0.1
CATEGORIES=     sysutils
MASTER_SITES=   https://github.com/kirinnokubinagai/caphetamine-packages/releases/download/v1.0.1/
COMMENT=        Prevent Linux sleep while Caps Lock is on
NO_BUILD=       yes
ONLY_FOR_PLATFORM= Linux-*-*

.if ${MACHINE_ARCH} == "x86_64"
DISTFILES=      caphetamine-linux-x86_64.tar.gz
WRKSRC=         ${WRKDIR}/caphetamine-1.0.1-linux-x86_64
.elif ${MACHINE_ARCH} == "aarch64"
DISTFILES=      caphetamine-linux-aarch64.tar.gz
WRKSRC=         ${WRKDIR}/caphetamine-1.0.1-linux-aarch64
.else
PKG_FAIL_REASON+= "Unsupported architecture ${MACHINE_ARCH}"
.endif

do-install:
	${INSTALL_PROGRAM} ${WRKSRC}/bin/caphetamine ${DESTDIR}${PREFIX}/bin
	${INSTALL_DATA_DIR} ${DESTDIR}${PREFIX}/share/applications
	${INSTALL_DATA} ${WRKSRC}/share/applications/caphetamine.desktop ${DESTDIR}${PREFIX}/share/applications
	${INSTALL_DATA_DIR} ${DESTDIR}${PREFIX}/share/icons/hicolor/scalable/apps
	${INSTALL_DATA} ${WRKSRC}/share/icons/hicolor/scalable/apps/caphetamine.svg ${DESTDIR}${PREFIX}/share/icons/hicolor/scalable/apps

.include "../../mk/bsd.pkg.mk"
