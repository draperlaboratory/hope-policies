#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "database.h"
#include "auth.h"
#include "user.h"
#include "test.h"
#include "test_status.h"

void
TestPasswordLeak(void)
{
  user_t *user;

  user = UserCreate("user", "password123", "User", "One", "123 Main St.");
  if(user == NULL) {
    t_printf("Failed to create user\n");
    return;
  }

  // leak will fail with password policy
  t_printf("User password: %s\n", user->password);
}

int test_main()
{
  test_negative();
  test_begin();
  
  TestPasswordLeak();

  return test_done();
}
