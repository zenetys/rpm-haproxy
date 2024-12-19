Supported targets: el6, el7, el8

The haproxy RPM spec file in this repository was initially forked from
https://git.centos.org/rpms/haproxy/tree/c8. As per the CentOS Project
Licensing Policy https://www.centos.org/legal/licensing-policy/, GPLv2
license applies to this RPM spec repository.

Notes:

  - This RPM spec file creates a single package: haproxy24z
  - The package can be built easily using the script `rpmbuild-docker` provided in this repository. In order to use this script, _**a functional Docker environment is needed**_, with ability to pull CentOS (el6, el7) or Rocky Linux (el8) images from internet if not already downloaded.

How to build?

```
## run from this git base tree
$ ./rpmbuild-docker -d el6
$ ./rpmbuild-docker -d el7
$ ./rpmbuild-docker -d el8
```

Prebuilt packages:

  - Builds of these packages are available on ZENETYS yum repositories:<br/>
https://packages.zenetys.com/latest/redhat/
  - For alternatives, checkout HAProxy wiki:<br/>
https://github.com/haproxy/wiki/wiki/Packages
