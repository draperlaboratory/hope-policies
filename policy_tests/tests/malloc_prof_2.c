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

// total number of mallocs
#define MALLOC_COUNT 2000
// amount of computation on the malloced values
#define TEST_LENGTH_COUNT 7500

// number of times to run the sort test
#define ITERATIONS      2


/*
 * Performance profiling test case, multiple calls to malloc / free
 *
 */
int isp_main(void){
    uintptr_t *ptr[MALLOC_COUNT];
    uintptr_t size = 1;
    uintptr_t index;

    test_positive(); // identify test as positive (will complete)
   
    for(int i= 0; i < ITERATIONS;i++){
 
      t_printf("allocate\n");
      for(int count = 0; count < MALLOC_COUNT; count++){
        size = (count & 0x07) +1;
        ptr[count] = malloc(size * sizeof(uintptr_t));
      } 
      
      t_printf("test\n");
      for(int j = 0; j < TEST_LENGTH_COUNT;j++){
        index = rand() % MALLOC_COUNT; // rand
        ptr[index][0]++;
      }
      
      
      t_printf("free\n");
      for(int count = 0; count < MALLOC_COUNT; count++){
        free(ptr[count]);
      }
      
    }

    // code to force violations
    /*
    uintptr_t *ptrx = (uintptr_t*) main;
    ptrx[0] = 0;

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

