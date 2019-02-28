#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "user.h"
#include "medical.h"
#include "test.h"
#include "test_status.h"

void
TestPrivilegeEscalation(void)
{
  user_t *user;

  user = UserCreate("user", "toor", "User", "Two", "123 Main St.");
  MedicalSetPatient(user);
  if(user == NULL) {
    t_printf("Failed to create user\n");
  }

  // illegal attempt tp escalate privilege
  t_printf("trying to set user to doctor\n");
  MedicalSetDoctor(user);
  t_printf("success\n");
}

int test_main() {
  test_negative();
  test_begin();

  TestPrivilegeEscalation();

  return test_done();
}
