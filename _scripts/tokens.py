SET = '='
APP = '+'
PRE = '-'
SWP = '#'
OPERATORS = [
    SET,
    APP,
    PRE,
    SWP
]

INFO_FULL    = '--info'
INFO_INIT    = '-i'
HELP_FULL    = '--help'
HELP_INIT    = '-h'
VERSION_FULL = '--version'
VERSION_INIT = '-v'
RESTART_FULL   = '--restart'
UPDATE_FULL  = '--update'
COMMANDS = [
    INFO_FULL,
    INFO_INIT,
    HELP_FULL,
    HELP_INIT,
    VERSION_FULL,
    VERSION_INIT,
    RESTART_FULL,
    UPDATE_FULL,
]

NULL = '.'
EXCLA  = '!'
COMMA = ','
# MODIFIERS = [
#     NULL,
#     EXCLA,
#     COMMA
# ]

# Assistants
def is_float(number: str) -> bool:
    try:
        dots = number.count('.')
        if dots != 1:
            return False
        float(number)
        return True
    except ValueError:
        return False
    
def is_int(number: str) -> bool:
    try:
        int(number)
        return True
    except ValueError:
        return False

# CPS TOKENS
STRING = 'STRING'
FLOAT  = 'FLOAT'
INT    = 'INTEGER'
NUMBER    = [FLOAT, INT]
OPER   = 'OPERATOR'
NAME   = 'NAME'
COMM   = 'COMMAND'

class Token:
    def __init__(self, type: str, value: str | None = None):
        self.type = type
        self.value = value
        
    def __repr__(self) -> str:
        if self.value is not None:
            return f'({self.type}: {self.value})'
        return f'({self.type})'
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.type == other
        if isinstance(other, Token):
            return self.type == other.type
        if isinstance(other, list):
            return self.type in other
        return False
    
    def __contains__(self, other):
        if isinstance(other, list):
            return self.type in other

# Returns the number of chunks consumed and the string result
def lex_string(argv: list[str]) -> tuple[int, str]:
    string = ''
    for consumed, arg in enumerate(argv):
        if arg.endswith('\''):
            return (consumed + 1, string[1:] + arg[:-1])
        else:
            string += arg + ' '
    assert 0, f"End of string not founded: {string}"

def tokenize_argv(argv: list[str]) -> list[Token]:
    tokens = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in COMMANDS:
            tokens.append(Token(COMM, arg))
        elif arg == NULL:
            tokens.append(Token(NULL, NULL))
        elif arg == EXCLA:
            tokens.append(Token(EXCLA, EXCLA))
        elif arg == COMMA:
            tokens.append(Token(COMMA, COMMA))
        elif arg in OPERATORS:
            tokens.append(Token(OPER, arg))
        elif arg.startswith('\''):
            if arg.endswith('\''):
                tokens.append(Token(STRING, arg[1:-1]))
            else:
                consumed, string = lex_string(argv[i:])
                i += consumed - 1
                tokens.append(Token(STRING, string))
        elif is_float(arg):
            tokens.append(Token(FLOAT, arg))
        elif is_int(arg):
            tokens.append(Token(INT, arg))
        else:
            tokens.append(Token(NAME, arg))
        i += 1
    return tokens

def extract_values(tokens: list[Token]) -> list[str]:
    return [token.value for token in tokens]

# [NAME, OPER] == [NAME, OPER, STRING]
def partial_match(match_list: list[str], tokens: list[Token]):
    tokens = tokens[:len(match_list)]
    return (match_list == tokens)

def partial_extract(match_len: int, tokens: list[Token]):
    """Returns the values of the first slice and the tokens of the second\n
    lit:
    ```
    return extract_values(
        tokens[:match_len]
    ), tokens[match_len:]
    ```"""
    return (extract_values(tokens[:match_len]), tokens[match_len:])