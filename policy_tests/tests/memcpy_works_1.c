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
#include <string.h>

#include "test_status.h"


/*
 * Test to check that lib Fn memcpy works correctly
 * 
 */
int test_main(void)
  {
    uintptr_t *ptr1, *ptr2;
    char *one_ptr, *two_ptr;

    test_positive(); // identify test as positive (will complete)
    test_begin();

    for(int length = 1; length <= 26; length++) {

      ptr1 = malloc(length * sizeof(char));
      ptr2 = malloc(length * sizeof(char));
      
      one_ptr = (char*) ptr1;
      for(int i =0; i < length;i++){
	*one_ptr = 'a' + i;
	one_ptr++;
      }
      
      one_ptr = (char*) ptr1;
      two_ptr = (char*) ptr2;
      
      memcpy(two_ptr, one_ptr, length);
      
      two_ptr = (char*) ptr2;
      
      
      for(int i =0; i < length;i++){
	if(*two_ptr != 'a' + i) {
	  test_error("test_memcpy_works2: Error -> ptr[%d] = %ld\n", i, *two_ptr );
	}
	two_ptr++;
      }
      
      free(ptr1);
      free(ptr2);
      
    }
    
    return test_done();
  }

