import sys
import code_to_tree.parser as parser
import tree_to_code.dump as dump


def main(module_py: str, module_cpp: str):
    python_tree = parser.get_python_tree(filename=module_py)
    print(python_tree)
    # cpp_tree = some_func(python_tree)
    print(dump.dump_module(python_tree))
    dump.dump_cpp_text(tree=python_tree, filename=module_cpp)


if __name__ == '__main__':
    main("test/python_programs/program_1.py", "test/cpp_programs/program_1.cpp")
