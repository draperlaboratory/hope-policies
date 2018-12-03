PYTHON ?= python3

build/main: 
	cd build && make

clean:
	rm -rf *.o build/main build/*.log
