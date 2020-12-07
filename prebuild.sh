#!/bin/bash -xe

case "$DIST" in
    el6)
        # el6 EOL, use archive repositories
        sed -i -re 's,mirror\.centos\.org,vault.centos.org,; s,^(mirrorlist),#\1,; s,^#(baseurl),\1,' \
            /etc/yum.repos.d/CentOS-Base.repo
        ;;
esac
