import subprocess
import code_to_tree.parser as parser
import tree_to_code.dump as dump
from ctypes import *
from annotation import jit
from struct import unpack


@jit
def exp(x: float) -> float:
    res: float = 0
    threshold: float = 1e-20
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
    threshold: float = 1e-20
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
    for i in range(1, 11):
        arg = i / 10
        value = exp(c_double(arg))
        print(arg, exp(c_double(arg)))
        print(arg, p_exp(arg))
