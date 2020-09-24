import subprocess

from ansible.module_utils.disk_space_check import base

#==
class x64_redhat_linux_6_yum( base.base ):
    #==
    def get_executables(self):
        return ["yum", "grep"]

    #==
    def get_disk_space_needed_for_all_packages(self, service_package_names):
        total_disk_space_needed_k = float(0)

        cmd_args_prefix = ["yum", "install"]
        cmd_args_suffix = ["--assumeno"]

        cmd_args = cmd_args_prefix + service_package_names + cmd_args_suffix
        p1 = subprocess.Popen(cmd_args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Installed"], stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        out, err = p2.communicate()
        if p2.returncode == 0:
            output_items = out.decode().replace('\n', '').replace('\r', '').split(" ")
            raw_disk_space_needed = float(output_items[2])  # space
            memory_unit = output_items[3]  # K or M or G
            total_disk_space_needed_k = self.convert_memory_size_to_kb(memory_unit, raw_disk_space_needed)
        return total_disk_space_needed_k
