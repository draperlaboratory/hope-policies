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

/*
 * Test to allocate multiple memory chunks and check that we can read and write it ok.
 */
int test_main(void)
  {
    uintptr_t* ptr[8];
    uintptr_t *write_ptr, *read_ptr;

    test_positive(); // identify test as positive (will complete)

    for(int j = 0; j < 8; j++){
      ptr[j] = malloc((j+1) * sizeof(uintptr_t));

      write_ptr = ptr[j];

      for(int i = 0; i < (j+1);i++){
	*write_ptr = 10 * j + i;
	write_ptr++;
      }
      
      read_ptr = ptr[j];

      for(int i = 0; i < (j+1);i++){
      	if(*read_ptr != 10 * j + i) {
	  test_error("test_malloc_works2: Error -> ptr[%d] = %ld\n", i, *read_ptr);
	}
	read_ptr++;
	}
    }

    for(int j =0; j < 8; j++){
      free(ptr[j]);
    }

    test_pass();
    return test_done();
  }

