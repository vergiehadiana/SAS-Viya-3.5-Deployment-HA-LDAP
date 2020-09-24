import json
import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.sas_lib import sas_lib
from ansible.module_utils.disk_space_check import build_type_factory

from sys import stdin


#==
def get_available_disk_space_on_system(path):
    statvfs = os.statvfs(path)
    available_bytes = statvfs.f_frsize * statvfs.f_bavail  # available non-privileged bytes
    available_bytes_k = available_bytes / 1024
    return available_bytes_k

#==
def get_group_names(group_names_list):
    ignored_groups = ["sas_all", "ungrouped"]
    for group in ignored_groups:
        if group in group_names_list:
            group_names_list.remove(group)
    group_names = ', '.join(group_names_list)
    return group_names

#==
def perform_validation_checks(module, failure_condition, failure_msg, success_msg):
    if failure_condition is True:
        module.fail_json(msg=failure_msg)
    else:
        module.exit_json(msg=success_msg, failed=False)

#==
def get_first_existing_ancestor(path):
    working_path = path
    while (os.path.exists(working_path) == False):
        working_path = os.path.dirname(working_path.rstrip(os.sep))
    return working_path

#==
def main():
    fields = {
        "sas_vars": {"required": True, "type": "dict"},
        "path": {"required": True, "type": "str"},
        "hostname": {"required": True, "type": "str"},
        "group_names": {"required": True, "type": "list"}
    }
    module = AnsibleModule(argument_spec=fields)
    sas_vars = module.params['sas_vars']
    requested_path = module.params['path']
    host = module.params['hostname']
    group_names_list = module.params['group_names']

    saslib = sas_lib(module)
    build_type = saslib.extract_build_type(sas_vars)

    factory = build_type_factory.factory(module)
    helper = factory.create(build_type)

    saslib.check_executables(helper)

    group_names = get_group_names(group_names_list)
    total_disk_space_needed = helper.get_disk_space_needed_for_all_packages(sas_vars['install_packages'])
    if total_disk_space_needed == None:
        message = "Could not estimate disk space required for packages"
        module.exit_json(failed=True, msg=message)

    total_static_space_needed = sas_vars['total_static_disk_space']
    total_disk_space_needed += total_static_space_needed
    path = get_first_existing_ancestor(requested_path)
    available_disk_space_on_system = get_available_disk_space_on_system(path)

    insufficient_disk_space_error_msg = "There is not enough disk space on host, %s, to deploy all of the software packages for group(s): %s. %s has %s K available and %s K is needed to install." % (host, group_names, path, available_disk_space_on_system, total_disk_space_needed)
    success_msg = "%s has %s K disk space available and %s K is needed to install." % (path, available_disk_space_on_system, total_disk_space_needed)
    failure_condition = available_disk_space_on_system < total_disk_space_needed
    perform_validation_checks(module, failure_condition=failure_condition, failure_msg=insufficient_disk_space_error_msg, success_msg=success_msg)

if __name__ == '__main__':
    main()
