# disable prof, docs, perf build
# NB This SHOULD be disabled (bcond_with) for all koji production builds
%bcond_with quickbuild

# to handle RCs
%global ghc_release %{version}

# build profiling libraries
# build docs (haddock and manuals)
# - combined since disabling haddock seems to cause no manuals built
# - <https://ghc.haskell.org/trac/ghc/ticket/15190>
# perf production build (disable for quick build)
%if %{with quickbuild}
%bcond_with prof
%bcond_with docs
%bcond_with perf_build
%else
%bcond_without prof
%bcond_without docs
%bcond_without perf_build
%endif

# no longer build testsuite (takes time and not really being used)
%bcond_with testsuite

# 8.4 needs llvm-5.0
%global llvm_major 5.0
%global ghc_llvm_archs armv7hl aarch64

%global ghc_unregisterized_arches s390 s390x %{mips}

Name: ghc
# ghc must be rebuilt after a version bump to avoid ABI change problems
Version: 8.4.4
# Since library subpackages are versioned:
# - release can only be reset if *all* library versions get bumped simultaneously
#   (sometimes after a major release)
# - minor release numbers for a branch should be incremented monotonically
Release: 72%{?dist}
Summary: Glasgow Haskell Compiler

License: BSD and HaskellReport
URL: https://haskell.org/ghc/
Source0: https://downloads.haskell.org/~ghc/%{ghc_release}/ghc-%{version}-src.tar.xz
%if %{with testsuite}
Source1: https://downloads.haskell.org/~ghc/%{ghc_release}/ghc-%{version}-testsuite.tar.xz
%endif
Source3: ghc-doc-index.cron
Source4: ghc-doc-index
Source5: ghc-pkg.man
Source6: haddock.man
Source7: runghc.man
# absolute haddock path (was for html/libraries -> libraries)
Patch1:  ghc-gen_contents_index-haddock-path.patch
Patch2:  ghc-Cabal-install-PATH-warning.patch
# https://github.com/ghc/ghc/pull/143
Patch5:  ghc-configure-fix-sphinx-version-check.patch

Patch12: ghc-armv7-VFPv3D16--NEON.patch

# for s390x
# https://ghc.haskell.org/trac/ghc/ticket/15689
Patch15: ghc-warnings.mk-CC-Wall.patch

# revert 8.4.4 llvm changes
# https://ghc.haskell.org/trac/ghc/ticket/15780
Patch16: https://github.com/ghc/ghc/commit/6e361d895dda4600a85e01c72ff219474b5c7190.patch

# Debian patches:
Patch24: buildpath-abi-stability.patch
Patch26: no-missing-haddock-file-warning.patch
Patch28: x32-use-native-x86_64-insn.patch
Patch30: fix-build-using-unregisterized-v8.2.patch

# fedora ghc has been bootstrapped on
# %%{ix86} x86_64 ppc ppc64 armv7hl s390 s390x ppc64le aarch64
# and retired arches: alpha sparcv9 armv5tel
# see also deprecated ghc_arches defined in /etc/rpm/macros.ghc-srpm by redhat-rpm-macros

BuildRequires: ghc-compiler
BuildRequires: ghc-rpm-macros-extra
BuildRequires: ghc-binary-devel
BuildRequires: ghc-bytestring-devel
BuildRequires: ghc-containers-devel
BuildRequires: ghc-directory-devel
BuildRequires: ghc-pretty-devel
BuildRequires: ghc-process-devel
BuildRequires: ghc-transformers-devel
BuildRequires: gmp-devel
BuildRequires: libffi-devel
# for terminfo
BuildRequires: ncurses-devel
# for man and docs
BuildRequires: perl-interpreter
%if %{with testsuite}
BuildRequires: python3
%endif
%if %{with docs}
# for /usr/bin/sphinx-build
BuildRequires: python-sphinx
%endif
%ifarch %{ghc_llvm_archs}
BuildRequires: llvm%{llvm_major}
%endif
# patch5
BuildRequires: autoconf
%ifarch armv7hl
# patch12
BuildRequires: autoconf, automake
%endif
Requires: ghc-compiler = %{version}-%{release}
Requires: ghc-ghc-devel = %{version}-%{release}
Requires: ghc-libraries = %{version}-%{release}
%if %{with docs}
Requires: ghc-doc-cron = %{version}-%{release}
Requires: ghc-manual = %{version}-%{release}
%endif

%description
GHC is a state-of-the-art, open source, compiler and interactive environment
for the functional language Haskell. Highlights:

- GHC supports the entire Haskell 2010 language plus a wide variety of
  extensions.
- GHC has particularly good support for concurrency and parallelism,
  including support for Software Transactional Memory (STM).
- GHC generates fast code, particularly for concurrent programs.
  Take a look at GHC's performance on The Computer Language Benchmarks Game.
- GHC works on several platforms including Windows, Mac, Linux,
  most varieties of Unix, and several different processor architectures.
- GHC has extensive optimisation capabilities, including inter-module
  optimisation.
- GHC compiles Haskell code either directly to native code or using LLVM
  as a back-end. GHC can also generate C code as an intermediate target for
  porting to new platforms. The interactive environment compiles Haskell to
  bytecode, and supports execution of mixed bytecode/compiled programs.
- Profiling is supported, both by time/allocation and various kinds of heap
  profiling.
- GHC comes with several libraries, and thousands more are available on Hackage.


%package compiler
Summary: GHC compiler and utilities
License: BSD
Requires: gcc%{?_isa}
Requires: ghc-base-devel%{?_isa}
# for alternatives
Requires(post): %{_sbindir}/update-alternatives
Requires(postun):  %{_sbindir}/update-alternatives
# added in f14
Obsoletes: ghc-doc < 6.12.3-4
%if %{without docs}
Obsoletes: ghc-doc-cron < %{version}-%{release}
# added in f28
Obsoletes: ghc-doc-index < %{version}-%{release}
%endif
%ifarch %{ghc_llvm_archs}
Requires: llvm%{llvm_major}
%endif

%description compiler
The package contains the GHC compiler, tools and utilities.

The ghc libraries are provided by ghc-libraries.
To install all of ghc (including the ghc library),
install the main ghc package.


