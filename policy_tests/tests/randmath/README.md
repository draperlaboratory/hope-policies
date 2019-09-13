# Randmath Test

This test was adapted from the Galois MiBench benchmark suite.
The `randmath.c` program generates the `abcmath.c` program using a sequence of
pseudorandom operations. The `abcmath.c` program is then used for benchmarking.

# Makefiles

* abcmath.mk

Used to generate `abcmath.c`. Do `make` to generate the file, and
`make clean` to remove the file along with `randmath` executable.

* common.mk
* Makefile.frtos
* Makefile.bare

Used to interact with the test framework and run the benchmark test.
