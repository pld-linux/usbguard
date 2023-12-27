#
# Conditional build:
%bcond_without	static_libs	# static library
%bcond_without	systemd		# systemd units

Summary:	Software framework for implementing USB device authorization policies
Name:		usbguard
Version:	1.1.2
Release:	1
License:	GPL v2+
Group:		Applications/System
Source0:	https://github.com/USBGuard/usbguard/releases/download/%{name}-%{version}/usbguard-%{version}.tar.gz
# Source0-md5:	3c9478e17bac575ff51b1d746e72f25c
Patch0:		gcc13.patch
URL:		https://usbguard.github.io/
BuildRequires:	PEGTL-devel
BuildRequires:	asciidoc
BuildRequires:	audit-libs-devel >= 2.7.7
BuildRequires:	dbus-devel
BuildRequires:	glib2-devel
%ifnarch %arch_with_atomics64
BuildRequires:	libatomic-devel
%endif
BuildRequires:	libcap-ng-devel >= 0.7.0
BuildRequires:	libqb-devel >= 0.16.0
BuildRequires:	libseccomp-devel >= 2.0.0
BuildRequires:	libsodium-devel >= 0.4.5
BuildRequires:	libstdc++-devel >= 6:8
BuildRequires:	libxml2-progs
BuildRequires:	libxslt-progs
BuildRequires:	linux-libc-headers >= 7:2.6.10
BuildRequires:	openldap-devel
BuildRequires:	pkgconfig
BuildRequires:	polkit-devel
BuildRequires:	protobuf-devel >= 2.5.0
BuildRequires:	rpmbuild(macros) >= 2.025
%{?with_systemd:BuildRequires:	systemd-devel}
BuildRequires:	umockdev-devel >= 0.8.0
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
Requires:	audit-libs >= 2.7.7
Requires:	libcap-ng >= 0.7.0
Requires:	libseccomp >= 2.0.0
%{?with_systemd:Requires:	systemd-units >= 38}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
USBGuard is a software framework for implementing USB device
authorization policies (what kind of USB devices are authorized) as
well as method of use policies (how a USB device may interact with the
system). Simply put, it is a USB device allowlisting tool.

%package libs
Summary:	usbguard library
Group:		Libraries
Requires:	libqb >= 0.16.0
Requires:	libsodium >= 0.4.5
Requires:	protobuf-libs >= 2.5.0
Requires:	umockdev >= 0.8.0

%description libs
usbguard library.

%package devel
Summary:	Header files for the usbguard library
Group:		Development/Libraries
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

%description devel
Header files for usbguard library.

%package static
Summary:	Static usbguard library
Group:		Development/Libraries
Requires:	%{name}-devel%{?_isa} = %{version}-%{release}

%description static
Static usbguard library.

%prep
%setup -q
%patch0 -p1

%build
%configure \
	--disable-silent-rules \
	%{__enable_disable static_libs static} \
	%{__enable_disable systemd} \
	--with-bash-completion-dir="%{bash_compdir}" \
	--with-bundled-catch \
	--with-ldap

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__rm} $RPM_BUILD_ROOT%{_libdir}/libusbguard.la

%clean
rm -rf $RPM_BUILD_ROOT

%post
%{?with_systemd:%systemd_post usbguard.service usbguard-dbus.service}

%preun
%{?with_systemd:%systemd_preun usbguard.service usbguard-dbus.service}

%postun
%{?with_systemd:%systemd_postun usbguard.service usbguard-dbus.service}

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc CHANGELOG.md README.adoc
%dir %{_sysconfdir}/usbguard
%dir %{_sysconfdir}/usbguard/IPCAccessControl.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/usbguard/rules.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/usbguard/usbguard-daemon.conf
%attr(755,root,root) %{_bindir}/usbguard
%attr(755,root,root) %{_bindir}/usbguard-rule-parser
%attr(755,root,root) %{_sbindir}/usbguard-daemon
%attr(755,root,root) %{_sbindir}/usbguard-dbus
%if %{with systemd}
%{systemdunitdir}/usbguard.service
%{systemdunitdir}/usbguard-dbus.service
%endif
%{bash_compdir}/usbguard
%{_datadir}/dbus-1/system.d/org.usbguard1.conf
%{_datadir}/dbus-1/system-services/org.usbguard1.service
%{_mandir}/man1/usbguard.1*
%{_mandir}/man5/usbguard-daemon.conf.5*
%{_mandir}/man5/usbguard-rules.conf.5*
%{_mandir}/man8/usbguard-daemon.8*
%{_mandir}/man8/usbguard-dbus.8*
%{_datadir}/polkit-1/actions/org.usbguard1.policy

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libusbguard.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libusbguard.so.1

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libusbguard.so
%{_includedir}/usbguard
%{_pkgconfigdir}/libusbguard.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libusbguard.a
%endif
