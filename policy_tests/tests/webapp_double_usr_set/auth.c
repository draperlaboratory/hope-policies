#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "auth.h"
#include "hashtable.h"
#include "database.h"

#define AUTH_TABLE_CAPACITY 0x1000

static hash_table_t active_session_table;

static uint8_t *
AuthGenerateSessionId(user_t *user)
{
  sha1_context_t context;
  uint8_t *session_id;

  session_id = malloc(AUTH_SESSION_ID_SIZE);
  if(session_id == NULL) {
    return NULL;
  }

  Sha1Init(&context);
  Sha1Update(&context, (uint8_t *)user, sizeof(user_t));
  Sha1Final(&context, session_id);
  session_id[AUTH_SESSION_ID_SIZE] = '\0';

  return session_id;
}

static bool
AuthCheckPassword(user_t *user, char *password)
{
  return strcmp(user->password, password) == 0;
}

bool
AuthInit()
{
  int result;

  result = HashTableSetup(&active_session_table,
                          AUTH_SESSION_ID_SIZE,
                          AUTH_TABLE_CAPACITY,
                          sizeof(user_t));       

  if(result == HASH_TABLE_ERROR) {
    return false;
  }

  return true;
}

auth_result_t
AuthStartSession(char *username, char *password, uint8_t *session_id_out)
{
  user_t *user;
  uint8_t *session_id;

  user = DatabaseGetUser(username);
  if(user == NULL) {
    return AUTH_USER_NOT_FOUND;
  }

  if(AuthCheckPassword(user, password) == false) {
    return AUTH_INVALID_CREDENTIALS;
  }

  session_id = AuthGenerateSessionId(user);
  if(session_id == NULL) {
    return AUTH_FAILURE;
  }

  if(HashTableInsert(&active_session_table, session_id, user) == HASH_TABLE_ERROR) {
    free(session_id);
    return AUTH_FAILURE;
  }

  if(session_id_out != NULL) {
    memcpy(session_id_out, session_id, AUTH_SESSION_ID_SIZE);
  }

  return AUTH_SUCCESS;
}

user_t *
AuthCheckSessionId(uint8_t *session_id)
{
  user_t *user;

  user = HashTableLookup(&active_session_table, session_id);
  if(user == NULL) {
    return NULL;
  }

  return user;
}

bool
AuthEndSession(uint8_t *session_id)
{
  if(HashTableErase(&active_session_table, session_id) == HASH_TABLE_ERROR) {
    return false;
  }
  return true;
}
