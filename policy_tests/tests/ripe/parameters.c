#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <limits.h>
#include <stdint.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include "parameters.h"

static bool output_debug_info = true;

static char *opt_techniques[] = 
  {"direct", "indirect"};
static char *opt_inject_params[] = 
  {"shellcode", "returnintolibc", "rop", "dataonly"};
static char *opt_code_ptrs[] = 
  {"ret", "funcptrstackvar", "funcptrstackparam",
   "funcptrheap", "funcptrbss", "funcptrdata",
   "longjmpstackvar", "longjmpstackparam",
   "longjmpheap", "longjmpbss", "longjmpdata",
   "structfuncptrstack","structfuncptrheap",
   "structfuncptrdata","structfuncptrbss", "bof", "iof", "leak"};
static char *opt_locations[] = 
  {"stack", "heap", "bss", "data"};
static char *opt_funcs[] = 
  {"memcpy", "strcpy", "strncpy", "sprintf", "snprintf",
   "strcat", "strncat", "sscanf", "homebrew"};

void
set_technique(char * choice, ripe_attack_form_t *attack)
{
  if (strcmp(choice, opt_techniques[0]) == 0) {
    attack->technique = DIRECT;
  } else if (strcmp(choice, opt_techniques[1]) == 0) {
    attack->technique = INDIRECT;
  } else {
    print_line("Unknown choice of technique");
  }
  print_debug("Technique: %d", attack->technique);
}
  
void
set_inject_param(char * choice, ripe_attack_form_t *attack)
{
  if (strcmp(choice, opt_inject_params[0]) == 0) {
    attack->inject_param = INJECTED_CODE_NO_NOP;
  } else if (strcmp(choice, opt_inject_params[1]) == 0) {
    attack->inject_param = RETURN_INTO_LIBC;
  } else if (strcmp(choice, opt_inject_params[2]) == 0) {
    attack->inject_param = RETURN_ORIENTED_PROGRAMMING;
  } else if (strcmp(choice, opt_inject_params[3]) == 0) {
    attack->inject_param = DATA_ONLY;
  } else {
    print_line("Unknown choice of injection parameter");
    exit(EXIT_FAILURE);
  }
  print_debug("Attack injection parameter: %d", attack->inject_param);
}

void
set_code_ptr(char * choice, ripe_attack_form_t *attack)
{
  if (strcmp(choice, opt_code_ptrs[0]) == 0) {
    attack->code_ptr = RET_ADDR;
  } else if (strcmp(choice, opt_code_ptrs[1]) == 0) {
    attack->code_ptr = FUNC_PTR_STACK_VAR;
  } else if (strcmp(choice, opt_code_ptrs[2]) == 0) {
    attack->code_ptr = FUNC_PTR_STACK_PARAM;
  } else if (strcmp(choice, opt_code_ptrs[3]) == 0) {
    attack->code_ptr = FUNC_PTR_HEAP;
  } else if (strcmp(choice, opt_code_ptrs[4]) == 0) {
    attack->code_ptr = FUNC_PTR_BSS;
  } else if (strcmp(choice, opt_code_ptrs[5]) == 0) {
    attack->code_ptr = FUNC_PTR_DATA;
  } else if (strcmp(choice, opt_code_ptrs[6]) == 0) {
    attack->code_ptr = LONGJMP_BUF_STACK_VAR;
  } else if (strcmp(choice, opt_code_ptrs[7]) == 0) {
    attack->code_ptr = LONGJMP_BUF_STACK_PARAM;
  } else if (strcmp(choice, opt_code_ptrs[8]) == 0) {
    attack->code_ptr = LONGJMP_BUF_HEAP;
  } else if (strcmp(choice, opt_code_ptrs[9]) == 0) {
    attack->code_ptr = LONGJMP_BUF_BSS;
  } else if (strcmp(choice, opt_code_ptrs[10]) == 0) {
    attack->code_ptr = LONGJMP_BUF_DATA;
  } else if (strcmp(choice, opt_code_ptrs[11]) == 0) {
    attack->code_ptr = STRUCT_FUNC_PTR_STACK;
  } else if (strcmp(choice, opt_code_ptrs[12]) == 0) {
    attack->code_ptr = STRUCT_FUNC_PTR_HEAP;
  } else if (strcmp(choice, opt_code_ptrs[13]) == 0) {
    attack->code_ptr = STRUCT_FUNC_PTR_DATA;
  } else if (strcmp(choice, opt_code_ptrs[14]) == 0) {
    attack->code_ptr = STRUCT_FUNC_PTR_BSS;
  } else if (strcmp(choice, opt_code_ptrs[15]) == 0) {
    attack->code_ptr = VAR_BOF;
  } else if (strcmp(choice, opt_code_ptrs[16]) == 0) {
    attack->code_ptr = VAR_IOF;
  } else if (strcmp(choice, opt_code_ptrs[17]) == 0) {
    attack->code_ptr = VAR_LEAK;
  } else {
    print_line("Unknown choice of code pointer");
    exit(EXIT_FAILURE);
  }
  print_debug("Code pointer: %d", attack->code_ptr);
}

