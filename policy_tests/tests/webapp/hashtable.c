#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "hashtable.h"

static void HashTableIntSwap(size_t* first, size_t* second);
static void HashTablePointerSwap(void** first, void** second);
static size_t HashTableDefaultHash(void* key, size_t key_size);
static int HashTableDefaultCompare(void* first_key, void* second_key, size_t key_size);
static size_t HashTableHash(const hash_table_t* table, void* key);
static bool HashTableEqual(const hash_table_t* table, void* first_key, void* second_key);
static bool HashTableShouldGrow(hash_table_t* table);
static bool HashTableShouldShrink(hash_table_t* table);
static hash_table_node_t* HashTableCreateNode(hash_table_t* table, void* key, void* value, hash_table_node_t* next);
static int HashTablePushFront(hash_table_t* table, size_t index, void* key, void* value);
static void HashTableDestroyNode(hash_table_node_t* node);
static int HashTableAdjustCapacity(hash_table_t* table);
static int HashTableAllocate(hash_table_t* table, size_t capacity);
static int HashTableResize(hash_table_t* table, size_t new_capacity);
static void HashTableRehash(hash_table_t* table, hash_table_node_t** old, size_t old_capacity);


int HashTableSetup(hash_table_t* table,
             size_t key_size,
             size_t value_size,
             size_t capacity)
{
  if (table == NULL) {
    return HASH_TABLE_ERROR;
  }

  if (capacity < HASH_TABLE_MINIMUM_CAPACITY) {
    capacity = HASH_TABLE_MINIMUM_CAPACITY;
  }

  if (HashTableAllocate(table, capacity) == HASH_TABLE_ERROR) {
    return HASH_TABLE_ERROR;
  }

  table->key_size = key_size;
  table->value_size = value_size;
  table->hash = HashTableDefaultHash;
  table->compare = HashTableDefaultCompare;
  table->size = 0;

  return HASH_TABLE_SUCCESS;
}

int HashTableCopy(hash_table_t* first, hash_table_t* second)
{
  size_t chain;
  hash_table_node_t* node;

  if (first == NULL) {
    return HASH_TABLE_ERROR;
  }

  if (!HashTableIsInitialized(second)) {
    return HASH_TABLE_ERROR;
  }

  if (HashTableAllocate(first, second->capacity) == HASH_TABLE_ERROR) {
    return HASH_TABLE_ERROR;
  }

  first->key_size = second->key_size;
  first->value_size = second->value_size;
  first->hash = second->hash;
  first->compare = second->compare;
  first->size = second->size;

  for (chain = 0; chain < second->capacity; ++chain) {
    for (node = second->nodes[chain]; node; node = node->next) {
      if (HashTablePushFront(first, chain, node->key, node->value) == HASH_TABLE_ERROR) {
        return HASH_TABLE_ERROR;
      }
    }
  }

  return HASH_TABLE_SUCCESS;
}

int HashTableMove(hash_table_t* first, hash_table_t* second)
{
  if (first == NULL) {
    return HASH_TABLE_ERROR;
  }

  if (!HashTableIsInitialized(second)) {
    return HASH_TABLE_ERROR;
  }

  *first = *second;
  second->nodes = NULL;

  return HASH_TABLE_SUCCESS;
}

int HashTableSwap(hash_table_t* first, hash_table_t* second)
{
  if (!HashTableIsInitialized(first)) {
    return HASH_TABLE_ERROR;
  }

  if (!HashTableIsInitialized(second)) {
    return HASH_TABLE_ERROR;
  }

  HashTableIntSwap(&first->key_size, &second->key_size);
  HashTableIntSwap(&first->value_size, &second->value_size);
  HashTableIntSwap(&first->size, &second->size);
  HashTablePointerSwap((void**)&first->hash, (void**)&second->hash);
  HashTablePointerSwap((void**)&first->compare, (void**)&second->compare);
  HashTablePointerSwap((void**)&first->nodes, (void**)&second->nodes);

  return HASH_TABLE_SUCCESS;
}

int HashTableDestroy(hash_table_t* table)
{
  hash_table_node_t* node;
  hash_table_node_t* next;
  size_t chain;

  if (!HashTableIsInitialized(table)) {
    return HASH_TABLE_ERROR;
  }

  for (chain = 0; chain < table->capacity; ++chain) {
    node = table->nodes[chain];
    while (node) {
      next = node->next;
      HashTableDestroyNode(node);
      node = next;
    }
  }

  free(table->nodes);

  return HASH_TABLE_SUCCESS;
}

