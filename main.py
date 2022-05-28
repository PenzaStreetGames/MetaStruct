import subprocess
import code_to_tree.parser as parser
import tree_to_code.dump as dump
from ctypes import *
from annotation import jit
from timeit import timeit, repeat
import numba
from struct import unpack


@jit
def jit_exp(x: float) -> float:
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


def py_exp(x: float) -> float:
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


@numba.jit(nopython=True)
def numba_exp(x: float) -> float:
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
    arg = 250
    print("Value:")
    print(f"exp({arg}) = {jit_exp(arg):.30f}")
    print(f"exp({arg}) = {py_exp(arg):.30f}")
    print(f"exp({arg}) = {numba_exp(arg):.30f}")
    print("Speed:")
    print("@jit\t\t", max(repeat(lambda: jit_exp(arg), number=10000)))
    print("@numba.jit\t", max(repeat(lambda: numba_exp(arg), number=10000)))
    print("pure python\t", max(repeat(lambda: py_exp(arg), number=10000)))

