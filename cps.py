from _scripts import *
import subprocess
import os
from typing import Literal

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
    Mac , Ins1, Ins2    Execute multiple instructions
""")

def assertMacro(macros: MacroList, macro_name: str) -> Literal[True]:
    assert macros.check(macro_name) is not None, f"Macro doesn't exists {macro_name}"
    return True

def updateCPS():
    script_path = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(script_path + '/.git'):
        return 1
    
    process = subprocess.Popen('git pull', cwd=script_path, shell=True)
    return process.wait()

def CPS(message: str, printable: bool):
    if printable: print(f'[CPS] {message}')
        
def CPSInput(message: str, printable = True) -> str:
    if printable:
        print(f'[CPS] {message}', end=' ')
        return input('>> ')
    return ''

def main(argv: list[str], argc: int, printable = True):
    try:
        macro_dict = loadJSONFile(MACROS_JSON)
    except FileNotFoundError:
        CPS('It seems the macros.json file path doesn\'t exists', True)
        if CPSInput('Create? (Y / ...)', True).upper() != 'Y':
            CPS('Cancelled.', True)
            return
        createJSONFileInData(MACROS_JSON)
        dumpJSONFile(MACROS_JSON, {}, DEFAULT_MACRO.getDictFormat())
        return main(argv, argc, printable)
    except json.decoder.JSONDecodeError:
        dumpJSONFile(MACROS_JSON, {}, DEFAULT_MACRO.getDictFormat())
        return main(argv, argc, printable)

    tokens = tokenizeArgv(argv)
    macros = MacroList([Macro(key, *content) for key, content in macro_dict.items()])

    # Index assistant
    def assertIndex(macro_name: str, index: str) -> tuple[Macro, int]:
        int_idx = int(index)
        assert (macro := macros.check(macro_name)) is not None, f"(in index) Macro doesn't exists: {macro_name}"
        assert (int_idx >= 0 and int_idx < (macro_len := macros.checkLen(macro, False))), f'Out of range {macro_name}(0, {macro_len}): {int_idx}.'
        return (macro, int_idx)

    # Run default macro
    if not argc:
        assert (default_macro := macros.check('default')) is not None, "(in default) Somehow macro doesn't exists: 'default'"
        arguments = defaultArguments(default_macro.code, default_macro.parameters)
        runMacro(arguments)

    # HELP, INFO, VERSION and SETUP
    elif COMM == tokens[0]:
        comm = tokens[0].value
        if comm in [HELP_FULL, HELP_INIT]:
            display_help()
            
        elif comm in [INFO_FULL, INFO_INIT]:
            for mac in macros.list_of:
                displayInfo(mac)
                print()
                
        elif comm in [VERSION_FULL, VERSION_INIT]:
            CPS(f'Version 2025: {VERSION}', printable)
            
        elif comm == RESTART_FULL:
            CPS('Restarting macros.json file...', printable)
            if 'Y' != CPSInput('Are you sure? (Y / ...)', printable).upper():
                CPS('Cancelled.', printable)
                return
            createJSONFileInData(MACROS_JSON)
            dumpJSONFile(MACROS_JSON, {}, DEFAULT_MACRO.getDictFormat())
            CPS('Restarted macros.json file.', printable)
            
        elif comm == UPDATE_FULL:
            CPS('Updating to the last version of CPS...', printable)
            if CPSInput('Are you sure? (Y / ...)', printable).upper() != 'Y':
                CPS('Cancelled.', printable)
                return
            if updateCPS():
                CPS('Failed to update to the last version of CPS:\n    Git is not installed?\n    ".git" folder was deleted?\n    Are you offline?.', printable)
                return
            
            default_format = DEFAULT_MACRO.getDictFormat()
            if (default_macro := macros.check('default')) is None:
                macros.add(default_format[0], *default_format[1])
            else:
                default_macro = DEFAULT_MACRO
            macros.changed = True

    # CALL WITH DEFAULT ARGUMENTS
    elif [NAME] == tokens:
        macro_name: str = tokens[0].value
        assert (macro := macros.check(macro_name)) is not None, f"Macro doesn't exists: {macro_name}"
        runMacro(defaultArguments(macro.code, macro.parameters))

    # INFO
    elif [NAME, COMM] == tokens:
        macro_name, operator = extractValues(tokens)
        if operator in [INFO_FULL, INFO_INIT]:
            assert (macro := macros.check(macro_name)) is not None, f"(in info) Macro doens't exists: {macro_name}"
            displayInfo(macro)

    # MODIFY PARAMETERS
    elif [NAME, PARAM_PREFIX, NAME, [STRING, INT, FLOAT]] == tokens:
        macro_name, _, param_name, param_value = extractValues(tokens)
        assert (macro := macros.check(macro_name)) is not None, f"(in modify param) Macro doens't exists: {macro_name}"
        if param_name in macro.parameters:
            CPS(f'Override {macro_name} argument {param_name}: {param_value}', printable)
        else:
            CPS(f'Created {param_name} for {macro_name}: {param_value}', printable)
        macro.parameters[param_name] = param_value
        macros.changed = True

    # DELETE PARAMETERS
    elif [NAME, PARAM_PREFIX, NAME, NULL] == tokens:
        macro_name, _, param_name, _ = extractValues(tokens)
        assert (macro := macros.check(macro_name)) is not None, f"(in delete param) Macro doens't exists: {macro_name}"
        assert param_name in macro.parameters, f"{macro_name}'s parameter {param_name} doesn't exists."
        macro.parameters.pop(param_name)
        CPS(f'Delete from {macro_name}: {param_name}', printable)
        macros.changed = True

    # INPUT ARGUMENTS
    elif partialMatch([NAME, EXCLA], tokens):
        matches, rest = partialExtract(2, tokens)
        macro_name, _ = matches
        assert (macro := macros.check(macro_name)) is not None, f"(in call args) Macro doesn't exists: {macro_name}"
        arguments = replaceArguments(macro, extractValues(rest))
        runMacro(macro.code)

    # CREATE, OVERRIDE, APPEND, PREPPEND
    elif [NAME, OPER, STRING] == tokens:
        macro_name, oper, string = extractValues(tokens)

        if oper == SET:
            if (macro := macros.check(macro_name)) is None:
                macros.add(macro_name, {}, [] if string == '' else [string])
                CPS(f'Create: {macro_name}', printable)
            elif not printable or CPSInput('Override existing macro? (Y / ...)', printable) == 'Y':
                macro.code = [] if string == '' else [string]
                CPS(f'Override: {macro_name}', printable)

        elif oper == APP:
            assert (macro := macros.check(macro_name)) is not None, f"(in append) Macro doens't exist: {macro_name}"
            macro.code.append(string)
            CPS(f'Append {macro_name}: {string}', printable)

        elif oper == PRE:
            assert (macro := macros.check(macro_name)) is not None, f"(in preppend) Macro doens't exists: {macro_name}"
            macro.code.insert(0, string)
            CPS(f'Preppend {macro_name}: {string}', printable)

        macros.changed = True

    # DUMP, EXTEND MACRO, PREXTEND MACRO, SWAP
    elif [NAME, OPER, NAME] == tokens:
        left_name, oper, right_name = extractValues(tokens)
        assert (right_macro := macros.check(right_name)) is not None, f"(in binary) Macro doens't exists: {right_name}"

        if oper == SET:
            if (left_macro := macros.check(left_name)) is None:
                macros.add(left_name, right_macro.parameters, right_macro.code)
                CPS(f'Created: {left_name} <= {right_name}', printable)
            else:
                left_macro.parameters = right_macro.parameters
                left_macro.code = right_macro.code
                CPS(f'Override: {left_name} <= {right_name}', printable)
        else:
            assert (left_macro := macros.check(left_name)) is not None, f"(in preppend copy) Macro doens't exists: {left_name}"
            
            if oper == APP:
                left_macro.code.extend(right_macro.code)
                CPS(f'Extend: {left_name} << {right_name}', printable)

            elif oper == PRE:
                for line_index, line_string in enumerate(reversed(right_macro.code)):
                    left_macro.code.insert(line_index, line_string)
                CPS(f'Prextend: {right_name} >> {left_name}', printable)

            elif oper == SWP:
                if left_macro == right_macro: return
                macros.remove(right_name)
                macros.remove(left_name)
                macros.add(right_name, left_macro.parameters, left_macro.code)
                macros.add(left_name, right_macro.parameters, right_macro.code)
                CPS(f'Swap: {left_name} <=> {right_name}', printable)

    # DELETE, POP FIRST, POP LAST
    elif [NAME, OPER, NULL] == tokens:
        macro_name, oper, _ = extractValues(tokens)
        
        if oper == SWP:
            CPS(f'Invalid operation: SWAP with NULL', printable)
            return

        assert (macro := macros.check(macro_name)) is not None, "(in pop) Macro doens't exists: {macro_name}"

        if oper == SET:
            macros.list_of.remove(macro)
            CPS(f'Delete: {macro_name}', printable)

        elif oper == APP:
            macros.checkLen(macro)
            CPS(f'Pop {macro_name}: {macro.code.pop()}', printable)

        elif oper == PRE:
            macros.checkLen(macro)
            CPS(f'Pop {macro_name}: {macro.code.pop(0)}', printable)
        macros.changed = True

    # INSERT
    elif [NAME, INT, STRING] == tokens:
        macro_name, integer, string = extractValues(tokens)
        macro, integer = assertIndex(macro_name, integer)
        macro.code.insert(integer, string)
        CPS(f'Insert in {macro_name}[{integer}]: {string}', printable)
        macros.changed = True

    # SET, CONCATENATE, PRE-CONCATENATE
    elif [NAME, INT, OPER, STRING] == tokens:
        macro_name, integer, oper, str_mod = extractValues(tokens)
        if oper == SWP:
            CPS(f'Invalid operation: SWAP with STRING', printable)
            return

        macro, integer = assertIndex(macro_name, integer)

        if oper == SET:
            macro.code[integer] = str_mod
            CPS(f'Override {macro_name}[{integer}]: {str_mod}', printable)

        elif oper == APP:
            macro.code[integer] += str_mod
            CPS(f'Concat {macro_name}[{integer}]: {str_mod}', printable)

        elif oper == PRE:
            macro.code[integer] = str_mod + macro.code[integer]
            CPS(f'Concat {macro_name}[{integer}]: {str_mod}', printable)
        macros.changed = True

    # DELETE LINE, POP LAST OF LINE, POP FIRST OF LINE
    elif [NAME, INT, OPER, NULL] == tokens:
        macro_name, integer, oper, _ = extractValues(tokens)
        if oper == SWP:
            CPS(f'Invalid operation: SWAP with NULL', printable)
            return

        macro, integer = assertIndex(macro_name, integer)

        if oper == SET:
            macro.code.pop(integer)
            CPS(f'Delete: {macro_name}[{integer}]', printable)

        elif oper == APP:
            last = macro.code[integer][-1]
            macro.code[integer] = macro.code[integer][:-1]
            CPS(f'Pop {macro_name}[{integer}]: {last}', printable)

        elif oper == PRE:
            first = macro.code[integer][0]
            macro.code[integer] = macro.code[integer][1:]
            CPS(f'Pop {macro_name}[{integer}]: {first}', printable)
        macros.changed = True

    # No output message
    elif partialMatch([NULL], tokens):
        main(argv[1:], argc - 1, False)
        
    elif partialMatch([NAME, NULL], tokens):
        main([argv[0]] + argv[2:], argc - 1, False)

    # Multi line operations
    elif partialMatch([NAME, COMMA], tokens):
        match, rest = partialExtract(2, tokens)
        macro_name, comm = match
        instructions: list[list[str]] = []
        row: list[str] = []
        for token in rest:
            if token == COMMA:
                instructions.append(row)
                row = []
            else:
                row.append(("'" + token.value + "'") if token.type == STRING else token.value)
        instructions.append(row)
        for ins in instructions:
            main([macro_name] + ins, len(ins) + 1, printable)
    else:
        CPS(f'Invalid instruction sequence: {tokens}.', True)
        return

    if macros.changed:
        try:
            dumpJSONFile(
                MACROS_JSON,
                dict([macro.getDictFormat() for macro in macros.list_of]),
                DEFAULT_MACRO.getDictFormat()
            )
        except FileNotFoundError:
            print('[ERROR] Failed to dump macros to JSON file.')

from sys import argv
if __name__ == '__main__':
    args = argv[1:]
    argc = len(args)

    if argc == 1 and args[0] in ['--repl', '-r']:
        print(f'CPS v{VERSION} 2025')
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
            CPS('Exit from keyboard interruption.', True)
        exit(1)
    try:
        main(args, argc)
    except AssertionError as ass:
        print(f'[ERROR] {ass}')
        exit(2)
    exit(0)