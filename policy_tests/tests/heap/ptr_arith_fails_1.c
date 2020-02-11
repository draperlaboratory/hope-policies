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
#include "test.h"


/*
 * Test to check that a forged pointer to heap memory of the wrong color fails.
 */
int test_main(void)
  {
    uintptr_t *ptr1, *ptr2;
    volatile  uintptr_t *one_ptr, *two_ptr;
    uintptr_t temp1, temp2;
    intptr_t delta;
    volatile uintptr_t dummy;

    test_negative(); // identify test as negative (should not complete)

    // Allocate two blocks on heap
    ptr1 = malloc(8 * sizeof(uintptr_t));
    ptr2 = malloc(8 * sizeof(uintptr_t));

    one_ptr = ptr1;
    two_ptr= ptr2;
    
    // Sanity check by write and read data, this part should work
    for(int i =0; i < 8;i++){
      *one_ptr = i;
      *two_ptr = 2 * i;
      one_ptr++;
      two_ptr++;
    }
	
    one_ptr = ptr1;
    two_ptr= ptr2;

    // check reading with correctly colored ptrs works ok
    for(int i =0; i < 8;i++){
      if(*one_ptr != i) {
	test_error("test_ptr_arith_fails1: Error -> one_ptr[%d] = %ld\n", i, *one_ptr );
      }
      one_ptr++;
      if(*two_ptr != 2* i) {
	test_error("test_ptr_arith_fails1: Error -> two_ptr[%d] = %ld\n", i, *two_ptr );
      }
      two_ptr++;
    }

    // Done with the warmup now the actual test

    // Have to call priveledged function for test setup
    temp1 = (uintptr_t) dover_remove_tag(ptr1);
    temp2 = (uintptr_t) dover_remove_tag(ptr2);
    // compute an untagged offset between blocks
    delta = temp2 - temp1;
    
    // use untagged offset to forge pts with wrong color
    one_ptr = ptr2 - delta;
    two_ptr = ptr1 + delta;

    test_begin(); // everything should work up to here

    dummy = *one_ptr; // illegal to read via wrong pointer color

      // None of the following code should execute

    test_error("test_ptr-arith_fails1: Error this should not execute\n");  

    free(ptr1);
    free(ptr2);

    return test_done();
  }

