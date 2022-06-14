import ast
import ctypes
import inspect
import os
import subprocess

from tree_to_code import dump
from typing import Callable, Tuple
from ctypes import LibraryLoader


def compile_dll(func: Callable) -> Tuple[ctypes.CDLL, dict]:
    source = inspect.getsource(func)
    ast_object = ast.parse(source)
    # print(ast.dump(ast_object, indent=4))
    if not os.path.exists("cache"):
        os.makedirs("cache")
    cpp_filename = f"cache/{func.__name__}.cpp"
    signatures = dump.dump_cpp_text(tree=ast_object, filename=cpp_filename)
    o_filename = cpp_filename.replace(".cpp", ".o")
    subprocess.run(["g++", "-O2", "-c", cpp_filename, "-o", o_filename])
    # subprocess.run(["g++", "-c", cpp_filename, "-o", o_filename])
    dll_filename = o_filename.replace(".o", ".dll")
    subprocess.run(["g++", "-shared", o_filename, "-o", dll_filename])
    os.remove(o_filename)
    dll = LibraryLoader(ctypes.CDLL).LoadLibrary(dll_filename)
    return dll, signatures


def jit(func: Callable) -> Callable:
    exec_module, signatures = compile_dll(func)
    name = func.__name__
    jit_func = exec_module[name]
    jit_func.argtypes = signatures[name]["argtypes"]
    jit_func.restype = signatures[name]["restype"]
    return jit_func

