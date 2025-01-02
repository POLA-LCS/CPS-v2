from _scripts import *
import subprocess
import os

# Run:
#     <nothing>     Run default macro with default arguments
#     Mac             Run Mac with default arguments
#     Mac % <p...>    Run Mac with arguments <p>
# Arguments:
#     Mac %% A P       Set macro Mac argument A prompt to P
#     Mac %% A .       Deletes argument A from Mac

def display_help():
    print("""[USAGE]

Commands:
    --help     | -h    Display this message
    --restart          Restarts the macros.json file
    --info     | -i    Display the macros dictionary info
    --version  | -v    Display the version
    --repl     | -r    Open the Read-Eval-Print-Loop
    --update           Upload to the last version of CPS without losing macros
    Mac --info | -i    Display the macro Mac info

Set:
    Mac = Str    Create macro Mac with the code Str
    Mac + Str    Append Str to Mac
    Mac - Str    Prepend Str to Mac

    Mac = Mac2    Override the Mac code with the Mac2 code
    Mac + Mac2    Extend Mac2 code into Mac code
    Mac - Mac2    Prextend Mac2 code into Mac code (not reverse)
    Mac # Mac2    Swap Mac with Mac2

    Mac Int = Str    Set the line number Int - 1 of Mac to Str
    Mac Int + Str    Concat Str to Mac line in index Int
    Mac Int - Str    Prepend Str to Mac line in index Int

Delete:
    Mac = .    Delete Mac
    Mac + .    Pop last Mac line
    Mac - .    Pop first Mac line

    Mac Int = .    Delete Mac line in index Int
    Mac Int + .    Pop last of Mac line in index Int
    Mac Int - .    Pop first of Mac line in index Int

Call:
    Mac                 Call Mac with default arguments
    Mac ! Args          Call Mac with the specified arguments
    Mac !! Name Value   Set the Mac parameter Name to Value
    Mac !! Name .       Delete the Mac parameter Name
""")

def update_cps():
    script_path = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(script_path + '/.git'):
        return 1
    
    process = subprocess.Popen('git pull', cwd=script_path, shell=True)
    return process.wait()

def cps(message: str, printable = True):
    if printable:
        print(f'[CPS] {message}')

