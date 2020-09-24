import sys
import yaml
from os import path
from ansible.module_utils.basic import AnsibleModule

def main():
    fields = {
        "yaml_file": { "required": True, "type": "str" },
        "must_exist": { "default": False, "type": "bool" },
    }
    module = AnsibleModule(argument_spec=fields)
    yaml_file = module.params['yaml_file']
    must_exist = module.params['must_exist']

    file_exists = path.isfile(yaml_file)

    if not file_exists:
        module.exit_json(failed=must_exist, file=yaml_file, msg="Does not exist")

    try:
        with open(yaml_file, 'r') as stream:
           content = yaml.load(stream)
    except:
        info = sys.exc_info()
        error_message = "Verification failed for {0}: {1} {2}".format(yaml_file, info[0], info[1])
        module.exit_json(failed=True, file=yaml_file, msg=error_message)

    module.exit_json(failed=False, file=yaml_file, content=content, msg="Loaded successfully")

if __name__ == '__main__':
    main()