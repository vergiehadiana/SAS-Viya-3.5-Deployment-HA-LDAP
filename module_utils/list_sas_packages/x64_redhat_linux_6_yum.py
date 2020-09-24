from ansible.module_utils.list_sas_packages import base

#==
class x64_redhat_linux_6_yum( base.base ):
    #==
    def get_executables(self):
        return ["tr", "sed", "rpm", "yum"]

    #==
    def get_packages_cmd(self):
        return "yum -q list installed $(rpm -qg SAS --qf '%{NAME} ') | tr '\\n' '#' | sed -e 's/# / /g' | tr '#' '\\n'| sed -e 's/\([^ .]*\)\.[^ ]*  *\([^ ]*\) .*/\\1 \\2/g' -e '1d' "

    #==
    def get_updatables_cmd(self):
        return "yum -q check-update $(rpm -qg SAS --qf '%{NAME} ') | tr '\\n' '#' | sed -e 's/# / /g' | tr '#' '\\n'| sed -e 's/\([^ .]*\)\.[^ ]*  *\([^ ]*\) .*/\\1 \\2/g' -e '1d' "
