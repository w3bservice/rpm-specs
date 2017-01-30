# License: MIT
# http://opensource.org/licenses/MIT
#
# Please, preserve the changelog entries

%define build_user mockbuild 


Name:		piler
Version:	1.2.0
Release:	1%{?dist}
Summary:	Piler is a feature rich open source email archiving solution

Group:		Applications/System
License:	GPLv3
URL:		http://www.mailpiler.org/
Source0:	https://bitbucket.org/jsuto/piler/downloads/%{name}-%{version}.tar.gz
Source1:	piler.service
Source2:	piler.initd
Source3:	piler.default
Source4:	searchd.initd
Source5:	searchd.service
Source6:	searchd.default

BuildRequires:  tcp_wrappers-devel openssl-devel libzip-devel mysql-devel clamav-devel
BuildRequires:  sysstat catdoc poppler-utils tnef unrtf wget
Requires:       tre openssl tcp_wrappers libzip sysstat catdoc poppler-utils tnef unrtf wget clamav-server clamav
Requires:	php php-mysql php-pecl-memcache mysql httpd memcached sphinx

%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
Requires:	mariadb-server
BuildRequires:  tre-devel
%else
Requires:	mysql-server
#CentOS 6/EPEL 6 comes with tre 0.7.6 which is too old
BuildRequires:	tre-devel >= 0.8
%endif


Provides:	libpiler.so()(64bit)

BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)



%if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
%global with_systemd 1
%else
%global with_systemd 0
%endif


%if %{with_systemd}
BuildRequires: systemd-devel
BuildRequires: systemd-units
Requires: systemd-units
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires(post): systemd-sysv
%else
Requires(preun): initscripts
Requires(postun): initscripts
%endif

Requires(pre): /usr/sbin/useradd


%description
Piler is a feature rich open source email archiving solution, and a viable alternative to commercial email archiving products.

%prep
%setup -q




%build
%configure \
	--sysconfdir=/etc \
	--localstatedir=/var \
	--with-database=mysql \
	--with-piler-user=%{build_user} \
	--enable-tcpwrappers \
	--enable-memcached \
	--enable-clamd

make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
getent group piler >/dev/null || /usr/sbin/groupadd -r piler >/dev/null 2>&1 || :
getent passwd piler >/dev/null || /usr/sbin/useradd -r -g piler -d /var/piler -s /bin/bash -c "Mailpiler Server" piler >/dev/null 2>&1 || :
make DESTDIR=$RPM_BUILD_ROOT install

%if %{with_systemd}
mkdir -vp %{buildroot}/usr/lib/systemd/system
install -m 644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/piler.service
#install -m 644 %{SOURCE5} %{buildroot}/usr/lib/systemd/system/searchd.service
%else
install -D -m 755 %{SOURCE2} %{buildroot}/%{_initrddir}/piler
#install -D -m 755 %{SOURCE4} %{buildroot}/%{_initrddir}/searchd
%endif

#sql schema
mv -f util/db-upgrade-0.1.24-vs-1.1.0.sql %{buildroot}/usr/share/piler
mv -f util/db-upgrade-1.1.0-vs-1.2.0.sql %{buildroot}/usr/share/piler

