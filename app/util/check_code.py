from ast import (
    Attribute,
    Call,
    ClassDef,
    FunctionDef,
    Import,
    ImportFrom,
    Load,
    Name,
    parse,
    walk,
)

from app.game.entities import Robot
from app.util.errors import (
    ROBOT_CODE_CLASSES_ERROR,
    ROBOT_CODE_UNIMPLEMENTED_ERROR,
    ROBOT_CODE_UNSAFE_ERROR,
    ROBOT_CODE_WAW_ERROR,
)

ALLOWED_IMPORTS = {"math", "random", "numpy", "tensorflow"}
FORBIDDEN_FUNCS = {
    "delattr",
    "eval",
    "exec",
    "getattr",
    "globals",
    "input",
    "locals",
    "open",
    "setattr",
    "vars",
}
ROBOT_ABSTR_FUNCS = {"initialize", "respond"}
ROBOT_FINAL_FUNCS = {
    f for f in dir(Robot) if not f.startswith("__") and f not in ROBOT_ABSTR_FUNCS
}
ROBOT_API_FUNCS = {f for f in ROBOT_FINAL_FUNCS if not f.startswith("_")}
ROBOT_PRIV_FUNCS = {f for f in ROBOT_FINAL_FUNCS if f.startswith("_")}

del Robot.__abstractmethods__
r = Robot(0, 0, (0, 0))
ROBOT_PRIV_VARS = {v for v in vars(r).keys()}


def check_code(src: bytes):
    tree = parse(src)

    methods = set()
    robot_count = 0
    for node in walk(tree):
        match node:
            # restrict imports
            case Import(names=names):
                if any(alias.name not in ALLOWED_IMPORTS for alias in names):
                    raise ROBOT_CODE_UNSAFE_ERROR
            case ImportFrom(module=module, level=level):
                if level != 0 or module not in ALLOWED_IMPORTS:
                    raise ROBOT_CODE_UNSAFE_ERROR
            # disable calls to some builtins and to private functions
            case Call(func=Name(id=name)):
                if name in FORBIDDEN_FUNCS or name in ROBOT_PRIV_FUNCS:
                    raise ROBOT_CODE_UNSAFE_ERROR
            # disable dunders
            case Name(id=name):
                if name.startswith("__"):
                    raise ROBOT_CODE_UNSAFE_ERROR
            # disable dunders and private variable access
            case Attribute(attr=attr):
                if attr.startswith("__"):
                    raise ROBOT_CODE_UNSAFE_ERROR
                if attr in ROBOT_PRIV_VARS:
                    raise ROBOT_CODE_UNSAFE_ERROR
            # redefining methods is not allowed
            case FunctionDef(name=name):
                if name in ROBOT_FINAL_FUNCS:
                    raise ROBOT_CODE_WAW_ERROR
                if name in ROBOT_ABSTR_FUNCS:
                    methods.add(name)
            # code must define exactly one robot
            case ClassDef(name=name, bases=bases):
                if any(b.id == "Robot" for b in bases):
                    robot_count += 1
                    if robot_count > 1:
                        raise ROBOT_CODE_CLASSES_ERROR
                    if len(bases) > 1:
                        raise ROBOT_CODE_UNSAFE_ERROR

    if methods != ROBOT_ABSTR_FUNCS:
        raise ROBOT_CODE_UNIMPLEMENTED_ERROR
    return
