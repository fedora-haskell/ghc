#!/bin/sh

# generates a Fedora distro package status file for hackage.haskell.org

PKGS="ghc-Boolean ghc-GLUT ghc-HTTP ghc-HUnit ghc-OpenGL ghc-QuickCheck ghc-X11 ghc-X11-xft alex ghc-attoparsec ghc-base64-bytestring ghc-binary ghc-bytestring-trie cabal-install ghc-cairo ghc-cgi ghc-chalmers-lava2000 ghc-cmdargs ghc-colour cpphs ghc-csv darcs ghc-dataenc ghc-deepseq ghc-editline ghc-feldspar-language ghc-fgl ghc-ghc-paths ghc-gio ghc-glade ghc-glib ghc-gtk gtk2hs-buildtools ghc-gtksourceview2 happy ghc-hashed-storage ghc-haskeline ghc-haskell-src ghc-haskell-src-exts ghc-hinotify hlint ghc-hslogger hscolour ghc-html ghc-libmpd ghc-mmap ghc-mtl ghc-network ghc-pango ghc-parallel ghc-parsec ghc-regex-base ghc-regex-compat ghc-regex-posix ghc-regex-tdfa ghc-split ghc-stm ghc-syb ghc-tagsoup ghc-tar ghc-terminfo ghc-text ghc-transformers ghc-type-level ghc-uniplate ghc-utf8-string ghc-xhtml xmobar xmonad ghc-xmonad-contrib ghc-zlib"

for p in $PKGS; do
  LATEST=$(koji latest-pkg --quiet dist-rawhide $p | cut -f1 -d' ' | sed -e "s/\(.*\)-.*/\1/")
  HACKAGE=$(echo $p | sed -e "s/^ghc-//")
  VERSION=$(echo $LATEST | sed -e "s/^$p-//")
  if [ -n "$VERSION" ]; then
    echo "(\"$HACKAGE\",\"$VERSION\",Just \"https://admin.fedoraproject.org/pkgdb/acls/name/$p\")"
  fi
done
