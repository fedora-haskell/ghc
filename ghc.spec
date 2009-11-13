# test builds can made faster and smaller by disabling profiled libraries
# (currently libHSrts_thr_p.a breaks no prof build)
%bcond_without prof
# build users_guide, etc
%bcond_without manual

# experimental
## shared libraries support available in ghc >= 6.11
%bcond_with shared
## include colored html src
%bcond_with hscolour

%global haddock_version 2.5.0

# Fixing packaging problems can be a tremendous pain because it
# generally requires a complete rebuild, which takes hours.  To offset
# the misery, do a complete build once using "rpmbuild -bc", then copy
# your built tree to a directory of the same name suffixed with
# ".built", using "cp -al".  Finally, set this variable, and it will
# copy the already-built tree into place during build instead of
# actually doing the build.
#
# Obviously, this can only work if you leave the build section
# completely untouched between builds.
%global package_debugging 0

Name: ghc
# part of haskell-platform-2009.2.0.2
Version: 6.12.0.20091010
Release: 3%{?dist}
Summary: Glasgow Haskell Compilation system
# fedora ghc has only been bootstrapped on the following archs:
ExclusiveArch: %{ix86} x86_64 alpha
License: BSD
Group: Development/Languages
Source0: http://www.haskell.org/ghc/dist/%{version}/ghc-%{version}-src.tar.bz2
URL: http://haskell.org/ghc/
Requires: gcc, gmp-devel
Requires(post): policycoreutils
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Obsoletes: ghc682, ghc681, ghc661, ghc66, haddock09
# introduced for f11 and can be removed for f13:
Obsoletes: haddock < %{haddock_version}, ghc-haddock-devel < %{haddock_version}
Provides: haddock = %{haddock_version}, ghc-haddock-devel = %{haddock_version}
BuildRequires: ghc, happy, sed, ncurses-devel
BuildRequires: gmp-devel
%if %{with shared}
# not sure if this is actually needed
BuildRequires: libffi-devel
%endif
%if %{with manual}
BuildRequires: libxslt, docbook-style-xsl
%endif
%if %{with hscolour}
BuildRequires: hscolour
%endif

%description
GHC is a state-of-the-art programming suite for Haskell, a purely
functional programming language.  It includes an optimising compiler
generating good code for a variety of platforms, together with an
interactive system for convenient, quick development.  The
distribution includes space and time profiling facilities, a large
collection of libraries, and support for various language
extensions, including concurrency, exceptions, and a foreign language
interface.

%package doc
Summary: Documentation for GHC
Group: Development/Languages
Requires: %{name} = %{version}-%{release}
# for haddock
Requires(posttrans): %{name} = %{version}-%{release}
Obsoletes: ghc-haddock-doc < %{haddock_version}
Provides: ghc-haddock-doc = %{haddock_version}

%description doc
Preformatted documentation for the Glorious Glasgow Haskell
Compilation System (GHC) and its libraries.  It should be installed if
you like to have local access to the documentation in HTML format.

%if %{with shared}
%package libs
Summary: Shared libraries for GHC
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description libs
Shared libraries for Glorious Glasgow Haskell Compilation System
(GHC).  They should be installed to build standalone programs.
%endif

%if %{with prof}
%package prof
Summary: Profiling libraries for GHC
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Obsoletes: ghc682-prof, ghc681-prof, ghc661-prof, ghc66-prof
Obsoletes: ghc-haddock-prof < %{haddock_version}
Provides: ghc-haddock-prof = %{haddock_version}

%description prof
Profiling libraries for Glorious Glasgow Haskell Compilation System
(GHC).  They should be installed when GHC's profiling subsystem is
needed.
%endif

# the debuginfo subpackage is currently empty anyway, so don't generate it
%global debug_package %{nil}

%prep
%setup -q -n %{name}-%{version}

