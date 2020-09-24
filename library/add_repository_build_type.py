import subprocess
from ansible.module_utils.basic import AnsibleModule

def add_repository_build_type(facts, key, host_variables, failure_msgs):
    """
    Determines the repository build type to use

    Arguments:
    facts -- the dictionary to receive the boolean
    key -- the key in the dictionary to place the repository build type
    host_variables -- the variables specific to this host
    failure_msgs -- in the event a failure occurs retrieving the hostname from the host, the
                    message to share with the user is added to this list
    """

    facts[key] = 'unknown'

    support_map = host_variables['support_map']
    architecture = host_variables['ansible_architecture']
    if architecture in support_map:
        supported_os = support_map[architecture]
        host_family = host_variables['ansible_os_family']
        if host_family in supported_os:
            supported_releases = supported_os[host_family]
            os_major_version = host_variables['ansible_distribution_major_version']
            if os_major_version in supported_releases:
                release_map = supported_releases[os_major_version]
                requested_repo_format = release_map['default_repository_format']
                if 'repository_format' in host_variables:
                    requested_repo_format = host_variables['repository_format']

                repository_build_types = release_map['repository_build_types']
                if requested_repo_format in repository_build_types:
                    facts[key] = repository_build_types[requested_repo_format]
                else:
                    failure_msgs.append("Unsupported %s %s %s repository format: %s" % (architecture, host_family, os_major_version, requested_repo_format))
            else:
                failure_msgs.append("Unsupported %s %s version: %s" % (architecture, host_family, os_major_version))
        else:
            failure_msgs.append("Unsupported %s operating system family: %s" % (architecture, host_family))
    else:
        failure_msgs.append("Unsupported architecture : %s" % architecture)

def init_module():
    """
    Initializes Ansible module handing
    """

    module = AnsibleModule(
        argument_spec = dict(
            host_variables=dict(required=True, type="dict")
        ),
        supports_check_mode=True
    )

    return module

def finish_module(module, failure_condition, failure_msg, success_msg, changed=False, ansible_facts=''):
    """
    Finishes this module by communicating back to Ansible the success or failure

    Arguments:
    module -- the module to return the results too
    failure_condition -- True if the this module succesfull completed the task,
                         otherwise False
    failure_msg -- The user message if failure_condition is False
    success_msg -- The user message if the failure_condition is True
    changed -- True if this module changes the target host, otherwise False
    ansible_facts - Include any results which should be saved in Ansible's hostvars
    """

    if failure_condition is True:
        module.fail_json(msg=failure_msg)
    else:
        module.exit_json(changed=changed, msg=success_msg, ansible_facts=ansible_facts)

def main():
    """
    Entry function for Ansible
    """

    module = init_module()
    failure_condition = False
    failure_msgs = []
    facts = {}

    host_variables = module.params['host_variables']

    add_repository_build_type(facts, "repository_build_type", host_variables, failure_msgs)

    all_failure_msgs = "Failure(s) occurred adding repository build type:"
    for failure_msg in failure_msgs:
        all_failure_msgs = "%s \n %s" %(all_failure_msgs, failure_msg)
        failure_condition = True

    ansible_facts = { "sas_vars":  facts }
    success_msg = "Successfully added repository build type."
    changed = False
    finish_module(module, failure_condition, all_failure_msgs, success_msg, changed, ansible_facts)

if __name__ == '__main__':
    main()
