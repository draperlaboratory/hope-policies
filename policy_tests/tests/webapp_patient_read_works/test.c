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

void TestPatientRead(void)
{
  user_t *patient_user1;
  user_t *patient_user2;
  user_t *doctor_user;
  patient_t *patient_data;

  patient_user1 = UserCreate("patient_user1", "password123", "Pat", "Ient", "123 Main St.");
  if(patient_user1 == NULL) {
    t_printf("Failed to create user\n");
    return;
  }

  patient_user2 = UserCreate("patient_user2", "password123", "Pat", "Ient", "123 Main St.");
  if(patient_user2 == NULL) {
    t_printf("Failed to create user\n");
    return;
  }

  doctor_user = UserCreate("doctor_user", "password123", "Pat", "Ient", "123 Main St.");
  if(doctor_user == NULL) {
    t_printf("Failed to create user\n");
    return;
  }

  MedicalSetPatient(patient_user1);
  MedicalSetPatient(patient_user2);
  MedicalSetDoctor(doctor_user);

  AuthSetCurrentUserType(doctor_user);
  MedicalAddRecord(doctor_user, patient_user1, "Sample Condition", "sample notes");

  AuthSetCurrentUserType(patient_user2);
  
  patient_data = MedicalGetPatient(patient_user2);

  // PPAC policy should not violate since patient 2 is the active user
  t_printf("Patient User 2 has %lu records\n", patient_data->record_count);
}

int test_main()
{
  test_positive();
  test_begin();

  TestPatientRead();
  return test_done();
}
