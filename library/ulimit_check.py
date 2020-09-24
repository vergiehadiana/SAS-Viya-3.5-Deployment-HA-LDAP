from ansible.module_utils.basic import AnsibleModule

import os
import sys
import grp
import pwd
import json

from subprocess import PIPE, STDOUT, Popen
from sys import stderr

class Utils:
    def exec_cmd(self, cmd, shell=True):
        return Popen(cmd, stdout=PIPE, shell=shell).communicate()

def ulimit_invocations():
    def execute():
        invocations = dict(
                open_files=dict(
                            description="The maximum number of open files allowed",
                            cmd="ulimit -n",
                            floor=48000
                        ),
                max_procs=dict(
                            description="The maximum number of processes allowed",
                            cmd="ulimit -u",
                            floor=65536
                        )
            )
        return invocations
    return execute

def main():
    utils = Utils()

    argument_spec = dict()

    module = AnsibleModule(argument_spec=argument_spec,
                           check_invalid_arguments=True,
                           supports_check_mode=True)

    uid = os.getuid()
    pw_entry = pwd.getpwuid(uid)
    user_name = pw_entry.pw_name

    stderr_template = 'Error executing {0} as user "{1}": {2}.'
    failure_template = '{0} ({1}) for user "{2}" currently is set to {3}. This value must be greater than or equal to {4}.'
    failures=[]

    ulimit_commands = ulimit_invocations()
    for description, invocation in ulimit_commands().items():
        cmd=invocation['cmd']
        value, stderr = utils.exec_cmd(cmd)

        if stderr:
            msg = stderr_template.format(invocation['cmd'], user_name, stderr)
            failures.append(msg)
        else:
            value = value.strip()
            if value.isdigit():
                value_int = int(value)
                if value_int < invocation['floor']:
                    msg = failure_template.format(invocation['description'], invocation['cmd'], user_name, value_int, invocation['floor'])
                    failures.append(msg)
            else:
              if value != "unlimited":
                    msg = "The ulimit {0} is not a supported value.".format(value)
                    failures.append(msg)

    msg_str='Passed'
    failed=False
    if len(failures) > 0:
        msg_str = ' '.join(failures)
        failed=True

    module.exit_json(failed=failed, msg=msg_str, user_name=user_name)

if __name__ == '__main__':
    main()

