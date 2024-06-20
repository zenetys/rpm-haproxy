| Package&nbsp;name | Supported&nbsp;targets | Includes |
| :--- | :--- | :--- |
| haproxy30z+quic | <nobr>el6, el7, el8, el9</nobr> | <nobr>lua 5.4 (static)</nobr><br/><nobr>quictls 1.1.1 (static)</nobr> |
<br/>


## Build:

The package can be built easily using the script rpmbuild-docker provided in this repository. In order to use this script, _**a functional Docker environment is needed**_, with ability to pull CentOS (el6, el7) or Rocky Linux (el8, el9) images from internet if not already downloaded.

```
## run from this git base tree
$ ./rpmbuild-docker -d el6
$ ./rpmbuild-docker -d el7
$ ./rpmbuild-docker -d el8
$ ./rpmbuild-docker -d el9
```

## Prebuilt packages:

Builds of these packages are available on ZENETYS yum repositories:<br/>
https://packages.zenetys.com/latest/redhat/

For alternatives, checkout HAProxy wiki:<br/>
https://github.com/haproxy/wiki/wiki/Packages