%if %{with docs}
%package doc-cron
Summary: GHC library documentation indexing cronjob
License: BSD
Requires: ghc-compiler = %{version}-%{release}
Requires: crontabs
# added in f28
Obsoletes: ghc-doc-index < %{version}-%{release}
BuildArch: noarch

%description doc-cron
The package provides a cronjob for re-indexing installed library development
documention.
%endif


%if %{with docs}
%package manual
Summary: GHC manual
License: BSD
BuildArch: noarch

%description manual
This package provides the User Guide and Haddock manual.
%endif


# ghclibdir also needs ghc_version_override for bootstrapping
%global ghc_version_override %{version}

# EL7 rpm supports fileattrs ghc.attr
%if 0%{?rhel} && 0%{?rhel} < 7
# needs ghc_version_override for bootstrapping
%global _use_internal_dependency_generator 0
%global __find_provides /usr/lib/rpm/rpmdeps --provides
%global __find_requires %{_rpmconfigdir}/ghc-deps.sh --requires %{buildroot}%{ghclibdir}
%endif

%global ghc_pkg_c_deps ghc-compiler = %{ghc_version_override}-%{release}

%global BSDHaskellReport %{quote:BSD and HaskellReport}

# use "./libraries-versions.sh" to check versions
%if %{defined ghclibdir}
%ghc_lib_subpackage -d -l BSD Cabal-2.2.0.1
%ghc_lib_subpackage -d -l %BSDHaskellReport array-0.5.2.0
%ghc_lib_subpackage -d -l %BSDHaskellReport -c gmp-devel%{?_isa},libffi-devel%{?_isa} base-4.11.1.0
%ghc_lib_subpackage -d -l BSD binary-0.8.5.1
%ghc_lib_subpackage -d -l BSD bytestring-0.10.8.2
%ghc_lib_subpackage -d -l %BSDHaskellReport containers-0.5.11.0
%ghc_lib_subpackage -d -l %BSDHaskellReport deepseq-1.4.3.0
%ghc_lib_subpackage -d -l %BSDHaskellReport directory-1.3.1.5
%ghc_lib_subpackage -d -l BSD filepath-1.4.2
# in ghc not ghc-libraries:
%ghc_lib_subpackage -d -x ghc-%{ghc_version_override}
%ghc_lib_subpackage -d -x -l BSD ghc-boot-%{ghc_version_override}
%ghc_lib_subpackage -d -l BSD ghc-boot-th-%{ghc_version_override}
%ghc_lib_subpackage -d -l BSD ghc-compact-0.1.0.0
%ghc_lib_subpackage -d -l BSD -x ghci-%{ghc_version_override}
%ghc_lib_subpackage -d -l BSD haskeline-0.7.4.2
%ghc_lib_subpackage -d -l BSD hpc-0.6.0.3
%ghc_lib_subpackage -d -l BSD mtl-2.2.2
%ghc_lib_subpackage -d -l BSD parsec-3.1.13.0
%ghc_lib_subpackage -d -l BSD pretty-1.1.3.6
%ghc_lib_subpackage -d -l %BSDHaskellReport process-1.6.3.0
%ghc_lib_subpackage -d -l BSD stm-2.4.5.1
%ghc_lib_subpackage -d -l BSD template-haskell-2.13.0.0
%ghc_lib_subpackage -d -l BSD -c ncurses-devel%{?_isa} terminfo-0.4.1.1
%ghc_lib_subpackage -d -l BSD text-1.2.3.1
%ghc_lib_subpackage -d -l BSD time-1.8.0.2
%ghc_lib_subpackage -d -l BSD transformers-0.5.5.0
%ghc_lib_subpackage -d -l BSD unix-2.7.2.2
%if %{with docs}
%ghc_lib_subpackage -d -l BSD xhtml-3000.2.2.1
%endif
%endif

%global version %{ghc_version_override}

%package libraries
Summary: GHC development libraries meta package
License: BSD and HaskellReport
Requires: ghc-compiler = %{version}-%{release}
Obsoletes: ghc-devel < %{version}-%{release}
Provides: ghc-devel = %{version}-%{release}
Obsoletes: ghc-prof < %{version}-%{release}
Provides: ghc-prof = %{version}-%{release}
# since f15
Obsoletes: ghc-libs < 7.0.1-3
%{?ghc_packages_list:Requires: %(echo %{ghc_packages_list} | sed -e "s/\([^ ]*\)-\([^ ]*\)/ghc-\1-devel = \2-%{release},/g")}

%description libraries
This is a meta-package for all the development library packages in GHC
except the ghc library, which is installed by the toplevel ghc metapackage.


%prep
%setup -q -n %{name}-%{version} %{?with_testsuite:-b1}

%patch1 -p1 -b .orig

%patch2 -p1 -b .orig
%patch5 -p1 -b .orig

%if 0%{?fedora} || 0%{?rhel} > 6
rm -r libffi-tarballs
%endif

%ifarch armv7hl
%patch12 -p1 -b .orig
%endif

%ifarch s390x
%patch15 -p1 -b .orig
%endif

%ifarch armv7hl aarch64
%patch16 -p1 -b .orig -R
%endif

%patch24 -p1 -b .orig
%patch26 -p1 -b .orig
%patch28 -p1 -b .orig
%ifarch s390x
%patch30 -p1 -b .orig
%endif

%global gen_contents_index gen_contents_index.orig
%if %{with docs}
if [ ! -f "libraries/%{gen_contents_index}" ]; then
  echo "Missing libraries/%{gen_contents_index}, needed at end of %%install!"
  exit 1
fi
%endif

# http://ghc.haskell.org/trac/ghc/wiki/Platforms
cat > mk/build.mk << EOF
%if %{with perf_build}
%ifarch %{ghc_llvm_archs}
BuildFlavour = perf-llvm
%else
BuildFlavour = perf
%endif
%else
%ifarch %{ghc_llvm_archs}
BuildFlavour = quick-llvm
%else
BuildFlavour = quick
%endif
%endif
GhcLibWays = v dyn %{?with_prof:p}
%if %{with docs}
HADDOCK_DOCS = YES
BUILD_MAN = YES
%else
HADDOCK_DOCS = NO
BUILD_MAN = NO
%endif
EXTRA_HADDOCK_OPTS += --hyperlinked-source
BUILD_SPHINX_PDF = NO
EOF
## for verbose build output
#GhcStage1HcOpts=-v4
## enable RTS debugging:
## (http://ghc.haskell.org/trac/ghc/wiki/Debugging/RuntimeSystem)
#EXTRA_HC_OPTS=-debug

