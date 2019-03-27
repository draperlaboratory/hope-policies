#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include "database.h"
#include "auth.h"
#include "user.h"
#include "medical.h"
#include "test.h"
#include "test_status.h"

void TestAdminModifyRecord(void)
{
  user_t *user;
  user_t *admin_user;
  patient_t *patient_data;

  user = UserCreate("patient_user", "password123", "Pat", "Ient", "123 Main St.");
  if(user == NULL) {
    t_printf("Failed to create user\n");
    return;
  }                                                                         

  admin_user = UserCreate("admin_user", "password123", "Pat", "Ient", "123 Main St.");
  if(admin_user == NULL) {
    t_printf("Failed to create user\n");
    return;
  }

  MedicalSetPatient(user);
  UserSetAdmin(admin_user);

  AuthSetCurrentUserType(admin_user);
  
  patient_data = MedicalGetPatient(user);
  
  // should not fail, since admin is active
  patient_data->record_count = 42;
}

int test_main()
{
  test_positive();
  test_begin();

  TestAdminModifyRecord();

  return test_done();
}
