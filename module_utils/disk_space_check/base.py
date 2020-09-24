import sys

#==
class base:
    #==
    def __init__(self, module):
        self.module = module

    #==
    def convert_memory_size_to_kb(self, memory_unit, size):
        memory_unit = memory_unit.lower()
        if memory_unit.find('k') > -1:
            return float(size)
        elif memory_unit.find('m') > -1:
            return float(size * 1024)
        elif memory_unit.find('g') > -1:
            return float(size * 1024 * 1024)
        elif memory_unit.find('t') > -1:
            return float(size * 1024 * 1024 * 1024)
        elif memory_unit.find('p') > -1:
            return float(size * 1024 * 1024 * 1024 * 1024)
        else:
            return float(0)  # if unit wasn't recognized