%build
# for patch12
%ifarch armv7hl
autoreconf
%else
# for patch5
autoconf
%endif

# replace later with ghc_set_gcc_flags
export CFLAGS="${CFLAGS:-%optflags}"
export LDFLAGS="${LDFLAGS:-%{?__global_ldflags}}"
# for ghc >= 8.2
export CC=%{_bindir}/gcc
# * %%configure induces cross-build due to different target/host/build platform names
./configure --prefix=%{_prefix} --exec-prefix=%{_exec_prefix} \
  --bindir=%{_bindir} --sbindir=%{_sbindir} --sysconfdir=%{_sysconfdir} \
  --datadir=%{_datadir} --includedir=%{_includedir} --libdir=%{_libdir} \
  --libexecdir=%{_libexecdir} --localstatedir=%{_localstatedir} \
  --sharedstatedir=%{_sharedstatedir} --mandir=%{_mandir} \
  --docdir=%{_docdir}/ghc \
%ifarch %{ghc_unregisterized_arches}
  --enable-unregisterised \
%endif
%if 0%{?fedora} || 0%{?rhel} > 6
  --with-system-libffi \
%endif
%{nil}

# avoid "ghc: hGetContents: invalid argument (invalid byte sequence)"
export LANG=C.utf8
make %{?_smp_mflags}


%install
make DESTDIR=%{buildroot} install

%if %{defined _ghcdynlibdir}
mv %{buildroot}%{ghclibdir}/*/libHS*ghc%{ghc_version}.so %{buildroot}%{_libdir}/
for i in $(find %{buildroot} -type f -exec sh -c "file {} | grep -q 'dynamically linked'" \; -print); do
  chrpath -d $i
done
for i in %{buildroot}%{ghclibdir}/package.conf.d/*.conf; do
  sed -i -e 's!^dynamic-library-dirs: .*!dynamic-library-dirs: %{_libdir}!' $i
done
sed -i -e 's!^library-dirs: %{ghclibdir}/rts!&\ndynamic-library-dirs: %{_libdir}!' %{buildroot}%{ghclibdir}/package.conf.d/rts.conf
%endif

for i in %{ghc_packages_list}; do
name=$(echo $i | sed -e "s/\(.*\)-.*/\1/")
ver=$(echo $i | sed -e "s/.*-\(.*\)/\1/")
%ghc_gen_filelists $name $ver
%if 0%{?rhel} && 0%{?rhel} < 7
echo "%%doc libraries/$name/LICENSE" >> ghc-$name.files
%else
echo "%%license libraries/$name/LICENSE" >> ghc-$name.files
%endif
done

echo "%%dir %{ghclibdir}" >> ghc-base%{?_ghcdynlibdir:-devel}.files

%ghc_gen_filelists ghc-boot %{ghc_version_override}
%ghc_gen_filelists ghc %{ghc_version_override}
%ghc_gen_filelists ghci %{ghc_version_override}
%ghc_gen_filelists ghc-prim 0.5.2.0
%ghc_gen_filelists integer-gmp 1.0.2.0

%define merge_filelist()\
cat ghc-%1.files >> ghc-%2.files\
cat ghc-%1-devel.files >> ghc-%2-devel.files\
cp -p libraries/%1/LICENSE libraries/LICENSE.%1\
%if 0%{?rhel} && 0%{?rhel} < 7\
echo "%%doc libraries/LICENSE.%1" >> ghc-%2.files\
%else\
echo "%%license libraries/LICENSE.%1" >> ghc-%2.files\
%endif

%merge_filelist integer-gmp base
%merge_filelist ghc-prim base

# add rts libs
%if %{defined _ghcdynlibdir}
echo "%{ghclibdir}/rts" >> ghc-base-devel.files
%else
echo "%%dir %{ghclibdir}/rts" >> ghc-base.files
ls -d %{buildroot}%{ghclibdir}/rts/lib*.a >> ghc-base-devel.files
%endif
ls %{buildroot}%{?_ghcdynlibdir}%{!?_ghcdynlibdir:%{ghclibdir}/rts}/libHSrts*.so >> ghc-base.files
%if 0%{?rhel} && 0%{?rhel} < 7
ls %{buildroot}%{ghclibdir}/rts/libffi.so.* >> ghc-base.files
%endif
%if %{defined _ghcdynlibdir}
sed -i -e 's!^library-dirs: %{ghclibdir}/rts!&\ndynamic-library-dirs: %{_libdir}!' %{buildroot}%{ghclibdir}/package.conf.d/rts.conf
%endif

ls -d %{buildroot}%{ghclibdir}/package.conf.d/rts.conf %{buildroot}%{ghclibdir}/include >> ghc-base-devel.files
%if 0%{?rhel} && 0%{?rhel} < 7
ls %{buildroot}%{ghclibdir}/rts/libffi.so >> ghc-base-devel.files
%endif

sed -i -e "s|^%{buildroot}||g" ghc-base*.files

# these are handled as alternatives
for i in hsc2hs runhaskell; do
  if [ -x %{buildroot}%{_bindir}/$i-ghc ]; then
    rm %{buildroot}%{_bindir}/$i
  else
    mv %{buildroot}%{_bindir}/$i{,-ghc}
  fi
  touch %{buildroot}%{_bindir}/$i
done

%ghc_strip_dynlinked

%if %{with docs}
mkdir -p %{buildroot}%{_sysconfdir}/cron.hourly
install -p --mode=0755 %SOURCE3 %{buildroot}%{_sysconfdir}/cron.hourly/ghc-doc-index
mkdir -p %{buildroot}%{_localstatedir}/lib/ghc
touch %{buildroot}%{_localstatedir}/lib/ghc/pkg-dir.cache{,.new}
install -p --mode=0755 %SOURCE4 %{buildroot}%{_bindir}/ghc-doc-index

# generate initial lib doc index
cd libraries
sh %{gen_contents_index} --intree --verbose
cd ..
%endif

# we package the library license files separately
find %{buildroot}%{ghc_html_libraries_dir} -name LICENSE -exec rm '{}' ';'

