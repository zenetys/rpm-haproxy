| Package&nbsp;name | Supported&nbsp;targets | Includes |
| :--- | :--- | :--- |
| haproxy30z | <nobr>el8, el9</nobr> | <nobr>lua 5.4 (static)</nobr> |
<br/>


## Build:

The package can be built easily using the script rpmbuild-docker provided in this repository. In order to use this script, _**a functional Docker environment is needed**_, with ability to pull Rocky Linux (el8, el9) images from internet if not already downloaded.

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
