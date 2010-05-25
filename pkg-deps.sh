#!/bin/sh

# script to generate dependency graph for fedora haskell libraries
# requires ghc, ghc-*-devel and graphviz to be installed 

set -e

mkdir -p .pkg-deps

cd .pkg-deps

ghc-pkg dot --global > pkgs.dot

cp -p pkgs.dot pkgs.dot.orig

GHC_PKGS="array base-4 base-3 bin-package-db bytestring Cabal containers directory dph extensible-exceptions filepath ghc-6.12 ghc-binary ghc-prim haskell98 hpc integer-gmp old-locale old-time pretty process random syb template-haskell time unix utf8-string-0.3.4 Win32"

# ignore library packages provided by ghc
for i in $GHC_PKGS; do sed -i -e /$i/d pkgs.dot; done

cat pkgs.dot | tred | dot -Nfontsize=8 -Tsvg >pkgs.svg

xdg-open pkgs.svg
