#include <stdbool.h>
#include <stdint.h>
#include <stdarg.h>
#include "test_status.h"
#include <time.h>
#include <sys/time.h>
#include <sys/times.h>
#include "test.h"

#define log printf

/*
 * Test status functions
 */

static bool test_status_passing = false;
static bool test_status_positive = false;
static bool test_status_negative = false;

extern uint32_t uiPortGetWallTimestampUs();

// Identify positive case (test will end)
void test_positive(){
  test_status_positive = true;
  //  struct timeval tv;
  //  gettimeofday(&tv,NULL);
  //  uint32_t sec = tv.tv_sec;
  //  uint32_t usec = tv.tv_usec;
  t_printf("MSG: Positive test.\n");
  t_printf("Start time: %u\n", uiPortGetWallTimestampUs());
  // t_printf("Clock time: %d.%06d\n", sec, usec);
}

// Identify negative case (test will never end)
void test_negative(){
  test_status_negative = true;
  t_printf("MSG: Negative test.\n");
}

// Set passing status at start of test
void test_begin(){
  t_printf("MSG: Begin test.\n");
  test_status_passing = true;
}

// Set passing status
void test_pass(){
  test_status_passing = true;
}

// Set failing status
void test_fail(){
  test_status_passing = false;
}

// print the test status for a positive test case
int test_done(){
  if(test_status_passing && test_status_positive && !test_status_negative){
    //  struct timeval tv;
    //  gettimeofday(&tv,NULL);
    //  uint32_t sec = tv.tv_sec;
    //  uint32_t usec = tv.tv_usec;
  t_printf("PASS: test passed.\n");
  t_printf("End time: %u\n", uiPortGetWallTimestampUs());
  //  t_printf("Clock time: %d.%06d\n", sec, usec);
  t_printf("MSG: End test.\n");
  return 0;
  }
  else if(test_status_positive && test_status_negative) {
    t_printf("FAIL: error in test, can't be both positive and negative test.\n");
    t_printf("MSG: End test.\n");
    return 1;
  }
  else {
    t_printf("FAIL: test failed.\n");
    t_printf("MSG: End test.\n");
    return 1;
  }
}


// print the test status
void test_error(const char *fmt, ...){
  va_list args;

  va_start(args, fmt);
  t_printf(fmt, args);
  va_end(args);

  test_fail();
}







