// Hashtable implementation for holding rule prefetching logic

#include <stdlib.h>
#include <stdio.h>
#include "prefetch_ht.h"

struct prefetch_ht * ht_create_prefetch(int size){
  struct prefetch_ht * new_ht = malloc(sizeof(struct prefetch_ht));
  memset(new_ht, 0, sizeof(struct prefetch_ht));
  new_ht -> stored_objects = 0;
  new_ht -> num_buckets = size;
  new_ht -> buckets = malloc(sizeof(struct prefetch_bucket *) * new_ht -> num_buckets);
  memset(new_ht -> buckets, 0, sizeof(struct prefetch_bucket *) * new_ht -> num_buckets);
  return new_ht;
}

struct prefetch_bucket * ht_lookup_prefetch(struct prefetch_ht * ht, operands_t * key){

  // Compute index
  unsigned int index = (unsigned int) key -> pc;
  index = index ^ (((unsigned int) key -> ci) << 1);  
  index = index ^ (((unsigned int) key -> op1) << 2);
  index = index ^ (((unsigned int) key -> op2) << 3);
  index = index ^ (((unsigned int) key -> op3) << 4);
  index = index ^ (((unsigned int) key -> mem) << 5);
  index = (index >> 2) % ht -> num_buckets;

  struct prefetch_bucket * curr = ht -> buckets[index];
  
  while (curr != NULL){
    if (curr -> key -> pc == key -> pc &&
	curr -> key -> ci == key -> ci &&
	curr -> key -> op1 == key -> op1 &&
	curr -> key -> op2 == key -> op2 &&	
	curr -> key -> op3 == key -> op3 &&
	curr -> key -> mem == key -> mem){
      return curr;
    }
    curr = curr -> next;
  }

  // Not found
  return NULL;
}

void ht_insert_prefetch(struct prefetch_ht * ht, operands_t * key, operands_t ** prefetch_ops, results_t ** prefetch_res, int num_target_rules){

  // Compute index
  unsigned int index = (unsigned int) key -> pc;
  index = index ^ (((unsigned int) key -> ci) << 1);
  index = index ^ (((unsigned int) key -> op1) << 2);
  index = index ^ (((unsigned int) key -> op2) << 3);
  index = index ^ (((unsigned int) key -> op3) << 4);
  index = index ^ (((unsigned int) key -> mem) << 5);
  index = (index >> 2) % ht -> num_buckets;
  
  // Make new bucket
  struct prefetch_bucket * new_bucket = malloc(sizeof(struct prefetch_bucket));
  new_bucket -> key = key;
  new_bucket -> num_rules = num_target_rules;
  new_bucket -> prefetch_ops = malloc(sizeof(operands_t*) * num_target_rules);
  new_bucket -> prefetch_res = malloc(sizeof(results_t*) * num_target_rules);  
  for (int i = 0; i < num_target_rules; i++){
    new_bucket -> prefetch_ops[i] = prefetch_ops[i];
    new_bucket -> prefetch_res[i] = prefetch_res[i];
  }
  new_bucket -> next = NULL;
  //new_bucket -> count = 1;

  // Increment object count
  ht -> stored_objects += 1;

  // Case 1: that bucket is empty. Insert and return.
  if (ht -> buckets[index] == NULL){
    ht -> buckets[index] = new_bucket;
    return;
  }

  // Case 2: that bucket is not empty. Add this to top, then return;
  struct prefetch_bucket * curr_head = ht -> buckets[index];
  ht -> buckets[index] = new_bucket;
  new_bucket -> next = curr_head;

}
