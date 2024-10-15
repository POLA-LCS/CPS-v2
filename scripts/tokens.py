from .operators import *

Number = int | float

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
    
def check_range(number: Number, from_val: Number, to_val: Number):
    assert from_val <= number <= to_val, f"Out of range({from_val} : {to_val}): {number}"

# CPS TOKENS
STRING = 'STRING'
FLOAT  = 'FLOAT'
INT    = 'INTEGER'
NUMBER = [FLOAT, INT]
OPER   = 'OPERATOR'
MOD    = 'MODIFIER'
NAME   = 'NAME'

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
        if arg in MODIFIERS:
            tokens.append(Token(MOD, arg))
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

def partial_split(match_len: int, tokens: list[Token]):
    """Returns the values of the first slice and the tokens of the second\n
    lit: `extract_values(tokens[:match_len]), tokens[match_len:]`"""
    return (extract_values(tokens[:match_len]), tokens[match_len:])