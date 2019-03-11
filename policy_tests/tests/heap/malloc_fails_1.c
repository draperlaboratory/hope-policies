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
#include "test.h"

// include malloc wrappers
#include "mem.h"

volatile int ALERT;

int bleh(int stackvar) {
  printf("stackvar addr = 0x%x\n", &stackvar);
}

/*
 * Test to allocate memory and check that we can 
 * catch out of bounds accesses.
 */
int test_main(void)
  {
    uintptr_t *ptr, *write_ptr, *read_ptr;
    volatile uintptr_t dummy;

    int stackvar = 9;

    bleh(stackvar);
    printf("stackvar = 0x%x\n", &stackvar);
    
    printf("addr of read_ptr = 0x%x\n", &read_ptr);
    
    test_negative(); // identify test as negative (should not complete)

    ptr = malloc(8 * sizeof(uintptr_t));
    ALERT = 3;
    write_ptr = ptr;

    printf("malloced ptr = 0x%x\n", ptr);
    
    for(int i =0; i < 8;i++){
      *write_ptr = i;
      write_ptr++;
    }

    ALERT = 2;
    read_ptr = ptr -1;

    test_begin();

    ALERT = 1;
    
    dummy = *read_ptr;  // this should fail

    // None of the following code should execute

    test_error("test_malloc_fails1: Error this should not execute\n");  

    free(ptr);

    return test_done();
  }

