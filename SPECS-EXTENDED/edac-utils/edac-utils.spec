## START: Set by rpmautospec
## (rpmautospec version 0.7.3)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 38;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

Name:           edac-utils
Version:        0.18
%global so_version 1
Release:        %autorelease
Summary:        Userspace helper for kernel EDAC drivers

# Everything that contributes to the licenses of the binary RPMs is
# GPL-2.0-or-later.
License:        GPL-2.0-or-later
# Any files under different licenses are part of the build system and do not
# contribute to the license of the binary RPM:
#   - configure is FSFUL AND GPL-2.0-or-later WITH Autoconf-exception-macro; we
#     should probably also consider it AND GPL-2.0-or-later, since it is
#     partially derived from configure.ac, which is GPL-2.0-or-later.
#   - install-sh is X11
SourceLicense:  %{shrink:
                %{license} AND
		FSFUL AND
		GPL-2.0-or-later WITH Autoconf-exception-macro AND
		X11}
URL:            https://github.com/grondo/edac-utils
Source0:        %{url}/archive/%{version}/edac-utils-%{version}.tar.gz
Source1:        edac.service

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

# Update obsolete FSF postal addresses
# https://github.com/grondo/edac-utils/pull/13
#
# Since upstream merged the PR, we feel justified in patching the COPYING file.
Patch:          %{url}/pull/13.patch

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  perl-generators

BuildRequires:  libsysfs-devel
BuildRequires:  systemd-rpm-macros

Requires:       libedac = %{version}-%{release}
Requires:       edac-util = %{version}-%{release}
Requires:       edac-ctl = %{version}-%{release}

%global common_description %{expand:
EDAC (Error Detection and Correction) is a set of Linux kernel modules that
handle reporting of hardware-related errors. Currently these modules mainly
handle detection of ECC memory errors for many x86 and x86-64 chipsets and PCI
bus parity errors.

The edac-utils project currently has three components: libedac, edac-util, and
edac-ctl. The libedac library presents a standard API for reading EDAC error
counts and other information from sysfs, and edac-util uses this API to
generate standard reports from the commandline. The edac-ctl utility is a perl
script which uses config files to load the appropriate EDAC driver for a given
chipset and register motherboard DIMM labels if they are configured. An init
script is also provided which uses edac-ctl to initialize EDAC at system
startup.}

%description %{common_description}

This is a metapackage that installs all three components.


%package -n libedac
Summary:        Standard API for reading EDAC error counts from sysfs

%description -n libedac %{common_description}

This package provides the libedac library.


%package -n libedac-devel
Summary:        Development files for libedac

Requires:       libedac%{?_isa} = %{version}-%{release}

Provides:       edac-utils-devel%{?_isa} = %{version}-%{release}
Provides:       edac-utils-devel = %{version}-%{release}
Obsoletes:      edac-utils-devel < 0.18-18

%description -n libedac-devel %{common_description}

This package contains the development headers and libraries and the man page
for libedac.


%package -n edac-util
Summary:        Command-line tool to generate standard EDAC reports

Requires:       libedac%{?_isa} = %{version}-%{release}

%description -n edac-util %{common_description}

This package provides the edac-util command-line tool.


%package -n edac-ctl
Summary:        Script to load EDAC driver and register DIMM labels

# Require dmidecode where it is available. Architecture list from
# ExclusiveArch in dmidecode.spec; updated 2021-12-06.
%ifarch %{ix86} x86_64 ia64 aarch64
Requires:       dmidecode
%endif
Requires:       hwdata
# for modprobe:
Requires:       kmod

# This subpackage would be BuildArch: noarch, except for the arch-conditional
# dependency on dmidecode.

%description -n edac-ctl %{common_description}

This package provides the edac-ctl script and the edac service.


%prep
%autosetup -p1


%conf
autoreconf --force --install --verbose
%configure --disable-static


%build
%make_build


%install
%make_install
find '%{buildroot}' -type f -name '*.la' -print -delete

install -D -p -m 0644 '%{SOURCE1}' '%{buildroot}%{_unitdir}/edac.service'
rm -f '%{buildroot}%{_sysconfdir}/init.d/edac'
install -d -m 0755 '%{buildroot}%{_sysconfdir}/edac/labels.d' \
    '%{buildroot}%{_sysconfdir}/edac/mainboard'


%post -n edac-ctl
%systemd_post edac.service


%preun -n edac-ctl
%systemd_preun edac.service


%postun -n edac-ctl
%systemd_postun_with_restart edac.service


%files
# Empty; the base package is now a metapackage


%files -n libedac
%license AUTHORS COPYING DISCLAIMER
%{_libdir}/libedac.so.%{so_version}{,.*}


%files -n libedac-devel
%doc README NEWS
%{_libdir}/libedac.so
%{_includedir}/edac.h
%{_mandir}/man3/edac.3*


%files -n edac-util
%{_bindir}/edac-util
%{_mandir}/man1/edac-util.1*


%files -n edac-ctl
%license AUTHORS COPYING DISCLAIMER
%doc README NEWS

%{_sbindir}/edac-ctl
%{_mandir}/man8/edac-ctl.8*
# The explicit directory permissions don’t seem necessary, but we don’t see a
# reason to change them now, either.
%dir %attr(0755,root,root) %{_sysconfdir}/edac
%config(noreplace) %{_sysconfdir}/edac/labels.db
%dir %attr(0755,root,root) %dir %{_sysconfdir}/edac/labels.d
%dir %attr(0755,root,root) %dir %{_sysconfdir}/edac/mainboard
%{_unitdir}/edac.service


