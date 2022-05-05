int main() {
	int i = 1;
	int x = 42;
	while (i < 1000) {
		x = ((x + 80) / 2);
		x = ((x - 34) * 7);
		x = (x % 103);
		x = ((x << 2) & 843);
		x = ((x | 55) >> 3);
		x = ((x * x) - x);
		x = (x % 68);
		i = (i + 1);
	}
	int y = x;
	return y;
}
