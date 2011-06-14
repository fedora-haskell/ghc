# shared haskell libraries supported for x86* archs
# (disabled for other archs in ghc-rpm-macros)

## default enabled options ##
%bcond_without doc
# test builds can made faster and smaller by disabling profiled libraries
# (currently libHSrts_thr_p.a breaks no prof build)
%bcond_without prof
# build xml manuals (users_guide, etc)
%bcond_without manual
# run testsuite
%bcond_with testsuite
# use system libffi
%ifarch %{ix86} x86_64
%bcond_without libffi
%endif

## default disabled options ##
# quick build profile
%bcond_with quick

# ghc does not output dwarf format so debuginfo is not useful
%global debug_package %{nil}

# workaround http://hackage.haskell.org/trac/ghc/ticket/5004
# override /usr/lib/rpm/redhat/macros
%global __os_install_post    \
    /usr/lib/rpm/redhat/brp-compress \
    %{!?__debug_package:\
    /usr/lib/rpm/redhat/brp-strip %{__strip} \
    /usr/lib/rpm/redhat/brp-strip-comment-note %{__strip} %{__objdump} \
    } \
# Disable static stripping since it breaks loading libHSghc.a for ghc 7.0.2 and 7.0.3\
#    /usr/lib/rpm/redhat/brp-strip-static-archive %{__strip} \
    /usr/lib/rpm/brp-python-bytecompile %{__python} %{?_python_bytecompile_errors_terminate_build} \
    /usr/lib/rpm/redhat/brp-python-hardlink \
    %{!?__jar_repack:/usr/lib/rpm/redhat/brp-java-repack-jars} \
%{nil}

Name: ghc
# haskell-platform-2011.2.0.0
# NB make sure to rebuild ghc after a version bump to avoid ABI change problems
Version: 7.0.2
# Since library subpackages are versioned:
# - release can only be reset if all library versions get bumped simultaneously
#   (eg for a major release)
# - minor release numbers should be incremented monotonically
Release: 24%{?dist}
Summary: Glasgow Haskell Compilation system
# fedora ghc has been bootstrapped on the following archs:
#ExclusiveArch: %{ix86} x86_64 ppc alpha sparcv9 ppc64
ExcludeArch: sparc64 s390x
License: BSD
Group: Development/Languages
Source0: http://www.haskell.org/ghc/dist/%{version}/ghc-%{version}-src.tar.bz2
%if %{with testsuite}
Source2: http://www.haskell.org/ghc/dist/%{version}/testsuite-%{version}.tar.bz2
%endif
Source3: ghc-doc-index.cron
URL: http://haskell.org/ghc/
# introduced for f14
Obsoletes: ghc-doc < 6.12.3-4
# BR for lib and binlib packages
Provides: ghc-doc = %{version}-%{release}
# introduced for f15
Obsoletes: ghc-libs < 7.0.1-3
Obsoletes: ghc-dph-base < 0.5, ghc-dph-base-devel < 0.5, ghc-dph-base-prof < 0.5
Obsoletes: ghc-dph-par < 0.5, ghc-dph-par-devel < 0.5, ghc-dph-par-prof < 0.5
Obsoletes: ghc-dph-prim-interface < 0.5, ghc-dph-prim-interface-devel < 0.5, ghc-dph-interface-prim-prof < 0.5
Obsoletes: ghc-dph-prim-par < 0.5, ghc-dph-prim-par-devel < 0.5, ghc-dph-prim-par-prof < 0.5
Obsoletes: ghc-dph-prim-seq < 0.5, ghc-dph-prim-seq-devel < 0.5, ghc-dph-prim-seq-prof < 0.5
Obsoletes: ghc-dph-seq < 0.5, ghc-dph-seq-devel < 0.5, ghc-dph-seq-prof < 0.5
Obsoletes: ghc-feldspar-language < 0.4, ghc-feldspar-language-devel < 0.4, ghc-feldspar-language-prof < 0.4
BuildRequires: ghc, ghc-rpm-macros >= 0.13
BuildRequires: gmp-devel, libffi-devel
BuildRequires: ghc-directory-devel, ghc-process-devel, ghc-pretty-devel, ghc-containers-devel, ghc-haskell98-devel, ghc-bytestring-devel
# for internal terminfo
BuildRequires: ncurses-devel
Requires: gcc
Requires: ghc-base-devel
# llvm is an optional dependency
%if %{with manual}
BuildRequires: libxslt, docbook-style-xsl
%endif
%if %{undefined without_hscolour}
BuildRequires: hscolour
%endif
%if %{with testsuite}
BuildRequires: python
%endif
%ifarch ppc64
BuildRequires: autoconf
%endif
Patch1: ghc-6.12.1-gen_contents_index-haddock-path.patch
Patch2: ghc-gen_contents_index-type-level.patch
Patch3: ghc-gen_contents_index-cron-batch.patch
Patch4: ghc-use-system-libffi.patch
# add cabal configure option --enable-executable-dynamic
# (see http://hackage.haskell.org/trac/hackage/ticket/600)
Patch5: Cabal-option-executable-dynamic.patch
Patch6: ghc-fix-linking-on-sparc.patch
Patch7: ghc-ppc64-pthread.patch
# http://hackage.haskell.org/trac/ghc/ticket/4999
Patch8: ghc-powerpc-linker-mmap.patch

