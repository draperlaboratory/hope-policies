#ifndef USER_H
#define USER_H

#include <stdbool.h>

#define USER_NAME_LENGTH 0x20
#define USER_PASSWORD_LENGTH 0x20
#define USER_ADDRESS_LENGTH 0x80

typedef enum {
  USER_ADMINISTRATOR,
  USER_PATIENT,
  USER_DOCTOR,
  USER_UNKNOWN,
} user_type_t;

typedef struct _user_t {
  char username[USER_NAME_LENGTH];
  char password[USER_PASSWORD_LENGTH];
  char first_name[USER_NAME_LENGTH];
  char last_name[USER_NAME_LENGTH];
  char address[USER_ADDRESS_LENGTH];
  user_type_t type;
  void *data;
} user_t;

user_t *UserCreate(char *user_name, char *password, 
                   char *first_name, char *last_name,
                   char *address);
void UserDestroy(user_t *user);

char *UserFullName(user_t *user);

void UserSetType(user_t *user, user_type_t type);

void UserUpdateAddress(user_t *user, char *address);

#endif // USER_H
