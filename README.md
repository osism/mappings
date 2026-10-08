# mappings

The mappings list the parameters defined in:

* role defaults (`defaults/main.yml` or `defaults/main/*.yml`) in the
  ceph-ansible, kolla-ansible, osism-ansible and osism-kubernetes images,
  including the collections and galaxy roles they ship
* kolla-ansible's `group_vars/all` (as `kolla.group_vars`)
* osism/defaults, one entry per inventory group (as `osism.defaults.<group>`).
  Files that mirror or override kolla-ansible parameters (`001-*`, `010-*`,
  `002-images-kolla`, `003-kolla-overlays`, `099-kolla`) are left out.

## mapping1: role -> parameters (1:n)

In this mapping all parameters belonging to a role are listed.

```
stackhpc.cephadm.cephadm:
- cephadm_ceph_release
- cephadm_skip_prechecks
- cephadm_fsid
- cephadm_recreate
[...]
```

## mapping2: parameter -> roles (1:n)

In this mapping all roles are listed in which a parameter occurs.

```
zabbix_version:
- community.zabbix.zabbix_server
- community.zabbix.zabbix_proxy
- community.zabbix.zabbix_agent
- community.zabbix.zabbix_web
- community.zabbix.zabbix_javagateway
```
