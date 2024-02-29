# Initially forked from https://git.centos.org/rpms/haproxy/tree/c8
# by Benoit Dolez <bdolez at zenetys.com>

%define major           2.8
%define minor           7

%define haproxy_user    haproxy
%define haproxy_group   %{haproxy_user}
%define haproxy_homedir %{_localstatedir}/lib/haproxy
%define haproxy_confdir %{_sysconfdir}/haproxy
%define haproxy_datadir %{_datadir}/haproxy
%define builddir        %{_builddir}/haproxy-%{version}

%define liblua          lua-5.3.6

%global _hardened_build 1
%global debug_package   %{nil}

Name:           haproxy28z
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

Source100:      http://www.lua.org/ftp/%{liblua}.tar.gz
Patch100:       lua-5.3-luaroot.patch

BuildRequires:      pcre-devel
BuildRequires:      zlib-devel
BuildRequires:      openssl-devel

Requires(pre):      shadow-utils

%if 0%{?rhel} < 7
%define __global_ldflags %{nil}
%endif

%if 0%{?rhel} < 8
%define build_ldflags    %{nil}
%endif

%if 0%{?rhel} >= 7
BuildRequires:      systemd-devel
BuildRequires:      systemd-units
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd
%endif

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
# haproxy
%setup -q -n haproxy-%{version}

# lua
%setup -T -D -a 100 -n haproxy-%{version}
cd %{liblua}
%patch100 -p1 -b .lua-path
cd ..


%build
# lua
cd %{liblua}/src
make liblua.a %{?_smp_mflags} SYSCFLAGS="-DLUA_USE_LINUX -fPIC" SYSLIBS="-Wl,-E"
lua_inc="$PWD"
lua_lib="$PWD"
cd ../..
[[ -e $lua_inc/lua.h ]] || exit 1
[[ -e $lua_lib/liblua.a ]] || exit 1

# haproxy
cpu_opts=
%if 0%{?rhel} <= 6
cpu_opts="CPU_CFLAGS=-O2 -fno-strict-aliasing"
%endif

%if 0%{?rhel} >= 7
systemd_opts="USE_SYSTEMD=1"
setns_opts="USE_NS=1"
%else
systemd_opts="USE_SYSTEMD="
setns_opts="USE_NS="
%endif

%{__make} \
    %{?_smp_mflags} \
    CPU="generic" TARGET="linux-glibc" \
    USE_OPENSSL=1 USE_PCRE=1 USE_ZLIB=1 USE_LUA=1 \
    USE_PROMEX=1 \
    USE_CRYPT_H=1 \
    USE_LINUX_TPROXY=1 \
    USE_GETADDRINFO=1 \
    ${systemd_opts:+"$systemd_opts"} \
    ${setns_opts:+"$setns_opts"} \
    ${cpu_opts:+"$cpu_opts"} \
    LUA_INC="$lua_inc" \
    LUA_LIB="$lua_lib" \
    LUA_LIB_NAME=lua \
    ADDINC="%{optflags}" \
    ADDLIB="%{__global_ldflags}"

%{__make} admin/halog/halog OPTIMIZE="%{optflags} %{build_ldflags}" LDFLAGS=
%{__make} admin/iprange/iprange OPTIMIZE="%{optflags} %{build_ldflags}" LDFLAGS=
%{__make} -C admin/systemd PREFIX=/usr

%install
%{__make} install-bin DESTDIR=%{buildroot} PREFIX=%{_prefix} TARGET="linux2628"
%{__make} install-man DESTDIR=%{buildroot} PREFIX=%{_prefix}

%if 0%{?rhel} < 7
%{__install} -p -D -m 0755 ./examples/haproxy.init %{buildroot}%{_initddir}/haproxy
%else
%{__install} -p -D -m 0644 admin/systemd/haproxy.service %{buildroot}%{_unitdir}/haproxy.service
%endif

%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{haproxy_confdir}/haproxy.cfg
%{__install} -p -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/haproxy
%{__install} -p -D -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/haproxy
%{__install} -p -D -m 0644 %{SOURCE5} %{buildroot}%{_mandir}/man1/halog.1
%{__install} -d -m 0755 %{buildroot}%{haproxy_homedir}
%{__install} -d -m 0755 %{buildroot}%{haproxy_datadir}
%{__install} -d -m 0755 %{buildroot}%{_bindir}
%{__install} -p -m 0755 ./admin/halog/halog %{buildroot}%{_bindir}/halog
%{__install} -p -m 0755 ./admin/iprange/iprange %{buildroot}%{_bindir}/iprange
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
%if 0%{?rhel} < 7
chkconfig --add haproxy
%else
%systemd_post haproxy.service
%endif

%preun
%if 0%{?rhel} < 7
if [ $1 -eq 0 ]; then
    service haproxy status >/dev/null && service haproxy stop
    chkconfig --del haproxy
fi
%else
%systemd_preun haproxy.service
%endif

%postun
%if 0%{?rhel} < 7
%else
%systemd_postun_with_restart haproxy.service
%endif

%files
%defattr(-,root,root,-)
%doc doc/* examples/*
%doc CHANGELOG README VERSION
%if 0%{?rhel} < 7
%doc LICENSE
%endif
%if 0%{?rhel} >= 7
%license LICENSE
%endif
%dir %{haproxy_homedir}
%dir %{haproxy_confdir}
%dir %{haproxy_datadir}
%{haproxy_datadir}/*
%config(noreplace) %{haproxy_confdir}/haproxy.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/haproxy
%config(noreplace) %{_sysconfdir}/sysconfig/haproxy
%if 0%{?rhel} < 7
%{_initddir}/haproxy
%else
%{_unitdir}/haproxy.service
%endif
%{_sbindir}/haproxy
%{_bindir}/halog
%{_bindir}/iprange
%{_mandir}/man1/*
