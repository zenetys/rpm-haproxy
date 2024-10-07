build_dl https://packages.zenetys.com/latest/redhat/zenetys-latest.repo /etc/yum.repos.d/
dnf --disablerepo=\* --enablerepo=zenetys-latest makecache