%build
# hack for building a local test package quickly from a prebuilt tree 
%if %{package_debugging}
pushd ..
rm -rf %{name}-%{version}
cp -al %{name}-%{version}.built %{name}-%{version}
popd
exit 0
%endif

%if %{without prof}
echo "GhcLibWays = %{?with_shared:dyn}" >> mk/build.mk
%endif

%if %{with manual}
echo "XMLDocWays = html" >> mk/build.mk
%endif

./configure --prefix=%{_prefix} --exec-prefix=%{_exec_prefix} \
  --bindir=%{_bindir} --sbindir=%{_sbindir} --sysconfdir=%{_sysconfdir} \
  --datadir=%{_datadir} --includedir=%{_includedir} --libdir=%{_libdir} \
  --libexecdir=%{_libexecdir} --localstatedir=%{_localstatedir} \
  --sharedstatedir=%{_sharedstatedir} --mandir=%{_mandir} \
  %{?with_shared:--enable-shared}

make %{_smp_mflags}

%if %{with manual}
echo XXX no longer supported - make %{_smp_mflags} html
%endif

%install
rm -rf $RPM_BUILD_ROOT

make DESTDIR=${RPM_BUILD_ROOT} install

%if %{with manual}
echo XXX unnecessary make DESTDIR=${RPM_BUILD_ROOT} install-docs
%endif

