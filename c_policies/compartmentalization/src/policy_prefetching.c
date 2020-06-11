#include "rule_IO.c"

int prefetching_enabled = 0;

// This file contains the logic to read in a prefetching policy (.pp) file.

// These are the hooks into the validator that the prefetching logic needs.
// Weak symbols so these are overwritten by the linking into final executable.
void
__attribute__((weak))
prefetch_rule(operands_t * ops, results_t * res){
}

void load_prefetching_policy(){
  
  FILE * infile = fopen("prefetch.pp", "rb");
  
  if (infile == NULL){
    printm("No prefetching.");
    return;
  } else {
    printm("Found prefetching file...");
    prefetching_enabled = 1;
    prefetch_ht = ht_create_prefetch(HT_PREFETCH_SIZE);
  }

  int ops_size;
  int res_size;

  fread(&ops_size, sizeof(ops_size), 1, infile);
  fread(&res_size, sizeof(res_size), 1, infile);

  printm("Read sizes from start of file: %d %d", ops_size, res_size);
  printm("My struct sizes: %d %d", sizeof(operands_t), sizeof(results_t));

  char rule1[2048];
  char rule2[2048];

  // Note: okay, so operands_t just has pointers to meta_set
  // so this is close but needs 1 more layer!
  int read_rules = 0;
  while (1){

    // Read structures out from the file
    operands_t * base_ops = load_operands_from_file(infile);
    operands_t * next_ops = load_operands_from_file(infile);
    results_t * res = load_results_from_file(infile);

    // If reading failed, then we're at EOF so exit
    if (base_ops != NULL && next_ops != NULL && res != NULL){
      //pretty_print_rule(rule1, base_ops -> ci, base_ops -> op1, base_ops -> op2, base_ops -> mem, base_ops -> pc);
      //pretty_print_rule(rule2, next_ops -> ci, next_ops -> op1, next_ops -> op2, next_ops -> mem, next_ops -> pc);
      //printm("Read prefetching rule: %s -> %s", rule1, rule2);
      //printm("\t Res: %p %p %p %d %d %d", res -> pc, res -> rd, res -> csr, res -> pcResult, res -> rdResult, res -> csrResult);
      ht_insert_prefetch(prefetch_ht, base_ops, next_ops, res);	
      read_rules += 1;
    } else {
      printm("Done reading prefetch file. Read %d prefetching rules.", read_rules);
      break;
    }
  }
}
