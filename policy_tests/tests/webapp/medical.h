#ifndef MEDICAL_H
#define MEDICAL_H

#define MEDICAL_MAX_RECORDS 0x4
#define MEDICAL_MAX_PATIENTS 0x4
#define MEDICAL_MAX_CERTS 0x4
#define MEDICAL_MAX_TREATMENTS 0x4

#define MEDICAL_NAME_LENGTH 0x20
#define MEDICAL_UNIT_NAME_LENGTH 0x4

#include "user.h"

typedef enum {
  MEDICAL_SUCCESS,
  MEDICAL_FAILURE,
  MEDICAL_INVALID_USER,
  MEDICAL_FIELD_FULL,
  MEDICAL_NOT_CERTIFIED,
  MEDICAL_NOT_FOUND,
} medical_result_t;

typedef struct _medical_treatment_t {
  char name[MEDICAL_NAME_LENGTH];
  char unit[MEDICAL_UNIT_NAME_LENGTH];
  double dose;
} medical_treatment_t;

typedef struct _medical_record_t {
  char condition[MEDICAL_NAME_LENGTH];
  medical_treatment_t treatments[MEDICAL_MAX_TREATMENTS];
  size_t treatment_count;
  user_t *doctor_user;
  char *notes;
} medical_record_t;

typedef struct _medical_cert_t {
  char condition[MEDICAL_NAME_LENGTH];
  size_t year_received;
} medical_cert_t;

typedef struct _patient_t {
  medical_record_t records[MEDICAL_MAX_RECORDS];
  size_t record_count;
} patient_t;

typedef struct _doctor_t {
  medical_cert_t certs[MEDICAL_MAX_CERTS];
  user_t *patient_users[MEDICAL_MAX_PATIENTS];
  size_t cert_count;
  size_t patient_count;
} doctor_t;

bool MedicalDoctorCertified(doctor_t *doctor, char *condition);

bool MedicalSetPatient(user_t *user);
patient_t *MedicalGetPatient(user_t *user);
bool MedicalSetDoctor(user_t *user);
doctor_t *MedicalGetDoctor(user_t *user);

medical_result_t MedicalAddRecord(user_t *doctor_user, user_t *patient_user,
                                  char *condition, char *notes);
medical_result_t MedicalRemoveRecord(user_t *doctor_user, user_t *patient_user, char *condition);

medical_result_t MedicalAddTreatment(user_t *doctor_user, medical_record_t *record,
                                     char *name, double dose, char *unit);
medical_result_t MedicalRemoveTreatment(user_t *doctor_user, medical_record_t *record,
                                        char *name);

medical_result_t MedicalAddCert(user_t *doctor_user, char *condition, size_t year_received);

#endif // MEDICAL_H
