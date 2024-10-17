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

def cps(message: str, printable = True):
    if printable:
        print(f'[CPS] {message}')

def cps_input(message: str, printable: bool):
    if printable:
        return input(f'[CPS] {message} >> ')
    return 'Y'

def main(argv: list[str], argc: int, printable = True):
    try:
        macro_dict = load_json_file(get_path(DATA_PATH, MACROS_JSON))
        
    except FileNotFoundError:
        cps('It seems the macros.json file path doesn\'t exists')
        if input('    Create? (Y / ...) >> ').upper() == 'Y':
            create_json_file(MACROS_JSON, DATA_PATH)
            return main(argv, argc, printable)

    except json.decoder.JSONDecodeError:
        dump_json_file(get_path(DATA_PATH, MACROS_JSON), {}, DEFAULT_MACRO.get_dict_format())
        return main(argv, argc, printable)
    
    tokens = tokenize_argv(argv)
    macros = MacroList([Macro(key, *content) for key, content in macro_dict.items()])
        
    # Assistants
    def assert_index(name: str, index: str) -> tuple[Macro, int]:
        index = int(index)
        macro = macros.check(name)
        macro_len = macros.check_len(macro, False)
        assert 0 >= index < macro_len, f'Out of range {name}(0, {macro_len}): {index}.'
        return macro, index
        
    # Run default macro
    if argc == 0:
        macros.run(macros.check('0'))
    
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
        macros.run(macros.check(tokens[0].value)) # assert
    
    # INFO
    elif [NAME, COMM] == tokens:
        name, oper = extract_values(tokens)
        if oper in [INFO_FULL, INFO_INIT]:
            macros.display_info(macros.check(name)) # assert
            
    # CREATE, OVERRIDE, APPEND, PREPPEND
    elif [NAME, OPER, STRING] == tokens:
        name, oper, string = extract_values(tokens)
        
        if oper == SET:
            macro = macros.check(name, False)
            if macro is None: # check
                macros.add(name, {}, [] if string == '' else [string])
                cps(f'Create: {name}', printable)
            elif cps_input('Override existing macro? (Y / ...)', printable) == 'Y':
                macro.code = [] if string == '' else [string]
                cps(f'Override: {name}', printable)

        elif oper == APP:
            macro = macros.check(name) # assert
            macro.code.append(string)
            cps(f'Append {name}: {string}', printable)

        elif oper == PRE:
            macro = macros.check(name) # assert
            macro.code.insert(0, string)
            cps(f'Preppend {name}: {string}', printable)
        
    # DUMP, EXTEND MACRO, PREXTEND MACRO, SWAP
    elif [NAME, OPER, NAME] == tokens:
        target_name, oper, from_name = extract_values(tokens)
        target = macros.check(from_name)

        if oper == SET:
            if (macro := macros.check(target_name, False)) is None:
                macros.add(target_name, target.param, target.code)
                cps(f'Created: {target_name} <= {from_name}', printable)
            else:
                macro.param = target.param
                macro.code = target.code
                cps(f'Override: {target_name} <= {from_name}', printable)

        elif oper == APP:
            macro = macros.check(target_name)
            macro.code.extend(target.code)
            cps(f'Extend: {target_name} << {from_name}', printable)
            
        elif oper == PRE:
            macro = macros.check(target_name)
            for i, line in enumerate(target.code):
                macro.code.insert(i, line)
            cps(f'Prextend: {from_name} >> {target_name}', printable)

        elif oper == SWP:
            macro = macros.check(target_name)
            macro, target = target, macro
            cps(f'Swap: {target_name} <=> {from_name}', printable)
            
    # DELETE, POP FIRST, POP LAST
    elif [NAME, OPER, MOD] == tokens:
        name, oper, mod = extract_values(tokens)

        if oper == SET:
            if mod == NULL:
                macros.list_of.remove(macros.check(name))
                cps(f'Delete: {name}', printable)

        elif oper == APP:
            if mod == NULL:
                macro = macros.check(name) # assert
                macros.check_len(macro)    # assert
                cps(f'Pop {name}: {macro.code.pop()}', printable)

        elif oper == PRE:
            if mod == NULL:
                macro = macros.check(name) # assert
                macros.check_len(macro)    # assert
                cps(f'Pop {name}: {macro.code.pop(0)}', printable)
      
    # INSERT          
    elif [NAME, INT, STRING] == tokens:
        name, integer, string = extract_values(tokens)
        macro = assert_index(name, integer)
        macro.code.insert(integer, string)
        cps(f'Insert in {name}[{integer}]: {string}', printable)
                
    # SET, CONCATENATE, PRE-CONCATENATE
    elif [NAME, INT, OPER, STRING] == tokens:
        name, integer, oper, str_mod = extract_values(tokens)
        macro, integer = assert_index(name, integer)
        
        if oper == SET:
            macro.code[integer] = str_mod
            cps(f'Override {name}[{integer}]: {str_mod}')

        elif oper == APP:
            macro.code[integer] += str_mod
            cps(f'Concat {name}[{integer}]: {str_mod}', printable)

        elif oper == PRE:
            macro.code[integer] = str_mod + macro.code[integer]
            cps(f'Concat {name}[{integer}]: {str_mod}', printable)
                
    elif [NAME, INT, OPER, MOD] == tokens:
        name, integer, oper, mod = extract_values(tokens)
        macro, integer = assert_index(name, integer)
        
        if oper == SET:
            if mod == NULL:
                macro.code.pop(integer)
                cps(f'Delete: {name}[{integer}]')

        elif oper == APP:
            if mod == NULL:
                last = macro.code[integer][-1]
                macro.code[integer] = macro.code[integer][:-1]
                cps(f'Pop {name}[{integer}]: {last}')

        elif oper == PRE:
            if mod == NULL:
                first = macro.code[integer][0]
                macro.code[integer] = macro.code[integer][1:]
                cps(f'Pop {name}[{integer}]: {first}')
                
    # No output message
    elif partial_match([MOD], tokens):
        mod, rest = partial_split(1, tokens)
        if mod[0] == NULL:
            main(argv[1:], argc - 1, False)

    # Multi-line execute
    elif partial_match([NAME], tokens):
        match_value, rest = partial_split(1, tokens)
        for line in rest:
            repetition_code = match_value + [f"'{line.value}'" if line.type == STRING else line.value]
            main(repetition_code, len(repetition_code), printable)

    else:
        assert 0, f'Invalid instruction sequence: {tokens}.'
    try:
        dump_json_file(
            get_path(DATA_PATH, MACROS_JSON),
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
        print('CPS v2.0.3 2024')
        print('| Type "--help" to check the help message.')
        print('| "exit" to closes the interpreter.')
    
        try:
            while (line := input('\n>>> ')) != 'exit':
                try:
                    main(chunks := line.split(' '), len(chunks))
                except AssertionError as ass:
                    print('[ERROR]', ass)
                except RecursionError:
                    print('[ERROR] Something went wrong. perhaps this syntax is invalid?')
        except EOFError:
            cps('Exit from keyboard interruption.')
        exit(1)
    try:
        main(args, argc)
    except AssertionError as ass:
        print(f'[ERROR] {ass}')
        exit(2)
    exit(0)