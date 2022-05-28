import subprocess
import code_to_tree.parser as parser
import tree_to_code.dump as dump
from ctypes import *
from annotation import jit
from timeit import timeit, repeat
from struct import unpack


@jit
def exp(x: float) -> float:
    res: float = 0
    threshold: float = 1e-30
    delta: float = 1
    elements: int = 0

    while delta > threshold:
        elements = elements + 1
        delta = delta * x / elements

    while elements >= 0:
        res += delta
        delta = delta * elements / x
        elements -= 1

    return res


def p_exp(x: float) -> float:
    res: float = 0
    threshold: float = 1e-30
    delta: float = 1
    elements: int = 0

    while delta > threshold:
        elements = elements + 1
        delta = delta * x / elements

    while elements >= 0:
        res += delta
        delta = delta * elements / x
        elements -= 1

    return res


if __name__ == '__main__':
    arg = 200
    print("Accuracy:")
    print(f"{exp(arg):.30f}")
    print(f"{p_exp(arg):.30f}")
    print("Speed:")
    print(max(repeat(lambda: exp(arg), number=10000)))
    print(max(repeat(lambda: p_exp(arg), number=10000)))

