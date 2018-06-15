#include <stdio.h>
#include <stdarg.h>
#include "test.h"
#include "platform.h"

uint32_t uiPortGetWallTimestampUs() {
  return (uint32_t)get_timer_value();
}

int t_printf(const char *s, ...) {
  va_list vl;

  va_start(vl, s);
  printf(s, vl);
  va_end(vl);
}

int main(void) {
  test_main();
}
