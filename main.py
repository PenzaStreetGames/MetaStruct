from annotation import jit
from timeit import timeit, repeat
import numba


def get_jit_numba_realisations(func):
    jit_func = jit(func)
    numba_func = numba.jit(func)
    return jit_func, numba_func


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


jit_exp, numba_exp = get_jit_numba_realisations(py_exp)



@jit
def jit_f(n: int) -> int:
    if n < 2:
        return 1
    return jit_f(n - 1) + jit_f(n - 2)


@numba.jit
def numba_f(n: int) -> int:
    if n < 2:
        return 1
    return numba_f(n - 1) + numba_f(n - 2)


def f(n: int) -> int:
    if n < 2:
        return 1
    return f(n - 1) + f(n - 2)


def py_hash(x: int) -> int:
    x = ((x >> 16) ^ x) * 0x45d9f3b
    x = ((x >> 16) ^ x) * 0x45d9f3b
    x = (x >> 16) ^ x
    return x


jit_hash, numba_hash = get_jit_numba_realisations(py_hash)


@jit
def jit_hash(x: int) -> int:
    n: int = 0
    while n < 1000:
        x = ((x >> 16) ^ x) * 0x45d9f3b
        x = ((x >> 16) ^ x) * 0x45d9f3b
        x = (x >> 16) ^ x
        n += 1
    return x


def py_n_primary(n: int) -> int:
    count: int = 0
    number: int = 2
    while count < n:
        i: int = 2
        is_prime: bool = True
        while i < number:
            if number % i == 0:
                is_prime = False
                break
            i += 1
        if is_prime:
            count += 1
        number += 1
    return number - 1


jit_n_primary, numba_n_primary = get_jit_numba_realisations(py_n_primary)


if __name__ == '__main__':
    # arg = 35
    # print("@jit\t\t", max(repeat(lambda: f(arg), number=1)))
    # print("@numba.jit\t", max(repeat(lambda: numba_f(arg), number=1)))
    # print("pure python\t", max(repeat(lambda: f(arg), number=1)))

    # arg = 250
    # print("Value:")
    # print(f"exp({arg}) = {jit_exp(arg):.30f}")
    # print(f"exp({arg}) = {py_exp(arg):.30f}")
    # print(f"exp({arg}) = {numba_exp(arg):.30f}")
    # print("Speed:")
    # print("@jit\t\t", max(repeat(lambda: jit_exp(arg), number=10000)))
    # print("@numba.jit\t", max(repeat(lambda: numba_exp(arg), number=10000)))
    # print("pure python\t", max(repeat(lambda: py_exp(arg), number=10000)))

    # arg = 10
    # print("Value:")
    # print(f"exp({arg}) = {jit_hash(arg)}")
    # print(f"exp({arg}) = {py_hash(arg)}")
    # print(f"exp({arg}) = {numba_hash(arg)}")
    # print("Speed:")
    # print("@jit\t\t", max(repeat(lambda: jit_hash(arg), number=100000)))
    # print("@numba.jit\t", max(repeat(lambda: numba_hash(arg), number=100000)))
    # print("pure python\t", max(repeat(lambda: py_hash(arg), number=100000)))

    arg = 10000
    print("@jit\t\t", max(repeat(lambda: jit_n_primary(arg), number=1)))
    print("@numba.jit\t", max(repeat(lambda: numba_n_primary(arg), number=1)))
    print("pure python\t", max(repeat(lambda: py_n_primary(arg), number=1)))

