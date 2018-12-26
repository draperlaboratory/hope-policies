#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "database.h"
#include "auth.h"
#include "user.h"


bool
TestDatabase(void)
{
  user_t *user1;
  user_t *user2;
  user_t *lookup_result;
  database_search_result_t *search_result;

  if(DatabaseInit() == false) {
    printf("Database failed to init\n");
    return false;
  }

  user1 = UserCreate("user1", "password123", "User", "One", "123 Main St.");
  if(user1 == NULL) {
    printf("Failed to create user1\n");
    return false;
  }

  user2 = UserCreate("user2", "toor", "User", "Two", "123 Main St.");
  if(user2 == NULL) {
    printf("Failed to create user2\n");
    return false;
  }

  if(DatabaseAddUser(user1) == false) {
    printf("Failed to add user1\n");
    return false;
  }

  if(DatabaseAddUser(user2) == false) {
    printf("Failed to add user2\n");
    return false;
  }

  lookup_result = DatabaseGetUser("user1");
  if(lookup_result == NULL) {
    printf("Failed to get user from database\n");
    return false;
  }
  printf("Looked up user with password %s\n", lookup_result->password);

  search_result = DatabaseSearch(NULL, "Two", NULL);
  if(search_result == NULL) {
    printf("Failed to retrieve search result\n");
    return false;
  }
  if(search_result->count != 1) {
    printf("Incorrect search results\n");
    return false;
  }
  printf("Retrieved %lu results with last name Two\n", search_result->count);
  DatabaseSearchResultFree(search_result);

  search_result = DatabaseSearch(NULL, NULL, "123 Main St.");
  if(search_result == NULL) {
    printf("Failed to retrieve search result\n");
    return false;
  }
  if(search_result->count != 2) {
    printf("Incorrect search results\n");
    return false;
  }
  printf("Retrieved %lu results with address 123 Main St.\n", search_result->count);
  DatabaseSearchResultFree(search_result);

  search_result = DatabaseSearch(NULL, "One", "123 Main St.");
  if(search_result == NULL) {
    printf("Failed to retrieve search result\n");
    return false;
  }
  if(search_result->count != 1) {
    printf("Incorrect search results\n");
    return false;
  }
  printf("Retrieved %lu results with last name One and address 123 Main St.\n", search_result->count);
  DatabaseSearchResultFree(search_result);

  return true;
}

void TestAuth(void)
{
  user_t *user;
  uint8_t session_id[AUTH_SESSION_ID_SIZE + 1];

  if(AuthInit() == false) {
    printf("Authentication failed to init\n");
    return;
  }

  printf("Logging in as user2 with password root\n");
  if(AuthStartSession("user2", "root", session_id) != AUTH_INVALID_CREDENTIALS) {
    printf("Failed to recognize incorrect password\n");
    return;
  }

  printf("Incorrect password. Trying again with password toor\n");
  if(AuthStartSession("user2", "toor", session_id) != AUTH_SUCCESS) {
    printf("Failed to log in\n");
  }
  session_id[AUTH_SESSION_ID_SIZE] = '\0';
  printf("Login successful. Session id: %s\n", (char *)session_id);

  printf("Verifying session_id %s is active\n", (char *)session_id);
  user = AuthCheckSessionId(session_id);
  if(user == NULL) {
    printf("Invalid session_id\n");
    return;
  }
  printf("Session id %s belongs to user %s\n", (char *)session_id, user->username);

  printf("Logging out as user2\n");
  if(AuthEndSession(session_id) == false) {
    printf("Failed to end session\n");
    return;
  }

  printf("Attempting to find user with invalid session_id %s\n", (char *)session_id);
  user = AuthCheckSessionId(session_id);
  if(user != NULL) {
    printf("Invalid session_id returned a user\n");
    return;
  }
  printf("User cannot be found with invalid session_id\n");

}

int webapp_main() {
  TestDatabase();
  printf("====\n");
  TestAuth();
  printf("====\n");

  return 0;
}
