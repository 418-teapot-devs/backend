import os
from os import path

# solution: restrict imports
import numpy

__import__("os")
# solution: `__import__` call is forbidden
numpy.__builtins__["__import__"]("os")
# solution: attribute `__builtins__` is forbidden
b = __builtins__
b["__import__"]("math")
# solution: name `__builtins__` is forbidden
getattr(numpy, "__builtins__")["__import__"]("math")
getattr(numpy, "__buil" + "tins__")["__import__"]("math")
# solution: disable getattr
# os.__dir__()
# `dir` is harmless: it returns only the names of the attributes
numpy.__dict__["__builtins__"]["__import__"]("math")
l = numpy.__loader__
# solution: disable ALL dunders
exec("import os\ni = os.__builtins__.__import__")
with open("./teguidore", "w") as f:
    f.write("TEGUIDORE")
# solution: disable `eval` and `open` (OBVIOUSLY)
list(filter(lambda x: x[0] == "__builtins__", globals().items()))[0][
    1
]  # == builtins module
# solution: disable `globals()` call
# ALSO DISABLE `locals()` BECAUSE.
# vars() is equivalent to locals()
# PARA LAS MOROCHAS DE EVAL:
[c for c in (.__class__.__base__.__subclasses__() if c.__name__ == 'catch_warnings'][0]()._module.__builtins__["open"]
