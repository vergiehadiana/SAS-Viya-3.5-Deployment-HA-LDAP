from ansible.module_utils.basic import AnsibleModule
import sys

class SelinuxCheck:
    def __init__(self, ansible_selinux):
        self.ansible_selinux = ansible_selinux

    def selinux_set_correctly(self):
        selinux_status = self.ansible_selinux['status']

        if selinux_status == 'disabled':
            return True
        if selinux_status == 'enabled':
            selinux_mode = self.ansible_selinux['mode']
            if selinux_mode == 'permissive':
                return True

        return False

    def get_attribute(self, attribute):
        return self.ansible_selinux[attribute]

def main():
    argument_spec = dict(
        ansible_selinux=dict(required=True, type='dict')
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           check_invalid_arguments=True,
                           supports_check_mode=True)

    ansible_selinux = module.params['ansible_selinux']

    check = SelinuxCheck(ansible_selinux)
    check_result = check.selinux_set_correctly()

    if check_result:
        message = "Passed"
        module.exit_json(failed=False, msg=message)
    else:
        message = "The pre-deployment validation has determined that SELinux is not set as expected. See the \"Configure SELinux\" topic in SAS Viya on Linux: Deployment Guide for information about deploying with SELinux."
        module.fail_json(msg=message)


if __name__ == '__main__':
    main()
