#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include "database.h"
#include "auth.h"
#include "user.h"
#include "medical.h"

void TestUnauthenticatedMedicalAddRecord(void)
{
  user_t *user;

  user = UserCreate("patient_user", "password123", "Pat", "Ient", "123 Main St.");
  if(user == NULL) {
    printf("Failed to create user\n");
    return;
  }                                                                         

  MedicalSetPatient(user);
  
  AuthSetCurrentUserType(user);
  
  // should fail with PPAC policy
  MedicalAddRecord(user, user, "Fractured Authentication", "The doctor is not logged in");

  printf("passed\n");
}
#if 0
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

  search_result = DatabaseSearch(USER_PATIENT, NULL, "Two", NULL, NULL);
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

  search_result = DatabaseSearch(USER_PATIENT, NULL, NULL, "123 Main St.", NULL);
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

  search_result = DatabaseSearch(USER_PATIENT, NULL, "One", "123 Main St.", NULL);
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
  char session_id[AUTH_SESSION_ID_SIZE + 1];

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

bool
TestInfoLeak1(void)
{
  user_t *user1;
  user_t *user2;
  uintptr_t first_name_addr;
  uintptr_t password_addr;
  size_t padding_amount;
  user_t **users;
  char *payload;
  char print_buffer[0x1000];

  if(DatabaseInit() == false) {
    printf("Database failed to init\n");
    return false;
  }

  if(AuthInit() == false) {
    printf("Authentication failed to init\n");
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

  users = DatabaseUserList(2);
  if(users == NULL) {
    printf("Failed to allocate memory for user list\n");
    return false;
  }

  if(AuthStartSession("user2", "toor", NULL) != AUTH_SUCCESS) {
    printf("Failed to start session\n");
    return false;
  }

  first_name_addr = (uintptr_t)&users[1]->first_name;
  password_addr = (uintptr_t)&users[0]->password;

  printf("user1 first name: 0x%lx\n", first_name_addr);
  printf("user2 password: 0x%lx\n", password_addr);

  padding_amount = password_addr - first_name_addr;
  printf("padding amount: %lx\n", padding_amount);

  payload = malloc(padding_amount + 1);
  if(payload == NULL) {
    printf("Failed to allocate memory for info leak payload\n");
    return false;
  }
  memset(payload, 'A', padding_amount);
  payload[padding_amount] = '\0';

  memcpy(users[1]->first_name, payload, sizeof(users[1]->first_name));

  memcpy(print_buffer, users[1]->first_name, strlen(payload));

  printf("result: %s\n", print_buffer);

  return true;
}

bool
TestInfoLeak2(void)
{
  user_t *user1;
  user_t *user2;
  user_t *temp_user;
  user_t **users;
  user_t *current_user;
  char input[0x100];
  char username[0x1000];
  char user_last_name[0x1000];
  char payload[0x100];
  size_t i;

  memset(payload, 'a', sizeof(payload));

  if(DatabaseInit() == false) {
    printf("Database failed to init\n");
    return false;
  }

  user1 = UserCreate("user0", "root", "User", "One", "123 Main St.");
  if(user1 == NULL) {
    printf("Failed to create user1\n");
    return false;
  }

  user2 = UserCreate("user1", "toor", "User", "Two", "123 Main St.");
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

	for(i = 2; i < 512; i++) {
    snprintf(username, sizeof(username), "user%lu", i);
    snprintf(user_last_name, sizeof(user_last_name), "%luLastName", i);
    temp_user = UserCreate(username, "password", "User", user_last_name, "address");
    if(temp_user == NULL) {
      printf("Failed to create temp user\n");
      return false;
    }

    if(DatabaseAddUser(temp_user) == false) {
      printf("Failed to add temp user\n");
      return false;
    }
  }

  users = DatabaseUserList(512);
  if(users == NULL) {
    printf("Failed to allocate memory for user list\n");
    return false;
  }

  for(i = 0; i < 512; i++) {
    current_user = users[i];
    // off-by-one changes pointer to current user, could leak passwords via brute force
    snprintf(input, sizeof(input) + 1, "%s", payload);
    printf("input: %p, &current_user: %p, current_user: %p\n", input, &current_user, current_user);
    printf("users[%lu]->first_name: %s\n", i, current_user->first_name);

    if((strcmp(current_user->first_name, "root") == 0) ||
       (strcmp(current_user->first_name, "toor") == 0)) {
      printf("Password printed\n");
      break;
    }
  }

  return true;
}

bool
TestUnauthenticatedMedicalAddRecord(void)
{
  user_t *patient_user;
  user_t *doctor_user;
  user_t *admin_user;
  medical_result_t medical_result;
  auth_result_t auth_result;
  char session_id[AUTH_SESSION_ID_SIZE];

  if(DatabaseInit() == false) {
    printf("Database failed to init\n");
    return false;
  }

  if(AuthInit() == false) {
    printf("Authentication failed to init\n");
    return false;
  }
  AuthClearCurrentUserType();

  patient_user = UserCreate("patient_user", "password123", "Pat", "Ient", "123 Main St.");
  if(patient_user == NULL) {
    printf("Failed to create patient_user\n");
    return false;
  }
  MedicalSetPatient(patient_user);

  doctor_user = UserCreate("doctor_user", "toor", "Doc", "Tor", "123 Main St.");
  if(doctor_user == NULL) {
    printf("Failed to create doctor_user\n");
    return false;
  }
  MedicalSetDoctor(doctor_user);

  admin_user = UserCreate("admin_user", "root", "Ad", "Min", "123 Main St.");
  if(admin_user == NULL) {
    printf("Failed to create admin_user\n");
    return false;
  }
  UserSetType(admin_user, USER_ADMINISTRATOR);

  if(DatabaseAddUser(patient_user) == false) {
    printf("Failed to add patient_user\n");
    return false;
  }

  if(DatabaseAddUser(doctor_user) == false) {
    printf("Failed to add doctor_user\n");
    return false;
  }

  if(DatabaseAddUser(admin_user) == false) {
    printf("Failed to add admin_user\n");
    return false;
  }

  auth_result = AuthStartSession("admin_user", "root", session_id);
  if(auth_result != AUTH_SUCCESS) {
    printf("Failed to authenticate admin user, result: %d\n", auth_result);
    return false;
  }
  AuthSetCurrentUserType(admin_user->type);

  // should succeed with PPAC policy
  medical_result = MedicalAddCert(doctor_user, "Fractured Authentication", 2019);
  if(medical_result != MEDICAL_SUCCESS) {
    printf("Failed to add medical certification, medical_result: %d\n", medical_result);
    return false;
  }

  if(AuthEndSession(session_id) == false) {
    printf("Failed to end auth session\n");
    return false;
  }
  AuthClearCurrentUserType();

  auth_result = AuthStartSession("patient_user", "password123", NULL);
  if(auth_result != AUTH_SUCCESS) {
    printf("Failed to authenticate patient user\n");
    return false;
  }
  AuthSetCurrentUserType(patient_user->type);

  // should fail with PPAC policy
  medical_result = MedicalAddRecord(doctor_user, patient_user, "Fractured Authentication", "The doctor is not logged in");
  if(medical_result != MEDICAL_SUCCESS) {
    printf("Failed to add medical record");
    return false;
  }
  printf("Added medical record to patient\n");

  return true;
}
#endif
int webapp_main(int argc, char *argv[]) {

  TestUnauthenticatedMedicalAddRecord();
  return 0;
#if 0
  TestDatabase();
  printf("====\n");
  TestAuth();
  printf("====\n");
  TestInfoLeak1();
  printf("====\n");
  //  TestInfoLeak2();
  printf("====\n");
  TestUnauthenticatedMedicalAddRecord();
  printf("====\n");
#endif
  return 0;
}
