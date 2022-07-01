from annotation import jit
from timeit import timeit, repeat
from json import dumps

results = {}


def pypy_sum(x: int, y: int) -> int:
    res: int = x + y
    return res


pypy_exec_time = repeat(lambda: pypy_sum(2, 2), repeat=10, number=1000000)
print(pypy_exec_time)
xs = range(1, 11)
results["sum"] = [list(xs), pypy_exec_time]


def pypy_exp(x: float) -> float:
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


arg = 250
print(f"exp({arg}) = {pypy_exp(arg):.30f}")
args = range(10, 260, 10)
pypy_exp_time = []
for arg in args:
    pypy_exp_time.append(timeit(lambda: pypy_exp(arg), number=10000))
print(pypy_exp_time)


results["exp"] = [list(args), pypy_exp_time]


def pypy_hash(x: int) -> int:
    x = ((x >> 16) ^ x) * 0x45d9f3b
    x = ((x >> 16) ^ x) * 0x45d9f3b
    x = (x >> 16) ^ x
    return x


pypy_hash_time = repeat(lambda: pypy_hash(42), repeat=10, number=1000000)
print(pypy_hash_time)


xs = range(1, 11)
results["hash"] = [list(xs), pypy_hash_time]


def pypy_fib(n: int) -> int:
    if n < 2:
        return 1
    return pypy_fib(n - 1) + pypy_fib(n - 2)

arg = 30
print(f"fib({arg}) = {pypy_fib(arg)}")
args = range(1, 31)
pypy_fib_time = []
for arg in args:
    pypy_fib_time.append(timeit(lambda: pypy_fib(arg), number=10))
print(pypy_fib_time)

results["fib"] = [list(args), pypy_fib_time]

with open("pypy_performance.json", "w", encoding="utf-8") as outfile:
    outfile.write(dumps(results, indent=2))


print(dumps(results, indent=2))
