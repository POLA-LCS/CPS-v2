from os import system
from .types import *

class Macro:
    def __init__(self, name: str, param: Param, code: Code):
        self.name = name
        self.param = param
        self.code = code
        
    def get_dict_format(self):
        return (self.name, (self.param, self.code))

    def __repr__(self):
        return f"{self.name}({self.param}){self.code}"
    
# MAIN MACRO LIST
class MacroList:
    _instance = None
    list_of: list[Macro] = []

    def __new__(cls, macro_list: list[Macro]):
        if cls._instance is None:
            cls._instance = super(MacroList, cls).__new__(cls)
        cls.list_of = macro_list
        return cls._instance

    def add(cls, name: str, param: Param, code: Code):
        cls.list_of.append(Macro(name, param, code))

    def get(cls, name: str, error = True):
        for macro in cls.list_of:
            if macro.name == name:
                return macro
        assert not error, f"Macro doesn't exists: {name}"
        return None

    def get_len(cls, macro: Macro, error = True):
        if error:
            assert macro is not None, f"Macro is empty: {macro.name}" 
        return len(macro.code)

    def display_info(cls, macro: Macro):
        print(f'[CPS] {macro.name}:')
        for line in macro.code:
            print(f'-  {line}')
        print()

    def run(cls, macro: Macro):
        for line in macro.code:
            system(line)