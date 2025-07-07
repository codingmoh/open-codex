#!/bin/bash

set -e

APPNAME="open-codex"
VERSION="0.1.17"
DEBBUILD_DIR="debbuild"
PKGROOT="$DEBBUILD_DIR/${APPNAME}_${VERSION}"

echo "Building .deb package for $APPNAME $VERSION"

# Prepare directories
rm -rf "$PKGROOT"
mkdir -p "$PKGROOT/DEBIAN"
mkdir -p "$PKGROOT/opt/$APPNAME"
mkdir -p "$PKGROOT/usr/bin"

cp -r dist/open-codex/* "$PKGROOT/opt/$APPNAME/"

cat <<CONTROL > "$PKGROOT/DEBIAN/control"
Package: $APPNAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Mo <coding.moh@gmail.com>
Description: LLM-Based CLI tool to generate shell commands from natural language
CONTROL

# start
cat <<WRAP > "$PKGROOT/usr/bin/$APPNAME"
#!/bin/bash
exec /opt/$APPNAME/open-codex "\$@"
WRAP

chmod +x "$PKGROOT/usr/bin/$APPNAME"

# Paket bauen
dpkg-deb --build "$PKGROOT"
echo "Done: $PKGROOT.deb"
