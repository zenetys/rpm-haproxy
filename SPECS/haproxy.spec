%define haproxy_user    haproxy
%define haproxy_group   %{haproxy_user}
%define haproxy_homedir %{_localstatedir}/lib/haproxy
%define haproxy_confdir %{_sysconfdir}/haproxy
%define haproxy_datadir %{_datadir}/haproxy

%global _hardened_build 1

Name:           haproxy
Version:        1.8.15
Release:        5%{?dist}
Summary:        HAProxy reverse proxy for high availability environments

Group:          System Environment/Daemons
License:        GPLv2+

URL:            http://www.haproxy.org/
Source0:        http://www.haproxy.org/download/1.8/src/haproxy-%{version}.tar.gz
Source1:        %{name}.service
Source2:        %{name}.cfg
Source3:        %{name}.logrotate
Source4:        %{name}.sysconfig
Source5:        halog.1

Patch0:		bz1664533-fix-handling-priority-flag-HTTP2-decoder.patch

BuildRequires:  lua-devel
BuildRequires:  pcre-devel
BuildRequires:  zlib-devel
BuildRequires:  openssl-devel
BuildRequires:  systemd-devel
BuildRequires:  systemd-units

Requires(pre):      shadow-utils
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
HAProxy is a TCP/HTTP reverse proxy which is particularly suited for high
availability environments. Indeed, it can:
 - route HTTP requests depending on statically assigned cookies
 - spread load among several servers while assuring server persistence
   through the use of HTTP cookies
 - switch to backup servers in the event a main one fails
 - accept connections to special ports dedicated to service monitoring
 - stop accepting connections without breaking existing ones
 - add, modify, and delete HTTP headers in both directions
 - block requests matching particular patterns
 - report detailed status to authenticated users from a URI
   intercepted from the application

%prep
%setup -q
%patch0 -p1

%build
regparm_opts=
%ifarch %ix86 x86_64
regparm_opts="USE_REGPARM=1"
%endif

%{__make} %{?_smp_mflags} CPU="generic" TARGET="linux2628" USE_OPENSSL=1 USE_PCRE=1 USE_ZLIB=1 USE_LUA=1 USE_CRYPT_H=1 USE_SYSTEMD=1 USE_LINUX_TPROXY=1 USE_GETADDRINFO=1 ${regparm_opts} ADDINC="%{optflags}" ADDLIB="%{__global_ldflags}"

pushd contrib/halog
%{__make} ${halog} OPTIMIZE="%{optflags} %{build_ldflags}" LDFLAGS=
popd

pushd contrib/iprange
%{__make} ${iprange} OPTIMIZE="%{optflags} %{build_ldflags}" LDFLAGS=
popd

%install
%{__make} install-bin DESTDIR=%{buildroot} PREFIX=%{_prefix} TARGET="linux2628"
%{__make} install-man DESTDIR=%{buildroot} PREFIX=%{_prefix}

