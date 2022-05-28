import ast
import ctypes
import inspect
import os
import subprocess
import sys

from tree_to_code import dump
from typing import Callable
from ctypes import cdll, LibraryLoader


def compile_dll(func: Callable):
    source = inspect.getsource(func)
    ast_object = ast.parse(source)
    print(ast.dump(ast_object, indent=4))
    if not os.path.exists("cache"):
        os.makedirs("cache")
    cpp_filename = f"cache/{func.__name__}.cpp"
    dump.dump_cpp_text(tree=ast_object, filename=cpp_filename)
    o_filename = cpp_filename.replace(".cpp", ".o")
    subprocess.run(["g++", "-c", cpp_filename, "-DLIBRARY_EXPORTS", "-o", o_filename])
    dll_filename = o_filename.replace(".o", ".dll")
    subprocess.run(["g++", "-shared", "-o", dll_filename, o_filename])
    # dll = cdll.LoadLibrary(dll_filename)
    dll = LibraryLoader(ctypes.CDLL).LoadLibrary(dll_filename)
    return dll


def jit(func: Callable) -> Callable:
    exec_module = compile_dll(func)

    def jit_func(*args, **kwargs):
        name = func.__name__
        print(args, kwargs)
        return exec_module[name](*args, **kwargs)

    return jit_func