int HashTableInsert(hash_table_t* table, void* key, void* value)
{
  size_t index;
  hash_table_node_t* node;

  if (!HashTableIsInitialized(table)) {
    return HASH_TABLE_ERROR;
  }

  if (key == NULL) {
    return HASH_TABLE_ERROR;
  }

  if (HashTableShouldGrow(table)) {
    HashTableAdjustCapacity(table);
  }

  index = HashTableHash(table, key);
  for (node = table->nodes[index]; node; node = node->next) {
    if (HashTableEqual(table, key, node->key)) {
      memcpy(node->value, value, table->value_size);
      return HASH_TABLE_UPDATED;
    }
  }

  if (HashTablePushFront(table, index, key, value) == HASH_TABLE_ERROR) {
    return HASH_TABLE_ERROR;
  }

  ++table->size;

  return HASH_TABLE_INSERTED;
}

int HashTableContains(hash_table_t* table, void* key)
{
  size_t index;
  hash_table_node_t* node;

  if (!HashTableIsInitialized(table)) {
    return HASH_TABLE_ERROR;
  }

  if (key == NULL) {
    return HASH_TABLE_ERROR;
  }

  index = HashTableHash(table, key);
  for (node = table->nodes[index]; node; node = node->next) {
    if (HashTableEqual(table, key, node->key)) {
      return HASH_TABLE_FOUND;
    }
  }

  return HASH_TABLE_NOT_FOUND;
}

void* HashTableLookup(hash_table_t* table, void* key) 
{
  hash_table_node_t* node;
  size_t index;

  if (table == NULL) {
    return NULL;
  }

  if (key == NULL) {
    return NULL;
  }

  index = HashTableHash(table, key);
  for (node = table->nodes[index]; node; node = node->next) {
    if (HashTableEqual(table, key, node->key)) {
      return node->value;
    }
  }

  return NULL;
}

const void* HashTableConstLookup(const hash_table_t* table, void* key)
{
  const hash_table_node_t* node;
  size_t index;

  if (table == NULL) {
    return NULL;
  }

  if (key == NULL) {
    return NULL;
  }

  index = HashTableHash(table, key);
  for (node = table->nodes[index]; node; node = node->next) {
    if (HashTableEqual(table, key, node->key)) {
      return node->value;
    }
  }

  return NULL;
}

int HashTableErase(hash_table_t* table, void* key)
{
  hash_table_node_t* node;
  hash_table_node_t* previous;
  size_t index;

  if (table == NULL) {
    return HASH_TABLE_ERROR;
  }

  if (key == NULL) {
    return HASH_TABLE_ERROR;
  }

  index = HashTableHash(table, key);
  node = table->nodes[index];

  for (previous = NULL; node; previous = node, node = node->next) {
    if (HashTableEqual(table, key, node->key)) {
      if (previous) {
        previous->next = node->next;
      } else {
        table->nodes[index] = node->next;
      }

      HashTableDestroyNode(node);
      --table->size;

      if (HashTableShouldShrink(table)) {
        if (HashTableAdjustCapacity(table) == HASH_TABLE_ERROR) {
          return HASH_TABLE_ERROR;
        }
      }

      return HASH_TABLE_SUCCESS;
    }
  }

  return HASH_TABLE_NOT_FOUND;
}

int HashTableClear(hash_table_t* table)
{
  if (table == NULL) {
    return HASH_TABLE_ERROR;
  }

  if (table->nodes == NULL) {
    return HASH_TABLE_ERROR;
  }

  HashTableDestroy(table);
  HashTableAllocate(table, HASH_TABLE_MINIMUM_CAPACITY);
  table->size = 0;

  return HASH_TABLE_SUCCESS;
}

int HashTableIsEmpty(hash_table_t* table)
{
  if (table == NULL) {
    return HASH_TABLE_ERROR;
  }
  return table->size == 0;
}

bool HashTableIsInitialized(hash_table_t* table)
{
  return table != NULL && table->nodes != NULL;
}

int HashTableReserve(hash_table_t* table, size_t minimum_capacity)
{
  if (!HashTableIsInitialized(table)) {
    return HASH_TABLE_ERROR;
  }

  /*
   * We expect the "minimum capacity" to be in elements, not in array indices.
   * This encapsulates the design.
   */
  if (minimum_capacity > table->threshold) {
    return HashTableResize(table, minimum_capacity / HASH_TABLE_LOAD_FACTOR);
  }

  return HASH_TABLE_SUCCESS;
}

void **HashTableToArray(hash_table_t *table)
{
  size_t i, j = 0;
  hash_table_node_t *node;
  void **result;

  result = calloc(table->size + 1, sizeof(void *));

  for(i = 0; i < table->capacity; i++) {
    for(node = table->nodes[i]; node != NULL; node = node->next) {
      result[j] = node->value;
      j++;
    }
  }

  return result;
}

