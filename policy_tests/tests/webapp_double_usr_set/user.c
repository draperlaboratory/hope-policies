#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "user.h"

//void isp_memset(

  
  
//}

void __attribute__ ((noinline))                  
UserSetType(user_t *user, user_type_t type)
{                                          
  user->type = type;                       
}     

user_t *UserCreate(char *username, char *password, 
                   char *first_name, char *last_name,
                   char *address)
{
  user_t *user;

  user = malloc(sizeof(user_t));
  if(user == NULL) {
    return NULL;
  }

  asm("user_create_memset:");
  memset(user, 0, sizeof(user_t));

  snprintf(user->username, USER_NAME_LENGTH, "%s", username);
  snprintf(user->password, USER_PASSWORD_LENGTH, "%s", password);
  snprintf(user->first_name, USER_NAME_LENGTH, "%s", first_name);
  snprintf(user->last_name, USER_NAME_LENGTH, "%s", last_name); 
  snprintf(user->address, USER_ADDRESS_LENGTH, "%s", address);

  user->type = USER_UNKNOWN;
  user->patient = NULL;
  user->doctor = NULL;
  user->administrator = NULL;

  return user;
}

void UserDestroy(user_t *user)
{
  if(user == NULL) {
    return;
  }

  if(user->patient != NULL) {
    free(user->patient);
  }

  if(user->doctor != NULL) {
    free(user->doctor);
  }

  if(user->administrator != NULL) {
    free(user->administrator);
  }

  free(user);
}

bool
UserSetPatient(user_t *user)
{

  UserSetType(user, USER_PATIENT);
  user->patient = malloc(sizeof(patient_t));
  if(user->patient == NULL) {
    return false;
  }

  user->patient->placeholder = 42;
  return true;
}

bool
UserSetDoctor(user_t *user)
{
  UserSetType(user, USER_DOCTOR);
  user->doctor = malloc(sizeof(doctor_t));
  if(user->doctor == NULL) {
    return false;
  }

  user->doctor->placeholder = 42;
  return true;
}

bool
UserSetAdministrator(user_t *user)
{
  UserSetType(user, USER_ADMINISTRATOR);
  user->administrator = malloc(sizeof(administrator_t));
  if(user->administrator == NULL) {
    return false;
  }

  user->administrator->placeholder = 42;
  return true;
}
