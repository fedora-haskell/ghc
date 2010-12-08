#!/usr/bin/python

# generates a Fedora distro package status file for hackage.haskell.org

from fedora.client import PackageDB
import koji

pkgdb = PackageDB()
p = pkgdb.user_packages('haskell-sig')

# exclude packages not in Hackage
packages = [pkg['name'] for pkg in p.pkgs if pkg['name'] not in ['cabal2spec','emacs-haskell-mode','ghc','ghc-gtk2hs','ghc-rpm-macros','haddock','haskell-platform','hugs98']]

session = koji.ClientSession('http://koji.fedoraproject.org/kojihub')

for pkg in packages:
    latest = session.getLatestBuilds('dist-rawhide', package=pkg)
    if latest:
        ver = latest[0]['version']
        name = pkg.replace('ghc-','',1)
        print "(\"%s\",\"%s\",Just \"https://admin.fedoraproject.org/pkgdb/acls/name/%s\")" % (name,ver,pkg)

# todo
## sort output
