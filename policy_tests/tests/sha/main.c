/* NIST Secure Hash Algorithm */

#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "sha.h"
#include "input.h"

#include "test_status.h"
#include "test.h"

int test_main()
{
  SHA_INFO sha_info;

  test_positive();
  test_begin();
  test_start_timer();

  sha_stream(&sha_info, inputString);
  sha_print(&sha_info);
  
  test_print_total_time();
  return test_done();
}
