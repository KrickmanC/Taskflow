#!/usr/bin/env bash
set -euo pipefail

VERSION="${VERSION:-1.3.0}"
ARCH="amd64"
PKG_ROOT="dist/taskflow-native_${VERSION}_${ARCH}"
REPO_ROOT="$(pwd)"

rm -rf "$PKG_ROOT"
mkdir -p "$PKG_ROOT/DEBIAN"
mkdir -p "$PKG_ROOT/opt/taskflow/repo"
mkdir -p "$PKG_ROOT/opt/taskflow/bin"
mkdir -p "$PKG_ROOT/etc/taskflow"
mkdir -p "$PKG_ROOT/var/lib/taskflow"
mkdir -p "$PKG_ROOT/var/log/taskflow"

rsync -a \
  --exclude ".git" \
  --exclude "node_modules" \
  --exclude ".turbo" \
  --exclude "dist" \
  "$REPO_ROOT/" "$PKG_ROOT/opt/taskflow/repo/"

curl -fsSL https://dl.min.io/server/minio/release/linux-amd64/minio -o "$PKG_ROOT/opt/taskflow/bin/minio"
chmod 755 "$PKG_ROOT/opt/taskflow/bin/minio"

cp tools/install/linux/debian/control "$PKG_ROOT/DEBIAN/control"
cp tools/install/linux/preinst "$PKG_ROOT/DEBIAN/preinst"
cp tools/install/linux/postinst "$PKG_ROOT/DEBIAN/postinst"
cp tools/install/linux/prerm "$PKG_ROOT/DEBIAN/prerm"
cp tools/install/linux/postrm "$PKG_ROOT/DEBIAN/postrm"

chmod 755 "$PKG_ROOT/DEBIAN/preinst"
chmod 755 "$PKG_ROOT/DEBIAN/postinst"
chmod 755 "$PKG_ROOT/DEBIAN/prerm"
chmod 755 "$PKG_ROOT/DEBIAN/postrm"

dpkg-deb --build "$PKG_ROOT"
