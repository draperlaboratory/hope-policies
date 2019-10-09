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

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

#include "test_status.h"

// include malloc wrappers
#include "mem.h"

/*
 * Test that printf works ok on a few different format params.
 */
int test_main(void)
  {
    uintptr_t *ptr, *write_ptr, *read_ptr;

    test_positive(); // identify test as positive (will complete)

    test_begin();

    // do some random work for no good reason
    ptr = malloc(4 * sizeof(uintptr_t));
    write_ptr = ptr;
    for(int i =0; i < 4;i++){
      *write_ptr = i;
      write_ptr++;
    }	
    read_ptr = ptr;

    // this is the actual test

    t_printf("test_printf_works1: print         int ptr @ %ld = %ld\n", read_ptr, *read_ptr );
    read_ptr++;
    t_printf("test_printf_works1: print         hex ptr @ %lx = %ld\n", read_ptr, *read_ptr );
    read_ptr++;
    t_printf("test_printf_works1: print         oct ptr @ %lo = %ld\n", read_ptr, *read_ptr );
    read_ptr++;
    t_printf("test_printf_works1: print     pointer ptr @ %p = %ld\n", read_ptr, *read_ptr );
    
    free(ptr);

    return test_done();
  }

