# mappings

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

## mapping3: role -> environment (1:1)