SRC_TOP=$PWD
rm -f rpm-*.files
( cd $RPM_BUILD_ROOT
  find .%{_libdir}/%{name}-%{version} \( -type d -fprintf $SRC_TOP/rpm-dir.files "%%%%dir %%p\n" \) -o \( -type f \( -name '*.p_hi' -o -name '*_p.a' \) -fprint $SRC_TOP/rpm-prof.files \) -o \( -not -name 'package.conf*' -fprint $SRC_TOP/rpm-lib.files \)
  find .%{_docdir}/%{name}/* -type d ! -name libraries ! -name src > $SRC_TOP/rpm-doc-dir.files
)

# make paths absolute (filter "./usr" to "/usr")
sed -i -e "s|\.%{_prefix}|%{_prefix}|" rpm-*.files

cat rpm-dir.files rpm-lib.files > rpm-base.files

# these are handled as alternatives
for i in hsc2hs runhaskell; do
  if [ -x ${RPM_BUILD_ROOT}%{_bindir}/$i-ghc ]; then
    rm ${RPM_BUILD_ROOT}%{_bindir}/$i
  else
    mv ${RPM_BUILD_ROOT}%{_bindir}/$i{,-ghc}
  fi
done

%check
# stolen from ghc6/debian/rules:
# Do some very simple tests that the compiler actually works
rm -rf testghc
mkdir testghc
echo 'main = putStrLn "Foo"' > testghc/foo.hs
inplace/bin/ghc-stage2 testghc/foo.hs -o testghc/foo
[ "$(testghc/foo)" = "Foo" ]
rm testghc/*
echo 'main = putStrLn "Foo"' > testghc/foo.hs
inplace/bin/ghc-stage2 testghc/foo.hs -o testghc/foo -O2
[ "$(testghc/foo)" = "Foo" ]
rm testghc/*

%clean
rm -rf $RPM_BUILD_ROOT

%post
# Alas, GHC, Hugs, and nhc all come with different set of tools in
# addition to a runFOO:
#
#   * GHC:  hsc2hs
#   * Hugs: hsc2hs, cpphs
#   * nhc:  cpphs
#
# Therefore it is currently not possible to use --slave below to form
# link groups under a single name 'runhaskell'. Either these tools
# should be disentangled from the Haskell implementations, or all
# implementations should have the same set of tools. *sigh*

update-alternatives --install %{_bindir}/runhaskell runhaskell \
  %{_bindir}/runghc 500
update-alternatives --install %{_bindir}/hsc2hs hsc2hs \
  %{_bindir}/hsc2hs-ghc 500

%if %{with shared}
%post libs -p /sbin/ldconfig
%endif

%preun
if [ "$1" = 0 ]; then
  update-alternatives --remove runhaskell %{_bindir}/runghc
  update-alternatives --remove hsc2hs     %{_bindir}/hsc2hs-ghc
fi

%if %{with shared}
%postun libs -p /sbin/ldconfig
%endif

%posttrans doc
# (posttrans to make sure any old documentation has been removed first)
( cd %{_docdir}/ghc/libraries && ./gen_contents_index ) || :

%files -f rpm-base.files
%defattr(-,root,root,-)
%doc ANNOUNCE HACKING LICENSE README
%{_bindir}/*
%if %{with manual}
%{_mandir}/man1/ghc.*
%endif
%config(noreplace) %{_libdir}/ghc-%{version}/package.conf

%files doc -f rpm-doc-dir.files
%defattr(-,root,root,-)
%dir %{_docdir}/%{name}
%{_docdir}/%{name}/LICENSE
%if %{with manual}
%{_docdir}/%{name}/index.html
%endif
%{_docdir}/%{name}/libraries/gen_contents_index
%{_docdir}/%{name}/libraries/prologue.txt
%dir %{_docdir}/%{name}/libraries
%ghost %{_docdir}/%{name}/libraries/doc-index.html
%ghost %{_docdir}/%{name}/libraries/haddock.css
%ghost %{_docdir}/%{name}/libraries/haddock-util.js
%ghost %{_docdir}/%{name}/libraries/haskell_icon.gif
%ghost %{_docdir}/%{name}/libraries/index.html
%ghost %{_docdir}/%{name}/libraries/minus.gif
%ghost %{_docdir}/%{name}/libraries/plus.gif

%if %{with prof}
%files prof -f rpm-prof.files
%defattr(-,root,root,-)
%endif

%changelog
* Thu Nov 12 2009 Bryan O'Sullivan <bos@serpentine.com> - 6.12.0.20091010-3
- fix %check

* Sun Oct 11 2009 Bryan O'Sullivan <bos@serpentine.com> - 6.12.0.20091010-2
- disable ppc for now (seems unsupported)
- buildreq ncurses-devel

* Sun Oct 11 2009 Bryan O'Sullivan <bos@serpentine.com> - 6.12.0.20091010-1
- Update to 6.12 RC 1

* Thu Oct  1 2009 Jens Petersen <petersen@redhat.com>
- selinux file context no longer needed in post script
- (for ghc-6.12-shared) drop ld.so.conf.d files

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.10.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 21 2009 Bryan O'Sullivan <bos@serpentine.com> - 6.10.4-1
- update to 6.10.4

* Sat May 30 2009 Jens Petersen <petersen@redhat.com> - 6.10.3-3
- add haddock_version and use it to obsolete haddock and ghc-haddock-*

* Fri May 22 2009 Jens Petersen <petersen@redhat.com> - 6.10.3-2
- update haddock provides and obsoletes
- drop ghc-mk-pkg-install-inplace.patch: no longer needed with new 6.11 buildsys
- add bcond for extralibs
- rename doc bcond to manual

* Wed May 13 2009 Jens Petersen <petersen@redhat.com> - 6.10.3-1
- update to 6.10.3
- haskline replaces editline, so it is no longer needed to build
- macros.ghc moved to ghc-rpm-macros package
- fix handling of hscolor files in filelist generation

* Tue Apr 28 2009 Jens Petersen <petersen@redhat.com> - 6.10.2-4
- add experimental bcond hscolour
- add experimental support for building shared libraries (for ghc-6.11)
  - add libs subpackage for shared libraries
  - create a ld.conf.d file for libghc*.so
  - BR libffi-devel
- drop redundant setting of GhcLibWays in build.mk for no prof
- drop redundant setting of HADDOCK_DOCS
- simplify filelist names
- add a check section based on tests from debian's package
- be more careful about doc files in filelist

* Fri Apr 24 2009 Jens Petersen <petersen@redhat.com> - 6.10.2-3
- define ghc_version in macros.ghc in place of ghcrequires
- drop ghc-requires script for now

* Sun Apr 19 2009 Jens Petersen <petersen@redhat.com> - 6.10.2-2
- add ghc-requires rpm script to generate ghc version dependencies
  (thanks to Till Maas)
- update macros.ghc:
  - add %%ghcrequires to call above script
  - pkg_libdir and pkg_docdir obsoleted in packages and replaced
    by ghcpkgdir and ghcdocdir inside macros.ghc
  - make filelist also for docs

* Wed Apr 08 2009 Bryan O'Sullivan <bos@serpentine.com> - 6.10.2-1
- Update to 6.10.2

* Fri Feb 27 2009 Jens Petersen <petersen@redhat.com> - 6.10.1-13
- ok let's stick with ExclusiveArch for brevity

* Fri Feb 27 2009 Jens Petersen <petersen@redhat.com> - 6.10.1-12
- drop ghc_archs since it breaks koji
- fix missing -devel in ghc_gen_filelists
- change from ExclusiveArch to ExcludeArch ppc64 since alpha was bootstrapped
  by oliver

* Wed Feb 25 2009 Jens Petersen <petersen@redhat.com> - 6.10.1-11
- use %%ix86 for change from i386 to i586 in rawhide
- add ghc_archs macro in macros.ghc for other packages
- obsolete haddock09
- use %%global instead of %%define
- use bcond for doc and prof
- rename ghc_gen_filelists lib filelist to -devel.files

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.10.1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Feb 13 2009 Jens Petersen <petersen@redhat.com> - 6.10.1-9
- require and buildrequire libedit-devel > 2.11-2
- protect ghc_register_pkg and ghc_unregister_pkg

* Fri Jan 23 2009 Jens Petersen <petersen@redhat.com> - 6.10.1-8
- fix to libedit means can drop ncurses-devel BR workaround (#481252)

* Mon Jan 19 2009 Jens Petersen <petersen@redhat.com> - 6.10.1-7
- buildrequire ncurses-devel to fix build of missing editline package needed
  for ghci line-editing (#478466)
- move spec templates to cabal2spec package for easy updating
- provide correct haddock version

* Mon Dec  1 2008 Jens Petersen <petersen@redhat.com> - 6.10.1-6
- update macros.ghc to latest proposed revised packaging guidelines:
  - use runghc
  - drop trivial cabal_build and cabal_haddock macros
  - ghc_register_pkg and ghc_unregister_pkg replace ghc_preinst_script,
    ghc_postinst_script, ghc_preun_script, and ghc_postun_script
- library templates prof subpackage requires main library again
- make cabal2spec work on .cabal files too, and
  read and check name and version directly from .cabal file
- ghc-prof does not need to own libraries dirs owned by main package

* Tue Nov 25 2008 Jens Petersen <petersen@redhat.com> - 6.10.1-5
- add cabal2spec and template files for easy cabal hackage packaging
- simplify script macros: make ghc_preinst_script and ghc_postun_script no-ops
  and ghc_preun_script only unregister for uninstall

* Tue Nov 11 2008 Jens Petersen <petersen@redhat.com> - 6.10.1-4
- fix broken urls to haddock docs created by gen_contents_index script
- avoid haddock errors when upgrading by making doc post script posttrans

* Wed Nov 05 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.10.1-3
- libraries/prologue.txt should not have been ghosted

* Tue Nov 04 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.10.1-2
- Fix a minor packaging glitch

* Tue Nov 04 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.10.1-1
- Update to 6.10.1

* Thu Oct 23 2008 Jens Petersen <petersen@redhat.com> - 6.10.0.20081007-9
- remove redundant --haddockdir from cabal_configure
- actually ghc-pkg no longer seems to create package.conf.old backups
- include LICENSE in doc

* Thu Oct 23 2008 Jens Petersen <petersen@redhat.com> - 6.10.0.20081007-8
- need to create ghost package.conf.old for ghc-6.10

* Thu Oct 23 2008 Jens Petersen <petersen@redhat.com> - 6.10.0.20081007-7
- use gen_contents_index to re-index haddock
- add %%pkg_docdir to cabal_configure
- requires(post) ghc for haddock for doc
- improve doc file lists
- no longer need to create ghost package.conf.old
- remove or rename alternatives files more consistently

* Tue Oct 14 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.10.0.20081007-6
- Update macros to install html and haddock bits in the right places

* Tue Oct 14 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.10.0.20081007-5
- Don't use a macro to update the docs for the main doc package

* Tue Oct 14 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.10.0.20081007-4
- Add ghc_haddock_reindex macro
- Generate haddock index after installing ghc-doc package

* Mon Oct 13 2008 Jens Petersen <petersen@redhat.com> - 6.10.0.20081007-3
- provide haddock = 2.2.2
- add selinux file context for unconfined_execmem following darcs package
- post requires policycoreutils

* Sun Oct 12 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.10.0.20081007-2.fc10
- Use libedit in preference to readline, for BSD license consistency
- With haddock bundled now, obsolete standalone versions (but not haddock09)
- Drop obsolete freeglut-devel, openal-devel, and haddock09 dependencies

* Sun Oct 12 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.10.0.20081007-1.fc10
- Update to 6.10.1 release candidate 1

* Wed Oct  1 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.10.0.20080921-1.fc10
- Drop unneeded haddock patch
- Rename hsc2hs to hsc2hs-ghc so the alternatives symlink to it will work

* Wed Sep 24 2008 Jens Petersen <petersen@redhat.com> - 6.8.3-5
- bring back including haddock-generated lib docs, now under docdir/ghc
- fix macros.ghc filepath (#460304)
- spec file cleanups:
- fix the source urls back
- drop requires chkconfig
- do not override __spec_install_post
- setup docs building in build.mk
- no longer need to remove network/include/Typeable.h
- install binaries under libdir not libexec
- remove hsc2hs and runhaskell binaries since they are alternatives

* Wed Sep 17 2008 Jens Petersen <petersen@redhat.com> - 6.8.3-4
- add macros.ghc for new Haskell Packaging Guidelines (#460304)

* Wed Jun 18 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.8.3-3
- Add symlinks from _libdir, where ghc looks, to _libexecdir
- Patch libraries/gen_contents_index to use haddock-0.9

* Wed Jun 18 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.8.3-2
- Remove unnecessary dependency on alex

* Wed Jun 18 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.8.3-1
- Upgrade to 6.8.3
- Drop the ghc682-style naming scheme, obsolete those packages
- Manually strip binaries

* Tue Apr  8 2008 Jens Petersen <petersen@redhat.com> - 6.8.2-10
- another rebuild attempt

* Thu Feb 14 2008 Jens Petersen <petersen@redhat.com> - 6.8.2-9
- remove unrecognized --docdir and --htmldir from configure
- drop old buildrequires on libX11-devel and libXt-devel
- rebuild with gcc43

* Sun Jan 06 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.8.2-7
- More attempts to fix docdir

* Sun Jan 06 2008 Bryan O'Sullivan <bos@serpentine.com> - 6.8.2-6
- Fix docdir

* Tue Dec 12 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.8.2-1
- Update to 6.8.2

* Fri Nov 23 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.8.1-2
- Exclude alpha

* Thu Nov  8 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.8.1-2
- Drop bit-rotted attempts at making package relocatable

* Sun Nov  4 2007 Michel Salim <michel.sylvan@gmail.com> - 6.8.1-1
- Update to 6.8.1

* Sat Sep 29 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.8.0.20070928-2
- add happy to BuildRequires

* Sat Sep 29 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.8.0.20070928-1
- prepare for GHC 6.8.1 by building a release candidate snapshot

* Thu May 10 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.6.1-3
- install man page for ghc

* Thu May 10 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.6.1-2
- exclude ppc64 for now, due to lack of time to bootstrap

* Wed May  9 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.6.1-1
- update to 6.6.1 release

* Mon Jan 22 2007 Jens Petersen <petersen@redhat.com> - 6.6-2
- remove truncated duplicate Typeable.h header in network package
  (Bryan O'Sullivan, #222865)

* Fri Nov  3 2006 Jens Petersen <petersen@redhat.com> - 6.6-1
- update to 6.6 release
- buildrequire haddock >= 0.8
- fix summary of ghcver package (Michel Salim, #209574)

* Thu Sep 28 2006 Jens Petersen <petersen@redhat.com> - 6.4.2-4
- turn on docs generation again

* Mon Sep 25 2006 Jens Petersen <petersen@redhat.com> - 6.4.2-3.fc6
- ghost package.conf.old (Gérard Milmeister)
- set unconfined_execmem_exec_t context on executables with ghc rts (#195821)
- turn off building docs until haddock is back

* Sat Apr 29 2006 Jens Petersen <petersen@redhat.com> - 6.4.2-2.fc6
- buildrequire libXt-devel so that the X11 package and deps get built
  (Garrett Mitchener, #190201)

* Thu Apr 20 2006 Jens Petersen <petersen@redhat.com> - 6.4.2-1.fc6
- update to 6.4.2 release

* Thu Mar  2 2006 Jens Petersen <petersen@redhat.com> - 6.4.1-3.fc5
- buildrequire libX11-devel instead of xorg-x11-devel (Kevin Fenzi, #181024)
- make ghc-doc require ghc (Michel Salim, #180449)

* Tue Oct 11 2005 Jens Petersen <petersen@redhat.com> - 6.4.1-2.fc5
- turn on build_doc since haddock is now in Extras
- no longer specify ghc version to build with (Ville Skyttä, #170176)

* Tue Sep 20 2005 Jens Petersen <petersen@redhat.com> - 6.4.1-1.fc5
- 6.4.1 release
  - the following patches are now upstream: ghc-6.4-powerpc.patch,
    rts-GCCompact.h-x86_64.patch, ghc-6.4-dsforeign-x86_64-1097471.patch,
    ghc-6.4-rts-adjustor-x86_64-1097471.patch
  - builds with gcc4 so drop %%_with_gcc32
  - x86_64 build restrictions (no ghci and split objects) no longer apply

* Tue May 31 2005 Jens Petersen <petersen@redhat.com>
- add %%dist to release

* Thu May 12 2005 Jens Petersen <petersen@redhat.com> - 6.4-8
- initial import into Fedora Extras

* Thu May 12 2005 Jens Petersen <petersen@haskell.org>
- add build_prof and build_doc switches for -doc and -prof subpackages
- add _with_gcc32 switch since ghc-6.4 doesn't build with gcc-4.0

* Wed May 11 2005 Jens Petersen <petersen@haskell.org> - 6.4-7
- make package relocatable (ghc#1084122)
  - add post install scripts to replace prefix in driver scripts
- buildrequire libxslt and docbook-style-xsl instead of docbook-utils and flex

* Fri May  6 2005 Jens Petersen <petersen@haskell.org> - 6.4-6
- add ghc-6.4-dsforeign-x86_64-1097471.patch and
  ghc-6.4-rts-adjustor-x86_64-1097471.patch from trunk to hopefully fix
  ffi support on x86_64 (Simon Marlow, ghc#1097471)
- use XMLDocWays instead of SGMLDocWays to build documentation fully

* Mon May  2 2005 Jens Petersen <petersen@haskell.org> - 6.4-5
- add rts-GCCompact.h-x86_64.patch to fix GC issue on x86_64 (Simon Marlow)

* Thu Mar 17 2005 Jens Petersen <petersen@haskell.org> - 6.4-4
- add ghc-6.4-powerpc.patch (Ryan Lortie)
- disable building interpreter rather than install and delete on x86_64

* Wed Mar 16 2005 Jens Petersen <petersen@haskell.org> - 6.4-3
- make ghc require ghcver of same ver-rel
- on x86_64 remove ghci for now since it doesn't work and all .o files

* Tue Mar 15 2005 Jens Petersen <petersen@haskell.org> - 6.4-2
- ghc requires ghcver (Amanda Clare)

* Sat Mar 12 2005 Jens Petersen <petersen@haskell.org> - 6.4-1
- 6.4 release
  - x86_64 build no longer unregisterised
- use sed instead of perl to tidy filelists
- buildrequire ghc64 instead of ghc-6.4
- no epoch for ghc64-prof's ghc64 requirement
- install docs directly in docdir

* Fri Jan 21 2005 Jens Petersen <petersen@haskell.org> - 6.2.2-2
- add x86_64 port
  - build unregistered and without splitobjs
  - specify libdir to configure and install
- rename ghc-prof to ghcXYZ-prof, which obsoletes ghc-prof

* Mon Dec  6 2004 Jens Petersen <petersen@haskell.org> - 6.2.2-1
- move ghc requires to ghcXYZ

* Wed Nov 24 2004 Jens Petersen <petersen@haskell.org> - 6.2.2-0.fdr.1
- ghc622
  - provide ghc = %%version
- require gcc, gmp-devel and readline-devel

* Fri Oct 15 2004 Gerard Milmeister <gemi@bluewin.ch> - 6.2.2-0.fdr.1
- New Version 6.2.2

* Mon Mar 22 2004 Gerard Milmeister <gemi@bluewin.ch> - 6.2.1-0.fdr.1
- New Version 6.2.1

* Tue Dec 16 2003 Gerard Milmeister <gemi@bluewin.ch> - 6.2-0.fdr.1
- New Version 6.2

* Tue Dec 16 2003 Gerard Milmeister <gemi@bluewin.ch> - 6.0.1-0.fdr.3
- A few minor specfile tweaks

* Mon Dec 15 2003 Gerard Milmeister <gemi@bluewin.ch> - 6.0.1-0.fdr.2
- Different file list generation

* Mon Oct 20 2003 Gerard Milmeister <gemi@bluewin.ch> - 6.0.1-0.fdr.1
- First Fedora release
- Added generated html docs, so that haddock is not needed

* Wed Sep 26 2001 Manuel Chakravarty
- small changes for 5.04

* Wed Sep 26 2001 Manuel Chakravarty
- split documentation off into a separate package
- adapt to new docbook setup in RH7.1

* Mon Apr 16 2001 Manuel Chakravarty
- revised for 5.00
- also runs autoconf automagically if no ./configure found

* Thu Jun 22 2000 Sven Panne
- removed explicit usage of hslibs/docs, it belongs to ghc/docs/set

* Sun Apr 23 2000 Manuel Chakravarty
- revised for ghc 4.07; added suggestions from Pixel <pixel@mandrakesoft.com>
- added profiling package

* Tue Dec 7 1999 Manuel Chakravarty
- version for use from CVS

* Thu Sep 16 1999 Manuel Chakravarty
- modified for GHC 4.04, patchlevel 1 (no more 62 tuple stuff); minimises use
  of patch files - instead emits a build.mk on-the-fly

* Sat Jul 31 1999 Manuel Chakravarty
- modified for GHC 4.04

* Wed Jun 30 1999 Manuel Chakravarty
- some more improvements from vbzoli

* Fri Feb 26 1999 Manuel Chakravarty
- modified for GHC 4.02

* Thu Dec 24 1998 Zoltan Vorosbaranyi 
- added BuildRoot
- files located in /usr/local/bin, /usr/local/lib moved to /usr/bin, /usr/lib

* Tue Jul 28 1998 Manuel Chakravarty
- original version
