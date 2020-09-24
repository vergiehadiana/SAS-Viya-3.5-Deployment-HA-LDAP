import json
import subprocess
from ansible.module_utils.basic import AnsibleModule
from sys import stdin

def get_inactive_services(hostvars, services, pattern):
    inactive_services = []
    for service in services:
        name = hostvars[service]['SERVICE_PRODUCT_NAME']
        if name == 'sas-cas':
           service_name = pattern.replace("SERVICE_PRODUCT_NAME", 'cascontroller')
           p = subprocess.Popen(["ps", "-ef"], stdout=subprocess.PIPE)
           out, err = p.communicate()
           service_name2 = pattern.replace("SERVICE_PRODUCT_NAME", 'casworker')
           p2 = subprocess.Popen(["ps", "-ef"], stdout=subprocess.PIPE)
           out2, err2 = p2.communicate()
           if ((service_name not in out) and (service_name2 not in out2)):
               inactive_services.append(service)
        else:
           service_name = pattern.replace("SERVICE_PRODUCT_NAME", name)
           p = subprocess.Popen(["ps", "-ef"], stdout=subprocess.PIPE)
           out, err = p.communicate()
           if (service_name not in out):
               inactive_services.append(service)
    return inactive_services

def get_group_names(group_names_list):
    ignored_groups = ["sas_all", "ungrouped"]
    for group in ignored_groups:
        if group in group_names_list:
            group_names_list.remove(group)
    group_names = ', '.join(group_names_list)
    return group_names

def get_memory_needed_for_inactive_services(hostvars, inactive_services):
    total_memory_needed_mb = 0
    for service in inactive_services:
        memory_needed = hostvars[service]['SERVICE_MEMORY_NEEDED']
        total_memory_needed_mb += memory_needed
    return total_memory_needed_mb

def get_services(hostvars):
    services = []
    for key in hostvars.keys():
        dictionary = hostvars[key]
        if type(dictionary) is dict:
            if 'SERVICE_PRODUCT_NAME' in dictionary:
                services.append(key)
    services.sort()
    return services

def perform_validation_checks(module, failure_condition, failure_msg, success_msg):
    if failure_condition is True:
        module.fail_json(msg=failure_msg)
    else:
        module.exit_json(msg=success_msg, failed=False)

def main():
    fields = {
        "hostvars_dictionary": {"required": True, "type": "dict"},
        "pattern": {"required": True, "type": "str"},
        "available_memory": {"required": True, "type": "int"},
        "hostname": {"required": True, "type": "str"},
        "group_names": {"required": True, "type": "list"}
    }
    module = AnsibleModule(argument_spec=fields)
    hostvars_dictionary = module.params['hostvars_dictionary']
    pattern = module.params['pattern']
    available_memory = module.params['available_memory']
    host = module.params['hostname']
    group_names_list = module.params['group_names']
    group_names = get_group_names(group_names_list)
    json_dump = json.dumps(hostvars_dictionary)
    hostvars = json.loads(json_dump)
    services = get_services(hostvars)
    inactive_services = get_inactive_services(hostvars, services, pattern)
    total_memory_needed = get_memory_needed_for_inactive_services(hostvars, inactive_services)

    insufficient_memory_error_msg = "There is not enough available memory on host, %s, to deploy all of the software packages for group(s): %s. %s Mb of memory is needed and only %s Mb is available." % (host, group_names, total_memory_needed, available_memory)
    success_msg="The host group needs %s Mb of memory and %s Mb is available." % (total_memory_needed, available_memory)
    failure_condition = available_memory < total_memory_needed
    perform_validation_checks(module, failure_condition=failure_condition, failure_msg=insufficient_memory_error_msg, success_msg=success_msg)

if __name__ == '__main__':
    main()