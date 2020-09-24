#!/usr/bin/env python
from ansible.module_utils.basic import AnsibleModule
import subprocess

class HostKeyRetriever:

    def get_host_key(self, host):

        ssh = subprocess.Popen(["ssh-keyscan", "-t", "rsa", host],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdout, stderr = ssh.communicate()
        results = stdout.splitlines()
        for line in results:
            content = line.decode().rstrip().split()
            if len(content) < 2:
                continue

            checked_host = content[0].lower()
            key_type     = content[1]
            host_key     = content[2]
            if key_type == "ssh-rsa" and checked_host == host:
                return host_key

        return None;

    def get_host_keys(self, host_list):
        host_keys = {}
        for host in host_list:
            host_key = self.get_host_key(host)
            if host_key is not None:
                host_keys[host] = host_key
        return host_keys

def main():
    argument_spec = dict(
        host_list=dict(required=True, type='list'),
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           check_invalid_arguments=False,
                           supports_check_mode=True)

    check_host_list = map(str.lower, module.params['host_list'])
    check_host_set = set(check_host_list)

    host_keys = HostKeyRetriever().get_host_keys(check_host_set)

    failed_hosts = []
    for host in check_host_set:
        if host not in host_keys:
            failed_hosts.append(host)

    failed = len(failed_hosts) > 0

    if failed:
        message = "Could not connect to host(s): " + ", ".join(failed_hosts) + "."
    else:
        message = "Passed"

    module.exit_json(failed=failed, host_keys=host_keys, msg=message)

if __name__ == '__main__':
    main()
