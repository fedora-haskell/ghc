#!/bin/sh

GHCVER=$(basename $PWD | sed -e "s/ghc-//")

if [ ! -d libraries ]; then
    echo Is CWD a ghc source tree?
    exit 1
fi

cd libraries

grep -i ^version: Cabal/Cabal/Cabal.cabal */*.cabal | grep -v -e "\(Win32\|gmp.old\|gmp2\|integer-simple\|$GHCVER\)" | sed -e "s!/.*: \+!_ver !" -e "s/-/_/g"
