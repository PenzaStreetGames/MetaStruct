import subprocess
import code_to_tree.parser as parser
import tree_to_code.dump as dump
from ctypes import *


def main(module_py: str, module_cpp: str):
    python_tree = parser.get_python_tree(filename=module_py)
    print(python_tree)
    print(dump.dump_module(python_tree))
    dump.dump_cpp_text(tree=python_tree, filename=module_cpp)
    object_module = module_cpp.replace(".cpp", ".o")
    subprocess.run(["g++", "-c", module_cpp, "-DLIBRARY_EXPORTS", "-o", object_module])
    dll_module = object_module.replace(".o", ".dll")
    subprocess.run(["g++", "-shared", "-o", dll_module, object_module])
    mydll = cdll.LoadLibrary(dll_module)
    result = mydll.main()
    print(result)


if __name__ == '__main__':
    main("test/python_programs/program_1.py", "test/cpp_programs/program_1.cpp")
