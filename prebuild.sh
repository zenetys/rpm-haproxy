#!/bin/bash -xe

case "$DIST" in
    el6)
        # perl-Data-Dumper to build openssl
        rpmforge_release_rpm=rpmforge-release-0.5.3-1.el6.rf.x86_64.rpm
        rpmforge_mirrors=(
            http://mirrors.ircam.fr/pub/dag
            http://mirror1.hs-esslingen.de/repoforge
            http://ftp.cc.uoc.gr/mirrors/repoforge
        )
        retval=1
        for i in "${rpmforge_mirrors[@]}"; do
            if build_dl "$i/redhat/el6/en/x86_64/rpmforge/RPMS/$rpmforge_release_rpm"; then
                retval=0
                break
            fi
        done
        (( retval == 0 )) || exit 1
        rpm -Uvh "$CACHEDIR/$rpmforge_release_rpm"
        ;;
esac
