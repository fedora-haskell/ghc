%define ghcver ghc682

# speed up test builds by not building profiled libraries
%define build_prof 1
%define build_doc 1

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
%define package_debugging 0

Name:		ghc
Version:	6.8.2
Release:	2%{?dist}
Summary:	Glasgow Haskell Compilation system
# See https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=239713
ExcludeArch:	alpha ppc64
License:	BSD
Group:		Development/Languages
Source0:	http://www.haskell.org/ghc/dist/%{version}/ghc-%{version}-src.tar.bz2
Source1:	http://www.haskell.org/ghc/dist/%{version}/ghc-%{version}-src-extralibs.tar.bz2
URL:		http://haskell.org/ghc/
Requires:	%{ghcver} = %{version}-%{release}, chkconfig
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  ghc, happy, sed
BuildRequires:  gmp-devel, readline-devel
BuildRequires:  libX11-devel, libXt-devel
BuildRequires:  freeglut-devel, openal-devel
%if %{build_doc}
# haddock generates docs in libraries
BuildRequires: libxslt, docbook-style-xsl, haddock >= 0.8
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

%package -n %{ghcver}
Summary:	Glasgow Haskell Compilation system
Group:		Development/Languages
Requires:	gcc gmp-devel readline-devel

%description -n %{ghcver}
GHC is a state-of-the-art programming suite for Haskell, a purely
functional programming language.  It includes an optimising compiler
generating good code for a variety of platforms, together with an
interactive system for convenient, quick development.  The
distribution includes space and time profiling facilities, a large
collection of libraries, and support for various language
extensions, including concurrency, exceptions, and a foreign language
interfaces.

This package contains all the main files and libraries of version %{version}.

%if %{build_prof}
%package -n %{ghcver}-prof
Summary:	Profiling libraries for GHC
Group:		Development/Libraries
Requires:	%{ghcver} = %{version}-%{release}
Obsoletes:	ghc-prof

%description -n %{ghcver}-prof
Profiling libraries for Glorious Glasgow Haskell Compilation System
(GHC).  They should be installed when GHC's profiling subsystem is
needed.
%endif

%package doc
Summary:	Documentation for GHC
Group:		Development/Languages
Requires:	%{name} = %{version}-%{release}

%description doc
Preformatted documentation for the Glorious Glasgow Haskell
Compilation System (GHC) and its libraries.  It should be installed if
you like to have local access to the documentation in HTML format.

# the debuginfo subpackage is currently empty anyway, so don't generate it
%define debug_package %{nil}
%define __spec_install_post /usr/lib/rpm/brp-compress

%prep
%setup -q -n %{name}-%{version} -b1

%build
%if %{package_debugging}
cd ..
rm -rf %{name}-%{version}
cp -al %{name}-%{version}.built %{name}-%{version}
cd %{name}-%{version}
exit 0
%endif

%if !%{build_prof}
echo "GhcLibWays=" >> mk/build.mk
echo "GhcRTSWays=thr debug" >> mk/build.mk
%endif

./configure --prefix=%{_prefix} --exec-prefix=%{_exec_prefix} \
  --bindir=%{_bindir} --sbindir=%{_sbindir} --sysconfdir=%{_sysconfdir} \
  --datadir=%{_datadir} --includedir=%{_includedir} --libdir=%{_libdir} \
  --libexecdir=%{_libexecdir} --localstatedir=%{_localstatedir} \
  --sharedstatedir=%{_sharedstatedir} --mandir=%{_mandir}

# drop truncated copy of header (#222865)
rm libraries/network/include/Typeable.h

make %{_smp_mflags} docdir=%{_docdir}/%{name}-%{version} all
%if %{build_doc}
make %{_smp_mflags} docdir=%{_docdir}/%{name}-%{version} html
make %{_smp_mflags} -C libraries HADDOCK_DOCS=YES
( cd libraries/Cabal && docbook2html doc/Cabal.xml --output doc/Cabal )
%endif

%install
rm -rf $RPM_BUILD_ROOT

make DESTDIR=${RPM_BUILD_ROOT} libdir=%{_libdir}/%{name}-%{version} install

%if %{build_doc}
make DESTDIR=${RPM_BUILD_ROOT} docdir=%{_docdir}/%{name}-%{version} \
  XMLDocWays="html" HADDOCK_DOCS=YES install-docs
mv ${RPM_BUILD_ROOT}/%{_docdir}/%{name}/libraries \
  ${RPM_BUILD_ROOT}/%{_docdir}/%{name}-%{version}
cp libraries/*.html ${RPM_BUILD_ROOT}/%{_docdir}/%{name}-%{version}/libraries
%endif

SRC_TOP=$PWD
rm -f rpm-*-filelist rpm-*.files
( cd $RPM_BUILD_ROOT
  find .%{_libdir}/%{name}-%{version} \( -type d -fprintf $SRC_TOP/rpm-dir.files "%%%%dir %%p\n" \) -o \( -type f \( -name '*.p_hi' -o -name '*_p.a' \) -fprint $SRC_TOP/rpm-prof.files \) -o \( -not -name 'package.conf' -fprint $SRC_TOP/rpm-lib.files \)
)

# make paths absolute (filter "./usr" to "/usr")
sed -i -e "s|\.%{_prefix}|%{_prefix}|" rpm-*.files

cat rpm-dir.files rpm-lib.files > rpm-base-filelist
%if %{build_prof}
cat rpm-dir.files rpm-prof.files > rpm-prof-filelist
%endif

# create package.conf.old
touch $RPM_BUILD_ROOT%{_libdir}/ghc-%{version}/package.conf.old

mv ${RPM_BUILD_ROOT}%{_bindir}/hsc2hs ${RPM_BUILD_ROOT}%{_bindir}/hsc2hs-ghc

%clean
rm -rf $RPM_BUILD_ROOT


%post
/usr/bin/chcon -t unconfined_execmem_exec_t %{_bindir}/{hasktags,runghc,runhaskell} >/dev/null 2>&1 || :

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

%post -n %{ghcver}
/usr/bin/chcon -t unconfined_execmem_exec_t %{_libdir}/ghc-%{version}/{ghc-%{version},ghc-pkg.bin,hsc2hs-bin} >/dev/null 2>&1 || :


%preun
if test "$1" = 0; then
  update-alternatives --remove runhaskell %{_bindir}/runghc
  update-alternatives --remove hsc2hs     %{_bindir}/hsc2hs-ghc
fi


%files
%defattr(-,root,root,-)
%{_bindir}/*
%exclude %{_bindir}/ghc*%{version}
%doc %{_mandir}/man1/ghc.*


%files -n %{ghcver} -f rpm-base-filelist
%defattr(-,root,root,-)
%doc ANNOUNCE HACKING LICENSE README
%{_bindir}/ghc*%{version}
%config(noreplace) %{_libdir}/ghc-%{version}/package.conf
%ghost %{_libdir}/ghc-%{version}/package.conf.old


%if %{build_prof}
%files -n %{ghcver}-prof -f rpm-prof-filelist
%defattr(-,root,root,-)
%endif


%if %{build_doc}
%files doc
%defattr(-,root,root,-)
%{_docdir}/%{name}-%{version}
%endif


%changelog
* Tue Dec 12 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.8.2-1
- Update to 6.8.2

* Fri Nov 23 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.8.1-2
- Exclude alpha

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
