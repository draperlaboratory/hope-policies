#ifndef HASHTABLE_H
#define HASHTABLE_H

#include <stdbool.h>
#include <stddef.h>

#define HASH_TABLE_MINIMUM_CAPACITY 8
#define HASH_TABLE_LOAD_FACTOR 5
#define HASH_TABLE_MINIMUM_THRESHOLD (HASH_TABLE_MINIMUM_CAPACITY) * (HASH_TABLE_LOAD_FACTOR)

#define HASH_TABLE_GROWTH_FACTOR 2
#define HASH_TABLE_SHRINK_THRESHOLD (1 / 4)

#define HASH_TABLE_ERROR -1
#define HASH_TABLE_SUCCESS 0

#define HASH_TABLE_UPDATED 1
#define HASH_TABLE_INSERTED 0

#define HASH_TABLE_NOT_FOUND 0
#define HASH_TABLE_FOUND 01

#define HASH_TABLE_INITIALIZER {0, 0, 0, 0, 0, NULL, NULL, NULL};

typedef int (*comparison_t)(void*, void*, size_t);
typedef size_t (*hash_t)(void*, size_t);

typedef struct _hash_table_node_t {
	struct _hash_table_node_t* next;
	void* key;
	void* value;

} hash_table_node_t;

typedef struct _hash_table_t {
	size_t size;
	size_t threshold;
	size_t capacity;

	size_t key_size;
	size_t value_size;

	comparison_t compare;
	hash_t hash;

	hash_table_node_t** nodes;

} hash_table_t;

int HashTableSetup(hash_table_t* table,
						 size_t key_size,
						 size_t value_size,
						 size_t capacity);

int HashTableCopy(hash_table_t* first, hash_table_t* second);
int HashTableMove(hash_table_t* first, hash_table_t* second);
int HashTableSwap(hash_table_t* first, hash_table_t* second);

int HashTableDestroy(hash_table_t* table);

int HashTableInsert(hash_table_t* table, void* key, void* value);

int HashTableContains(hash_table_t* table, void* key);
void* HashTableLookup(hash_table_t* table, void* key);
const void* HashTableConstLookup(const hash_table_t* table, void* key);

#define HASH_TABLE_LOOKUP_AS(type, table_pointer, key_pointer) \
	(*(type*)HashTableLookup((table_pointer), (key_pointer)))

int HashTableErase(hash_table_t* table, void* key);
int HashTableClear(hash_table_t* table);

int HashTableIsEmpty(hash_table_t* table);
bool HashTableIsInitialized(hash_table_t* table);

int HashTableReserve(hash_table_t* table, size_t minimum_capacity);

void **HashTableToArray(hash_table_t *table);

#endif /* HASHTABLE_H */
