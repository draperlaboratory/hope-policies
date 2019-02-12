#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "auth.h"
#include "hashtable.h"
#include "database.h"

#define AUTH_TABLE_CAPACITY 0x10

static hash_table_t active_session_table;

volatile int current_auth_user_type;

void
AuthClearCurrentUserType(void)
{
}

void __attribute__ ((noinline))
AuthSetCurrentUserType(user_t *user)
{
  current_auth_user_type = user->type;
}

static char *
AuthDigestToSessionId(uint8_t *digest)
{
  size_t i, j = 0;
  char hex[3];
  char *session_id;

  session_id = malloc(AUTH_SESSION_ID_SIZE + 1);
  if(session_id == NULL) {
    return NULL;
  }

  for(i = 0 ; i < SHA1_BLOCK_SIZE; i++) {
    snprintf(hex, sizeof(hex), "%02x", digest[i]);
    session_id[j] = hex[0];
    session_id[j + 1] = hex[1];
    j += 2;
  }
  session_id[AUTH_SESSION_ID_SIZE] = '\0';

  return session_id;
}

static char *
AuthGenerateSessionId(user_t *user)
{
  sha1_context_t context;
  uint8_t digest[SHA1_BLOCK_SIZE];
  char *session_id;

  Sha1Init(&context);
  Sha1Update(&context, (uint8_t *)user, sizeof(user_t));
  Sha1Final(&context, digest);

  session_id = AuthDigestToSessionId(digest);
  if(session_id == NULL) {
    return NULL;
  }

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
AuthStartSession(char *username, char *password, char *session_id_out)
{
  user_t *user;
  char *session_id;

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
    snprintf(session_id_out, AUTH_SESSION_ID_SIZE + 1, "%s", session_id);
  }

  return AUTH_SUCCESS;
}

user_t *
AuthCheckSessionId(char *session_id)
{
  user_t *user;

  user = HashTableLookup(&active_session_table, session_id);
  if(user == NULL) {
    return NULL;
  }

  return user;
}

bool
AuthEndSession(char *session_id)
{
  if(HashTableErase(&active_session_table, session_id) == HASH_TABLE_ERROR) {
    return false;
  }
  return true;
}
