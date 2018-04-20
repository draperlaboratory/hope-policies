/*
 * Copyright © 2017-2018 Dover Microsystems, Inc.
 * All rights reserved. 
 *
 * Use and disclosure subject to license. 
 */


#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

#include "test_status.h"
#include "test.h"

// include malloc wrappers
#include "mem.h"

/* Kernel includes. */
#include "FreeRTOS.h"
#include "task.h"
#include "timers.h"
#include "queue.h"
#include "utils.h"

#define TICK_INTERVAL 2
#define MSG_MAX 4
#define TIMER_INTERVAL (TICK_INTERVAL * configTICK_CLOCK_HZ / configTICK_RATE_HZ)

#define PREEMPTIVE

extern uint64_t xPortRawTime( void );

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
            uint64_t raw = xPortRawTime();
            uint32_t low = (uint32_t)(raw & 0xFFFFFFFF);
            uint32_t high = ((uint32_t)(raw >> 32)) & 0xFFFFFFFF;
            printf_uart("Check if done: %x %x\r\n", high, low);
        }
#ifdef PREEMPTIVE  
        vTaskDelayUntil(&last_wake_time, TICK_INTERVAL);
#else
        taskYIELD();
#endif
    }
}


static void hello_task(void *p) {
  TickType_t last_wake_time;
  
  (void)p;
  last_wake_time = xTaskGetTickCount();
  while (1) {
      printf_uart("wake hello\r\n");
      if(pong == false){
          uint64_t raw = xPortRawTime();
          uint32_t low = (uint32_t)(raw & 0xFFFFFFFF);
          uint32_t high = ((uint32_t)(raw >> 32)) & 0xFFFFFFFF;
          printf_uart("hello %x %x\r\n", high, low);
          pong = true;
      }
#ifdef PREEMPTIVE  
      vTaskDelayUntil(&last_wake_time, TICK_INTERVAL);
#else
      taskYIELD();
#endif
  }
}

static void world_task(void *p) {
  TickType_t last_wake_time;
  
  (void)p;

  last_wake_time = xTaskGetTickCount();
  while (1) {
      printf_uart("wake world\r\n");
      if(pong == true){
          uint64_t raw = xPortRawTime();
          uint32_t low = (uint32_t)(raw & 0xFFFFFFFF);
          uint32_t high = ((uint32_t)(raw >> 32)) & 0xFFFFFFFF;
          printf_uart("world %x %x\r\n", high, low);
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

  /* no need to init uart */
  printf_uart("main: create hello task\r\n");
  xTaskCreate(hello_task, "Hello task", 1000, NULL, 1, NULL);
  printf_uart("main: create world task\r\n");
  xTaskCreate(world_task, "World task", 1000, NULL, 1, NULL);

  printf_uart("main: create done task\r\n");
  xTaskCreate(done_task, "Done task", 1000, NULL, 1, NULL);

  printf_uart("timer ticks: 0x%x\r\n", TIMER_INTERVAL);

  printf_uart("start scheduler\r\n");
  vTaskStartScheduler();
  
  // scheduler shouldn't get here unless a task calls xTaskEndScheduler()
  for (;;){
      for(volatile int i=0;i<10000;i++);
      uint64_t raw = xPortRawTime();
      uint32_t low = (uint32_t)(raw & 0xFFFFFFFF);
      uint32_t high = ((uint32_t)(raw >> 32)) & 0xFFFFFFFF;
      printf_uart("timer: %x %x\r\n", high, low);

  }
}

