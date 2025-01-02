from os import system
from .constants import *
from .tokens import NULL, EXCLA

class Macro:
    def __init__(self, name: str, parameters: Param, code: Code):
        self.name = name
        self.parameters = parameters
        self.code = code
        
    def get_dict_format(self):
        return (self.name, (self.parameters, self.code))

    def __repr__(self):
        return f"{self.name}({self.parameters}){self.code}"
    
# MAIN MACRO LIST
class MacroList:
    _instance = None
    changed = False
    list_of: list[Macro] = []

    def __new__(cls, macro_list: list[Macro]):
        if cls._instance is None:
            cls._instance = super(MacroList, cls).__new__(cls)
        cls.list_of = macro_list
        return cls._instance

    def add(cls, name: str, parameters: Param, code: Code):
        cls.list_of.append(Macro(name, parameters, code))
        cls.changed = True

    def check(cls, name: str, error = True):
        for macro in cls.list_of:
            if macro.name == name:
                return macro
        assert not error, f"Macro doesn't exists: {name}"
        return None

    def check_len(cls, macro: Macro, error = True):
        length = len(macro.code)
        if error:
            assert length != 0, f"Macro is empty: {macro.name}" 
        return length

def display_info(macro: Macro):
    print(f'[CPS] {macro.name}: {macro.parameters}:')
    for line in macro.code:
        print(f'-  {line}')

def run_macro(code: Code):
    for line in code:
        system(line)
        
PARAM_PREFIX = EXCLA + EXCLA
        
def default_arguments(code: Code, parameters: Param):
    if len(parameters) == 0:
        return code
    formated_code: Code = []
    for line in code:
        for param in parameters:
            line = line.replace(PARAM_PREFIX + param, parameters[param])
        formated_code.append(line)
    return formated_code

def replace_arguments(macro: Macro, argv: list[str] | None = None):
    if not argv:
        return default_arguments(macro.code, macro.parameters)
    
    if len(macro.parameters) == 0:
        return macro.code

    formated_code: Code = []
    for line in macro.code:
        for i, param in enumerate(macro.parameters):
            line = line.replace(
                PARAM_PREFIX + param,
                argv[i] if (len(argv) > i and argv[i] != NULL) else macro.parameters[param]
            )
        formated_code.append(line)
    return formated_code