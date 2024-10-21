# Initially forked from https://git.centos.org/rpms/haproxy/tree/c8
# by Benoit Dolez <bdolez at zenetys.com>

%define major           3.0
%define minor           5

%define haproxy_user    haproxy
%define haproxy_group   %{haproxy_user}
%define haproxy_homedir %{_localstatedir}/lib/haproxy
%define haproxy_confdir %{_sysconfdir}/haproxy
%define haproxy_datadir %{_datadir}/haproxy
%define builddir        %{_builddir}/haproxy-%{version}

%{!?make_verbose: %define make_verbose 0}

%global source_date_epoch_from_changelog 0
%global _hardened_build 1

Name:           haproxy30z+quic
Version:        %{major}.%{minor}
Release:        1%{?dist}.zenetys
Summary:        HAProxy reverse proxy for high availability environments

Group:          System Environment/Daemons
License:        GPLv2+
URL:            http://www.haproxy.org/

Source0:        http://www.haproxy.org/download/%{major}/src/haproxy-%{version}.tar.gz
Source2:        haproxy.cfg
Source3:        haproxy.logrotate
Source4:        haproxy.sysconfig
Source5:        halog.1

BuildRequires:      aws-lc-0z-devel
BuildRequires:      gcc
BuildRequires:      lua-devel
BuildRequires:      make
BuildRequires:      pcre2-devel
BuildRequires:      systemd-devel
BuildRequires:      systemd-rpm-macros

Requires:           aws-lc-0z
Requires(pre):      shadow-utils

%{?systemd_requires}

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
%setup -q -n haproxy-%{version}

%build
%{__make} \
    %{?_smp_mflags} \
    V=%{make_verbose} \
    CPU=generic \
    TARGET=linux-glibc \
    USE_OPENSSL_AWSLC=1 \
    USE_QUIC=1 \
    USE_PCRE2=1 \
    USE_SLZ=1 \
    USE_LUA=1 \
    USE_PROMEX=1 \
    USE_CRYPT_H=1 \
    USE_LINUX_TPROXY=1 \
    USE_GETADDRINFO=1 \
    USE_SYSTEMD=1 \
    USE_NS=1 \
    SSL_LIB='%{aws_lc_0z_prefix}/%{_lib} -Wl,-rpath,%{aws_lc_0z_prefix}/%{_lib}' \
    SSL_INC='%{aws_lc_0z_prefix}/include' \
    CFLAGS="%{build_cflags}" \
    LDFLAGS="%{build_ldflags}"

%{__make} admin/halog/halog V=%{make_verbose} CFLAGS="%{build_cflags}" LDFLAGS="%{build_ldflags}"
%{__make} -C admin/iprange V=%{make_verbose} OPTIMIZE="%{build_cflags}" LDFLAGS="%{build_ldflags}"
%{__make} -C admin/systemd PREFIX=%{_prefix}

%install
%{__make} install-bin DESTDIR=%{buildroot} PREFIX=%{_prefix} TARGET="linux2628"
%{__make} install-man DESTDIR=%{buildroot} PREFIX=%{_prefix}

%{__install} -p -D -m 0644 admin/systemd/haproxy.service %{buildroot}%{_unitdir}/haproxy.service
%{__install} -p -D -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/haproxy

%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{haproxy_confdir}/haproxy.cfg
%{__install} -p -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/haproxy
%{__install} -p -D -m 0644 %{SOURCE5} %{buildroot}%{_mandir}/man1/halog.1
%{__install} -d -m 0755 %{buildroot}%{haproxy_homedir}
%{__install} -d -m 0755 %{buildroot}%{haproxy_datadir}
%{__install} -d -m 0755 %{buildroot}%{_bindir}
%{__install} -p -m 0755 ./admin/halog/halog %{buildroot}%{_bindir}/halog
%{__install} -p -m 0755 ./admin/iprange/iprange %{buildroot}%{_bindir}/iprange
%{__install} -p -m 0755 ./admin/iprange/ip6range %{buildroot}%{_bindir}/ip6range
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
%systemd_post haproxy.service

%preun
%systemd_preun haproxy.service

%postun
%systemd_postun_with_restart haproxy.service

%files
%defattr(-,root,root,-)
%doc doc/* examples/*
%doc CHANGELOG README VERSION
%license LICENSE
%dir %{haproxy_homedir}
%dir %{haproxy_confdir}
%dir %{haproxy_datadir}
%{haproxy_datadir}/*
%config(noreplace) %{haproxy_confdir}/haproxy.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/haproxy
%{_unitdir}/haproxy.service
%config(noreplace) %{_sysconfdir}/sysconfig/haproxy
%{_sbindir}/haproxy
%{_bindir}/halog
%{_bindir}/iprange
%{_bindir}/ip6range
%{_mandir}/man1/*