void
set_location(char * choice, ripe_attack_form_t *attack)
{
  if (strcmp(choice, opt_locations[0]) == 0) {
    attack->location = STACK;
  } else if (strcmp(choice, opt_locations[1]) == 0) {
    attack->location = HEAP;
  } else if (strcmp(choice, opt_locations[2]) == 0) {
    attack->location = BSS;
  } else if (strcmp(choice, opt_locations[3]) == 0) {
    attack->location = DATA;
  } else {
    print_line("Unknown choice of memory location");
    exit(EXIT_FAILURE);
  }
  print_debug("Memory location: %d", attack->location);
}

void
set_function(char * choice, ripe_attack_form_t *attack)
{
  if (strcmp(choice, opt_funcs[0]) == 0) {
    attack->function = MEMCPY;
  } else if (strcmp(choice, opt_funcs[1]) == 0) {
    attack->function = STRCPY;
  } else if (strcmp(choice, opt_funcs[2]) == 0) {
    attack->function = STRNCPY;
  } else if (strcmp(choice, opt_funcs[3]) == 0) {
    attack->function = SPRINTF;
  } else if (strcmp(choice, opt_funcs[4]) == 0) {
    attack->function = SNPRINTF;
  } else if (strcmp(choice, opt_funcs[5]) == 0) {
    attack->function = STRCAT;
  } else if (strcmp(choice, opt_funcs[6]) == 0) {
    attack->function = STRNCAT;
  } else if (strcmp(choice, opt_funcs[7]) == 0) {
    attack->function = SSCANF;
  } else if (strcmp(choice, opt_funcs[8]) == 0) {
    attack->function = HOMEBREW;
  } else {
    print_line("Unknown choice of vulnerable function");
    exit(EXIT_FAILURE);
  }
  print_debug("Vulnerable function: %d", attack->function);
}