def main(argv: list[str], argc: int, printable = True):
    try:
        macro_dict = load_json_file(DATA_PATH/MACROS_JSON)
    except FileNotFoundError:
        cps('It seems the macros.json file path doesn\'t exists')
        if input('    Create? (Y / ...) >> ').upper() == 'Y':
            create_json_file(MACROS_JSON, DATA_PATH)
            dump_json_file(DATA_PATH/MACROS_JSON, {}, DEFAULT_MACRO.get_dict_format())
            return main(argv, argc, printable)
        cps('Cancelled.')
        return None
    except json.decoder.JSONDecodeError:
        dump_json_file(DATA_PATH/MACROS_JSON, {}, DEFAULT_MACRO.get_dict_format())
        return main(argv, argc, printable)

    tokens = tokenize_argv(argv)
    macros = MacroList([Macro(key, *content) for key, content in macro_dict.items()])

    # Index assistant
    def assert_index(name: str, index: str) -> tuple[Macro, int]:
        int_idx = int(index)
        macro = macros.check(name) # assert
        macro_len = macros.check_len(macro, False)
        assert (int_idx >= 0 and int_idx < macro_len), f'Out of range {name}(0, {macro_len}): {int_idx}.'
        return macro, int_idx

    # Run default macro
    if argc == 0:
        default_macro = macros.check('0')
        run_macro(default_arguments(default_macro.code, default_macro.parameters))

    # HELP, INFO, VERSION and SETUP
    elif COMM == tokens[0]:
        comm = tokens[0].value
        if comm in [HELP_FULL, HELP_INIT]:
            display_help()
            
        elif comm in [INFO_FULL, INFO_INIT]:
            for mac in macros.list_of:
                display_info(mac)
                print()
                
        elif comm in [VERSION_FULL, VERSION_INIT]:
            cps(f'Version 2025: {VERSION}')
            
        elif comm == RESTART_FULL:
            cps('Restarting macros.json file...')
            if 'Y' != input('    Are you sure? (Y / ...) >> ').upper():
                cps('Cancelled.')
                return
            create_json_file(MACROS_JSON, DATA_PATH)
            dump_json_file(DATA_PATH/MACROS_JSON, {}, DEFAULT_MACRO.get_dict_format())
            cps('Restarted macros.json file.')
            
        elif comm == UPDATE_FULL:
            cps('Updating to the last version of CPS...')
            if 'Y' != input('    Are you sure? (Y / ...) >> ').upper():
                cps('Cancelled.')
                return
            if update_cps():
                cps('Failed to update to the last version of CPS:\n    Git is not installed?\n    ".git" folder was deleted?\n    Are you offline?.')
                return
            
            default_format = DEFAULT_MACRO.get_dict_format()
            if (default_macro := macros.check('0', False)) is None:
                macros.add(default_format[0], *default_format[1:])
            else:
                default_macro = DEFAULT_MACRO
            macros.changed = True

    # CALL WITH DEFAULT ARGUMENTS
    elif [NAME] == tokens:
        macro = macros.check(tokens[0].value)
        run_macro(default_arguments(macro.code, macro.parameters))

    # INFO
    elif [NAME, COMM] == tokens:
        name, oper = extract_values(tokens)
        if oper in [INFO_FULL, INFO_INIT]:
            display_info(macros.check(name)) # assert

    # MODIFY PARAMETERS
    elif [NAME, PARAM_PREFIX, NAME, [STRING, INT, FLOAT]] == tokens:
        name, _, param_name, param_value = extract_values(tokens)
        macro = macros.check(name)
        if param_name in macro.parameters:
            cps(f'Override {name} argument {param_name}: {param_value}')
        else:
            cps(f'Created {param_name} for {name}: {param_value}')
        macro.parameters[param_name] = param_value
        macros.changed = True

    # DELETE PARAMETERS
    elif [NAME, PARAM_PREFIX, NAME, NULL] == tokens:
        name, _, param_name, _ = extract_values(tokens)
        macro = macros.check(name)
        assert param_name in macro.parameters, f"{name}'s parameter {param_name} doesn't exists."
        macro.parameters.pop(param_name)
        cps(f'Delete from {name}: {param_name}')
        macros.changed = True

    # INPUT ARGUMENTS
    elif partial_match([NAME, EXCLA], tokens):
        matches, rest = partial_extract(2, tokens)
        name, _ = matches
        macro = macros.check(name)
        run_macro(replace_arguments(macro, extract_values(rest)))

    # CREATE, OVERRIDE, APPEND, PREPPEND
    elif [NAME, OPER, STRING] == tokens:
        name, oper, string = extract_values(tokens)

        if oper == SET:
            macro = macros.check(name, False)
            if macro is None: # check
                macros.add(name, {}, [] if string == '' else [string])
                cps(f'Create: {name}', printable)
            elif not printable or input('[CPS] Override existing macro? (Y / ...) >> ') == 'Y':
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
        macros.changed = True

    # DUMP, EXTEND MACRO, PREXTEND MACRO, SWAP
    elif [NAME, OPER, NAME] == tokens:
        left, oper, right = extract_values(tokens)
        right_macro = macros.check(right) # assert

        if oper == SET:
            if (left_macro := macros.check(left, False)) is None:
                macros.add(left, right_macro.parameters, right_macro.code)
                cps(f'Created: {left} <= {right}', printable)
            else:
                left_macro.parameters = right_macro.parameters
                left_macro.code = right_macro.code
                cps(f'Override: {left} <= {right}', printable)

        elif oper == APP:
            left_macro = macros.check(left) # assert
            left_macro.code.extend(right_macro.code)
            cps(f'Extend: {left} << {right}', printable)

        elif oper == PRE:
            left_macro = macros.check(left) # assert
            for i, line in enumerate(right_macro.code):
                left_macro.code.insert(i, line)
            cps(f'Prextend: {right} >> {left}', printable)

        elif oper == SWP:
            left_macro = macros.check(left) # assert
            if left_macro == right_macro:
                cps(f'Invalid operation: SWAP with the same macro', printable)
                return
            macros.remove(right)
            macros.remove(left)
            macros.add(right, left_macro.parameters, left_macro.code)
            macros.add(left, right_macro.parameters, right_macro.code)
            cps(f'Swap: {left} <=> {right}', printable)

    # DELETE, POP FIRST, POP LAST
    elif [NAME, OPER, NULL] == tokens:
        name, oper, _ = extract_values(tokens)

        if oper == SET:
            macros.list_of.remove(macros.check(name))
            cps(f'Delete: {name}', printable)

        elif oper == APP:
            macro = macros.check(name) # assert
            macros.check_len(macro)    # assert
            cps(f'Pop {name}: {macro.code.pop()}', printable)

        elif oper == PRE:
            macro = macros.check(name) # assert
            macros.check_len(macro)    # assert
            cps(f'Pop {name}: {macro.code.pop(0)}', printable)

        elif oper == SWP:
            cps(f'Invalid operation: SWAP with NULL', printable)
            return

        macros.changed = True

    # INSERT
    elif [NAME, INT, STRING] == tokens:
        name, integer, string = extract_values(tokens)
        macro, integer = assert_index(name, integer)
        macro.code.insert(integer, string)
        cps(f'Insert in {name}[{integer}]: {string}', printable)
        macros.changed = True

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

        elif oper == SWP:
            cps(f'Invalid operation: SWAP with STRING', printable)
            return

        macros.changed = True

    # DELETE LINE, POP LAST OF LINE, POP FIRST OF LINE
    elif [NAME, INT, OPER, NULL] == tokens:
        name, integer, oper, _ = extract_values(tokens)
        macro, integer = assert_index(name, integer)

        if oper == SET:
            macro.code.pop(integer)
            cps(f'Delete: {name}[{integer}]')

        elif oper == APP:
            last = macro.code[integer][-1]
            macro.code[integer] = macro.code[integer][:-1]
            cps(f'Pop {name}[{integer}]: {last}')

        elif oper == PRE:
            first = macro.code[integer][0]
            macro.code[integer] = macro.code[integer][1:]
            cps(f'Pop {name}[{integer}]: {first}')

        elif oper == SWP:
            cps(f'Invalid operation: SWAP with NULL', printable)
            return

        macros.changed = True

    # No output message
    elif partial_match([NULL], tokens):
        main(argv[1:], argc - 1, False)

    else:
        assert 0, f'Invalid instruction sequence: {tokens}.'

    if macros.changed:
        try:
            dump_json_file(
                DATA_PATH/MACROS_JSON,
                dict([macro.get_dict_format() for macro in macros.list_of]),
                DEFAULT_MACRO.get_dict_format()
            )
        except FileNotFoundError:
            print('[ERROR] Failed to dump macros to JSON file.')

from sys import argv
if __name__ == '__main__':
    args = argv[1:]
    argc = len(args)

    if argc == 1 and args[0] in ['--repl', '-r']:
        print(f'CPS v{VERSION} 2024')
        print('| Type "--help" to check the help message.')
        print('| "exit" to close the interpreter.')

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