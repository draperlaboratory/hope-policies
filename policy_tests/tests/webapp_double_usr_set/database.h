#ifndef DATABASE_H
#define DATABASE_H

#include <stdbool.h>
#include "user.h"

typedef struct _database_search_result_node_t {
  user_t *user;
  struct _database_search_result_node_t *next;
} database_search_result_node_t;

typedef struct _database_search_result_t {
  database_search_result_node_t *head;
  size_t count;
} database_search_result_t;

bool DatabaseInit(void);

bool DatabaseAddUser(user_t *user);
bool DatabaseRemoveUser(user_t *user);
user_t *DatabaseGetUser(char *username);
size_t DatabaseSize(void);

database_search_result_t *DatabaseSearch(char *first_name, char *last_name, char *address);
void DatabaseSearchResultFree(database_search_result_t *result);

#endif // DATABASE_H
