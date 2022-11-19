from ast import Attribute, Call, Import, ImportFrom, Name, parse, walk
from importlib.util import module_from_spec, spec_from_loader
from inspect import getmembers, getmodule, isclass, isfunction
from app.game.entities import Robot
from app.util.errors import ROBOT_CODE_CLASSES_ERROR, ROBOT_CODE_UNIMPLEMENTED_ERROR, ROBOT_CODE_WAW_ERROR


ALLOWED_IMPORTS = {"math", "random", "numpy", "tensorflow"}
FORBIDDEN_FUNCS = {"delattr", "eval", "exec", "getattr", "globals", "input", "locals", "open", "setattr", "vars"}
ROBOT_ABSTR_FUNCS = {"initialize", "respond"}
ROBOT_FINAL_FUNCS = {f for f in dir(Robot) if not f.startswith("__") and f not in ROBOT_ABSTR_FUNCS}
ROBOT_API_FUNCS = {f for f in ROBOT_FINAL_FUNCS if not f.startswith("_")}
ROBOT_PRIV_FUNCS = {f for f in ROBOT_FINAL_FUNCS if f.startswith("_")}

del Robot.__abstractmethods__
r = Robot(0, 0, (0, 0))
ROBOT_PIRV_VARS = {v for v in vars(r).keys()}


def safe_to_exec(src: bytes):
    tree = parse(src)

    for node in walk(tree):
        match node:
            # restrict imports
            case Import(names=names):
                if any(alias.name not in ALLOWED_IMPORTS for alias in names):
                    return False
            case ImportFrom(module=module, level=level):
                if level != 0 or module not in ALLOWED_IMPORTS:
                    return False
            # disable dunders
            case Attribute(attr=attr):
                if attr.startswith("__"):
                    return False
            case Name(id=name):
                if name.startswith("__"):
                    return False
            # disable calls to some builtins and to private functions
            case Call(func=Name(id=name)):
                if name in FORBIDDEN_FUNCS or name in ROBOT_PRIV_FUNCS:
                    return False

    return True


def check_code_format(src):
    # create temporary module
    spec = spec_from_loader("mod", loader=None)
    assert spec is not None
    mod = module_from_spec(spec)
    exec(src, mod.__dict__)
    # get classes of module
    classes = [c for c in getmembers(mod, isclass) if c[0] != "Robot"]
    if len(classes) != 1:
        raise ROBOT_CODE_CLASSES_ERROR
    # check that no important function is overwritten
    r = classes[0][1]
    f_methods = (f[1] for f in getmembers(r, isfunction) if f[0] in ROBOT_FINAL_FUNCS)
    a_methods = (f[1] for f in getmembers(r, isfunction) if f[0] in ROBOT_ABSTR_FUNCS)
    if any(getmodule(f).__name__ != "app.game.entities" for f in f_methods):
        raise ROBOT_CODE_WAW_ERROR
    if any(getmodule(f).__name__ == "app.game.entities" for f in a_methods):
        raise ROBOT_CODE_UNIMPLEMENTED_ERROR

