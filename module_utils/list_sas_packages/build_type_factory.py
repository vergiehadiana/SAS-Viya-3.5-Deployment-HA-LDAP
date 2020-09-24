#==
class factory:
    #==
    def __init__(self, module):
        self.module = module

    #==
    def create(self, build_type):
        if ('x64_redhat_linux_6-yum' == build_type):
            from ansible.module_utils.list_sas_packages import x64_redhat_linux_6_yum
            return x64_redhat_linux_6_yum.x64_redhat_linux_6_yum(self.module)

        self.module.exit_json(failed=True, msg='list_sas_packages factory: - unknown build type')
