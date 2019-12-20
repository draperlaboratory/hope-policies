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

#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

#include "test_status.h"
#include "test.h"


/* Kernel includes. */
#include "FreeRTOS.h"
#include "task.h"
#include "timers.h"
#include "queue.h"

/*
 * Ping Pong tests makes sure that task switching works
 */

#define TICK_INTERVAL 2
#define MSG_MAX 6
#define TIMER_INTERVAL (TICK_INTERVAL * configCPU_CLOCK_HZ / configTICK_RATE_HZ)

#define PREEMPTIVE

uint64_t xPortRawTime(void) {
  return get_timer_value();
}

bool pong;
int msg_count = 0;

static void done_task(void *p) {
  TickType_t last_wake_time;
  
  (void)p;
  last_wake_time = xTaskGetTickCount();
  vTaskDelayUntil(&last_wake_time, TICK_INTERVAL);

    while (1) {
        if(msg_count > MSG_MAX){
            test_done();
        }
        else {
            t_printf("Check if done: %d < %d\r\n",msg_count, MSG_MAX);
        }
#ifdef PREEMPTIVE  
        vTaskDelayUntil(&last_wake_time, TICK_INTERVAL);
#else
        taskYIELD();
#endif
    }
}


static void ping_task(void *p) {
  TickType_t last_wake_time;
  
  (void)p;
  last_wake_time = xTaskGetTickCount();
  while (1) {
      if(pong == false){
          uint64_t raw = xPortRawTime();
          uint32_t low = (uint32_t)(raw & 0xFFFFFFFF);
          uint32_t high = ((uint32_t)(raw >> 32)) & 0xFFFFFFFF;
          t_printf("ping %x %x\r\n", high, low);
          pong = true;
      }
#ifdef PREEMPTIVE  
      vTaskDelayUntil(&last_wake_time, TICK_INTERVAL);
#else
      taskYIELD();
#endif
  }
}

static void pong_task(void *p) {
  TickType_t last_wake_time;
  
  (void)p;

  last_wake_time = xTaskGetTickCount();
  while (1) {
      if(pong == true){
          uint64_t raw = xPortRawTime();
          uint32_t low = (uint32_t)(raw & 0xFFFFFFFF);
          uint32_t high = ((uint32_t)(raw >> 32)) & 0xFFFFFFFF;
          t_printf("pong %x %x\r\n", high, low);
          pong = false;
          msg_count++;
      }
#ifdef PREEMPTIVE  
      vTaskDelayUntil(&last_wake_time, TICK_INTERVAL);
#else
      taskYIELD();
#endif
  }
}


int test_main( void )
{
    test_positive(); // identify test as positive (will complete)
    test_begin();
    
  /* no need to init uart */
  t_printf("main: create ping task\r\n");
  xTaskCreate(ping_task, "Ping task", 1000, NULL, 1, NULL);
  t_printf("main: create pong task\r\n");
  xTaskCreate(pong_task, "Pong task", 1000, NULL, 1, NULL);

  t_printf("main: create done task\r\n");
  xTaskCreate(done_task, "Done task", 1000, NULL, 1, NULL);

  t_printf("timer ticks: 0x%x\r\n", TIMER_INTERVAL);

  // scheduler is already running so just wait
  TickType_t last_wake_time;
  
  last_wake_time = xTaskGetTickCount();
  for (;;){
#ifdef PREEMPTIVE  
      vTaskDelayUntil(&last_wake_time, TICK_INTERVAL);
#else
      taskYIELD();
#endif
  }
}

