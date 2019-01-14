#ifndef USER_H
#define USER_H

#include <stdbool.h>

#define USER_NAME_LENGTH 0x20
#define USER_PASSWORD_LENGTH 0x20
#define USER_ADDRESS_LENGTH 0x80

typedef enum {
  USER_UNKNOWN,
  USER_PATIENT,
  USER_DOCTOR,
  USER_ADMINISTRATOR,
} user_type_t;

typedef struct _patient_user_t {
  int placeholder;
} patient_t;

typedef struct _doctor_user_t {
  int placeholder;
} doctor_t;

typedef struct _administrator_user_t {
  int placeholder;
} administrator_t;

typedef struct _user_t {
  char username[USER_NAME_LENGTH];
  char password[USER_PASSWORD_LENGTH];
  char first_name[USER_NAME_LENGTH];
  char last_name[USER_NAME_LENGTH];
  char address[USER_ADDRESS_LENGTH];
  user_type_t type;
  patient_t *patient;
  doctor_t *doctor;
  administrator_t *administrator;
} user_t;

user_t *UserCreate(char *user_name, char *password, 
                   char *first_name, char *last_name,
                   char *address);
bool UserSetPatient(user_t *user);
bool UserSetDoctor(user_t *user);
bool UserSetAdministrator(user_t *user);

void UserDestroy(user_t *user);

#endif // USER_H
