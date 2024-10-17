from _scripts import *

# Run:
#     <nothing>     Run default macro with default arguments
#     Mac             Run Mac with default arguments
#     Mac % <p...>    Run Mac with arguments <p>
# Arguments:
#     Mac %% A P       Set macro Mac argument A prompt to P
#     Mac %% A .       Deletes argument A from Mac

def display_help():
    print("""[USAGE]
          
Nomenclature:
    Mac = Macro name
    Str = String

Info:
    --help      Display this message
    --info      Display the macros dictionary info
    --version   Display the version 
    Mac --info    Display the macro Mac info
    
Set:
    Mac = Str    Create Mac with the line Str
    Mac + Str    Append Str to Mac
    Mac - Str    Prepend Str to Mac
    Mac = Mac2    Override the Mac code with the Mac2 code
    Mac + Mac2    Extend Mac2 code into Mac code
    Mac - Mac2    Prextend Mac2 code into Mac code (not reverse)
    Mac # Mac2    Swap Mac with Mac2

Delete:
    Mac = .    Delete Mac
    Mac + .    Delete Mac last line
    Mac - .    Delete Mac first line
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
    try:
        macro_dict = load_json_file(DATA_PATH + '\\' + MACROS_JSON)
    except FileNotFoundError:
        create_json_file(DATA_PATH, MACROS_JSON)
        return main(argv, argc, printable)
    
    macros = MacroList([Macro(key, *content) for key, content in macro_dict.items()])
        
    # Run default macro
    if argc == 0:
        macros.run(macros.get('0'))
    
    # Display HELP
    elif [COMM] == tokens:
        comm = tokens[0].value
        if comm in [HELP_FULL, HELP_INIT]:
            display_help()
        elif comm in [INFO_FULL, INFO_INIT]:
            for mac in macros.list_of:
                macros.display_info(mac)
        elif comm in [VERSION_FULL, VERSION_INIT]:
            cps(f'Version 2024: {VERSION}')
                
    # CALL
    elif [NAME] == tokens:
        macros.run(macros.get(tokens[0].value)) # assert
    
    # INFO
    elif [NAME, COMM] == tokens:
        name, oper = extract_values(tokens)
        if oper in [INFO_FULL, INFO_INIT]:
            macros.display_info(macros.get(name)) # assert
            
    # CREATE, OVERRIDE, APPEND, PREPPEND
    elif [NAME, OPER, STRING] == tokens:
        name, oper, string = extract_values(tokens)
        
        if oper == SET:
            macro = macros.get(name, False)
            if macro is None: # get
                macros.add(name, {}, [] if string == '' else [string])
                cps(f'Create: {name}', printable)
            elif cps_input('Override existing macro? (Y / ...)', printable) == 'Y':
                macro.code = [] if string == '' else [string]
                cps(f'Override: {name}', printable)

        elif oper == APP:
            macro = macros.get(name) # assert
            macro.code.append(string)

            cps(f'Append {name}: {string}', printable)
        elif oper == PRE:
            macro = macros.get(name) # assert
            cps(f'Preppend {name}: {string}', printable)
            macro.code.insert(0, string)
        
    # DUMP, EXTEND, PREXTEND
    elif [NAME, OPER, NAME] == tokens:
        target_name, oper, from_name = extract_values(tokens)
        target = macros.get(from_name)

        if oper == SET:
            if (macro := macros.get(target_name, False)) is None:
                macros.add(target_name, target.param, target.code)
                cps(f'Created: {target_name} <= {from_name}', printable)
            else:
                macro.param = target.param
                macro.code = target.code
                cps(f'Override: {target_name} <= {from_name}', printable)

        elif oper == APP:
            macro = macros.get(target_name)
            macro.code.extend(target.code)
            cps(f'Extend: {target_name} << {from_name}', printable)
            
        elif oper == PRE:
            macro = macros.get(target_name)
            for i, line in enumerate(target.code):
                macro.code.insert(i, line)
            cps(f'Prextend: {from_name} >> {target_name}', printable)

        elif oper == SWP:
            macro = macros.get(target_name)
            macro, target = target, macro
            cps(f'Swap: {target_name} <=> {from_name}', printable)
            
    # DELETE, POP FIRST, POP LAST
    elif [NAME, OPER, MOD] == tokens:
        name, oper, mod = extract_values(tokens)

        if oper == SET:
            if mod == NULL:
                macro = macros.get(name)
                macros.list_of.remove(macro)
                cps(f'Delete: {name}', printable)

        elif oper == APP:
            if mod == NULL:
                macro = macros.get(name) # assert
                macros.get_len(macro)    # assert
                cps(f'Pop last {name}: {macro.code.pop()}', printable)

        elif oper == PRE:
            if mod == NULL:
                macro = macros.get(name) # assert
                macros.get_len(macro)    # assert
                cps(f'Pop first {name}: {macro.code.pop(0)}', printable)
                
    elif [NAME, INT, STRING] == tokens:
        name, integer, string = extract_values(tokens)
        integer = int(integer)
        macro = macros.get(name)
        macro_len = macros.get_len(macro, False)
        if 0 >= integer < macro_len:
            macro.code.insert(integer, string)
            cps(f'Insert in {integer}: {name} << {string}')
        else:
            cps(f'Out of range {name}(0, {macro_len}): {integer}.', printable)
                
    elif [NAME, INT, OPER, STRING] == tokens:
        name, integer, oper, string = extract_values(tokens)
        integer = int(integer)
        macro = macros.get(name)
        macro_len = macros.get_len(macro, False)
        if 0 >= integer < macro_len:
            if oper == SET:
                macro.code[integer] = string
            elif oper == APP:
                macro.code[integer] += string
            elif oper == PRE:
                macro.code[integer] = string + macro.code[integer]
        else:
            cps(f'Out of range {name}(0, {macro_len}): {integer}.', printable)
                
    # No output message
    elif partial_match([MOD], tokens):
        mod, rest = partial_split(1, tokens)
        if mod[0] == NULL:
            main(argv[1:], argc - 1, False)

    # Multi-line execute
    elif partial_match([NAME, OPER], tokens):
        match_value, rest = partial_split(2, tokens)
        name, oper = match_value
        for line in rest:
            main(match_value + [f"'{line.value}'" if line.type == STRING else line.value], 3, printable)

    else:
        cps(f'Invalid instruction sequence: {tokens}.', printable)
    try:
        dump_json_file(
            DATA_PATH + '\\' + MACROS_JSON,
            dict([macro.get_dict_format() for macro in macros.list_of]),
            (DEFAULT_MACRO.name, DEFAULT_MACRO.get_dict_format())
        )
    except FileNotFoundError:
        print('[ERROR] Failed to dump macros to JSON file.')
        
from sys import argv
if __name__ == '__main__':
    args = argv[1:]
    argc = len(args)
    
    if argc == 0:
        print('CPS v2.0.1 2024')
        print('| Type "--help" to get the help message.')
        print('| "exit" to closes the interpreter.')
    
        while (line := input('\n>>> ')) != 'exit':
            try:
                main(chunks := line.split(' '), len(chunks))
            except AssertionError as ass:
                print('[ERROR]', ass)
        exit(1)
    try:
        main(args, argc)
            
    except AssertionError as ass:
        print(f'[ERROR] {ass}')
        exit(2)
    exit(0)