#contrib stuff
mkdir %{buildroot}/usr/share/piler/contrib
mv -f contrib/* %{buildroot}/usr/share/piler/contrib



#webui stuff
#mkdir -p %{buildroot}/%{_localstatedir}/lib/%{name}
#mv -f webui/* %{buildroot}/%{_localstatedir}/lib/%{name}
mkdir -p %{buildroot}/var/www/%{name}
mv -f webui/* %{buildroot}/var/www/%{name}
mv -f webui/.htaccess %{buildroot}/var/www/%{name}

#sysconfig and systemd/sysv-init stuff:
mkdir %{buildroot}/etc/sysconfig
mv -f %{SOURCE3} %{buildroot}/etc/sysconfig/piler

#we don't gonna use the original init scripts but our own!
rm -f %{buildroot}/etc/init.d/rc.piler
rm -f %{buildroot}/etc/init.d/rc.searchd


mkdir -p $RPM_BUILD_ROOT/etc/ld.so.conf.d
mkdir -p $RPM_BUILD_ROOT/%{_libdir}/piler
mv -f $RPM_BUILD_ROOT/%{_libdir}/libpiler* $RPM_BUILD_ROOT/%{_libdir}/piler
echo "%{_libdir}/piler" > $RPM_BUILD_ROOT/etc/ld.so.conf.d/%{name}-%{_arch}.conf



%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group piler >/dev/null || /usr/sbin/groupadd -r piler >/dev/null 2>&1 || :
getent passwd piler >/dev/null || /usr/sbin/useradd -r -g piler -d /var/piler -s /bin/bash -c "Mailpiler Server" piler >/dev/null 2>&1 || :

%post
/sbin/ldconfig

%if %{with_systemd}
%systemd_post piler.service
#%systemd_post searchd.service
%else
if [ $1 = 1 ]; then
    # Initial installation
%if %{with_systemd}
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
%else
    /sbin/chkconfig --add piler

%endif
fi
%endif

# print postinstall instructions
echo -e "--------------------------------------------------------"
echo -e "Thanks for using Piler!"
echo -e ""
echo -e "Do not forget to run the Piler postinstallation script"
echo -e "which can be found in: /usr/libexec/piler/postinstall.sh"
echo -e ""
echo -e "--------------------------------------------------------"




%preun

%if 0%{?systemd_preun:1}
%systemd_preun piler.service
%else
if [ $1 = 0 ]; then
    # Package removal, not upgrade
%if %{with_systemd}
    /bin/systemctl --no-reload disable piler.service >/dev/null 2>&1 || :
    /bin/systemctl stop piler.service >/dev/null 2>&1 || :
%else
    /sbin/service piler stop >/dev/null 2>&1
    /sbin/chkconfig --del piler
%endif
fi
%endif


%postun
if [ $1 = 0 ] ; then
    /sbin/ldconfig
fi

%if 0%{?systemd_postun_with_restart:1}
%systemd_postun_with_restart piler.service
%else
%if %{with_systemd}
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ]; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart piler.service >/dev/null 2>&1 || :
fi
%else
if [ $1 -ge 1 ]; then
    /sbin/service piler restart >/dev/null 2>&1 || :
fi
%endif
%endif



%files
%defattr(-,root,root,-)
%doc README RELEASE_NOTES VERSION LICENSE CREDITS
%dir /usr/libexec/piler
%dir /etc/piler
%dir /var/piler
%dir /var/piler/store
%dir /var/piler/stat
%dir /var/piler/tmp
%dir /var/piler/sphinx

%dir %{_libdir}/piler
%{_libdir}/piler/libpiler.a
%{_libdir}/piler/libpiler.so.0.1.1
%{_libdir}/piler/libpiler.so
%{_libdir}/piler/libpiler.so.0
/etc/ld.so.conf.d/piler-%{_arch}.conf


%attr(0755,root,piler) %{_sbindir}/piler
%attr(0755,root,piler) %{_sbindir}/pilerconf
%attr(0755,root,piler) /usr/bin/pilerget
%attr(0755,root,piler) /usr/bin/pileraget
%attr(0755,root,piler) /usr/bin/pilerimport
%attr(0755,root,piler) /usr/bin/pilerexport
%attr(0755,root,piler) /usr/bin/pilerpurge
%attr(0755,root,piler) /usr/bin/reindex
%attr(0755,root,piler) /usr/bin/pilertest
#%attr(6555,piler,piler) /usr/bin/pilertest
/etc/piler/piler.conf.dist

%config(noreplace) /etc/sysconfig/piler
%attr(0640,root,piler) %config(noreplace) /etc/piler/piler.conf

/etc/piler/sphinx.conf.dist
%{_libexecdir}/%{name}/automated-search.php
%{_libexecdir}/%{name}/daily-report.php
%{_libexecdir}/%{name}/gmail-imap-import.php
%{_libexecdir}/%{name}/generate_stats.php
%{_libexecdir}/%{name}/mailstat.php
%{_libexecdir}/%{name}/sign.php
%attr(0755,root,piler) %{_libexecdir}/%{name}/indexer.delta.sh
%attr(0755,root,piler) %{_libexecdir}/%{name}/indexer.main.sh
%attr(0755,root,piler) %{_libexecdir}/%{name}/indexer.attachment.sh
%attr(0755,root,piler) %{_libexecdir}/%{name}/import.sh
%attr(0755,root,piler) %{_libexecdir}/%{name}/purge.sh
%attr(0755,root,piler) %{_libexecdir}/%{name}/postinstall.sh
/usr/share/piler/db-mysql.sql
/usr/share/piler/db-mysql-root.sql.in
%attr(0755,root,piler) /usr/share/piler/deduphelper
/usr/share/piler/db-upgrade-1.1.0-vs-1.2.0.sql
/usr/share/piler/db-upgrade-0.1.24-vs-1.1.0.sql

#%{_localstatedir}/lib/%{name}/*
/var/www/%{name}/*
/var/www/%{name}/.htaccess

/usr/share/piler/contrib/*

%if %{with_systemd}
/usr/lib/systemd/system/piler.service
%else
%{_initrddir}/piler
%endif



%changelog
* Tue Jan 24 2017 Michael Seevogel <michael at michaelseevogel.de> - 1:1.2.0-1
- Piler 1.2.0. release