static void HashTableIntSwap(size_t* first, size_t* second)
{
  size_t temp = *first;
  *first = *second;
  *second = temp;
}

static void HashTablePointerSwap(void** first, void** second)
{
  void* temp = *first;
  *first = *second;
  *second = temp;
}

static int HashTableDefaultCompare(void* first_key, void* second_key, size_t key_size)
{
  return memcmp(first_key, second_key, key_size);
}

size_t HashTableDefaultHash(void* raw_key, size_t key_size)
{
  // djb2 string hashing algorithm
  // sstp://www.cse.yorku.ca/~oz/hash.ssml
  size_t byte;
  size_t hash = 5381;
  char* key = raw_key;

  for (byte = 0; byte < key_size; ++byte) {
    // (hash << 5) + hash = hash * 33
    hash = ((hash << 5) + hash) ^ key[byte];
  }

  return hash;
}

static size_t HashTableHash(const hash_table_t* table, void* key)
{
#ifdef HASH_TABLE_USING_POWER_OF_TWO
  return table->hash(key, table->key_size) & table->capacity;
#else
  return table->hash(key, table->key_size) % table->capacity;
#endif
}

static bool HashTableEqual(const hash_table_t* table, void* first_key, void* second_key)
{
  return table->compare(first_key, second_key, table->key_size) == 0;
}

static bool HashTableShouldGrow(hash_table_t* table)
{
  return table->size == table->capacity;
}

static bool HashTableShouldShrink(hash_table_t* table)
{
  return table->size == table->capacity * HASH_TABLE_SHRINK_THRESHOLD;
}

static hash_table_node_t*
HashTableCreateNode(hash_table_t* table, void* key, void* value, hash_table_node_t* next)
{
  hash_table_node_t* node;

  if((table == NULL) ||
     (key == NULL) ||
     (value == NULL)) {
    return NULL;
  }

  if ((node = malloc(sizeof *node)) == NULL) {
    return NULL;
  }
  if ((node->key = malloc(table->key_size)) == NULL) {
    return NULL;
  }
  if ((node->value = malloc(table->value_size)) == NULL) {
    return NULL;
  }

  memcpy(node->key, key, table->key_size);
  memcpy(node->value, value, table->value_size);
  node->next = next;

  return node;
}

static int HashTablePushFront(hash_table_t* table, size_t index, void* key, void* value)
{
  table->nodes[index] = HashTableCreateNode(table, key, value, table->nodes[index]);
  return table->nodes[index] == NULL ? HASH_TABLE_ERROR : HASH_TABLE_SUCCESS;
}

static void HashTableDestroyNode(hash_table_node_t* node)
{
  if(node == NULL) {
    return;
  }

  free(node->key);
  free(node->value);
  free(node);
}

static int HashTableAdjustCapacity(hash_table_t* table)
{
  return HashTableResize(table, table->size * HASH_TABLE_GROWTH_FACTOR);
}

static int HashTableAllocate(hash_table_t* table, size_t capacity)
{
  if ((table->nodes = malloc(capacity * sizeof(hash_table_node_t*))) == NULL) {
    return HASH_TABLE_ERROR;
  }
  memset(table->nodes, 0, capacity * sizeof(hash_table_node_t*));

  table->capacity = capacity;
  table->threshold = capacity * HASH_TABLE_LOAD_FACTOR;

  return HASH_TABLE_SUCCESS;
}

static int HashTableResize(hash_table_t* table, size_t new_capacity)
{
  hash_table_node_t** old;
  size_t old_capacity;

  if (new_capacity < HASH_TABLE_MINIMUM_CAPACITY) {
    if (table->capacity > HASH_TABLE_MINIMUM_CAPACITY) {
      new_capacity = HASH_TABLE_MINIMUM_CAPACITY;
    } else {
      /* NO-OP */
      return HASH_TABLE_SUCCESS;
    }
  }

  old = table->nodes;
  old_capacity = table->capacity;
  if (HashTableAllocate(table, new_capacity) == HASH_TABLE_ERROR) {
    return HASH_TABLE_ERROR;
  }

  HashTableRehash(table, old, old_capacity);

  free(old);

  return HASH_TABLE_SUCCESS;
}

static void HashTableRehash(hash_table_t* table, hash_table_node_t** old, size_t old_capacity)
{
  hash_table_node_t* node;
  hash_table_node_t* next;
  size_t new_index;
  size_t chain;

  for (chain = 0; chain < old_capacity; ++chain) {
    for (node = old[chain]; node;) {
      next = node->next;

      new_index = HashTableHash(table, node->key);
      node->next = table->nodes[new_index];
      table->nodes[new_index] = node;

      node = next;
    }
  }
}
