%global commit c2f5d130c91b1696385a6ae0b5bcfd5214bcc9ca
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name: tre
Version: 0.8.0
Release: 18.20140228git%{shortcommit}%{?dist}
License: BSD
Source0: https://github.com/laurikari/tre/archive/%{commit}/tre-%{commit}.tar.gz
Patch0: %{name}-chicken.patch
# make internal tests of agrep work with just-built shared library
Patch1: %{name}-tests.patch
# don't force build-time LDFLAGS into tre.pc
Patch2: %{name}-ldflags.patch
# CVE-2016-8859, based on http://seclists.org/oss-sec/2016/q4/att-183/0001-fix-missing-integer-overflow-checks-in-regexec-buffe.patch
Patch3: %{name}-CVE-2016-8859.patch
# last hunk from the patch from https://github.com/laurikari/tre/issues/37
Patch4: %{name}-issue37.patch
Summary: POSIX compatible regexp library with approximate matching
URL: http://laurikari.net/tre/
# rebuild autotools for bug #926655
BuildRequires: gettext-devel
BuildRequires: libtool
BuildRequires: python2-devel
Requires: %{name}-common = %{version}-%{release}

%description
TRE is a lightweight, robust, and efficient POSIX compatible regexp
matching library with some exciting features such as approximate
matching.

%package common
Summary: Cross-platform files for use with the tre package
BuildArch: noarch

%description common
This package contains platform-agnostic files used by the TRE
library.

%package devel
Requires: tre = %{version}-%{release}
Summary: Development files for use with the tre package

%description devel
This package contains header files and static libraries for use when
building applications which use the TRE library.

%package -n python2-%{name}
Summary: Python bindings for the tre library
%{?python_provide:%python_provide python2-tre}

%description -n python2-%{name}
This package contains the python bindings for the TRE library.

%package -n agrep
Summary: Approximate grep utility

%description -n agrep
The agrep tool is similar to the commonly used grep utility, but agrep
can be used to search for approximate matches.

The agrep tool searches text input for lines (or records separated by
strings matching arbitrary regexps) that contain an approximate, or
fuzzy, match to a specified regexp, and prints the matching lines.
Limits can be set on how many errors of each kind are allowed, or
only the best matching lines can be output.

Unlike other agrep implementations, TRE agrep allows full POSIX
regexps of any length, any number of errors, and non-uniform costs.

%prep
%setup -q -n tre-%{commit}
# hack to fix python bindings build
ln -s lib tre
%patch0 -p1 -b .chicken
%patch1 -p1 -b .tests
%patch2 -p1 -b .ldflags
%patch3 -p1 -b .CVE-2016-8859
%patch4 -p1 -b .issue37
# rebuild autotools for bug #926655
touch ChangeLog
autoreconf -vif

%build
%configure --disable-static --disable-rpath
%{__make} %{?_smp_mflags}
pushd python
%py2_build
popd

