extern "C" bool func(bool x, bool y) {
    bool a = true;
    bool b = false;
    bool c = (!b);
    if (x && y) {
        return true;
    }
    else {
        return false;
    }
}
