#!/bin/sh

# script to generate dependency graph for fedora haskell libraries
# requires ghc, ghc-*-devel and graphviz to be installed 

set -e

mkdir -p .pkg-deps

cd .pkg-deps

# remove the closing line
ghc-pkg dot --global | sed '$d' > pkgs.dot

# check for binary deps too
for i in alex cabal-install cpphs darcs happy haskell-platform hedgewars hscolour kaya xmonad; do
  PKG=`rpm -q --qf "%{name}-%{version}" $i` || echo $i is not installed
  rpm -q --requires $i | grep ghc6 | sed -e "s/libHS/\"$PKG\" -> \"/g" -e "s/-ghc6.*/\"/" >> pkgs.dot
done

# and add it back
echo "}" >> pkgs.dot

cp -p pkgs.dot pkgs.dot.orig

# ignore library packages provided by ghc
GHC_PKGS="array base-4 base-3 bin-package-db bytestring Cabal containers directory dph extensible-exceptions filepath ffi ghc-6.12 ghc-binary ghc-prim haskell98 hpc integer-gmp old-locale old-time pretty process random rts syb template-haskell time unix utf8-string-0.3.4 Win32"
for i in $GHC_PKGS; do sed -i -e /$i/d pkgs.dot; done

cat pkgs.dot | tred | dot -Nfontsize=8 -Tsvg >pkgs.svg

xdg-open pkgs.svg
