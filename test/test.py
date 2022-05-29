from annotation import jit

@jit
def func(x: bool, y: bool) -> bool:
    a: bool = True
    b: bool = False
    c: bool = not b
    if x and y:
        return True
    else:
        return False


if __name__ == '__main__':
    print(func(False, False))
    print(func(False, True))
    print(func(True, False))
    print(func(True, True))
