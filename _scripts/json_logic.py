from .macros import Macro
from .constants import *
from pathlib import Path
import json
from platform import system as getOperativeSystem

def getLocalPath():
    return Path(__file__).resolve().parent.parent

LOCAL_PATH : Path = getLocalPath()
DATA_PATH  : Path = LOCAL_PATH/'DATA'
MACROS_JSON: Path = DATA_PATH/'macros.json'
VARS_JSON  : Path = DATA_PATH/'vars.json'

DEFAULT_MACRO: Macro = Macro(
    'default',
    {},
    [
        f'{'cls' if getOperativeSystem() == 'Windows' else 'clear'}',
        f'echo Hello, CPS! v{VERSION} 2025'
    ]
)

def createJSONFileInData(
    path: Path,
    folder_path: Path | None = None
) -> None:
    if not DATA_PATH.exists():
        DATA_PATH.mkdir(parents=True)
    if folder_path is not None:
        full_path = folder_path/path
        if folder_path and not folder_path.exists():
            folder_path.mkdir(parents=True)
    else:
        full_path = path

    with open(full_path.absolute(), 'w') as f:
        json.dump({}, f, indent=JSON_INDENT)

def loadJSONFile(path: Path) -> dict[str, tuple[Param, Code]]:
    with path.open('r') as f:
        return json.load(f)

def dumpJSONFile(
    json_path: Path,
    content: dict,
    default: tuple | None = None
) -> None:
    with json_path.open('w') as f:
        if default is not None:
            content.setdefault(*default)
        json.dump(content, f, indent=JSON_INDENT)