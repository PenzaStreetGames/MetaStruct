# MetaStruct

JIT-ускоритель программ на языке Python

## Алгоритм

1. Программа переводится в абстрактное синтаксическое дерево (АСТ) с помощью модуля питона `ast`
2. По дереву строится текст программы на языке C++
3. Программа на C++ компилируется в динамическую библиотеку .dll
4. DLL-библиотека загружается в Python с помощью модуля `ctypes`
5. С помощью аннотации `@jit` функция на языке Python заменяется её скомпилированным вариантом


## Требования к программам

* Python версии 3.9 и выше
* Компилятор `g++`

Также желательно, чтобы скрипт в папке исполнения имел права на чтение и запись файлов, либо был запущен от
имени администратора.

## Пример

Допустим, есть алгоритм, вычисляющий значение функции в точке, при известной производной и разложении 
в ряд Тейлора. Для примера возьмём функцию экспоненты.

```python
from annotation import jit

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
```

Переменные, аргументы и возвращаемый тип должны быть указаны с использованием 
[аннотаций типов](https://docs.python.org/3/library/typing.html) для однозначной компиляции.

В примере выше выполняется вычисление производной по формуле:
$$e^x = \displaystyle\sum_{n=0}^\infty \frac{x^n}{n!}$$

Переменная `threshold` задаёт предельную точность вычисления, равную тридцати знакам после запятой. При
различных по абсолютной величине значениях функций точность может отличаться. При достижении предела точности
или машинного нуля в `delta` суммирование прекращается.

Следует отметить, что в алгоритме суммирование происходит от самого маленького члена к самому большому
(справа налево), что позволяет не терять точность при сложении больших чисел с маленькими.

Показанная выше функция будет преобразована к такому эквиваленту на языке C++:

```cpp
extern "C" double jit_exp(double x) {
    double res = 0;
    double threshold = 1e-30;
    double delta = 1;
    int elements = 0;
    while ((delta > threshold)) {
        elements = (elements + 1);
        delta = ((delta * x) / elements);
    }
    while ((elements >= 0)) {
        res += delta;
        delta = ((delta * elements) / x);
        elements -= 1;
    }
    return res;
}
```

Избыточность некоторых скобок объясняется автогенерацией кода.

## Замеры скорости выполнения

Для сравнения напишем такую же функцию расчёта экспоненты написанную на Python, и её же, но с использованием
jit-ускорения из библиотеки [numba](https://numba.pydata.org/)

```python
import numba


def py_exp(x: float) -> float:
    ...


@numba.jit(nopython=True)
def numba_exp(x: float) -> float:
    ...
```

Выполним замер скорости вычисления $e^250$

```python
from timeit import repeat

arg = 250
print("Value:")
print(f"exp({arg}) = {jit_exp(arg):.30f}")
print(f"exp({arg}) = {py_exp(arg):.30f}")
print(f"exp({arg}) = {numba_exp(arg):.30f}")
print("Speed:")
print("@jit\t\t", max(repeat(lambda: jit_exp(arg), number=10000)))
print("@numba.jit\t", max(repeat(lambda: numba_exp(arg), number=10000)))
print("pure python\t", max(repeat(lambda: py_exp(arg), number=10000)))
```

Результаты могут быть примерно такими:
```
Value:
exp(250) = 3746454614502660877998657881484689260451454624001099543290316630153610787704025897267034669677141296546840576.000000000000000000000000000000
exp(250) = 3746454614502660877998657881484689260451454624001099543290316630153610787704025897267034669677141296546840576.000000000000000000000000000000
exp(250) = 3746454614502660877998657881484689260451454624001099543290316630153610787704025897267034669677141296546840576.000000000000000000000000000000
Speed:
@jit		 0.08759210000000006
@numba.jit	 0.05849660000000001
pure python	 1.2867625000000003
```

По вычисленным значениям можно сказать, что разница в реализации не отразилась на точности.

При этом на скорости выполнения реализация как раз отразилась. 

Реализация с аннотацией `@jit` выполнилась
в 15 раз быстрее версии, написанной на питоне без оптимизации. 

Реализация с аннотацией `@numba.jit`
выполнилась в 1,5 раза быстрее представленной в этом проекте реализации, что, в принципе, сопоставимо. 


## Ограничения по синтаксису

* Все переменные должны быть аннотированы согласно своему типу
* Все функции в своей сигнатуре должны быть аннотированы согласно типам аргументов и возвращаемого значения
* Поддержка строк и булевых переменных не реализована
* Коллекции данных пока что не поддерживаются
* Желательна реализация ускоряемого кода в виде одной функции

## Перспективы
* Поддержка строк и булевых значений в качестве входных и выходных параметров `str`, `bool`
* Поддержка стандартного ввода-вывода `print()` и `input()`
* Поддержка простых коллекций, таких как `list`, `map`, `set`
* Поддержка работы с объектами Python `object`