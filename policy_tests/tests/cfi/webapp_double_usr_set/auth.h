#ifndef AUTHENTICATION_H
#define AUTHENTICATION_H

#include <stdbool.h>
#include <stdint.h>

#include "user.h"
#include "sha1.h"

#define AUTH_SESSION_ID_SIZE SHA1_BLOCK_SIZE

typedef enum {
  AUTH_SUCCESS,
  AUTH_FAILURE,
  AUTH_USER_NOT_FOUND,
  AUTH_INVALID_CREDENTIALS,
} auth_result_t;

bool AuthInit(void);

auth_result_t AuthStartSession(char *username, char *password, uint8_t *session_id_out);
user_t *AuthCheckSessionId(uint8_t *session_id);
bool AuthEndSession(uint8_t *session_id);

#endif // AUTHENTICATION_H