%description
GHC is a state-of-the-art programming suite for Haskell, a purely
functional programming language.  It includes an optimizing compiler
generating good code for a variety of platforms, together with an
interactive system for convenient, quick development.  The
distribution includes space and time profiling facilities, a large
collection of libraries, and support for various language
extensions, including concurrency, exceptions, and a foreign language
interface.

%global ghc_version_override %{version}

%global ghc_pkg_c_deps ghc = %{ghc_version_override}-%{release}

%if %{defined ghclibdir}
%ghc_binlib_package Cabal 1.10.1.0
%ghc_binlib_package array 0.3.0.2
%ghc_binlib_package -c gmp-devel,libffi-devel base 4.3.1.0
%ghc_binlib_package bytestring 0.9.1.10
%ghc_binlib_package containers 0.4.0.0
%ghc_binlib_package directory 1.1.0.0
%ghc_binlib_package extensible-exceptions 0.1.1.2
%ghc_binlib_package filepath 1.2.0.0
%define ghc_pkg_obsoletes ghc-bin-package-db-devel < 0.0.0.0-12
%ghc_binlib_package -x ghc %{ghc_version_override}
%undefine ghc_pkg_obsoletes
%ghc_binlib_package haskell2010 1.0.0.0
%ghc_binlib_package haskell98 1.1.0.1
%ghc_binlib_package hpc 0.5.0.6
%ghc_binlib_package old-locale 1.0.0.2
%ghc_binlib_package old-time 1.0.0.6
%ghc_binlib_package pretty 1.0.1.2
%ghc_binlib_package process 1.0.1.5
%ghc_binlib_package random 1.0.0.3
%ghc_binlib_package template-haskell 2.5.0.0
%ghc_binlib_package time 1.2.0.3
%ghc_binlib_package unix 2.4.2.0
%endif

%global version %{ghc_version_override}

%package devel
Summary: GHC development libraries meta package
Group: Development/Libraries
Requires: ghc = %{version}-%{release}
Obsoletes: ghc-prof < %{version}-%{release}
Provides: ghc-prof = %{version}-%{release}
%{?ghc_packages_list:Requires: %(echo %{ghc_packages_list} | sed -e "s/\([^ ]*\)-\([^ ]*\)/ghc-\1-devel = \2-%{release},/g")}

%description devel
This is a meta-package for all the development library packages in GHC.

%prep
%setup -q -n %{name}-%{version} %{?with_testsuite:-b2}
# absolute haddock path (was for html/libraries -> libraries)
%patch1 -p1 -b .orig
# type-level too big so skip it in gen_contents_index
%patch2 -p1
# disable gen_contents_index when not --batch for cron
%patch3 -p1

# make sure we don't use these
rm -r ghc-tarballs/{mingw,perl}
# use system libffi
%if %{with libffi}
%patch4 -p1 -b .libffi
rm -r ghc-tarballs/libffi
%endif

%patch5 -p1 -b .orig

%patch6 -p1 -b .sparclinking