%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{haproxy_confdir}/%{name}.cfg
%{__install} -p -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -p -D -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__install} -p -D -m 0644 %{SOURCE5} %{buildroot}%{_mandir}/man1/halog.1
%{__install} -d -m 0755 %{buildroot}%{haproxy_homedir}
%{__install} -d -m 0755 %{buildroot}%{haproxy_datadir}
%{__install} -d -m 0755 %{buildroot}%{_bindir}
%{__install} -p -m 0755 ./contrib/halog/halog %{buildroot}%{_bindir}/halog
%{__install} -p -m 0755 ./contrib/iprange/iprange %{buildroot}%{_bindir}/iprange
%{__install} -p -m 0644 ./examples/errorfiles/* %{buildroot}%{haproxy_datadir}

for httpfile in $(find ./examples/errorfiles/ -type f) 
do
    %{__install} -p -m 0644 $httpfile %{buildroot}%{haproxy_datadir}
done

%{__rm} -rf ./examples/errorfiles/

find ./examples/* -type f ! -name "*.cfg" -exec %{__rm} -f "{}" \;

for textfile in $(find ./ -type f -name '*.txt')
do
    %{__mv} $textfile $textfile.old
    iconv --from-code ISO8859-1 --to-code UTF-8 --output $textfile $textfile.old
    %{__rm} -f $textfile.old
done

%pre
getent group %{haproxy_group} >/dev/null || \
    groupadd -r %{haproxy_group}
getent passwd %{haproxy_user} >/dev/null || \
    useradd -r -g %{haproxy_user} -d %{haproxy_homedir} \
    -s /sbin/nologin -c "haproxy" %{haproxy_user}
exit 0

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%defattr(-,root,root,-)
%doc doc/* examples/*
%doc CHANGELOG README ROADMAP VERSION
%license LICENSE
%dir %{haproxy_homedir}
%dir %{haproxy_confdir}
%dir %{haproxy_datadir}
%{haproxy_datadir}/*
%config(noreplace) %{haproxy_confdir}/%{name}.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_unitdir}/%{name}.service
%{_sbindir}/%{name}
%{_bindir}/halog
%{_bindir}/iprange
%{_mandir}/man1/*

%changelog
* Wed Jan 09 2019 Ryan O'Hara <rohara@redhat.com> - 1.8.15-5
- Resolve CVE-2018-20615 (#1664533)

* Sun Dec 16 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.15-4
- Use empty LDFLAGS to prevent stripping, maintain hardened build

* Sat Dec 15 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.15-3
- Use LDFLAGS when building contib tools to prevent binary stripping

* Fri Dec 14 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.15-2
- Bump release

* Thu Dec 13 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.15-1
- Update to 1.8.15 (#1631815)
- Resolve CVE-2018-20102 (#1659017)
- Resolve CVE-2018-20103 (#1659019)

* Tue Oct 02 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.14-1
- Update to 1.8.14 (#1631815)
- Resolve CVE-2018-14645 (#1631539)

* Wed Jul 25 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.12-2
- Fix ownership of /var/lib/haproxy/ to avoid selinux DAC override errors

* Mon Jul 02 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.12-1
- Update to 1.8.12
- Resolve CVE-2018-10184 (#1569643)
- Resolve CVE-2018-11469 (#1584787)

* Thu Apr 19 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.8-1
- Update to 1.8.8 (#1560121)

* Mon Apr 09 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.7-1
- Update to 1.8.7 (#1560121)

* Fri Apr 06 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.6-1
- Update to 1.8.6 (#1560121)

* Mon Mar 26 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.5-1
- Update to 1.8.5 (#1560121)

* Mon Feb 26 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.4-2
- Define USE_SYSTEMD at build time (#1549027)

* Mon Feb 26 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.4-1
- Update to 1.8.4 (#1543668)

* Thu Feb 08 2018 Florian Weimer <fweimer@redhat.com> - 1.8.3-5
- Build halog and iprange with linker flags from redhat-rpm-config
- Tell build to include <crypt.h>

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 1.8.3-3
- Rebuilt for switch to libxcrypt

* Fri Jan 05 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.3-2
- Remove haproxy-systemd-wrapper

* Fri Jan 05 2018 Ryan O'Hara <rohara@redhat.com> - 1.8.3-1
- Update to 1.8.3 (#1528829)

* Wed Dec 27 2017 Ryan O'Hara <rohara@redhat.com> - 1.8.2-1
- Update to 1.8.2

* Fri Dec 15 2017 Ryan O'Hara <rohara@redhat.com> - 1.8.1-1
- Update to 1.8.1

* Fri Dec 15 2017 Ryan O'Hara <rohara@redhat.com> - 1.8.0-1
- Update to 1.8.0

* Mon Sep 11 2017 Ryan O'Hara <rohara@redhat.com> - 1.7.9-1
- Update to 1.7.9 (#1485084)

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.7.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.7.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 10 2017 Ryan O'Hara <rohara@redhat.com> - 1.7.8-1
- Update to 1.7.8 (#1436669)

* Mon May 01 2017 Ryan O'Hara <rohara@redhat.com> - 1.7.3-2
- Use KillMode=mixed in systemd service file (#1447085)

* Sun Mar 26 2017 Ryan O'Hara <rohara@redhat.com> - 1.7.3-1
- Update to 1.7.3 (#1413276)

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.7.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Jan 18 2017 Ryan O'Hara <rohara@redhat.com> - 1.7.2-1
- Update to 1.7.2 (#1413276)

* Thu Dec 29 2016 Ryan O'Hara <rohara@redhat.com> - 1.7.1-1
- Update to 1.7.1

* Mon Nov 28 2016 Ryan O'Hara <rohara@redhat.com> - 1.7.0-1
- Update to 1.7.0

* Mon Nov 21 2016 Ryan O'Hara <rohara@redhat.com> - 1.6.10-1
- Update to 1.6.10 (#1397013)

* Wed Aug 31 2016 Ryan O'Hara <rohara@redhat.com> - 1.6.9-1
- Update to 1.6.9 (#1370709)

* Thu Jul 14 2016 Ryan O'Hara <rohara@redhat.com> - 1.6.7-2
- Fix main frontend in default config file (#1348674)

* Thu Jul 14 2016 Ryan O'Hara <rohara@redhat.com> - 1.6.7-1
- Update to 1.6.7 (#1356578)

* Tue Jun 28 2016 Ryan O'Hara <rohara@redhat.com> - 1.6.6-2
- Remove patch for CVE-2016-5360

* Tue Jun 28 2016 Ryan O'Hara <rohara@redhat.com> - 1.6.6-1
- Update to 1.6.6 (#1350426)

* Wed Jun 15 2016 Ryan O'Hara <rohara@redhat.com> - 1.6.5-3
- Fix reqdeny causing random crashes (CVE-2016-5360, #1346672)

* Fri Jun 03 2016 Ryan O'Hara <rohara@redhat.com> - 1.6.5-2
- Utilize system-wide crypto-policies (#1256253)

* Mon May 23 2016 Ryan O'Hara <rohara@redhat.com> - 1.6.5-1
- Update to 1.6.5 (#1317313)

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.6.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 20 2016 Ryan O'Hara <rohara@redhat.com> - 1.6.3-1
- Update to 1.6.3 (#1276288)

* Wed Nov 18 2015 Ryan O'Hara <rohara@redhat.com> - 1.6.2-3
- Enable Lua support

* Tue Nov 03 2015 Ryan O'Hara <rohara@redhat.com> - 1.6.2-2
- Update to 1.6.2 (#1276288)

* Fri Oct 30 2015 Ryan O'Hara <rohara@redhat.com> - 1.6.1-1
- Update to 1.6.1 (#1276288)

* Mon Jul 06 2015 Ryan O'Hara <rohara@redhat.com> - 1.5.14-1
- Update to 1.5.14 (CVE-2015-3281, #1239181)

* Fri Jun 26 2015 Ryan O'Hara <rohara@redhat.com> - 1.5.13-1
- Update to 1.5.13 (#1236056)

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.12-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue May 05 2015 Ryan O'Hara <rohara@redhat.com> - 1.5.12-2
- Remove unused patches

* Tue May 05 2015 Ryan O'Hara <rohara@redhat.com> - 1.5.12-1
- Update to 1.5.12 (#1217922)

* Wed Mar 04 2015 Ryan O'Hara <rohara@redhat.com> - 1.5.11-4
- Rework systemd service and sysconfig file

* Wed Feb 11 2015 Ryan O'Hara <rohara@redhat.com> - 1.5.11-3
- Add sysconfig file

* Tue Feb 10 2015 Ryan O'Hara <rohara@redhat.com> - 1.5.11-2
- Add tcp-ut bind option to set TCP_USER_TIMEOUT (#1190783)

* Sun Feb 01 2015 Ryan O'Hara <rohara@redhat.com> - 1.5.11-1
- Update to 1.5.11 (#1188029)

* Mon Jan 05 2015 Ryan O'Hara <rohara@redhat.com> - 1.5.10-1
- Update to 1.5.10

* Mon Dec 01 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.9-1
- Update to 1.5.9

* Sat Nov 01 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.8-1
- Update to 1.5.8

* Thu Oct 30 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.7-1
- Update to 1.5.7

* Mon Oct 20 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.6-1
- Update to 1.5.6

* Wed Oct 08 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.5-1
- Update to 1.5.5

* Tue Sep 02 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.4-1
- Update to 1.5.4

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Aug 06 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.3-2
- Use haproxy-systemd-wrapper in service file (#1126955)

* Fri Jul 25 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.3-1
- Update to 1.5.3

* Tue Jul 15 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.2-1
- Update to 1.5.2

* Tue Jun 24 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.1-1
- Update to 1.5.1

* Thu Jun 19 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.0-2
- Build with zlib and openssl support

* Thu Jun 19 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.0-1
- Update to 1.5.0

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.25-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Mar 27 2014 Ryan O'Hara <rohara@redhat.com> - 1.4.25-1
- Update to 1.4.25

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.24-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jun 17 2013 Ryan O'Hara <rohara@redhat.com> - 1.4.24-1
- Update to 1.4.24 (CVE-2013-2174, #975160)

* Tue Apr 30 2013 Ryan O'Hara <rohara@redhat.com> - 1.4.23-3
- Build with PIE flags (#955182)

* Mon Apr 22 2013 Ryan O'Hara <rohara@redhat.com> - 1.4.23-2
- Build with PIE flags (#955182)

* Tue Apr 02 2013 Ryan O'Hara <rohara@redhat.com> - 1.4.23-1
- Update to 1.4.23 (CVE-2013-1912, #947697)
- Drop supplementary groups after setuid/setgid (#894626)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.22-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Oct 12 2012 Robin Lee <cheeselee@fedoraproject.org> - 1.4.22-1
- Update to 1.4.22 (CVE-2012-2942, #824544)
- Use linux2628 build target
- No separate x86_64 build target for halog
- halog build honors rpmbuild optflags
- Specfile cleanup

* Mon Sep 17 2012 Václav Pavlín <vpavlin@redhat.com> - 1.4.20-3
- Scriptlets replaced with new systemd macros (#850143)

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.20-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Apr 03 2012 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.4.20-1
- Update to 1.4.20

* Sun Feb 19 2012 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.4.19-4
- fix haproxy.services file

* Sun Feb 19 2012 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.4.19-3
- Update to use systemd fixing bug #770305

* Fri Feb 10 2012 Petr Pisar <ppisar@redhat.com> - 1.4.19-2
- Rebuild against PCRE 8.30

* Sun Jan 29 2012 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.4.19-1
- Update to 1.4.19

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.18-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Sep 22 2011 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.4.18-1
- Update to 1.4.18

* Tue Apr 26 2011 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.4.15-1
- Update to 1.4.15

* Sun Feb 27 2011 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.4.11-1
- update to 1.4.11

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Dec 12 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.4.9-1
- update to 1.4.9

* Sun Jun 20 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.4.8-1
- update to 1.4.8

* Sun May 30 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.4.6-1
- update to 1.4.6

* Thu Feb 18 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.23-1
- update to 1.3.23

* Sat Oct 17 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.22-1
- update to 1.3.22
- added logrotate configuration

* Mon Oct 12 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.21-1
- update to 1.3.21

* Sun Oct 11 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.20-1
- update to 1.3.20

* Sun Aug 02 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.19-1
- update to 1.3.19

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.18-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun May 17 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.18-1
- update to 1.3.18

* Sat Apr 11 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.17-1
-  Update to 1.3.17

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.15.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Dec 30 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.15.7-1
- update to 1.3.15.7
- remove upstream patches, they are now part of source distribution

* Sat Nov 22 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.15.6-2
- apply upstream patches 

* Sat Nov 15 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.15.6-1
- update to 1.3.15.6
- use new build targets from upstream
- add in recommended build options for x86 from upstream

* Sat Jun 28 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.14.6-1
- update to 1.3.14.6
- remove gcc 4.3 patch, it has been applied upstream
- remove MIT license as that code has been removed from upstream

* Mon Apr 14 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.14.4-1
- update to 1.3.14.4

* Sun Mar 16 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.14.3-1
- update to 1.3.14.3

* Sat Mar 01 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.14.2-4
- apply the gcc 4.3 patch to the build process

* Sat Mar 01 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.14.2-3
- fix gcc 4.3 bug [#434144]
- update init script to properly reload configuration

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.3.14.2-2
- Autorebuild for GCC 4.3

* Sun Jan 20 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.14.2-1
- update to 1.3.14.2
- update make flags that changed with this upstream release
- added man page installation

* Sun Dec 16 2007 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.3.14-1
- update to 1.3.14

* Mon Nov 05 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 1.3.12.4-1
- update to 1.3.12.4

* Thu Nov 01 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 1.3.12.3-1
- update to 1.3.12.3

* Fri Sep 21 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 1.3.12.2-3
- fix init script 'reload' task

* Thu Sep 20 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 1.3.12.2-2
- update License field

* Thu Sep 20 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 1.3.12.2-1
- update to 1.3.12.2
- remove the upstream patch

* Tue Sep 18 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 1.3.12.1-1
- switch to 1.3.12.1 branch
- add patch from upstream with O'Reilly licensing updates.
- convert ISO-8859-1 doc files to UTF-8

* Sat Mar 24 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 1.2.17-2
- addition of haproxy user
- add license information

* Fri Mar 23 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 1.2.17-1
- initial packaging
