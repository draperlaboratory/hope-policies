/*
 * Copyright © 2017-2018 The Charles Stark Draper Laboratory, Inc. and/or Dover Microsystems, Inc.
 * All rights reserved. 
 *
 * Use and disclosure subject to the following license. 
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 * 
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

#include "test_status.h"

// include malloc wrappers
#include "mem.h"

#define MALLOC_COUNT 256
/*
 * Performance profiling test case, multiple calls to malloc / free
 *
 */
int test_main(void)
  {
    uintptr_t* ptr;
    uintptr_t *write_ptr, *read_ptr;
    uintptr_t size = 1;

    test_positive(); // identify test as positive (will complete)

    for(int count = MALLOC_COUNT; count > 1; count = count >> 1){
      for(int j = 0; j < count; j++){

	//t_printf("test_malloc_prof_1: malloc # %d\n", count); 

	ptr = malloc(size * sizeof(uintptr_t));

	write_ptr = ptr;

	for(int i = 0; i < size;i++){
	  *write_ptr = size * j + i;
	  write_ptr++;
	}
	
	read_ptr = ptr;
	
	for(int i = 0; i < size;i++){
	  if(*read_ptr != size * j + i) {
	    test_error("test_malloc_prof_1: Error -> ptr[%d] = %ld\n", i, *read_ptr);
	  }
	  read_ptr++;
	}

      free(ptr);
      }
      size = size << 1;
    }

    /*
    ptr = (uintptr_t*) main;
    ptr[0] = 0;

    int foo = 42;
    void (*foo_fn_ptr)()= NULL;
    foo_fn_ptr = (void (*)()) &foo;
    foo_fn_ptr();

    ptr = malloc(8);
    ptr[20] = 0;
    */
    test_pass();
    return test_done();
  }