bool
is_attack_possible(ripe_attack_form_t attack)
{
  if ((attack.inject_param == INJECTED_CODE_NO_NOP) &&
      (attack.function != MEMCPY && attack.function != HOMEBREW))
  {
    print_line("Impossible to inject shellcode with string functions");
    return false;
  }

  if (attack.inject_param == RETURN_ORIENTED_PROGRAMMING &&
      attack.technique != DIRECT)
  {
    print_line("Impossible to perform indirect ROP attacks");
    return false;
  }

  if (attack.inject_param == DATA_ONLY) {
    if (attack.code_ptr != VAR_BOF &&
        attack.code_ptr != VAR_IOF &&
        attack.code_ptr != VAR_LEAK)
    {
      print_line("Misused data only code pointe parameters");
      return false;
    }

    if ((attack.code_ptr == VAR_LEAK || attack.code_ptr == VAR_IOF) && attack.technique == INDIRECT) {
      print_line("Impossible to perform an indirect integer overflow attack");
      return false;
    }

    if (attack.location == HEAP && attack.technique == INDIRECT) {
      print_line("Impossible to indirect attack the heap flag");
      return false;
    }
  } else if (attack.code_ptr == VAR_BOF ||
      attack.code_ptr == VAR_IOF ||
      attack.code_ptr == VAR_LEAK) {
    print_line("Error: Must use \"dataonly\" injection parameter for DOP attacks.");
    return false;
  }

  switch (attack.location) {
    case STACK:
      if (attack.technique == DIRECT) {
        if ((attack.code_ptr == FUNC_PTR_HEAP) ||
            (attack.code_ptr == FUNC_PTR_BSS) ||
            (attack.code_ptr == FUNC_PTR_DATA) ||
            (attack.code_ptr == LONGJMP_BUF_HEAP) ||
            (attack.code_ptr == LONGJMP_BUF_DATA) ||
            (attack.code_ptr == LONGJMP_BUF_BSS) ||
            (attack.code_ptr == STRUCT_FUNC_PTR_HEAP) ||
            (attack.code_ptr == STRUCT_FUNC_PTR_DATA) ||
            (attack.code_ptr == STRUCT_FUNC_PTR_BSS) )
        {
          print_line("Impossible to perform a direct attack on the stack into another memory segment.");
          return false;
        } else if ((attack.code_ptr == FUNC_PTR_STACK_PARAM) &&
            ((attack.function == STRCAT) ||
             (attack.function == SNPRINTF) ||
             (attack.function == SSCANF) ||
             (attack.function == HOMEBREW)))
        {
          print_line("Impossible to attack the stack parameter directly with the following functions: strcat(), snprintf(), sscanf(), homebrew_memcpy()");
          return false;
        }
      }
      break;

    case HEAP:
      if ((attack.technique == DIRECT) &&
          ((attack.code_ptr == RET_ADDR) ||
           (attack.code_ptr == FUNC_PTR_STACK_VAR) ||
           (attack.code_ptr == FUNC_PTR_STACK_PARAM) ||
           (attack.code_ptr == FUNC_PTR_BSS) ||
           (attack.code_ptr == FUNC_PTR_DATA) ||
           (attack.code_ptr == LONGJMP_BUF_STACK_VAR) ||
           (attack.code_ptr == LONGJMP_BUF_STACK_PARAM) ||
           (attack.code_ptr == LONGJMP_BUF_BSS) ||
           (attack.code_ptr == LONGJMP_BUF_DATA) ||
           (attack.code_ptr == STRUCT_FUNC_PTR_STACK) ||
           (attack.code_ptr == STRUCT_FUNC_PTR_DATA) ||
           (attack.code_ptr == STRUCT_FUNC_PTR_BSS) ))
      {
        print_line("Impossible to perform a direct attack on the heap into another memory segment");
        return false;
      }
      break;

    case DATA:
      if ((attack.technique == DIRECT) &&
          ((attack.code_ptr == RET_ADDR) ||
           (attack.code_ptr == FUNC_PTR_STACK_VAR) ||
           (attack.code_ptr == FUNC_PTR_STACK_PARAM) ||
           (attack.code_ptr == FUNC_PTR_BSS) ||
           (attack.code_ptr == FUNC_PTR_HEAP) ||
           (attack.code_ptr == LONGJMP_BUF_STACK_VAR) ||
           (attack.code_ptr == LONGJMP_BUF_STACK_PARAM) ||
           (attack.code_ptr == LONGJMP_BUF_HEAP) ||
           (attack.code_ptr == LONGJMP_BUF_BSS) ||
           (attack.code_ptr == STRUCT_FUNC_PTR_STACK) ||
           (attack.code_ptr == STRUCT_FUNC_PTR_HEAP) ||
           (attack.code_ptr == STRUCT_FUNC_PTR_BSS) ))
      {
        print_line("Impossible to perform a direct attack on the data segment into another memory segment");
        return false;
      }
      break;


    case BSS:
      if ((attack.technique == DIRECT) &&
          ((attack.code_ptr == RET_ADDR) ||
           (attack.code_ptr == FUNC_PTR_STACK_VAR) ||
           (attack.code_ptr == FUNC_PTR_STACK_PARAM) ||
           (attack.code_ptr == FUNC_PTR_DATA) ||
           (attack.code_ptr == FUNC_PTR_HEAP) ||
           (attack.code_ptr == LONGJMP_BUF_STACK_VAR) ||
           (attack.code_ptr == LONGJMP_BUF_STACK_PARAM) ||
           (attack.code_ptr == LONGJMP_BUF_HEAP) ||
           (attack.code_ptr == LONGJMP_BUF_DATA) ||
           (attack.code_ptr == STRUCT_FUNC_PTR_STACK) ||
           (attack.code_ptr == STRUCT_FUNC_PTR_HEAP) ||
           (attack.code_ptr == STRUCT_FUNC_PTR_DATA) ))
      {
        print_line("Impossible to perform a direct attack on the bss into another memory segment");
        return false;
      } else if ((attack.technique == INDIRECT) &&
          (attack.code_ptr == LONGJMP_BUF_HEAP) &&
          (!(attack.function == MEMCPY) &&
           !(attack.function == STRNCPY) &&
           !(attack.function == HOMEBREW)))
      {
        print_line("Impossible to perform BSS->Heap Longjmp attacks using string functions");
        return false;
      }
      break;
  }

  return true;
}
