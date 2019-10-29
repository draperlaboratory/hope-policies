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
#include <FreeRTOS.h>
#include <task.h>

#include "test_status.h"
#include "test.h"


int adone, bdone;

void procA_main(void *arg) {

  int a, i, j;
  a=0;
  int adder='a';
  int adder2='c';

  for ( j = 0; j < 4; j++ ) { 
    t_printf("Proc A in loop\n");

    for ( i = 0; i < 2; i++ )
      adder = adder + j;
      int temp = i + adder2;
      a += temp;
    
    vTaskDelay(0);
  }

}

void procB_main(void *a) {

  int b, i, j;
  b=0;
  int adder='b';
  int adder2='d';

  for ( j = 0; j < 4; j++ ) {
    t_printf("Proc B in loop\n");
    
    for ( i = 0; i < 2; i++ )
      b += j + i + adder + adder2;
    
    vTaskDelay(0);
  }

  bdone = 1;
}

/*
 * Hello world sanity test to check we can execute code i.e. main and 
 *     call printf
 */
int test_main(void)
  {

    int i;
    
    test_positive(); // identify test as positive (will complete)

    t_printf("hello doing context test\n");
    
    xTaskCreate(procB_main, "procB", 1000, NULL, 1, NULL);

    t_printf("before scheduler invokation\n");
    
    procA_main(0x0);

    t_printf("after scheduler invokation\n");

    t_printf("Hello Test\n");
    
    test_pass();
    
    return test_done();
  }


