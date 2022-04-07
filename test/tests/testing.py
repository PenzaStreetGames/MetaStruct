import code_to_tree.parser as parser
from tests import results


def testing(*args, **params):
    for module, output in results.items():
        with open(f"../python_programs/{module}.py", "r", encoding="utf-8"):
            text = module
        print(parser.get_python_tree(text))