mkdir -p %{buildroot}%{_mandir}/man1
install -p -m 0644 %{SOURCE5} %{buildroot}%{_mandir}/man1/ghc-pkg.1
install -p -m 0644 %{SOURCE6} %{buildroot}%{_mandir}/man1/haddock.1
install -p -m 0644 %{SOURCE7} %{buildroot}%{_mandir}/man1/runghc.1

%check
export LANG=en_US.utf8
# stolen from ghc6/debian/rules:
GHC=inplace/bin/ghc-stage2
# Do some very simple tests that the compiler actually works
rm -rf testghc
mkdir testghc
echo 'main = putStrLn "Foo"' > testghc/foo.hs
$GHC testghc/foo.hs -o testghc/foo
[ "$(testghc/foo)" = "Foo" ]
# doesn't seem to work inplace:
#[ "$(inplace/bin/runghc testghc/foo.hs)" = "Foo" ]
rm testghc/*
echo 'main = putStrLn "Foo"' > testghc/foo.hs
$GHC testghc/foo.hs -o testghc/foo -O2
[ "$(testghc/foo)" = "Foo" ]
rm testghc/*
echo 'main = putStrLn "Foo"' > testghc/foo.hs
$GHC testghc/foo.hs -o testghc/foo -dynamic
[ "$(testghc/foo)" = "Foo" ]
rm testghc/*
%if %{with testsuite}
make test
%endif


%post compiler
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

%preun compiler
if [ "$1" = 0 ]; then
  update-alternatives --remove runhaskell %{_bindir}/runghc
  update-alternatives --remove hsc2hs     %{_bindir}/hsc2hs-ghc
fi


%files

%files compiler
%license LICENSE
%doc ANNOUNCE
%{_bindir}/ghc
%{_bindir}/ghc-%{version}
%{_bindir}/ghc-pkg
%{_bindir}/ghc-pkg-%{version}
%{_bindir}/ghci
%{_bindir}/ghci-%{version}
%{_bindir}/hp2ps
%{_bindir}/hpc
%ghost %{_bindir}/hsc2hs
%{_bindir}/hsc2hs-ghc
%{_bindir}/runghc*
%ghost %{_bindir}/runhaskell
%{_bindir}/runhaskell-ghc
%dir %{ghclibdir}/bin
%{ghclibdir}/bin/ghc
%{ghclibdir}/bin/ghc-pkg
%{ghclibdir}/bin/hpc
%{ghclibdir}/bin/hsc2hs
%{ghclibdir}/bin/ghc-iserv
%{ghclibdir}/bin/ghc-iserv-dyn
%if %{with prof}
%{ghclibdir}/bin/ghc-iserv-prof
%endif
%{ghclibdir}/bin/runghc
%ifnarch %{ghc_unregisterized_arches}
%{ghclibdir}/bin/ghc-split
%endif
%{ghclibdir}/bin/hp2ps
%{ghclibdir}/bin/unlit
%{ghclibdir}/ghc-usage.txt
%{ghclibdir}/ghci-usage.txt
%{ghclibdir}/llvm-targets
%dir %{ghclibdir}/package.conf.d
%ghost %{ghclibdir}/package.conf.d/package.cache
%{ghclibdir}/package.conf.d/package.cache.lock
%{ghclibdir}/platformConstants
%{ghclibdir}/settings
%{ghclibdir}/template-hsc.h
%dir %{_docdir}/ghc
%dir %{ghc_html_dir}
%{_mandir}/man1/ghc-pkg.1*
%{_mandir}/man1/haddock.1*
%{_mandir}/man1/runghc.1*

%if %{with docs}
%{_bindir}/ghc-doc-index
%{_bindir}/haddock
%{_bindir}/haddock-ghc-%{version}
%{ghclibdir}/bin/haddock
%{ghclibdir}/html
%{ghclibdir}/latex
%if %{with docs}
%{_mandir}/man1/ghc.1*
%endif
%dir %{ghc_html_dir}/libraries
%{ghc_html_dir}/libraries/gen_contents_index
%{ghc_html_dir}/libraries/prologue.txt
%ghost %{ghc_html_dir}/libraries/doc-index*.html
%ghost %{ghc_html_dir}/libraries/haddock-bundle.min.js
%ghost %{ghc_html_dir}/libraries/haddock-util.js
%ghost %{ghc_html_dir}/libraries/hslogo-16.png
%ghost %{ghc_html_dir}/libraries/index*.html
%ghost %{ghc_html_dir}/libraries/minus.gif
%ghost %{ghc_html_dir}/libraries/ocean.css
%ghost %{ghc_html_dir}/libraries/plus.gif
%ghost %{ghc_html_dir}/libraries/quick-jump.css
%ghost %{ghc_html_dir}/libraries/synopsis.png
%dir %{_localstatedir}/lib/ghc
%ghost %{_localstatedir}/lib/ghc/pkg-dir.cache
%ghost %{_localstatedir}/lib/ghc/pkg-dir.cache.new
%endif

%if %{with docs}
%files doc-cron
%config(noreplace) %{_sysconfdir}/cron.hourly/ghc-doc-index
%endif

%files libraries


%if %{with docs}
%files manual
## needs pandoc
#%%{ghc_html_dir}/Cabal
%if %{with docs}
%{ghc_html_dir}/haddock
%endif
%{ghc_html_dir}/index.html
%{ghc_html_dir}/users_guide
%endif


%changelog
* Sun Nov 18 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl>
- Use C.UTF-8 locale
  See https://fedoraproject.org/wiki/Changes/Remove_glibc-langpacks-all_from_buildroot

* Wed Oct 17 2018 Jens Petersen <petersen@redhat.com> - 8.4.4-72
- update to 8.4.4 bugfix release

* Wed Oct 17 2018 Jens Petersen <petersen@redhat.com>
- use with_prof
- extend quickbuild to handle perf_build

* Tue Oct 16 2018 Peter Robinson <pbrobinson@fedoraproject.org>
- Update alternatives dependencies

* Wed May 30 2018 Jens Petersen <petersen@redhat.com> - 8.4.3-70.7
- 8.4.3 release
- package changes from Fedora Rawhide:
- fix sphinx-build version detection
- merge bcond for haddock and manual
- move manuals to ghc-manual (noarch)
- rename ghc-doc-index to ghc-doc-cron (noarch)
- ghost the ghc-doc-index local state files
- ghost some newer libraries index files
- simplify and extend bcond for build configuration
- drop bootstrap builds
- no longer need autotools on aarch64

* Mon Apr 30 2018 Jens Petersen <petersen@redhat.com> - 8.4.2-70.6
- 8.4.2 perf build

* Fri Apr 20 2018 Jens Petersen <petersen@redhat.com> - 8.4.2-70.5
- 8.4.2 quick build

* Wed Mar 14 2018 Jens Petersen <petersen@redhat.com> - 8.4.1-70.4
- disable testsuite for rhel7 to avoid python3

* Tue Mar 13 2018 Jens Petersen <petersen@redhat.com> - 8.4.1-70.3
- 8.4.1 perf build

* Tue Mar 13 2018 Jens Petersen <petersen@redhat.com> - 8.4.1-70.2
- 8.4.1 quick build

* Thu Mar  1 2018 Jens Petersen <petersen@redhat.com> - 8.4.0.20180224-70.1
- 8.4.1 RC1 quick build
- use python-sphinx
- move build.mk into %prep
- rts files fixes to allow building for older releases without _ghcdynlibdir

* Tue Feb 27 2018 Jens Petersen <petersen@redhat.com> - 8.2.2-65.1
- re-enable buildpath-abi-stability.patch
- add manpages from debian for ghc-pkg, haddock, runghc
- forward port changes from Fedora 28:
- apply Phabricator D4159.patch to workaround
  https://ghc.haskell.org/trac/ghc/ticket/14381
- python3

* Mon Jan 22 2018 Jens Petersen <petersen@localhost.localdomain> - 8.2.2-60.6
- install ghc libs in libdir and remove RUNPATHs

* Sun Jan 14 2018 Jens Petersen <petersen@redhat.com> - 8.2.2-60.5
- add shadowed-deps.patch (haskell/cabal#4728)

* Fri Dec 15 2017 Jens Petersen <petersen@redhat.com> - 8.2.2-60.4
- 8.2.2 release perf build

* Wed Nov 29 2017 Jens Petersen <petersen@redhat.com> - 8.2.2-60.3
- 8.2.2 release bootstrap build

* Mon Nov  6 2017 Jens Petersen <petersen@redhat.com> - 8.2.1.20171030-60.2
- 8.2.2 RC2 bootstrap build

* Fri Oct 27 2017 Jens Petersen <petersen@redhat.com> - 8.2.1.20170929-60.1
- 8.2.2 RC1 bootstrap build
- fix space in BSDHaskellReport license macro for rpm-4.14
- mark other subpackages correctly as BSD license
- drop ghc-boot from ghc-libraries

* Wed Aug  2 2017 Jens Petersen <petersen@redhat.com> - 8.2.1-58.6
- 8.2.1 perf build

* Tue Jul 25 2017 Jens Petersen <petersen@redhat.com> - 8.2.1-58.5
- 8.2.1 bootstrap

* Thu Jul  6 2017 Jens Petersen <petersen@redhat.com>
- 8.2.1 rc3 bootstrap

* Tue May 23 2017 Jens Petersen <petersen@redhat.com> - 8.2.0.20170507-58.4
- 8.2.1 rc2 perf

* Mon May 22 2017 Jens Petersen <petersen@redhat.com> - 8.2.0.20170507-58.3
- 8.2.1 rc2 bootstrap

* Wed Apr  5 2017 Jens Petersen <petersen@redhat.com> - 8.2.0.20170404-58.2
- 8.2.1 rc1 perf build
- patch testsuite for https://ghc.haskell.org/trac/ghc/ticket/13534

* Wed Apr  5 2017 Jens Petersen <petersen@redhat.com> - 8.2.0.20170404-58.1
- 8.2.1 rc1
- bootstrap
- new ghc-compact library
- exclude ghc-boot for ghc-libraries

* Fri Feb 17 2017 Jens Petersen <petersen@redhat.com> - 8.0.2-55.5
- config versioned llc and opt for all archs
- use ghc_lib_subpackage -d to find .files
- add Debian patches: no-missing-haddock-file-warning, reproducible-tmp-names,
  x32-use-native-x86_64-insn, osdecommitmemory-compat

* Thu Jan 19 2017 Jens Petersen <petersen@redhat.com> - 8.0.2-55.4
- Cabal: install dynlibs next to static libs to simplify packaging

* Fri Jan  6 2017 Jens Petersen <petersen@redhat.com> - 8.0.2-55.3
- 8.0.2 perf build

* Thu Jan  5 2017 Jens Petersen <petersen@redhat.com> - 8.0.2-55.1
- 8.0.2 quick build

* Fri Dec 16 2016 Jens Petersen <petersen@redhat.com> - 8.0.1.20161213-54.5
- 8.0.2 RC2 perf build

* Fri Dec 16 2016 Jens Petersen <petersen@redhat.com> - 8.0.1.20161213-54.4
- 8.0.2 RC2 quick build
- Cabal, directory, haskeline, process bumped

* Wed Dec  7 2016 Jens Petersen <petersen@redhat.com> - 8.0.1.20161117-54.3
- patch Cabal to install dynlibs in libdir itself instead of abi dir

* Tue Nov 22 2016 Jens Petersen <petersen@redhat.com> - 8.0.1.20161117-54.2
- 8.0.2 RC1 perf build
- no manpage installed

* Sun Nov 20 2016 Jens Petersen <petersen@redhat.com> - 8.0.1.20161117-54.1
- 8.0.2 RC1 quick build
- Cabal, base, filepath, template-haskell, unix bumped

* Fri Oct  7 2016 Jens Petersen <petersen@redhat.com> - 8.0.1-53.5
- use llvm3.7 (needed for armv7hl)
- drop armv5tel
- update for latest ghc-rpm-macros
- quick build

* Thu May 19 2016 Jens Petersen <petersen@redhat.com> - 8.0.1-53.4
- 8.0.1 perf

* Wed May 18 2016 Jens Petersen <petersen@redhat.com> - 8.0.1-53.3
- 8.0.1 respin 3

* Fri May 13 2016 Jens Petersen <petersen@redhat.com> - 8.0.1-53.2
- 8.0.1 respin

* Thu May 12 2016 Jens Petersen <petersen@redhat.com> - 8.0.1-53.1
- 8.0.1 quick build

* Thu Apr 28 2016 Jens Petersen <petersen@redhat.com> - 8.0.0.20160421-52.6
- RC4 perf

* Mon Apr 25 2016 Jens Petersen <petersen@redhat.com> - 8.0.0.20160421-52.5
- RC4 quick

* Thu Apr 21 2016 Jens Petersen <petersen@redhat.com> - 8.0.0.20160411-52.4
- RC3 perf

* Wed Apr 20 2016 Jens Petersen <petersen@redhat.com> - 8.0.0.20160411-52.3
- RC3 quick

* Tue Feb 23 2016 Jens Petersen <petersen@redhat.com> - 8.0.0.20160204-52.2
- https://ghc.haskell.org/trac/ghc/wiki/Status/GHC-8.0.1
- perf build
- BR sphinx for manual

* Mon Feb 22 2016 Jens Petersen <petersen@redhat.com> - 8.0.0.20160204-52.1
- 8.0.1 RC2 bootstrap

* Wed Dec  9 2015 Jens Petersen <petersen@redhat.com> - 7.10.3-52
- 7.30.3 perf build

* Wed Dec  9 2015 Jens Petersen <petersen@redhat.com> - 7.10.3-51
- 7.10.3 quick build
- Cabal-1.22.5.0

* Sat Nov 28 2015 Jens Petersen <petersen@fedoraproject.org> - 7.10.2.20151114-50
- perf build

* Sat Nov 28 2015 Jens Petersen <petersen@fedoraproject.org> - 7.10.2.20151114-49
- 7.10.3 RC3
- bootstrap build

* Mon Nov  9 2015 Jens Petersen <petersen@redhat.com> - 7.10.2.20151105-48
- 7.10.3 RC2 bootstrap
- base bump

* Mon Oct 26 2015 Jens Petersen <petersen@redhat.com> - 7.10.2-47
- bump release over xhtml

* Fri Oct 23 2015 Jens Petersen <petersen@redhat.com> - 7.10.2-9
- forward port el6 tweaks from 7.8.4 branch

* Fri Jul 31 2015 Jens Petersen <petersen@redhat.com> - 7.10.2-8
- perf build

* Fri Jul 31 2015 Jens Petersen <petersen@redhat.com> - 7.10.2-7
- 7.10.2

* Mon Jul 13 2015 Jens Petersen <petersen@redhat.com> - 7.10.1.20150630-6
- perf build

* Mon Jul 13 2015 Jens Petersen <petersen@redhat.com> - 7.10.1.20150630-5
- 7.10.2 RC2
- bump Cabal
- aarch64 SMP/ghci patch is upstream

* Tue Jun 16 2015 Jens Petersen <petersen@redhat.com> - 7.10.1.20150612-4
- perf build

* Mon Jun 15 2015 Jens Petersen <petersen@redhat.com> - 7.10.1.20150612-3
- 7.10.2 RC1
- bump Cabal and binary

* Thu Jun 11 2015 Jens Petersen <petersen@redhat.com> - 7.10.1.20150511-2
- reenable dynamic linking of the ghc programs

* Fri May 15 2015 Jens Petersen <petersen@redhat.com> - 7.10.1.20150511-1
- 7.10.2 snapshot: quick build
- bump base
- enable ghci and smp on aarch64

* Mon May 11 2015 Jens Petersen <petersen@redhat.com> - 7.10.1-2
- production build

* Mon May 11 2015 Jens Petersen <petersen@redhat.com> - 7.10.1-1
- 7.10.1 bootstrap
- bump Cabal, deepseq, ghc-prim, haskeline

* Fri Mar 20 2015 Jens Petersen <petersen@redhat.com> - 7.10.0.20150316-0.6
- production

* Tue Mar 17 2015 Jens Petersen <petersen@redhat.com> - 7.10.0.20150316-0.5
- RC3 bootstrap
- Cabal, array, deepseq, filepath, and process bumped
- on aarch64 link ghc programs statically
- disabling ld hardening (for F23)

* Mon Feb  9 2015 Jens Petersen <petersen@redhat.com> - 7.10.0.20150123-0.4
- RC2 production

* Mon Feb  9 2015 Jens Petersen <petersen@redhat.com> - 7.10.0.20150123-0.3
- RC2 bootstrap
- Cabal and binary bumped

* Sat Jan 17 2015 Jens Petersen <petersen@redhat.com> - 7.10.0.20150116-0.2
- production build

* Sat Jan 17 2015 Jens Petersen <petersen@redhat.com> - 7.10.0.20150116-0.1
- update to latest ghc-7.10 git snapshot

* Thu Jan 15 2015 Jens Petersen <petersen@redhat.com> - 7.10.0.20141222-0.1
- 7.10.1 RC1
- haskell2010, haskell98, old-locale, and old-time libraries gone
- all libraries bumped wrt 7.8.4

* Fri Jan  9 2015 Jens Petersen <petersen@redhat.com> - 7.8.4-38.1
- production build

* Fri Jan  9 2015 Jens Petersen <petersen@redhat.com> - 7.8.4-38
- update to 7.8.4 bugfix release bootstrap

* Fri Jan  9 2015 Jens Petersen <petersen@redhat.com> - 7.8.3-38.4
- sync with latest changes from rawhide 7.8.3 for arm and secondary archs

* Fri Sep  5 2014 Jens Petersen <petersen@redhat.com> - 7.8.3-38.3
- use rpm internal dependency generator with ghc.attr on F22

* Wed Sep  3 2014 Jens Petersen <petersen@redhat.com> - 7.8.3-38.2
- 7.8.3 final release performance build

* Wed Sep  3 2014 Jens Petersen <petersen@redhat.com> - 7.8.3-38.1
- 7.8.3 final release: bootstrap build
- sync with fedora pkg git:
- simpler Cabal PATH warning
- configure ARM with VFPv3D16 and without NEON (#995419)
- hide llvm version warning on ARM now up to 3.4
- add aarch64 with Debian patch by Karel Gardas and Colin Watson
- patch Stg.h to define _DEFAULT_SOURCE instead of _BSD_SOURCE to quieten
  glibc 2.20 warnings (see #1067110)
- add ppc64le support patch from Debian by Colin Watson

* Sat Aug  2 2014 Jens Petersen <petersen@redhat.com> - 7.8.3-36.5
- only apply the Cabal unversion docdir patch to F21 and later

* Thu Jul 10 2014 Jens Petersen <petersen@redhat.com> - 7.8.3-36.4
- 7.8.3 almost final: performance build

* Tue Jul  8 2014 Jens Petersen <petersen@redhat.com> - 7.8.3-36.3
- 7.8.3 almost final release: bootstrap build
- terminfo devel needs ncurses-devel

* Tue Jun 10 2014 Jens Petersen <petersen@redhat.com> - 7.8.3-36.2
- 7.8.3 prerelease snapshot (git 32b4bf3) performance build
- ghc-package-xhtml-terminfo-haskeline.patch obsolete

* Mon Jun  9 2014 Jens Petersen <petersen@redhat.com> - 7.8.3-36.1
- 7.8.3 prerelease snapshot (git aede2d6) bootstrap build
- bump over haskell-platform xhtml

* Sat Apr 12 2014 Jens Petersen <petersen@redhat.com> - 7.8.2-33.3
- production build

* Sat Apr 12 2014 Jens Petersen <petersen@redhat.com> - 7.8.2-33.2
- 7.8.2 bugfix release
- https://www.haskell.org/ghc/docs/7.8.2/html/users_guide/release-7-8-2.html

* Thu Apr 10 2014 Jens Petersen <petersen@redhat.com> - 7.8.1-33.1
- 7.8.1 bootstrap
  https://www.haskell.org/ghc/docs/7.8.1/html/users_guide/release-7-8-1.html
- revert dynlinking in ARM build (upstream abb86ad): it requires gold linker
  which only works with ghc-7.8 for llvm backend

* Thu Mar 13 2014 Jens Petersen <petersen@redhat.com> - 7.8.0.20140228-30.2.1
- shared libs on all secondary archs too

* Sat Mar  1 2014 Jens Petersen <petersen@redhat.com> - 7.8.0.20140226-30.2
- 7.8.1 RC2' bootstrap with testsuite
- unix bumped
- run check section in utf8 encoding

* Fri Feb 28 2014 Jens Petersen <petersen@redhat.com> - 7.8.0.20140226-30.1
- 7.8.1 RC2 bootstrap
- use new xz tarballs
- own libdir/bin/ and libdir/rts-1.0/
- without_vanilla
- no prof
- turn off testsuite

* Mon Feb 10 2014 Jens Petersen <petersen@redhat.com> - 7.8.0.20140201-29.2
- production build without testsuite
- unversion pkgdoc htmldir

* Mon Feb  3 2014 Jens Petersen <petersen@redhat.com> - 7.8.0.20140201-29.1
- update library versions
- merge some updates from master
- handle manpage in filelist whether without_manual or not
- enable shared on ARM

* Mon Oct  7 2013 Jens Petersen <petersen@redhat.com> - 7.7.20131005-25.4
- update to latest git
- update libraries versions
- build with utf8 locale to avoid hGetContents encoding errors

* Wed Oct  2 2013 Jens Petersen <petersen@redhat.com>
- enable dyn by default

* Thu Sep  5 2013 Jens Petersen <petersen@redhat.com> - 7.7.20130828-25.1
- subpackage haskeline, terminfo and xhtml

* Tue Sep  3 2013 Jens Petersen <petersen@redhat.com> - 7.7.20130828-25
- 7.7.20130828 snapshot
- ghc-use-system-libffi.patch, Cabal-fix-dynamic-exec-for-TH.patch,
  Patch12: ghc-7.4.2-Cabal-disable-ghci-libs.patch,
  ghc-llvmCodeGen-empty-array.patch, ghc-7.6.3-LlvmCodeGen-no-3.3-warning.patch
  no longer needed
- library versions of containers, directory, haskell2010, old-locale,
  and old-time unchanged
- transformers now provided by ghc so bump release above current haskell-platform
- needs binary library to build
- dph TH seems to break on ARM

* Sat Jul 27 2013 Jóhann B. Guðmundsson <johannbg@fedoraproject.org> - 7.6.3-18
- ghc-doc-index requires crontabs and mark cron file config noreplace
  (http://fedoraproject.org/wiki/Packaging:CronFiles)

* Wed Jul 24 2013 Jens Petersen <petersen@redhat.com> - 7.6.3-17
- silence warnings about unsupported llvm version (> 3.1) on ARM

* Thu Jul 11 2013 Jens Petersen <petersen@redhat.com> - 7.6.3-16
- revert the executable stack patch since it didn't fully fix the problem
  and yet changed the ghc library hash

* Wed Jul 10 2013 Jens Petersen <petersen@redhat.com> - 7.6.3-15
- turn off executable stack flag in executables (#973512)
  (thanks Edward Zhang for upstream patch and Dhiru Kholia for report)

* Tue Jun 25 2013 Jens Petersen <petersen@redhat.com> - 7.6.3-14
- fix compilation with llvm-3.3 (#977652)
  see http://hackage.haskell.org/trac/ghc/ticket/7996

* Thu Jun 20 2013 Jens Petersen <petersen@redhat.com> - 7.6.3-13
- production perf -O2 build
- see release notes:
  http://www.haskell.org/ghc/docs/7.6.3/html/users_guide/release-7-6-1.html
  http://www.haskell.org/ghc/docs/7.6.3/html/users_guide/release-7-6-2.html
  http://www.haskell.org/ghc/docs/7.6.3/html/users_guide/release-7-6-3.html

* Thu Jun 20 2013 Jens Petersen <petersen@redhat.com> - 7.6.3-12
- bootstrap 7.6.3
- all library versions bumped except pretty
- ghc-7.4-add-support-for-ARM-hard-float-ABI-fixes-5914.patch, and
  ghc-7.4-silence-gen_contents_index.patch are no longer needed
- build with ghc-rpm-macros-extra
- no longer filter type-level package from haddock index
- process obsoletes process-leksah
- do production build with BuildFlavour perf (#880135)

* Tue Feb  5 2013 Jens Petersen <petersen@redhat.com> - 7.4.2-11
- ghclibdir should be owned at runtime by ghc-base instead of ghc-compiler
  (thanks Michael Scherer, #907671)

* Thu Jan 17 2013 Jens Petersen <petersen@redhat.com> - 7.4.2-10
- rebuild for F19 libffi soname bump

* Wed Nov 21 2012 Jens Petersen <petersen@redhat.com> - 7.4.2-9
- fix permissions of ghc-doc-index and only run when root
- ghc-doc-index cronjob no longer looks at /etc/sysconfig/ghc-doc-index

* Sat Nov 17 2012 Jens Petersen <petersen@redhat.com> - 7.4.2-8
- production 7.4.2 build
  http://www.haskell.org/ghc/docs/7.4.2/html/users_guide/release-7-4-2.html

* Sat Nov 17 2012 Jens Petersen <petersen@redhat.com> - 7.4.2-7
- 7.4.2 bootstrap
- update base and unix library versions
- ARM StgCRun patches not longer needed
- use Karel Gardas' ARM hardfloat patch committed upstream
- use _smp_mflags again
- disable Cabal building ghci lib files
- silence the doc re-indexing script and move the doc indexing cronjob
  to a new ghc-doc-index subpackage (#870694)
- do not disable hscolour in build.mk
- drop the explicit hscolour BR
- without_hscolour should now be set by ghc-rpm-macros for bootstrapping

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 7.4.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jun 15 2012 Jens Petersen <petersen@redhat.com> - 7.4.1-5
- use ghc_lib_subpackage instead of ghc_binlib_package (ghc-rpm-macros 0.91)

* Wed May  2 2012 Jens Petersen <petersen@redhat.com> - 7.4.1-4
- add ghc-wrapper-libffi-include.patch to workaround "missing libffi.h"
  for prof compiling on secondary archs

* Sat Apr 28 2012 Jens Petersen <petersen@redhat.com> - 7.4.1-3
- build with llvm-3.0 on ARM
- remove ARM from unregisterised_archs
- add 4 Debian ARM patches for armel and armhf (Iain Lane)

* Wed Mar 21 2012 Jens Petersen <petersen@redhat.com> - 7.4.1-2
- full build

* Wed Feb 15 2012 Jens Petersen <petersen@redhat.com> - 7.4.1-1
- update to new 7.4.1 major release
  http://www.haskell.org/ghc/docs/7.4.1/html/users_guide/release-7-4-1.html
- all library versions bumped
- binary package replaces ghc-binary
- random library dropped
- new hoopl library
- deepseq is now included in ghc
- Cabal --enable-executable-dynamic patch is upstream
- add Cabal-fix-dynamic-exec-for-TH.patch
- sparc linking fix is upstream
- use Debian's system-libffi patch by Joachim Breitner
- setup ghc-deps.sh after ghc_version_override for bootstrapping
- drop ppc64 config, pthread and mmap patches
- do not set GhcUnregisterised explicitly
- add s390 and s390x to unregisterised_archs
- Cabal manual needs pandoc

* Thu Jan 19 2012 Jens Petersen <petersen@redhat.com> - 7.0.4-42
- move ghc-ghc-devel from ghc-libraries to the ghc metapackage

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 7.0.4-41
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Nov 14 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-40
- do alternatives handling correctly (reported by Giam Teck Choon, #753661)
  see https://fedoraproject.org/wiki/Packaging:Alternatives

* Sat Nov 12 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-39
- move ghc-doc and ghc-libs obsoletes
- add HaskellReport license also to the base and libraries subpackages

* Thu Nov 10 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-38
- the post and postun scripts are now for the compiler subpackage

* Wed Nov  2 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-37
- rename ghc-devel metapackage to ghc-libraries
- require ghc-rpm-macros-0.14

* Tue Nov  1 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-36
- move compiler and tools to ghc-compiler
- the ghc base package is now a metapackage that installs all of ghc,
  ie ghc-compiler and ghc-devel (#750317)
- drop ghc-doc provides

* Fri Oct 28 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-35.1
- rebuild against new gmp

* Fri Oct 28 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-35
- add HaskellReport license tag to some of the library subpackages
  which contain some code from the Haskell Reports

* Thu Oct 20 2011 Marcela Mašláňová <mmaslano@redhat.com> - 7.0.4-34.1
- rebuild with new gmp without compat lib

* Thu Oct 20 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-34
- setup ghc-deps.sh after ghc_version_override for bootstrapping

* Tue Oct 18 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-33
- add armv5tel (ported by Henrik Nordström)
- also use ghc-deps.sh when bootstrapping (ghc-rpm-macros-0.13.13)

* Mon Oct 17 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-32
- remove libffi_archs: not allowed to bundle libffi on any arch
- include the ghc (ghci) library in ghc-devel (Narasim)

* Tue Oct 11 2011 Peter Schiffer <pschiffe@redhat.com> - 7.0.4-31.1
- rebuild with new gmp

* Fri Sep 30 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-31
- build with ghc-rpm-macros >= 0.13.11 to fix provides and obsoletes versions
  in library devel subpackages

* Thu Sep 29 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-30
- no need to specify -lffi in build.mk (Henrik Nordström)

* Wed Sep 28 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-29
- port to armv7hl by Henrik Nordström (#741725)

* Wed Sep 14 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-28
- setup ghc-deps.sh when not bootstrapping!

* Wed Sep 14 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-27
- setup dependency generation with ghc-deps.sh since it was moved to
  ghc_lib_install in ghc-rpm-macros

* Fri Jun 17 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-26
- BR same ghc version unless ghc_bootstrapping defined
- add libffi_archs
- drop the quick build profile
- put dyn before p in GhcLibWays
- explain new bootstrapping mode using ghc_bootstrap (ghc-rpm-macros-0.13.5)

* Thu Jun 16 2011 Jens Petersen <petersen@redhat.com> - 7.0.4-25
- update to 7.0.4 bugfix release
  http://haskell.org/ghc/docs/7.0.4/html/users_guide/release-7-0-4.html
- strip static again (upstream #5004 fixed)
- Cabal updated to 1.10.2.0
- re-enable testsuite
- update summary and description

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
- fix %%check

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

* Wed Dec 12 2007 Bryan O'Sullivan <bos@serpentine.com> - 6.8.2-1
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
