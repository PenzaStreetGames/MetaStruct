extern "C" double exp(double x) {
    double res = 0;
    double threshold = 1e-20;
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