import subprocess
from ansible.module_utils.basic import AnsibleModule

def get_consul_url(install_packages, consul_address, consul_secured):
    """
    Calculates the contextual address to use for this machine to reach a consul agent or server.

    Arguments:
    install_packages -- the list of packages that will be installed on this machine
    consul_address -- the fully qualified domain name of a consul server in the deployment
    consul_secured -- boolean representation of whether or not consul is being secured

    Returns:
    The url that this particular machine can use to reference a consul agent or server.
    """
    scheme = "http"
    port = 8500
    if consul_secured == True:
        scheme = "https"
        port = 8501
    host = consul_address
    if "sas-consul" in install_packages or "sas-localconsul" in install_packages:
        host = "localhost"
    return scheme + "://" + host + ":" + repr(port)

def init_module():
    """
    Initializes Ansible module handing
    """

    module = AnsibleModule(argument_spec={
        "install_packages": {"required": True, "type": "list"},
        "consul_address": {"required": True, "type": "str"},
        "consul_secured": {"required": True, "type": "bool"}
    })

    return module

def main():
    """
    Entry function for Ansible
    """

    module = init_module()

    install_packages = module.params['install_packages']
    consul_address = module.params['consul_address']
    consul_secured = module.params['consul_secured']

    url = get_consul_url(install_packages, consul_address, consul_secured)

    success_msg = "Successfully gathered additional host facts."
    changed = False
    module.exit_json(changed=changed, msg=success_msg, url=url)

if __name__ == '__main__':
    main()