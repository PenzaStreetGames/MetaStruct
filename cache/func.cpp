extern "C" int func(int x) {
    while ((x > 1 && x < 1000)) {
        x = (x * x);
    }
    int y = x;
    return y;
}
