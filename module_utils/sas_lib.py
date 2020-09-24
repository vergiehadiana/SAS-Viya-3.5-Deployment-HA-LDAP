import subprocess

#==
class sas_lib:
    #==
    def __init__(self, module):
        self.module = module

    #==
    def extract_build_type(self, sas_vars):
        return sas_vars['repository_build_type']

    #==
    def check_executable(self, ename):
        s = "command -v " + ename
        p = subprocess.Popen(s,  shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retVal = p.wait()
        if (retVal != 0):
            message = "Required utility {0} is not available".format(ename)
            self.module.exit_json(failed=True, msg=message)
        return True

    #==
    def check_executables(self, helper):
        executables = helper.get_executables()
        for executable in executables:
            self.check_executable(executable)

