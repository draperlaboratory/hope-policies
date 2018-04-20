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

typedef struct element {
  struct element *last;
  struct element *next;
} element_t;

/*
 * Link list traversal test to verify ptrs to structure of ptrs works correctly 
 *     with the Heap policy
 */
int test_main(void)
  {
    element_t* ptr[8];
    element_t *next_ptr, *last_ptr;
    int index;

    test_positive(); // identify test as positive (will complete)

    for(int j =0; j < 8; j++)
      ptr[j] = malloc(sizeof(element_t));

    last_ptr = ptr[6];
    next_ptr = 0;
    ptr[7]->last = last_ptr;
    ptr[7]->next = next_ptr;
      
    last_ptr = 0;
    next_ptr = ptr[1];
    ptr[0]->last = last_ptr;
    ptr[0]->next = next_ptr;
      
    for(int i = 1; i < 7;i++){
      ptr[i]->last = ptr[i-1];
      ptr[i]->next = ptr[i+1];

      }

    test_begin();

    // traverse forward
    next_ptr = ptr[0];
    index =0;
    while(next_ptr != 0) {
	if(next_ptr != ptr[index]) {
	  test_error("test_link_list_works: Error -> ptr[%d]: %ld != %ld\n", index, *next_ptr, ptr[index] );
	}
	next_ptr = next_ptr->next;
	index++;
      }

    if(index != 8) {
      test_error("test_link_list_works: Error premature list end, index = %d\n", index);
    }
    
    //traverse backward
    next_ptr = ptr[7];
    index = 7;
    while(next_ptr != 0) {
      if(next_ptr != ptr[index]) {
	test_error("test_link_list_works: Error -> ptr[%d]: %ld != %ld\n", index, *next_ptr, ptr[index] );
      }
      next_ptr = next_ptr->last;
      index--;
    }
    
    if(index != -1) {
      test_error("test_link_list_works: Error premature list end, index = %d\n", index);
    }
    
    for(int j =0; j < 8; j++)
      free(ptr[j]);

    return test_done();

  }