%changelog
## START: Generated by rpmautospec
* Thu Dec 12 2024 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-38
- Add a SourceLicense field

* Fri Nov 01 2024 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-37
- Invoke autoreconf and configure in %%conf rather than in %%build

* Wed Jul 17 2024 Fedora Release Engineering <releng@fedoraproject.org> - 0.18-36
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Tue Mar 19 2024 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-35
- Fully patch obsolete FSF postal address in license text
- Since upstream merged the PR for this, we now patch the license text file

* Wed Jan 24 2024 Fedora Release Engineering <releng@fedoraproject.org> - 0.18-32
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Fri Jan 19 2024 Fedora Release Engineering <releng@fedoraproject.org> - 0.18-31
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Wed Jul 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 0.18-30
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Thu Jan 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 0.18-29
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Tue Dec 20 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-28
- Leaf package: remove i686 support

* Tue Dec 20 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-27
- Slightly simplify a files list

* Mon Aug 01 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-26
- Fix typo in spec file comment

* Mon Aug 01 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-25
- Update License field to SPDX

* Thu Jul 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 0.18-24
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Fri Jul 08 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-23
- Fix extra newline in description

* Sat Apr 16 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-22
- Stop numbering patches

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 0.18-21
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-20
- Depend on dmidecode (from edac-ctl) on aarch64, too

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-19
- Create and own supported config subdirectories

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-18
- Split into subpackages by component

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-17
- Drop ExcludeArch: s390x

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-16
- Mark AUTHORS and DISCLAIMER as license files, too

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-15
- Use stricter file path globs

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-14
- Drop obsolete ldconfig_scriptlets macro

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-13
- Depend on kmod for /usr/sbin/modprobe

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-12
- Drop sysfsutils dependency, which seems to be bogus

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-11
- Lighten explicit systemd dependencies

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-10
- Fix obsolete FSF postal addresses (except in license file)

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-9
- Improved source URL

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-8
- Make -devel dependency on base package arched

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-7
- Re-generate configure script (fix RHBZ#1987449)

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-6
- Improved package description

* Mon Dec 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18-5
- Various spec file style adjustments

* Wed Jul 21 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.18-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Tue Mar 02 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 0.18-2
- Rebuilt for updated systemd-rpm-macros
  See https://pagure.io/fesco/issue/2583.

* Tue Feb 02 2021 Peter Robinson <pbrobinson@fedoraproject.org> - 0.18-1
- Update to 0.18
- Spec cleanup
- New upstream URLs/Source

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.16-24
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.16-23
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.16-22
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.16-21
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.16-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.16-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.16-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.16-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.16-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.16-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.16-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sun Aug 23 2015 Ralf Corsépius <corsepiu@fedoraproject.org> - 0.16-13
- BR: systemd (Fix F23FTBFS, RHBZ#1239443).

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.16-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Aug 22 2014 Peter Robinson <pbrobinson@fedoraproject.org> 0.16-11
- edac supported in the kernel for ppc64/aarch64 too

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.16-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.16-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug  3 2013 Peter Robinson <pbrobinson@fedoraproject.org> 0.16-7
- Minor spec cleanups to fix FTBFS

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.16-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 0.16-5
- Perl 5.18 rebuild

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.16-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Oct 11 2012 Peter Robinson <pbrobinson@fedoraproject.org> 0.16-3
- ARM has support for EDAC so enable the utils

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.16-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May 02 2012 Aristeu Rozanski <aris@redhat.com> - 0.16-1
- New upstream release 0.16

* Wed Mar 14 2012 Jon Ciesla <limburgher@gmail.com> - 0.9-14
- Migrate to systemd, BZ 767784.

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed May 21 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0.9-9
- fix license tag

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.9-8
- Autorebuild for GCC 4.3

* Wed Jul 18 2007 Aristeu Rozanski <arozansk@redhat.com> 0.9-7
- including missing .patch file

* Tue Jul 17 2007 Aristeu Rozanski <arozansk@redhat.com> 0.9-6
- building FC7 package

* Thu Jul 09 2007 Aristeu Rozanski <arozansk@redhat.com> 0.9-5
- Fixed start/stop message, missing echo
- Fixed status command to use edac-util

* Thu Jun 15 2007 Aristeu Rozanski <arozansk@redhat.com> 0.9-4
- Removed debug code left by mistake on initrd file
- Fixed model comparing in edac-ctl script

* Wed Jun 13 2007 Aristeu Rozanski <arozansk@redhat.com> 0.9-3
- Adding COPYING to documents
- Fixing Requires to use a single equal sign, instead of two

* Wed Jun 13 2007 Aristeu Rozanski <arozansk@redhat.com> 0.9-2
- Multiple updates in spec file to conform to the standards pointed by
  Jarod Wilson

* Wed Jun 06 2007 Aristeu Rozanski <arozansk@redhat.com> 0.9-1
- Updated version to 0.9, separate project now
- Updated spec file based on upstream edac-utils spec file
- Removed driver loading portion in a separate patch, it'll be removed from
  upstream too
- Fixed init script to use functions and daemon function

* Thu Apr 19 2007 Aristeu Rozanski <arozansk@redhat.com> 20061222-3
- Updated initrd script to start after syslogd, otherwise if the board isn't
  supported, the user will never know.

* Thu Apr 19 2007 Aristeu Rozanski <arozansk@redhat.com> 20061222-2
- Changing this package to noarch and preventing the build on ia64, ppc64,
  s390 and s390x

* Thu Mar 12 2007 Aristeu Rozanski <arozansk@redhat.com> 20061222-1
- Package created

## END: Generated by rpmautospec
