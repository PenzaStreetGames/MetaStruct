from annotation import jit


@jit
def func(x: int) -> int:
    x = x + 0
    x = 0 + x
    x = x + x
    x = x
    return x


if __name__ == '__main__':
    print(func(4))
