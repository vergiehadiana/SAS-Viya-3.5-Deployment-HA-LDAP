#!/usr/bin/env python
from ansible.module_utils.basic import AnsibleModule


def main():
    argument_spec = dict(
        hostvars=dict(required=True, type='dict'),
        inventory_hostname=dict(required=True, type='str')
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           check_invalid_arguments=False,
                           supports_check_mode=True)

    hostvars = module.params['hostvars']
    check_inv_hostname = module.params['inventory_hostname']
    host_keys = {}
    host_references = {}
    output=[]

    # Populate the expected host keys
    # Check for any same-machine inconsistencies
    for inventory_name in hostvars:
        if 'sas_vars' not in hostvars[inventory_name]:
            continue

        sas_vars = hostvars[inventory_name]['sas_vars']

        self_ipv4 = sas_vars['self_deployment_ipv4']
        comparisons = []
        for key in ['hostname_fqdn', 'internal_deployment_ipv4']:
            if key in sas_vars:
                comparisons.append(sas_vars[key].lower())

        t_h_k = sas_vars['target_host_keys']
        # Missing t_h_k entries imply that the host check portion
        # already failed, so no alignment check is needed.

        if self_ipv4 in t_h_k:
            for compare in comparisons:
                if compare not in t_h_k:
                    continue

                host_keys[compare] = t_h_k[compare]
                host_references[compare] = inventory_name
                if inventory_name == check_inv_hostname and t_h_k[self_ipv4] != t_h_k[compare]:
                    output.append("{0} resolves different hosts for {1} and {2}.".format(inventory_name, self_ipv4, compare))

    # Check for any cross-machine inconsistencies
    if 'sas_vars' in hostvars[check_inv_hostname]:
        t_h_k = hostvars[check_inv_hostname]['sas_vars']['target_host_keys']
        # Missing t_h_k entries imply that the host check portion
        # already failed, so no alignment check is needed.

        for host in host_keys:
            if host in t_h_k:
                if host_keys[host] != t_h_k[host]:
                    output.append("{0} and {1} resolve different hosts for {2}.".format(check_inv_hostname, host_references[host], host))

    failed = len(output) > 0

    if failed:
        message = "Failed: " + " ".join(output)
    else:
        message = "Passed"

    module.exit_json(failed=failed, msg=message)


if __name__ == '__main__':
    main()
