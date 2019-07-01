abcmath.c : clean randmath
	./randmath

randmath : randmath.c
	gcc -o randmath randmath.c

clean:
	rm -f randmath abcmath.c
