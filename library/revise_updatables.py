#!/usr/bin/python
import json
from ansible.module_utils.basic import AnsibleModule



#==
def main():
  argument_spec = {
    "before": {"required": True, "type": "dict"},
    "after": {"required": True, "type": "dict"},
  }

  module = AnsibleModule(argument_spec=argument_spec,
                           check_invalid_arguments=True,
                           supports_check_mode=True)

# find all the items from before.all that have a different version from after.all *and* are not already listed in the before.updatables
# put them in before.updatables and return before.

  before = module.params['before']
  before_all = before['all']
  updatables = before['updatables']

  after=module.params['after']
  after_all = after['all']

  mgs = ""

  for pkg in after_all:
    if pkg in before_all:
      ver1= after_all[pkg]
      ver2= before_all[pkg]
      if ver1 != ver2:
        if pkg not in updatables:
          updatables[pkg] = before_all[pkg]

  module.exit_json(failed=False, changed=False, all=before_all, updatables=updatables)

#==
if __name__ == '__main__':
    main()
