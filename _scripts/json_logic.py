from .macros import Macro
from .types import *
import os
import json

def get_local_path():
    return (LOCAL := os.path.dirname(os.path.abspath(__file__)))[:LOCAL.rfind('\\')]

def get_path(folder: str, path: str):
    return folder + '\\' + path

LOCAL_PATH = get_local_path()
DATA_PATH   = get_path(LOCAL_PATH, 'DATA')
MACROS_JSON = 'macros.json'
VARS_JSON   = 'vars.json'
INDENT = 4

DEFAULT_MACRO: Macro = Macro("print", {"value": "Hello, CPS!"}, ["echo #value", "echo."])

def create_json_file(path: str, folder_path: str | None = None):
    path = get_path(folder_path, path)
    print(f'[DEBUG] Creating json: {path}...')

    if folder_path is not None and not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    with open(path, 'w') as f:
        json.dump({}, f, indent=INDENT)

def load_json_file(path: str) -> dict[str, tuple[Param, Code]]:
    with open(path, 'r') as f:
        return json.load(f)
        
def dump_json_file(json_path: str, content: dict, default: tuple | None = None):
    with open(json_path, 'w') as f:
        if default is not None:
            content.setdefault(*default)
        json.dump(content, f, indent=INDENT)