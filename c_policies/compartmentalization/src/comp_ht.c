// Hashtable implementation for compartment learning policy, see comp_ht.h

#include <stdlib.h>
#include <stdio.h>

struct comp_ht * ht_create(int size){
  struct comp_ht * new_ht = malloc(sizeof(struct comp_ht));
  memset(new_ht, 0, sizeof(struct comp_ht));
  new_ht -> num_buckets = size;
  new_ht -> buckets = malloc(sizeof(struct comp_bucket *) * new_ht -> num_buckets);
  memset(new_ht -> buckets, 0, sizeof(struct comp_bucket *) * new_ht -> num_buckets);
  return new_ht;
}

struct comp_bucket * ht_lookup(struct comp_ht * ht, int src, int dest, int edge_type){

  // Compute index
  int index = ((src << 8) ^ dest ^ edge_type) % ht -> num_buckets;

  struct comp_bucket * curr = ht -> buckets[index];
  
  while (curr != NULL){
    // Check to see if found
    if (curr -> src == src &&
	curr -> dest == dest &&
	curr -> edge_type == edge_type){
      curr -> count += 1;
      return curr;
    }
    curr = curr -> next;
  }

  // Not found
  return NULL;
}

void ht_insert(struct comp_ht * ht, int src, int dest, int edge_type){

  // Compute index
  int index = ((src << 8) ^ dest ^ edge_type) % ht -> num_buckets;

  // Make new bucket
  struct comp_bucket * new_bucket = malloc(sizeof(struct comp_bucket));
  new_bucket -> src = src;
  new_bucket -> dest = dest;
  new_bucket -> edge_type = edge_type;
  new_bucket -> next = NULL;
  new_bucket -> count = 1;

  // Increment object count
  ht -> stored_objects += 1; 
  ht -> new_additions += 1; 
  switch (edge_type){
  case EDGE_READ:
    ht -> reads++; break;
  case EDGE_WRITE:
    ht -> writes++; break;
  case EDGE_CALL:
    ht -> calls++; break;
  case EDGE_RETURN:
    ht -> returns++; break;
  }

  // Print new count if not loading from CAPMAP file
  if (ht -> initialized){

#ifdef DEBUG
    printm("Total interactions captured = %d", ht -> stored_objects);
    printm("Reads=%d, writes=%d, calls=%d, returns=%d",
	   ht -> reads, ht -> writes, ht -> calls, ht -> returns);
#endif
  }

  // Case 1: that bucket is empty. Insert and return.
  if (ht -> buckets[index] == NULL){
    ht -> buckets[index] = new_bucket;
    return;
  }

  // Case 2: that bucket is not empty. Add this to top, then return;
  struct comp_bucket * curr_head = ht -> buckets[index];
  ht -> buckets[index] = new_bucket;
  new_bucket -> next = curr_head;

}

// Dump the CAPMAP data for a specific function.
// Print calls, then returns, then reads, then writes
void print_func_data(struct comp_ht * ht, int func, int weights, FILE * outfile){

  int b;
  struct comp_bucket * bucket;

  fprintf(outfile, "%s\n", func_defs[func]);
  
  // Calls
  for (b = 0; b < ht -> num_buckets; b++){
    bucket = ht -> buckets[b];
    while (bucket != NULL){
      if (bucket -> edge_type == EDGE_CALL && bucket -> src == func){
	if (weights)
	  fprintf(outfile, "\tCall %s %d\n", func_defs[bucket -> dest], bucket -> count);
	else
	  fprintf(outfile, "\tCall %s\n", func_defs[bucket -> dest]);
      }
      bucket = bucket -> next;
    }
  }

  // Returns
  for (b = 0; b < ht -> num_buckets; b++){
    bucket = ht -> buckets[b];
    while (bucket != NULL){
      if (bucket -> edge_type == EDGE_RETURN && bucket -> src == func){
	if (weights)
	  fprintf(outfile, "\tReturn %s %d\n", func_defs[bucket -> dest], bucket -> count);
	else
	  fprintf(outfile, "\tReturn %s\n", func_defs[bucket -> dest]);
      }
      bucket = bucket -> next;
    }
  }

  // Reads
  for (b = 0; b < ht -> num_buckets; b++){
    bucket = ht -> buckets[b];
    while (bucket != NULL){
      if (bucket -> edge_type == EDGE_READ && bucket -> src == func){
	if (weights)
	  fprintf(outfile, "\tRead %s %d\n", object_defs[bucket -> dest], bucket -> count);
	else
	  fprintf(outfile, "\tRead %s\n", object_defs[bucket -> dest]);
      }
      bucket = bucket -> next;
    }
  }

  // Writes
  for (b = 0; b < ht -> num_buckets; b++){
    bucket = ht -> buckets[b];
    while (bucket != NULL){
      if (bucket -> edge_type == EDGE_WRITE && bucket -> src == func){
	if (weights)
	  fprintf(outfile, "\tWrite %s %d\n", object_defs[bucket -> dest], bucket -> count);
	else
	  fprintf(outfile, "\tWrite %s\n", object_defs[bucket -> dest]);
      }
      bucket = bucket -> next;
    }
  } 
}
