#include <stdio.h>
#include <stdarg.h>
#include "test.h"
#include "platform.h"

uint32_t uiPortGetWallTimestampUs() {
  return (uint32_t)get_timer_value();
}

int t_printf(const char *s, ...) {
  char buf[128];
  va_list vl;

  const char *p = &buf[0];

  va_start(vl, s);
  vsnprintf(buf, sizeof buf, s, vl);
  va_end(vl);

  puts(p);
}

int main(void) {
  test_main();
}
