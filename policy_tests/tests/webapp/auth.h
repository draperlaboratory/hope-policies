#ifndef AUTHENTICATION_H
#define AUTHENTICATION_H

#include <stdbool.h>
#include <stdint.h>

#include "user.h"
#include "sha1.h"

#define AUTH_SESSION_ID_SIZE (SHA1_BLOCK_SIZE * 2)

typedef enum {
  AUTH_SUCCESS,
  AUTH_FAILURE,
  AUTH_USER_NOT_FOUND,
  AUTH_INVALID_CREDENTIALS,
  AUTH_NOT_LOGGED_IN,
} auth_result_t;

bool AuthInit(void);

auth_result_t AuthStartSession(char *username, char *password, char *session_id_out);
user_t *AuthCheckSessionId(char *session_id);
bool AuthEndSession(char *session_id);

// Hooks for tagging the current user
void AuthClearCurrentUserType(void);
void AuthSetCurrentUserType(user_t *user);

#endif // AUTHENTICATION_H
