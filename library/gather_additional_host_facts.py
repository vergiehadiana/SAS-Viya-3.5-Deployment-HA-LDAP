import subprocess
from ansible.module_utils.basic import AnsibleModule

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

def add_hostname_fqdn(host_facts, sas_facts, key, failure_msgs):
    """
    Adds the user-defined value for network_conf.SAS_HOSTNAME, if defined, to the sas_facts dictionary.
    Otherwise, determines the fully qualified hostname using hostname -f and adds this to the sas_facts dictionary.

    Arguments:
    host_facts -- the dictionary containing all of the host's facts
    sas_facts -- the SAS dictionary to add the hostname value too
    key -- the key in the dictionary to place the hostname value
    failure_msgs -- in the event a failure occurs retrieving the hostname from the host, the
                    message to share with the user is added to this list

    Returns: True if the hostname was obtained successfully and added to the dictionary,
             otherwise False
    """

    if "network_conf" in host_facts and "SAS_HOSTNAME" in host_facts["network_conf"]:
       hostname = host_facts["network_conf"]["SAS_HOSTNAME"]
    else:
       proc = subprocess.Popen(["hostname", "-f"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
       stdout, stderr = proc.communicate()
       hostname = stdout.decode().replace('\n', '').replace('\r', '')
       if proc.returncode != 0:
          stderr_msg = stderr.replace('\n', '').replace('\r', '').encode()
          failure_msgs.append("Error determining fully qualified domain name using hostname -f, stderr: %s" % stderr_msg)
          return

    sas_facts[key] = hostname

def get_sas_host_group_variable_entries(host_variables):
    magic_prefix = "sas_host_group_variables_"
    sas_all_key = magic_prefix + "sas_all"

    # The sas_all entry is relevant only when there is some
    # other entry present for the host.  This approach
    # mimics having a host included/excluded through the
    # inventory.

    entries = []
    for host_key in host_variables.keys():
        if host_key.startswith(magic_prefix):
            if host_key == sas_all_key:
                continue
            entries.append(host_variables[host_key])

    if entries:
        if sas_all_key in host_variables:
            entries.append(host_variables[sas_all_key])

    return entries

def get_sas_host_group_services(host_variables, sas_host_group_variable_entry):
    services = []
    services_key = "installables-" + host_variables['sas_vars']['repository_build_type']

    if services_key in sas_host_group_variable_entry:
        service_definitions = sas_host_group_variable_entry[services_key]
        if type(service_definitions) is not dict:
            return services

        for service_key in service_definitions:
            service_definition = service_definitions[service_key]
            if type(service_definition) is not dict:
                continue
            if 'SERVICE_PRODUCT_NAME' not in service_definition:
                continue
            services.append(service_definition)

    return services

def get_services(host_variables):
    """
    Determines the services for this host

    Arguments:
    host_variables -- the hostvars entry for this host

    Returns: A list of the service definitions applicable for this host
    """
    service_set = { }
    sas_host_group_variable_entries = get_sas_host_group_variable_entries(host_variables)
    for sas_host_group_variable_entry in sas_host_group_variable_entries:
        host_group_services = get_sas_host_group_services(host_variables, sas_host_group_variable_entry)
        for host_group_service in host_group_services:
            service_name = host_group_service['SERVICE_PRODUCT_NAME']
            service_set[service_name] = host_group_service

    return service_set.values()

def add_active_in_deployment(facts, key, services):
    """
    Determines if the host is active in the deployment

    Arguments:
    facts -- the dictionary to receive the boolean
    key -- the key in the dictionary to place the boolean
    services -- the services applicable for this host (from get_services)
    """

    facts[key] = bool(services)

def add_install_list(facts, key, install_key, services):
    """
    Determines the list of items to install and adds it to the facts dictionary

    Arguments:
    facts -- the dictionary to receive the install list
    key -- the key in the dictionary to place the install list
    install_key -- the service definition key identifying the item to add
                   to the install list (either "SERVICE_YUM_PACKAGE" or
                   "SERVICE_YUM_GROUP")
    services -- the services applicable for this host (from get_services)
    """
    install_list = []
    for service in services:
        if install_key in service:
            install_list.append(service[install_key])

    install_list.sort()

    facts[key] = install_list

def add_total_static_disk_space(facts, key, services):
    """
    Determines the total amount of static disk space needed and adds it to the facts dictionary

    Arguments:
    facts -- the dictionary to receive the total amount of static disk space
    key -- the key in the dictionary to place the total amount of static disk space
    services -- the services applicable for this host (from get_services)
    """
    total_static_disk_space = 0
    app_names = []
    for service in services:
        if 'SERVICE_STATIC_DISKSPACE' in service:
            service_app_name = service['SERVICE_APP_NAME']
            if service_app_name not in app_names:
                app_names.append(service_app_name)
                service_static_space = float(service['SERVICE_STATIC_DISKSPACE'])
                total_static_disk_space += service_static_space

    facts[key] = float(total_static_disk_space)

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

def main():
    """
    Entry function for Ansible
    """

    module = init_module()
    failure_condition = False
    failure_msgs = []
    facts = {}

    host_variables = module.params['host_variables']

    if host_variables['sas_vars']:
      facts = host_variables['sas_vars']

    # Add hostname_fqdn fact
    add_hostname_fqdn(host_variables, facts, "hostname_fqdn", failure_msgs)

    services = get_services(host_variables)
    add_active_in_deployment(facts, "active_in_deployment", services)
    add_install_list(facts, "install_packages", "SERVICE_YUM_PACKAGE", services)
    add_install_list(facts, "install_groups", "SERVICE_YUM_GROUP", services)
    add_total_static_disk_space(facts, "total_static_disk_space", services)

    # place additional fact add calls here

    all_failure_msgs = "Failure(s) occurred gathering additional host facts:"
    for failure_msg in failure_msgs:
        all_failure_msgs = "%s \n %s" %(all_failure_msgs, failure_msg)
        failure_condition = True

    ansible_facts = { "sas_vars":  facts }
    success_msg = "Successfully gathered additional host facts."
    changed = False
    finish_module(module, failure_condition, all_failure_msgs, success_msg, changed, ansible_facts)

if __name__ == '__main__':
    main()
