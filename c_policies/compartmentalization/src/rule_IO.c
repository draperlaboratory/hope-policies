extern operands_t *
__attribute__((weak))
  canonize_and_make_operands(meta_set_t * pc, meta_set_t * ci, meta_set_t * op1, meta_set_t * op2, meta_set_t * op3, meta_set_t * mem){
  return NULL;
}

extern operands_t *
__attribute__((weak))
  canonize_and_make_results(meta_set_t * pc, meta_set_t * rd, meta_set_t * csr, bool pcResult, bool rdResult, bool csrResult){
  return NULL;
}

void set_null_if_buffer_empty(char * buff, int buff_size, meta_set_t ** ptr){
  
  bool is_null = 1;
  for (int i = 0; i < buff_size; i++){
    if (buff[i] != 'A'){
      is_null = 0;
    }
  }

  if (is_null)
    *ptr = NULL;
}

// Load in the meta_set_ts for an operands_t in binary form, then canonicalize and return
// If all are empty, return a NULL
operands_t * load_operands_from_file(FILE * f){
  //printf("Loading operands from file.\n");
  int read = 0;
  meta_set_t pc, ci, op1, op2, op3, mem;
  meta_set_t *pc_ptr, *ci_ptr, *op1_ptr, *op2_ptr, *op3_ptr, *mem_ptr;
  pc_ptr = &pc;
  ci_ptr = &ci;
  op1_ptr = &op1;
  op2_ptr = &op2;
  op3_ptr = &op3;
  mem_ptr = &mem;  
  read += fread(&pc, sizeof(meta_set_t), 1, f);
  read += fread(&ci, sizeof(meta_set_t), 1, f);
  read += fread(&op1, sizeof(meta_set_t), 1, f);
  read += fread(&op2, sizeof(meta_set_t), 1, f);
  read += fread(&op3, sizeof(meta_set_t), 1, f);
  read += fread(&mem, sizeof(meta_set_t), 1, f);
  if (read != 6){
    //printf("Didn't read enough.\n");
    return NULL;
  }
  set_null_if_buffer_empty(&pc, sizeof(meta_set_t), &pc_ptr);
  set_null_if_buffer_empty(&ci, sizeof(meta_set_t), &ci_ptr);
  set_null_if_buffer_empty(&op1, sizeof(meta_set_t), &op1_ptr);
  set_null_if_buffer_empty(&op2, sizeof(meta_set_t), &op2_ptr);
  set_null_if_buffer_empty(&op3, sizeof(meta_set_t), &op3_ptr);
  set_null_if_buffer_empty(&mem, sizeof(meta_set_t), &mem_ptr);
  if (pc_ptr == NULL &&
      ci_ptr == NULL &&
      op1_ptr == NULL &&
      op2_ptr == NULL &&
      op3_ptr == NULL &&
      mem_ptr == NULL){
    return NULL;
  }
  operands_t * ops = canonize_and_make_operands(pc_ptr, ci_ptr, op1_ptr, op2_ptr, op3_ptr, mem_ptr);
  return ops;
}

// Load in the meta_set_ts for a results_t in binary form, then canonicalize and return
results_t * load_results_from_file(FILE * f){
  //printf("Loading results from file.\n");  
  int read = 0;
  meta_set_t pc, rd, csr;
  meta_set_t *pc_ptr, *rd_ptr, *csr_ptr;
  pc_ptr = &pc;
  rd_ptr = &rd;
  csr_ptr = &csr;
  bool pcResult, rdResult, csrResult;

  // Read in the three meta_sets
  read += fread(&pc, sizeof(meta_set_t), 1, f);
  read += fread(&rd, sizeof(meta_set_t), 1, f);
  read += fread(&csr, sizeof(meta_set_t), 1, f);
  if (read != 3)
    return NULL;
  set_null_if_buffer_empty(&pc, sizeof(meta_set_t), &pc_ptr);
  set_null_if_buffer_empty(&rd, sizeof(meta_set_t), &rd_ptr);
  set_null_if_buffer_empty(&csr, sizeof(meta_set_t), &csr_ptr);

  // Then load in the 3 booleans
  read = fread(&pcResult, sizeof(bool), 1, f);
  read += fread(&rdResult, sizeof(bool), 1, f);
  read += fread(&csrResult, sizeof(bool), 1, f);
  if (read != 3)
    return NULL;

  // Null if all results ptrs are null?
  if (pc_ptr == NULL &&
      rd_ptr == NULL &&
      csr_ptr == NULL){
    return NULL;
  }

  results_t * res = canonize_and_make_results(pc_ptr, rd_ptr, csr_ptr, pcResult, rdResult, csrResult);
  return res;
}
