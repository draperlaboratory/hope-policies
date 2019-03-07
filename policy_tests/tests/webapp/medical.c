#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#include "medical.h"
#include "test.h"
#include "mem.h"

bool
MedicalDoctorCertified(doctor_t *doctor, char *condition)
{
  size_t i;

  for(i = 0; i < doctor->cert_count; i++) {
    if(strcmp(doctor->certs[i].condition, condition) == 0) {
      return true;
    }
  }

  return false;
}

static void
MedicalRecordFree(medical_record_t *record)
{
  free(record->notes);
}

bool
MedicalSetPatient(user_t *user)
{
  UserSetType(user, USER_PATIENT);
  user->data = malloc(sizeof(patient_t));
  if(user->data == NULL) {
    return false;
  }

  ((patient_t *)user->data)->record_count = 0;
  return true;
}

patient_t *
MedicalGetPatient(user_t *user)
{
  if(user->type != USER_PATIENT) {
    return NULL;
  }
  
  return (patient_t *)user->data;
}

bool
MedicalSetDoctor(user_t *user)
{
  UserSetType(user, USER_DOCTOR);
  user->data = malloc(sizeof(doctor_t));
  if(user->data == NULL) {
    return false;
  }

  ((doctor_t *)user->data)->cert_count = 0;
  ((doctor_t *)user->data)->patient_count = 0;
  return true;
}

doctor_t *
MedicalGetDoctor(user_t *user)
{
  if(user->type != USER_DOCTOR) {
    return NULL;
  }
  
  return (doctor_t *)user->data;
}

medical_result_t
MedicalAddRecord(user_t *doctor_user, user_t *patient_user,
                 char *condition, char *notes)
{
  doctor_t *doctor;
  patient_t *patient;

  doctor = MedicalGetDoctor(doctor_user);
  patient = MedicalGetPatient(patient_user);

  if(patient == NULL || doctor == NULL) {
    return MEDICAL_INVALID_USER;
  }

  if(patient->record_count == MEDICAL_MAX_RECORDS) {
    return MEDICAL_FIELD_FULL;
  }

  snprintf(patient->records[patient->record_count].condition,
           MEDICAL_NAME_LENGTH, "%s", condition);

  patient->records[patient->record_count].doctor_user = doctor_user;

  patient->records[patient->record_count].notes = malloc(strlen(notes) + 1);
  snprintf(patient->records[patient->record_count].notes, strlen(notes), "%s", notes);

  if(patient->records[patient->record_count].notes == NULL) {
    return MEDICAL_FAILURE;
  }

  patient->record_count++;
  return MEDICAL_SUCCESS;
}

medical_result_t
MedicalRemoveRecord(user_t *doctor_user, user_t *patient_user, char *condition)
{
  patient_t *patient;
  doctor_t *doctor;
  medical_record_t new_records[MEDICAL_MAX_RECORDS];
  size_t i, j = 0;

  doctor = MedicalGetDoctor(doctor_user);
  patient = MedicalGetPatient(patient_user);
  if(patient == NULL || doctor == NULL) {
    return MEDICAL_INVALID_USER;
  }

  if(MedicalDoctorCertified(doctor, condition) == false) {
    return MEDICAL_NOT_CERTIFIED;
  }

  for(i = 0; i < patient->record_count; i++) {
    if(strcmp(patient->records[i].condition, condition) == 0) {
      MedicalRecordFree(&patient->records[i]);
      continue;
    }
    new_records[j] = patient->records[i];
    j++;
  }

  memcpy(patient->records, new_records, sizeof(patient->records));
  memcpy(patient->records, new_records, sizeof(patient->records));

  return MEDICAL_SUCCESS;
}

medical_result_t
MedicalAddTreatment(user_t *doctor_user, medical_record_t *record,
                    char *name, double dose, char *unit)
{
  doctor_t *doctor;

  doctor = MedicalGetDoctor(doctor_user);
  if(doctor == NULL) {
    return MEDICAL_INVALID_USER;
  }

  if(MedicalDoctorCertified(doctor, record->condition) == false) {
    return MEDICAL_NOT_CERTIFIED;
  }

  if(record->treatment_count == MEDICAL_MAX_RECORDS) {
    return MEDICAL_FIELD_FULL;
  }

  snprintf(record->treatments[record->treatment_count].name,
           MEDICAL_NAME_LENGTH, "%s", name);

  snprintf(record->treatments[record->treatment_count].unit,
           MEDICAL_UNIT_NAME_LENGTH, "%s", unit);

  record->treatments[record->treatment_count].dose = dose;

  record->treatment_count++;
  return MEDICAL_SUCCESS;
}

medical_result_t
MedicalRemoveTreatment(user_t *doctor_user, medical_record_t *record, char *name)
{
  doctor_t *doctor;
  medical_treatment_t new_treatments[MEDICAL_MAX_TREATMENTS];
  size_t i, j = 0;

  doctor = MedicalGetDoctor(doctor_user);
  if(doctor == NULL) {
    return MEDICAL_INVALID_USER;
  }

  if(MedicalDoctorCertified(doctor, record->condition) == false) {
    return MEDICAL_NOT_CERTIFIED;
  }

  for(i = 0; i < record->treatment_count; i++) {
    if(strcmp(record->treatments[i].name, name) == 0) {
      continue;
    }
    new_treatments[j] = record->treatments[i];
    j++;
  }

  memset(record->treatments, 0, sizeof(record->treatments));
  memcpy(record->treatments, new_treatments, sizeof(record->treatments));

  return MEDICAL_SUCCESS;
}

medical_result_t
MedicalAddCert(user_t *doctor_user, char *condition, size_t year_received)
{
  doctor_t *doctor;

  doctor = MedicalGetDoctor(doctor_user);
  if(doctor == NULL) {
    return MEDICAL_INVALID_USER;
  }

  if(doctor->cert_count == MEDICAL_MAX_CERTS) {
    return MEDICAL_FIELD_FULL;
  }

  snprintf(doctor->certs[doctor->cert_count].condition, MEDICAL_NAME_LENGTH, "%s", condition);
  doctor->certs[doctor->cert_count].year_received = year_received;

  doctor->cert_count++;

  return MEDICAL_SUCCESS;
}
