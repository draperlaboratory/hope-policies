#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "database.h"
#include "hashtable.h"
#include "medical.h"

#define DATABASE_KEY_LENGTH USER_NAME_LENGTH
#define DATABASE_CAPACITY 0x10

static hash_table_t database_table;


static database_search_result_t *
DatabaseSearchResultAlloc(void)
{
  database_search_result_t *result;

  result = malloc(sizeof(database_search_result_t));
  if(result == NULL) {
    return NULL;
  }

  result->head = malloc(sizeof(database_search_result_node_t));
  if(result->head == NULL) {
    free(result);
    return NULL;
  }
  result->head->user = NULL;
  result->head->next = NULL;

  result->count = 0;

  return result;
}

static bool
DatabaseSearchResultAppend(database_search_result_t *result, user_t *user)
{
  database_search_result_node_t *new_node;
  database_search_result_node_t *iter_node;

  if(result->head->user == NULL) {
    result->head->user = user;
    result->count++;
    return true;
  }

  new_node = malloc(sizeof(database_search_result_node_t));
  if(new_node == NULL) {
    return false;
  }

  new_node->user = user;
  new_node->next = NULL;

  iter_node = result->head;
  while(iter_node->next != NULL) {
    iter_node = iter_node->next;
  }

  iter_node->next = new_node;
  result->count++;

  return true;
}

bool 
DatabaseInit(void)
{
  int result;

  result = HashTableSetup(&database_table,
                          DATABASE_KEY_LENGTH,
                          DATABASE_CAPACITY,
                          sizeof(user_t));

  if(result == HASH_TABLE_ERROR) {
    return false;
  }

  return true;
}

bool
DatabaseAddUser(user_t *user)
{
  if(HashTableContains(&database_table, user->username) == HASH_TABLE_FOUND) {
    return false;
  }

  if(HashTableInsert(&database_table, user->username, user) == HASH_TABLE_ERROR) {
    return false;
  }

  return true;
}

bool
DatabaseRemoveUser(user_t *user)
{
  if(HashTableErase(&database_table, user->username) == HASH_TABLE_ERROR) {
    return false;
  }

  return true;
}

user_t *
DatabaseGetUser(char *username)
{
  char key[USER_NAME_LENGTH];
  user_t *result;

  memset(key, '\0', USER_NAME_LENGTH);
  snprintf(key, USER_NAME_LENGTH, "%s", username);

  result = (user_t *)HashTableLookup(&database_table, key);

  return result;
}

size_t DatabaseSize()
{
  return database_table.size;
}

database_search_result_t *
DatabaseSearch(user_type_t type, char *first_name, char *last_name, char *address, char *condition)
{
  size_t i;
  size_t size;
  user_t **users;
  database_search_result_t *result;

  size = DatabaseSize();
  users = (user_t **)HashTableToArray(&database_table);
  if(users == NULL) {
    return NULL;
  }

  result = DatabaseSearchResultAlloc();
  if(result == NULL) {
    return NULL;
  }

  for(i = 0; i < size; i++) {
    if((type != USER_UNKNOWN) && (users[i]->type != type)) {
      continue;
    }

    if((first_name != NULL) &&
       (strcmp(first_name, users[i]->first_name) != 0)) {
      continue;
    }
    if((last_name != NULL) &&
       (strcmp(last_name, users[i]->last_name) != 0)) {
      continue;
    }
    if((address != NULL) &&
       (strcmp(address, users[i]->address) != 0)) {
      continue;
    }

    if((type == USER_DOCTOR) && (condition != NULL)) {
      if(MedicalDoctorCertified(MedicalGetDoctor(users[i]), condition) == false) {
        continue;
      }
    }
    
    if(DatabaseSearchResultAppend(result, users[i]) == false) {
      free(users);
      DatabaseSearchResultFree(result);
      return NULL;
    }
  }

  free(users);

  return result;
}

user_t **
DatabaseUserList(size_t max)
{
  user_t **users;

  users = (user_t **)HashTableToArray(&database_table);
  if(users == NULL) {
    return NULL;
  }

  return users;
}

void
DatabaseSearchResultFree(database_search_result_t *result)
{
  database_search_result_node_t *node;

  node = result->head;

  while(node != NULL) {
    free(node);
    node = node->next;
  }

  free(result);
}