%install
%{__make} install DESTDIR=$RPM_BUILD_ROOT
pushd python
%py2_install
popd
rm $RPM_BUILD_ROOT%{_libdir}/*.la
%find_lang %{name}

%check
%{__make} check

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%{_libdir}/libtre.so.*

%files common -f %{name}.lang
%doc AUTHORS ChangeLog LICENSE NEWS README THANKS TODO
%doc doc/*.html doc/*.css

%files devel
%{_libdir}/libtre.so
%{_libdir}/pkgconfig/*
%{_includedir}/*

%files -n python2-%{name}
%attr(0755,root,root) %{python2_sitearch}/tre.so
%{python2_sitearch}/tre-%{version}-py2.?.egg-info

%files -n agrep
%{_bindir}/agrep
%{_mandir}/man1/agrep.1*

%changelog
* Wed Nov 02 2016 Dominik Mierzejewski <rpm@greysector.net> 0.8.0-18.20140228gitc2f5d13
- fix CVE-2016-8859 (#1387112, #1387113)
- probably fix CVE-2015-3796 (see upstream issue #37 and
  https://bugs.chromium.org/p/project-zero/issues/detail?id=428)
- update python bindings subpackage to current guidelines
- fix parallel installation of multilib packages (patch by joseba.gar at gmail.com)
  (bug #1275830)

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-17.20140228gitc2f5d13
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.0-16.20140228gitc2f5d13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jan 05 2016 Dominik Mierzejewski <rpm@greysector.net> 0.8.0-15.20140228gitc2f5d13
- keep old timestamps embedded in .mo files (bug #1275830)

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-14.20140228gitc2f5d13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 08 2015 Dominik Mierzejewski <rpm@greysector.net> 0.8.0-13.20140228gitc2f5d13
- update to latest snapshot from github
- drop patches merged upstream
- fix broken LDFLAGS in tre.pc (#1224203)

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Mar 06 2014 Dominik Mierzejewski <rpm@greysector.net> 0.8.0-10
- fix build on aarch64 (bug #926655)
- drop obsolete specfile parts
- fix deprecated python macro usage

* Tue Feb  4 2014 Tom Callaway <spot@fedoraproject.org> - 0.8.0-9
- add missing changes from R to be able to use tre in R as system lib (and resolve arm fails)
  Credit to Orion Poplawski.

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jul 27 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Oct 26 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-4
- Rebuilt for glibc bug#747377

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 0.8.0-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Sun Sep 20 2009 Dominik Mierzejewski <rpm@greysector.net> 0.8.0-1
- updated to 0.8.0 (ABI change)

* Sat Aug 22 2009 Dominik Mierzejewski <rpm@greysector.net> 0.7.6-2
- added missing defattr for python subpackage
- dropped conditionals for Fedora <10
- used alternative method for rpath removal
- fixed internal testsuite to run with just-built shared library
- dropped unnecessary build dependencies

* Tue Jul 28 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 0.7.6-1
- new version 0.7.6

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.5-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.5-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.7.5-6
- Rebuild for Python 2.6

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.7.5-5
- Autorebuild for GCC 4.3

* Tue Jan 01 2008 Dominik Mierzejewski <rpm@greysector.net> 0.7.5-4
- fix build in rawhide (include python egg-info file)

* Wed Oct 31 2007 Dominik Mierzejewski <rpm@greysector.net> 0.7.5-3
- include python bindings (bug #355241)
- fix chicken-and-egg problem when building python bindings

* Wed Aug 29 2007 Dominik Mierzejewski <rpm@greysector.net> 0.7.5-2
- rebuild for BuildID
- update license tag

* Mon Jan 29 2007 Dominik Mierzejewski <rpm@greysector.net> 0.7.5-1
- update to 0.7.5
- remove redundant BRs
- add %%check

* Thu Sep 14 2006 Dominik Mierzejewski <rpm@greysector.net> 0.7.4-6
- remove ExcludeArch, the bug is in crm114

* Tue Aug 29 2006 Dominik Mierzejewski <rpm@greysector.net> 0.7.4-5
- mass rebuild

* Fri Aug 04 2006 Dominik Mierzejewski <rpm@greysector.net> 0.7.4-4
- bump release to fix CVS tag

* Thu Aug 03 2006 Dominik Mierzejewski <rpm@greysector.net> 0.7.4-3
- per FE guidelines, ExcludeArch only those problematic arches

* Wed Aug 02 2006 Dominik Mierzejewski <rpm@greysector.net> 0.7.4-2
- fixed rpmlint warnings
- ExclusiveArch: %%{ix86} until amd64 crash is fixed and somebody
  tests ppc(32)

* Wed Jul 26 2006 Dominik Mierzejewski <rpm@greysector.net> 0.7.4-1
- 0.7.4
- disable evil rpath
- added necessary BRs
- license changed to LGPL

* Sun Feb 19 2006 Dominik Mierzejewski <rpm@greysector.net> 0.7.2-1
- \E bug patch
- FE compliance

* Sun Nov 21 2004 Ville Laurikari <vl@iki.fi>
- added agrep man page

* Sun Mar 21 2004 Ville Laurikari <vl@iki.fi>
- added %%doc doc

* Wed Feb 25 2004 Ville Laurikari <vl@iki.fi>
- removed the .la file from devel package

* Mon Dec 22 2003 Ville Laurikari <vl@iki.fi>
- added %%post/%%postun ldconfig scriplets.

* Fri Oct 03 2003 Ville Laurikari <vl@iki.fi>
- included in the TRE source tree as `tre.spec.in'.

* Tue Sep 30 2003 Matthew Berg <mberg@synacor.com>
- tagged release 1
- initial build
