import subprocess
import code_to_tree.parser as parser
import tree_to_code.dump as dump
from ctypes import *
from annotation import jit


@jit
def func(x: int) -> int:
    while x > 1 and x < 1000:
        x = x * x
    # i: int = 1
    # x: int = 42
    # while i < 500:
    # x = (x + 80) // 2
    # x = (x - 34) * 7
    # x = x % 103
    # x = (x << 2) & 843
    # x = (x | 55) >> 3
    # x = x * x - x
    # x = x % 68
    # i = i + 1
    y: int = x
    return y


if __name__ == '__main__':
    for i in range(100):
        print(func(i))
