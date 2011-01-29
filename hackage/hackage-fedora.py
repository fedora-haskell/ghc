#!/usr/bin/python

# generates a Fedora distro package status file for hackage.haskell.org

from fedora.client import PackageDB
import koji

pkgdb = PackageDB()
p = pkgdb.user_packages('haskell-sig')

# exclude packages not in Hackage
packages = [pkg['name'] for pkg in p.pkgs if pkg['name'] not in ['cabal2spec','emacs-haskell-mode','ghc','ghc-gtk2hs','ghc-rpm-macros','haskell-platform','hugs98']]

session = koji.ClientSession('http://koji.fedoraproject.org/kojihub')

outlist = []

for pkg in packages:
    latest = session.getLatestBuilds('dist-f14-updates', package=pkg)
    if latest:
        ver = latest[0]['version']
        name = pkg.replace('ghc-','',1)
        print "%s-%s" % (name,ver)
        result = "(\"%s\",\"%s\",Just \"https://admin.fedoraproject.org/community/?package=%s#package_maintenance\")" % (name,ver,pkg)
        outlist.append(result)

f = open('Fedora', 'w')

for l in sorted(outlist):
    f.write(l+'\n')
