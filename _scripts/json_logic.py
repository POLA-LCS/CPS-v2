from .macros import Macro
from .constants import *
from pathlib import Path
import json
from platform import system as operative_system

def get_local_path():
    return Path(__file__).resolve().parent.parent

LOCAL_PATH = get_local_path()
DATA_PATH = LOCAL_PATH/'DATA'
MACROS_JSON = 'macros.json'
VARS_JSON = 'vars.json'
INDENT = 4

DEFAULT_MACRO: Macro = Macro(
    '0',
    {},
    ['cls' if operative_system() == 'Windows' else 'clear'] + [f'echo Hello, CPS v{VERSION}!']
)

def create_json_file(path: str, folder_path: Path | None = None):
    full_path = (folder_path/path) if folder_path else Path(path)

    if folder_path and not folder_path.exists():
        folder_path.mkdir(parents=True)

    with full_path.open('w') as f:
        json.dump({}, f, indent=INDENT)

def load_json_file(path: Path) -> dict[str, tuple[Param, Code]]:
    with path.open('r') as f:
        return json.load(f)

def dump_json_file(json_path: Path, content: dict, default: tuple | None = None):
    with json_path.open('w') as f:
        if default is not None:
            content.setdefault(*default)
        json.dump(content, f, indent=INDENT)
