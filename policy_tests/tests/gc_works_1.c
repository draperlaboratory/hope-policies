/*
 * Copyright © 2017-2018 The Charles Stark Draper Laboratory, Inc. and/or Dover
 * Microsystems, Inc. All rights reserved.
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

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "test.h"
#include "test_status.h"

// include malloc wrappers
#include "mem.h"

// FreeRTOS stuff
#include "FreeRTOS.h"
#include "task.h"

volatile void *old_ptr = NULL;
volatile void *ptr;

static void mutator_task(void *p) {
  (void)p;

  t_printf("Address of old_ptr is %p\n", &old_ptr);
  t_printf("Address of ptr is %p\n", &ptr);

  for (int i = 0;; i++) {
    for (int allocs = 0; allocs < 5; allocs++) {
      ptr = malloc(12);

      // if (old_ptr != NULL) {
      //   t_printf("TRYING TO ACCESS STUFF!! %d\n", ((uint32_t *)old_ptr)[0]);
      //   t_printf("THIS SHOULD NOT HAVE BEEN PRINTED!!!\n");
      // }

      free(ptr);
      old_ptr = ptr;
    }

    if (i == 2) {
      t_printf("DONE!!\n");
      test_done();
    }

    vTaskDelay(3);
  }
}

static void collector_task(void *p) {
  (void)p;

  for (int i = 0;; i++) {
    t_printf("Collecting\n");

    vTaskDelay(2);
  }
}

int test_main(void) {
  test_positive(); // identify test as positive (will complete)
  test_begin();

  t_printf("GC Test\n");

  xTaskCreate(mutator_task, "Mutator", 1000, NULL, 1, NULL);
  xTaskCreate(collector_task, "Collector", 1000, NULL, 1, NULL);

  TickType_t last_wake_time;
  last_wake_time = xTaskGetTickCount();
  for (;;) {
    vTaskDelayUntil(&last_wake_time, 2);
  }
}
