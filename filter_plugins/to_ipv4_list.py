#!/usr/bin/python

from ansible import errors
import json
try:
    from ansible.vars.hostvars import HostVars
except Exception:
    pass

def check_key(key, dictionary, dictionaryName, host):
    if key in dictionary:
        return True

    err_msg = "Key %s does not exist in %s for host %s" % (key, dictionaryName, host)
    raise errors.AnsibleFilterError(err_msg)
    return False

def to_ipv4_list(host_vars, groups, target = 'sas_all'):
    if type(host_vars) != HostVars:
        raise errors.AnsibleFilterError("failed expects a HostVars")

    if type(groups) != dict:
        raise errors.AnsibleFilterError("failed expects a Dictionary")

    data_ipaddrs = []
    for host in groups[target]:
        key = "sas_vars"
        if check_key(key, host_vars[host], "hostvars", host):
            sas_vars = host_vars[host][key]
            key = "internal_deployment_ipv4"
            if check_key(key, sas_vars, "hostvars.sas_vars", host):
                data_ipaddrs.append(sas_vars["internal_deployment_ipv4"])

    return data_ipaddrs

class FilterModule (object):
    def filters(self):
        return {"to_ipv4_list": to_ipv4_list}
