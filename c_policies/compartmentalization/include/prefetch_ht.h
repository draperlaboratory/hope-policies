// Simple hashtable implementation for compartmentalization policy
// to track various kinds of interactions (read, write, call, return)

#ifndef PREFETCH_HT_H
#define PREFETCH_HT_H

#include <stdio.h>

#define HT_PREFETCH_SIZE 4096

#define PREFETCH_NUM 4

struct prefetch_bucket {
  operands_t * key;
  int num_rules;
  operands_t ** prefetch_ops;
  results_t ** prefetch_res;
  struct prefetch_bucket * next;
};

struct prefetch_ht {
  int num_buckets;
  int initialized;
  int stored_objects;
  struct prefetch_bucket ** buckets;
};

struct prefetch_ht * ht_create_prefetch(int size);
struct prefetch_bucket * ht_lookup_prefetch(struct prefetch_ht *, operands_t * key);
void ht_insert_prefetch(struct prefetch_ht *, operands_t * key, operands_t ** prefetch_ops, results_t ** prefetch_res, int num_rules);

struct prefetch_ht * prefetch_ht = NULL;
#endif
