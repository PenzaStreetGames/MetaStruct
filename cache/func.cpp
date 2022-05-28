extern "C" double func(double x) {
    if ((x % 2) == 0) {
        x = 0;
    }
    else if ((x % 3) == 0) {
        x = 2;
    }
    else if ((x % 5) == 0) {
        x = 5;
    }
    else {
        x = 1;
    }
    double y = x;
    return y;
}
