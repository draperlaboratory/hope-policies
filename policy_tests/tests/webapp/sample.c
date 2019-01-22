#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "sample.h"
#include "database.h"
#include "auth.h"
#include "medical.h"
#include "cgi-util.h"

bool
SampleConfiguration()
{
  user_t *patient_user1;
  user_t *patient_user2;
  user_t *doctor_user;
  medical_record_t *record;
  char *patient_first_name = "John";
  char *patient_last_name = "Doe";

  if(DatabaseInit() == false) {
    return false;
  }

  if(AuthInit() == false) {
    return false;
  }

  patient_user1 = UserCreate("user1", "password1", patient_first_name, patient_last_name, "123 Main St.");
  if(patient_user1 == NULL) {
    return false;
  }
  if(MedicalSetPatient(patient_user1) == false) {
    return false;
  }

  patient_user2 = UserCreate("user2", "password2", "Foo", "Bar", "456 Second St.");
  if(patient_user2 == NULL) {
    return false;
  }
  if(MedicalSetPatient(patient_user2) == false) {
    return false;
  }

  doctor_user = UserCreate("the_doctor", "root", "Doctor", "User", "789 Third St.");
  if(doctor_user == NULL) {
    return NULL;
  }
  if(MedicalSetDoctor(doctor_user) == false) {
    return false;
  }

  if(DatabaseAddUser(patient_user1) == false) {
    return false;
  }

  if(DatabaseAddUser(patient_user2) == false) {
    return false;
  }

  if(DatabaseAddUser(doctor_user) == false) {
    return false;
  }

  if(AuthStartSession("the_doctor", "root", NULL) != AUTH_SUCCESS) {
    return false;
  }

  if(MedicalAddCert(doctor_user, "Wrist sprain", 2019) != MEDICAL_SUCCESS) {
    return false;
  }

  if(MedicalAddRecord(doctor_user, patient_user1,
                      "Wrist sprain", "Take medication twice daily")
     != MEDICAL_SUCCESS) {
    return false;
  }

  record = &((patient_t *)patient_user1->data)->records[0];
  if(MedicalAddTreatment(doctor_user, record, "Ibuprofen", 200, "mg")
     != MEDICAL_SUCCESS) {
    return false;
  }

  return true;
}