%ifarch ppc64
%patch7 -p1 -b .pthread
%endif

%ifarch ppc ppc64
%patch8 -p1 -b .mmap
%endif


%build
cat > mk/build.mk << EOF
GhcLibWays = v %{?with_prof:p} %{!?ghc_without_shared:dyn} 
%if %{without doc}
HADDOCK_DOCS = NO
%endif
%if %{without manual}
BUILD_DOCBOOK_HTML = NO
%endif
%if %{with quick}
SRC_HC_OPTS = -H64m -O0 -fasm
GhcStage1HcOpts = -O -fasm
GhcStage2HcOpts = -O0 -fasm
GhcLibHcOpts = -O0 -fasm
SplitObjs = NO
%endif
%if %{undefined without_hscolour}
HSCOLOUR_SRCS = NO
%endif
%if %{with libffi}
SRC_HC_OPTS += -lffi
%endif
%ifarch ppc64
GhcUnregisterised=YES
GhcWithNativeCodeGen=NO
SplitObjs=NO
GhcWithInterpreter=NO
GhcNotThreaded=YES
SRC_HC_OPTS+=-optc-mminimal-toc -optl-pthread
SRC_CC_OPTS+=-mminimal-toc -pthread -Wa,--noexecstack
%endif
EOF

%ifarch ppc64
autoreconf
%endif
export CFLAGS="${CFLAGS:-%optflags}"
# specify gcc to avoid problems when bootstrapping with ccache
./configure --prefix=%{_prefix} --exec-prefix=%{_exec_prefix} \
  --bindir=%{_bindir} --sbindir=%{_sbindir} --sysconfdir=%{_sysconfdir} \
  --datadir=%{_datadir} --includedir=%{_includedir} --libdir=%{_libdir} \
  --libexecdir=%{_libexecdir} --localstatedir=%{_localstatedir} \
  --sharedstatedir=%{_sharedstatedir} --mandir=%{_mandir} \
  --with-gcc=%{_bindir}/gcc \
  %{!?ghc_without_shared:--enable-shared}

# >4 cpus tends to break build
[ -z "$RPM_BUILD_NCPUS" ] && RPM_BUILD_NCPUS=$(%{_bindir}/getconf _NPROCESSORS_ONLN)
[ "$RPM_BUILD_NCPUS" -gt 4 ] && RPM_BUILD_NCPUS=4
make -j$RPM_BUILD_NCPUS

%install
make DESTDIR=${RPM_BUILD_ROOT} install

for i in %{ghc_packages_list}; do
name=$(echo $i | sed -e "s/\(.*\)-.*/\1/")
ver=$(echo $i | sed -e "s/.*-\(.*\)/\1/")
%ghc_gen_filelists $name $ver
echo "%doc libraries/$name/LICENSE" >> ghc-$name%{?ghc_without_shared:-devel}.files
done

%ghc_gen_filelists bin-package-db 0.0.0.0
%ghc_gen_filelists ghc %{ghc_version_override}
%ghc_gen_filelists ghc-binary 0.5.0.2
%ghc_gen_filelists ghc-prim 0.2.0.0
%ghc_gen_filelists integer-gmp 0.2.0.3

%define merge_filelist()\
%if %{undefined ghc_without_shared}\
cat ghc-%1.files >> ghc-%2.files\
%endif\
cat ghc-%1-devel.files >> ghc-%2-devel.files\
cp -p libraries/%1/LICENSE libraries/LICENSE.%1\
echo "%doc libraries/LICENSE.%1" >> ghc-%2.files

%merge_filelist integer-gmp base
%merge_filelist ghc-prim base
%merge_filelist ghc-binary ghc
%merge_filelist bin-package-db ghc

%if %{undefined ghc_without_shared}
ls $RPM_BUILD_ROOT%{ghclibdir}/libHS*.so >> ghc-base.files
sed -i -e "s|^$RPM_BUILD_ROOT||g" ghc-base.files
%endif
ls -d $RPM_BUILD_ROOT%{ghclibdir}/libHS*.a %{!?with_libffi:$RPM_BUILD_ROOT%{ghclibdir}/HSffi.o} $RPM_BUILD_ROOT%{ghclibdir}/package.conf.d/builtin_*.conf $RPM_BUILD_ROOT%{ghclibdir}/include >> ghc-base-devel.files
sed -i -e "s|^$RPM_BUILD_ROOT||g" ghc-base-devel.files

