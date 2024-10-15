from os import system

# TODO: ADD ARGUMENTS
macros: dict[str, list[str]] = {
    '0': ['echo Hello, CPS!'],
    'cls': ['cls'],
    'clear': ['clear']
}


def display_macro_info(name: str):
    print(f'[CPS] {name}:')
    for line in macros[name]:
        print(f'-  {line}')

def check_macro(name: str, error = True) -> (list[str] | None):
    if not error:
        return macros.get(name)
    assert (code := macros.get(name)) is not None, f"Macro doesn't exists: {name}"
    return code

def check_macro_len(name: str, get_len = True):
    if get_len:
        return len(macros[name])
    assert (code_len := len(macros[name]) > 0), f"Macro is empty: {name}"
    return code_len

def run_macro(code: list[str]):
    for line in code:
        system(line)