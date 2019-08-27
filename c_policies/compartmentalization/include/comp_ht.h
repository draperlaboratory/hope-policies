// Simple hashtable implementation for compartmentalization policy
// to track various kinds of interactions (read, write, call, return)

#ifndef COMP_HT_H
#define COMP_HT_H

#include <stdio.h>

/* Number of top-level bins in the hash table.
 * For FreeRTOS alone, we're looking at ~1000 interactions stored
 * total. With mid-sized applications, can get to 6-10k. Can turn this
 * knob below, only impacts space-time tradeoff. 1024-8192 seem
 * reasonable. Too small will impact performance, too large wasteful
 * of memory for HT array. TODO automatically resizing based on use
 * obviosly better. */
#define HT_SIZE 4096

struct comp_bucket {
  int src, dest, edge_type;
  unsigned long count;
  struct comp_bucket * next;
};

struct comp_ht {
  int num_buckets;
  int stored_objects;
  int new_additions;
  int initialized;
  int reads, writes, calls, returns;
  struct comp_bucket ** buckets;
};

// The edge types: 
#define EDGE_READ 1
#define EDGE_WRITE 2
#define EDGE_CALL 3
#define EDGE_RETURN 4

struct comp_ht * ht_create(int size);
struct comp_bucket * ht_lookup(struct comp_ht *, int src, int dest, int edge_type);
void ht_insert(struct comp_ht *, int src, int dest, int edge_type);
void print_func_data(struct comp_ht *, int func, int weights, FILE * outfile);

#endif
