| <nobr>Package name</nobr> | <nobr>Supported targets</nobr> |
| :--- | :--- |
| haproxy32z+quic | <nobr>el8, el9</nobr> |
<br/>

The haproxy RPM spec file in this repository was initially forked from
https://git.centos.org/rpms/haproxy/tree/c8. As per the CentOS Project
Licensing Policy https://www.centos.org/legal/licensing-policy/, GPLv2
license applies to this RPM spec repository.

This package depends on shared libraries provided by:

* [zenetys/rpm-aws-lc](https://github.com/zenetys/rpm-aws-lc)
<br/>

## Build:

The package can be built easily using the script rpmbuild-docker provided
in this repository. In order to use this script, _**a functional Docker
environment is needed**_, with ability to pull Rocky Linux (el8, el9)
images from internet if not already downloaded.

```
## run from this git base tree
$ ./rpmbuild-docker -d el8
$ ./rpmbuild-docker -d el9
```

## Prebuilt packages:

Builds of these packages are available on ZENETYS yum repositories:<br/>
https://packages.zenetys.com/latest/redhat/

For alternatives, checkout HAProxy wiki:<br/>
https://github.com/haproxy/wiki/wiki/Packages