# these are handled as alternatives
for i in hsc2hs runhaskell; do
  if [ -x ${RPM_BUILD_ROOT}%{_bindir}/$i-ghc ]; then
    rm ${RPM_BUILD_ROOT}%{_bindir}/$i
  else
    mv ${RPM_BUILD_ROOT}%{_bindir}/$i{,-ghc}
  fi
done

%ghc_strip_dynlinked

%if %{with doc}
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/cron.hourly
install -p --mode=755 %SOURCE3 ${RPM_BUILD_ROOT}%{_sysconfdir}/cron.hourly/ghc-doc-index
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/lib/ghc
%endif

%check
# stolen from ghc6/debian/rules:
# Do some very simple tests that the compiler actually works
rm -rf testghc
mkdir testghc
echo 'main = putStrLn "Foo"' > testghc/foo.hs
inplace/bin/ghc-stage2 testghc/foo.hs -o testghc/foo
[ "$(testghc/foo)" = "Foo" ]
# doesn't seem to work inplace:
#[ "$(inplace/bin/runghc testghc/foo.hs)" = "Foo" ]
rm testghc/*
echo 'main = putStrLn "Foo"' > testghc/foo.hs
inplace/bin/ghc-stage2 testghc/foo.hs -o testghc/foo -O2
[ "$(testghc/foo)" = "Foo" ]
rm testghc/*
%if %{undefined ghc_without_shared}
echo 'main = putStrLn "Foo"' > testghc/foo.hs
inplace/bin/ghc-stage2 testghc/foo.hs -o testghc/foo -dynamic
[ "$(testghc/foo)" = "Foo" ]
rm testghc/*
%endif
%if %{with testsuite}
make -C testsuite/tests/ghc-regress fast
%endif

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

%preun
if [ "$1" = 0 ]; then
  update-alternatives --remove runhaskell %{_bindir}/runghc
  update-alternatives --remove hsc2hs     %{_bindir}/hsc2hs-ghc
fi

%files
%defattr(-,root,root,-)
%doc ANNOUNCE HACKING LICENSE README
%{_bindir}/*
%dir %{ghclibdir}
%{ghclibdir}/extra-gcc-opts
%{ghclibdir}/ghc
%{ghclibdir}/ghc-pkg
%ifnarch ppc64
%{ghclibdir}/ghc-asm
%{ghclibdir}/ghc-split
%endif
%{ghclibdir}/ghc-usage.txt
%{ghclibdir}/ghci-usage.txt
%{ghclibdir}/hsc2hs
%if %{with doc}
%{ghclibdir}/haddock
%{ghclibdir}/html
%{ghclibdir}/latex
%endif
%dir %{ghclibdir}/package.conf.d
%ghost %{ghclibdir}/package.conf.d/package.cache
%{ghclibdir}/runghc
%{ghclibdir}/template-hsc.h
%{ghclibdir}/unlit
%{_mandir}/man1/ghc.*
%dir %{_docdir}/ghc
%dir %{ghcdocbasedir}
%if %{with doc}
%{ghcdocbasedir}/html
%if %{with manual}
%{ghcdocbasedir}/Cabal
%{ghcdocbasedir}/haddock
%{ghcdocbasedir}/users_guide
%endif
%dir %{ghcdocbasedir}/libraries
%{ghcdocbasedir}/libraries/frames.html
%{ghcdocbasedir}/libraries/gen_contents_index
%{ghcdocbasedir}/libraries/hscolour.css
%{ghcdocbasedir}/libraries/ocean.css
%{ghcdocbasedir}/libraries/prologue.txt
%{ghcdocbasedir}/index.html
%ghost %{ghcdocbasedir}/libraries/doc-index*.html
%ghost %{ghcdocbasedir}/libraries/haddock-util.js
%ghost %{ghcdocbasedir}/libraries/index*.html
%ghost %{ghcdocbasedir}/libraries/minus.gif
%ghost %{ghcdocbasedir}/libraries/plus.gif
%{_sysconfdir}/cron.hourly/ghc-doc-index
%{_localstatedir}/lib/ghc
%endif

%files devel
%defattr(-,root,root,-)

%changelog
* Tue Jun 14 2011 Jens Petersen <petersen@redhat.com> - 7.0.2-24
- finally change from ExclusiveArch to ExcludeArch to target more archs

* Sat May 21 2011 Jens Petersen <petersen@redhat.com> - 7.0.2-23
- obsolete dph libraries and feldspar-language

* Mon May 16 2011 Jens Petersen <petersen@redhat.com> - 7.0.2-22
- merge prof subpackages into the devel subpackages with ghc-rpm-macros-0.13

* Wed May 11 2011 Jens Petersen <petersen@redhat.com> - 7.0.2-21
- configure with /usr/bin/gcc to help bootstrapping to new archs
  (otherwise ccache tends to get hardcoded as gcc, which not in koji)
- posttrans scriplet for ghc_pkg_recache is redundant

* Mon May  9 2011 Jens Petersen <petersen@redhat.com> - 7.0.2-20
- make devel and prof meta packages require libs with release
- make ghc-*-devel subpackages require ghc with release

* Wed May 04 2011 Jiri Skala <jskala@redhat.com> - 7.0.2-19.1
- fixes path to gcc on ppc64 arch

* Tue Apr 26 2011 Jens Petersen <petersen@redhat.com> - 7.0.2-19
- add upstream ghc-powerpc-linker-mmap.patch for ppc64 (Jiri Skala)

* Thu Apr 21 2011 Jiri Skala <jskala@redhat.com> - 7.0.2-18
- bootstrap to ppc64

* Fri Apr  1 2011 Jens Petersen <petersen@redhat.com> - 7.0.2-17
- rebuild against ghc-rpm-macros-0.11.14 to provide ghc-*-doc

* Fri Apr  1 2011 Jens Petersen <petersen@redhat.com> - 7.0.2-16
- provides ghc-doc again: it is still a buildrequires for libraries
- ghc-prof now requires ghc-devel
- ghc-devel now requires ghc explicitly

* Wed Mar 30 2011 Jens Petersen <petersen@redhat.com> - 7.0.2-15
- do not strip static libs since it breaks ghci-7.0.2 loading libHSghc.a
  (see http://hackage.haskell.org/trac/ghc/ticket/5004)
- no longer provide ghc-doc
- no longer obsolete old haddock

* Tue Mar 29 2011 Jens Petersen <petersen@redhat.com> - 7.0.2-14
- fix back missing LICENSE files in library subpackages
- drop ghc_reindex_haddock from install script

* Thu Mar 10 2011 Jens Petersen <petersen@redhat.com> - 7.0.2-13
- rebuild against 7.0.2

* Wed Mar  9 2011 Jens Petersen <petersen@redhat.com> - 7.0.2-12
- update to 7.0.2 release
- move bin-package-db into ghc-ghc
- disable broken testsuite

* Wed Feb 23 2011 Fabio M. Di Nitto <fdinitto@redhat.com> 7.0.1-11
- enable build on sparcv9
- add ghc-fix-linking-on-sparc.patch to fix ld being called
  at the same time with --relax and -r. The two options conflict
  on sparc.
- bump BuildRequires on ghc-rpm-macros to >= 0.11.10 that guarantees
  a correct build on secondary architectures.

* Sun Feb 13 2011 Jens Petersen <petersen@redhat.com>
- without_shared renamed to ghc_without_shared

* Thu Feb 10 2011 Jens Petersen <petersen@redhat.com> - 7.0.1-10
- rebuild

* Thu Feb 10 2011 Jens Petersen <petersen@redhat.com> - 7.0.1-9
- fix without_shared build (thanks Adrian Reber)
- disable system libffi for secondary archs
- temporarily disable ghc-*-devel BRs for ppc

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 7.0.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 31 2011 Jens Petersen <petersen@redhat.com> - 7.0.1-7
- include LICENSE files in the shared lib subpackages

* Sat Jan 22 2011 Jens Petersen <petersen@redhat.com> - 7.0.1-6
- patch Cabal to add configure option --enable-executable-dynamic
- exclude huge ghc API library from devel and prof metapackages

* Thu Jan 13 2011 Jens Petersen <petersen@redhat.com> - 7.0.1-5
- fix no doc and no manual builds

* Thu Jan 13 2011 Jens Petersen <petersen@redhat.com> - 7.0.1-4
- add BRs for various subpackaged ghc libraries needed to build ghc
- condition rts .so libraries for non-shared builds

* Thu Dec 30 2010 Jens Petersen <petersen@redhat.com> - 7.0.1-3
- subpackage all the libraries with ghc-rpm-macros-0.11.1
- put rts, integer-gmp and ghc-prim in base, and ghc-binary in bin-package-db
- drop the libs mega-subpackage
- prof now a meta-package for backward compatibility
- add devel meta-subpackage to easily install all ghc libraries
- store doc cronjob package cache file under /var (#664850)
- drop old extralibs bcond
- no longer need to define or clean buildroot
- ghc base package now requires ghc-base-devel
- drop ghc-time obsoletes

* Wed Nov 24 2010 Jens Petersen <petersen@redhat.com> - 7.0.1-2
- require libffi-devel

* Tue Nov 16 2010 Jens Petersen <petersen@redhat.com> - 7.0.1-1
- update to 7.0.1 release
- turn on system libffi now

* Mon Nov  8 2010 Jens Petersen <petersen@redhat.com> - 6.12.3-9
- disable the libffi changes for now since they break libHSffi*.so

* Thu Nov  4 2010 Jens Petersen <petersen@redhat.com> - 6.12.3-8
- add a cronjob for doc indexing
- disable gen_contents_index when not run with --batch for cron
- use system libffi with ghc-use-system-libffi.patch from debian
- add bcond for system libffi

* Thu Nov  4 2010 Jens Petersen <petersen@redhat.com> - 6.12.3-7
- skip huge type-level docs from haddock re-indexing (#649228)

* Thu Sep 30 2010 Jens Petersen <petersen@redhat.com> - 6.12.3-6
- move gtk2hs obsoletes to ghc-glib and ghc-gtk
- drop happy buildrequires
- smp build with max 4 cpus

* Fri Jul 30 2010 Jens Petersen <petersen@redhat.com> - 6.12.3-5
- obsolete old gtk2hs packages for smooth upgrades

* Thu Jul 15 2010 Jens Petersen <petersen@redhat.com> - 6.12.3-4
- merge ghc-doc into base package
- obsolete ghc-time and ghc-ghc-doc (ghc-rpm-macros-0.8.0)
- note that ghc-6.12.3 is part of haskell-platform-2010.2.0.0

* Thu Jun 24 2010 Jens Petersen <petersen@redhat.com> - 6.12.3-3
- drop the broken summary and description args to the ghc-ghc package
  and use ghc-rpm-macros-0.6.1

* Wed Jun 23 2010 Jens Petersen <petersen@redhat.com> - 6.12.3-2
- strip all dynlinked files not just shared objects (ghc-rpm-macros-0.5.9)

* Mon Jun 14 2010 Jens Petersen <petersen@redhat.com> - 6.12.3-1
- 6.12.3 release:
  http://darcs.haskell.org/download/docs/6.12.3/html/users_guide/release-6-12-3.html
- build with hscolour
- use ghc-rpm-macro-0.5.8 for ghc_strip_shared macro

* Fri May 28 2010 Jens Petersen <petersen@redhat.com> - 6.12.2.20100521-1
- 6.12.3 rc1
- ghost package.cache
- drop ghc-utf8-string obsoletes since it is no longer provided
- run testsuite fast
- fix description and summary of ghc internal library (John Obbele)

* Fri Apr 23 2010 Jens Petersen <petersen@redhat.com> - 6.12.2-1
- update to 6.12.2
- add testsuite with bcond, run it in check section, and BR python

* Mon Apr 12 2010 Jens Petersen <petersen@redhat.com> - 6.12.1-6
- ghc-6.12.1 is part of haskell-platform-2010.1.0.0
- drop old ghc682, ghc681, haddock09 obsoletes
- drop haddock_version and no longer provide haddock explicitly
- update ghc-rpm-macros BR to 0.5.6 for ghc_pkg_recache

* Mon Jan 11 2010 Jens Petersen <petersen@redhat.com> - 6.12.1-5
- drop ghc-6.12.1-no-filter-libs.patch and extras packages again
- filter ghc-ghc-prof files from ghc-prof
- ghc-mtl package was added to fedora

* Mon Jan 11 2010 Jens Petersen <petersen@redhat.com> - 6.12.1-4
- ghc-rpm-macros-0.5.4 fixes wrong version requires between lib subpackages

* Mon Jan 11 2010 Jens Petersen <petersen@redhat.com> - 6.12.1-3
- ghc-rpm-macros-0.5.2 fixes broken pkg_name requires for lib subpackages

* Tue Dec 22 2009 Jens Petersen <petersen@redhat.com> - 6.12.1-2
- include haskeline, mtl, and terminfo for now with
  ghc-6.12.1-no-filter-libs.patch
- use ghc_binlibpackage, grep -v and ghc_gen_filelists to generate
  the library subpackages (ghc-rpm-macros-0.5.1)
- always set GhcLibWays (Lorenzo Villani)
- use ghcdocbasedir to revert html doc path to upstream's html/ for consistency

* Wed Dec 16 2009 Jens Petersen <petersen@redhat.com> - 6.12.1-1
- pre became 6.12.1 final
- exclude ghc .conf file from package.conf.d in base package
- use ghc_reindex_haddock
- add scripts for ghc-ghc-devel and ghc-ghc-doc
- add doc bcond
- add ghc-6.12.1-gen_contents_index-haddock-path.patch to adjust haddock path
  since we removed html/ from libraries path
- require ghc-rpm-macros-0.3.1 and use ghc_version_override

* Sat Dec 12 2009 Jens Petersen <petersen@redhat.com> - 6.12.1-0.2
- remove redundant mingw and perl from ghc-tarballs/
- fix exclusion of ghc internals lib from base packages with -mindepth
- rename the final file lists to PKGNAME.files for clarity

* Fri Dec 11 2009 Jens Petersen <petersen@redhat.com> - 6.12.1-0.1
- update to ghc-6.12.1-pre
- separate bcond options into enabled and disabled for clarity
- only enable shared for intel x86 archs (Lorenzo Villani)
- add quick build profile (Lorenzo Villani)
- remove package_debugging hack (use "make install-short")
- drop sed BR (Lorenzo Villani)
- put all build.mk config into one cat block (Lorenzo Villani)
- export CFLAGS to configure (Lorenzo Villani)
- add dynamic linking test to check section (thanks Lorenzo Villani)
- remove old ghc66 obsoletes
- subpackage huge ghc internals library (thanks Lorenzo Villani)
  - BR ghc-rpm-macros >= 0.3.0
- move html docs to docdir/ghc from html subdir (Lorenzo Villani)
- disable smp build for now: broken for 8 cpus at least

* Wed Nov 18 2009 Jens Petersen <petersen@redhat.com> - 6.12.0.20091121-1
- update to 6.12.1 rc2
- build shared libs, yay! and package in standalone libs subpackage
- add bcond for manual and extralibs
- reenable ppc secondary arch
- don't provide ghc-haddock-*
- remove obsolete post requires policycoreutils
- add vanilla v to GhcLibWays when building without prof
- handle without hscolour
- can't smp make currently
- lots of filelist fixes for handling shared libs
- run ghc-pkg recache posttrans
- no need to install gen_contents_index by hand
- manpage is back

* Thu Nov 12 2009 Bryan O'Sullivan <bos@serpentine.com> - 6.12.0.20091010-8
- comprehensive attempts at packaging fixes

* Thu Nov 12 2009 Bryan O'Sullivan <bos@serpentine.com> - 6.12.0.20091010-7
- fix package.conf stuff

* Thu Nov 12 2009 Bryan O'Sullivan <bos@serpentine.com> - 6.12.0.20091010-6
- give up trying to install man pages

* Thu Nov 12 2009 Bryan O'Sullivan <bos@serpentine.com> - 6.12.0.20091010-5
- try to install man pages

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
