from ansible.module_utils.basic import AnsibleModule

import re

from subprocess import PIPE, Popen


def exec_cmd(cmd):
    response, stderr = Popen(cmd, stdout=PIPE, shell=True).communicate()
    if stderr:
        stderr_template = 'Error executing {0}: {1}.'
        msg = stderr_template.format(cmd, stderr)
        module.exit_json(failed=True, msg=msg)
    stripped = response.strip()
    return stripped


def ensure_systemd_okay(module, major_min, minor_min):
    systemd_package = exec_cmd('rpm -q systemd')
    match = re.search('^[^-]*-(\d+)-(\d+)', systemd_package)
    if not match:
        template = 'Cannot determine the systemd version from {0}.'
        msg = template.format(systemd_package)
        module.exit_json(failed=True, msg=msg)

    major_str = match.group(1)
    major = int(major_str)
    minor_str = match.group(2)
    minor = int(minor_str)

    is_fine = False
    if major > major_min:
        is_fine = True
    elif major == major_min:
        if minor >= minor_min:
            is_fine = True

    if is_fine:
        template = 'systemd version {0}-{1} is at least {2}-{3}.'
        msg = template.format(major, minor, major_min, minor_min)
        module.exit_json(failed=False, msg=msg)

    template = (
        'systemd version {0}-{1} '
        'does not meet the requirement '
        'for at least {2}-{3}.'
    )
    msg = template.format(major, minor, major_min, minor_min)
    module.exit_json(failed=True, msg=msg)


def main():
    fields = {
        "systemd_major_min": {"required": True, "type": "int"},
        "systemd_minor_min": {"required": True, "type": "int"}
    }
    module = AnsibleModule(argument_spec=fields,
                           check_invalid_arguments=True,
                           supports_check_mode=True)

    init_command = exec_cmd('ps -p 1 -o comm=')

    if init_command == 'systemd':
        systemd_major_min = module.params['systemd_major_min']
        systemd_minor_min = module.params['systemd_minor_min']
        ensure_systemd_okay(module, systemd_major_min, systemd_minor_min)

    msg = 'Init system satisfies the requirements.'
    module.exit_json(failed=False, msg=msg, init_system=init_command)

if __name__ == '__main__':
    main()
