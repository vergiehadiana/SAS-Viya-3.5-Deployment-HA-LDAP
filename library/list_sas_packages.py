#!/usr/bin/python

import json
import subprocess
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.sas_lib import sas_lib
from ansible.module_utils.list_sas_packages import build_type_factory

#==
def get_sas_packages(helper):
  packages = {}
  cmd_string = helper.get_packages_cmd()

  p = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  for line in p.stdout.readlines():
      flds = line.decode().split()
      pkg=""
      ver=""
      if (len(flds) == 2):
        pkg = flds[0]
        ver=flds[1]
        packages[pkg] = ver
  retVal = p.wait()
  if (retVal  != 0):
    message = "The command {0} failed.".format(s)
    module.exit_json(failed=True, msg=message)
  return packages

#==
def get_updatables(helper):
  updatables = {}
  cmd_string = helper.get_updatables_cmd()

  p = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  for line in p.stdout.readlines():
      flds = line.decode().split()
      pkg=""
      ver=""
      if (len(flds) == 2):
        pkg = flds[0]
        ver=flds[1]
        updatables[pkg] = ver
  retVal = p.wait()
  if (retVal  != 0):
    message = "The command {0} failed.".format(s)
    module.exit_json(failed=True, msg=message)
  return updatables


#==
def main():
  fields = {
    "sas_vars": {"required": True, "type": "dict"}
  }
  module = AnsibleModule(argument_spec=fields, supports_check_mode=True)
  sas_vars = module.params['sas_vars']

  saslib = sas_lib(module)
  build_type = saslib.extract_build_type(sas_vars)

  factory = build_type_factory.factory(module)
  helper = factory.create(build_type)

  saslib.check_executables(helper)

  a = get_sas_packages(helper)
  b = get_updatables(helper)
  module.exit_json(failed=False, changed=True, updatables=b, all=a)

#==
if __name__ == '__main__':
    main()
