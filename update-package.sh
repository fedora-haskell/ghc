#!/bin/sh

set -e -x

PKG=$1

cd ~/fedora/haskell/$PKG/master
git pull

cat ~/fedora/haskell/cabal2spec/master/cabal2spec-0.22.4.diff | sed -e "s/@PKG@/$PKG/" | patch -p1

rpmdev-bumpspec --comment="update to cabal2spec-0.22.4" $PKG.spec

fedpkg commit -p -m "update to cabal2spec-0.22.4"
