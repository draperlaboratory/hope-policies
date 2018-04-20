#include <stdarg.h>
#include <stdio.h>

/*
 * Test wrapper for dover-os that calls the test case in test.c
 */
extern int test_main(void);

int main(void)
  {
    return test_main();
  }

/*
 * Provides wrapper for printf for all test output
 */
int t_printf(const char *fmt, ...){
  va_list args;

  va_start(args, fmt);
  printf(fmt, args);
  va_end(args);
}  
