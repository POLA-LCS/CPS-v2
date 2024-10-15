from scripts import *

# TODO
# from os.path import dirname, abspath
# import json
# PATH = dirname(abspath(__file__))
# JSON_PATH = PATH + '/cps.json, printable'
# INDENT = 4
# Run:
#     <nothing>     Run default macro with default arguments
#     M             Run M with default arguments
#     M % <p...>    Run M with arguments <p>
# Arguments:
#     M %% A P       Set macro M argument A prompt to P
#     M %% A .       Deletes argument A from M

def display_help():
    print("""[USAGE]
          
Nomenclature:
    M = Macro name
    N = Integer
    S = String

Info:
    --help      Display this message
    --info      Display the macros info
    M --info    Display the macro M info
    
Set:
    M = S    Create M with the line S
    M + S    Append S to M
    M - S    Prepend S to M
    M = M2    Override the M code with the M2 code
    M + M2    Extend M2 code into M code
    M - M2    Prextend M2 code into M code (not reverse)
    M # M2    Swap M with M2

Delete:
    M = .    Delete M
    M + .    Delete M last line
    M - .    Delete M first line
""")

def cps(message: str, printable: bool):
    if printable:
        print(f'[CPS] {message}')

def cps_input(message: str, printable: bool):
    if printable:
        return input(f'[CPS] {message} >> ')
    return 'Y'

def main(argv: list[str], argc: int, printable = True):
    tokens = tokenize_argv(argv)
    
    # Run default macro
    if argc == 0:
        run_macro(macros['0'])
    
    # Display HELP
    elif [OPER] == tokens:
        oper = tokens[0].value
        if oper in [HELP_FULL, HELP_INIT]:
            display_help()
        elif oper in [INFO_FULL, INFO_INIT]:
            for mac in macros:
                display_macro_info(mac)
                print()
                
    # CALL
    elif [NAME] == tokens:
        name = tokens[0].value
        check_macro(name) # assert
        run_macro(macros[name])
    
    # INFO
    elif [NAME, OPER] == tokens:
        name, oper = extract_values(tokens)
        if oper in [INFO_FULL, INFO_INIT]:
            check_macro(name) # assert
            display_macro_info(name)
            
    # CREATE, OVERRIDE, APPEND, PREPPEND
    elif [NAME, OPER, STRING] == tokens:
        name, oper, string = extract_values(tokens)
        if oper == SET:
            if check_macro(name, False) is None: # get
                macros[name] = [] if string == '' else [string]
                cps(f'Create: {name}', printable)
            elif cps_input('Override existing macro? (Y / ...)', printable) == 'Y':
                macros[name] = [] if string == '' else [string]
                cps(f'Override: {name}', printable)
        elif oper == APP:
            check_macro(name) # assert
            macros[name].append(string)
            cps(f'Append {name}: {string}', printable)
        elif oper == PRE:
            check_macro(name) # assert
            cps(f'Preppend {name}: {string}', printable)
            macros[name].insert(0, string)
        
    # DUMP, EXTEND, PREXTEND
    elif [NAME, OPER, NAME] == tokens:
        to_name, oper, from_name = extract_values(tokens)
        check_macro(from_name)
        if oper == SET:
            macros[to_name] = [line for line in macros[from_name]]
            cps(f'Dump: {from_name} => {to_name}', printable)
        elif oper == APP:
            check_macro(to_name)
            macros[to_name].extend(macros[from_name])
            cps(f'Extend: {from_name} -> {to_name}', printable)
        elif oper == PRE:
            check_macro(to_name)
            for i, line in enumerate(macros[from_name]):
                macros[to_name].insert(i, line)
            cps(f'Prextend: {from_name} -> {to_name}', printable)
        elif oper == SWP:
            check_macro(to_name)
            macro_pivot = macros[to_name]
            macros[to_name] = macros[from_name]
            macros[from_name] = macro_pivot
            cps(f'Swap: {to_name} <=> {from_name}', printable)
            
    # DELETE, POP FIRST, POP LAST
    elif [NAME, OPER, MOD] == tokens:
        name, oper, mod = extract_values(tokens)
        if oper == SET:
            if mod == NUL:
                check_macro(name)
                macros.pop(name)
                cps(f'Deleted: {name}', printable)
        elif oper == APP:
            if mod == NUL:
                check_macro(name)
                check_macro_len(name)
                cps(f'Pop last {name}: {macros[name].pop()}', printable)
        elif oper == PRE:
            if mod == NUL:
                check_macro(name)
                check_macro_len(name)
                cps(f'Pop first {name}: {macros[name].pop(0)}', printable)
                
    # No print
    elif partial_match([MOD], tokens):
        mod, rest = partial_split(1, tokens)
        if mod[0] == NUL:
            main(argv[1:], argc - 1, False)

    # MULTIPLE LINES CREATE, APPEND, PREPPEND
    elif partial_match([NAME, OPER], tokens):
        match_value, rest = partial_split(2, tokens)
        name, oper = match_value
        for line in rest:
            main(match_value + [f"'{line.value}'" if line.type == STRING else line.value], 3, printable)
        
from sys import argv
if __name__ == '__main__':
    args = argv[1:]
    argc = len(args)
    if argc == 0:
        print('CPS v2.0 2024')
        print('| Type "--help" to get the help message.')
        print('| "exit" to closes the interpreter.')
        while (line := input('\n>>> ')) != 'exit':
            try:
                main(chunks := line.split(' '), len(chunks))
            except AssertionError as ass:
                print('[ERROR]', ass)
    else:
        try:
            main(args, argc)
        except AssertionError as ass:
            print(f'[ERROR] {ass}')
            exit(1)
        finally:
            exit(2)
    exit(0)