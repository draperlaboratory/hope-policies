#ifndef RIPE_TYPES_H
#define RIPE_TYPES_H

#include <setjmp.h>

#define STACK_PARAMETER_FUNCTION(_type, _name, ...)                            \
  _type _name(int _arg0, int _arg1, int _arg2, int _arg3,                      \
              int _arg4, int _arg5, int _arg6, int _arg7,                      \
              __VA_ARGS__)

#define STACK_PARAMETER_CALL(_name, ...)                                       \
  _name(0, 0, 0, 0, 0, 0, 0, 0, __VA_ARGS__)

#define INITIALIZE_BUFFER(_buffer) _buffer[0] = 'a'

#define print_line(_format, ...)                                               \
  printf(_format, ##__VA_ARGS__);                                              \
  printf("\n");

#define print_debug(_format, ...)                                              \
  if(output_debug_info == true) {                                              \
    print_line(_format, ##__VA_ARGS__);                                        \
  }

/* Enumerations for typing of attack form parameters                        */
/* Each enumeration has its own integer space to provide better type safety */
enum techniques {DIRECT=100, INDIRECT};
enum inject_params {
  INJECTED_CODE_NO_NOP=200, RETURN_INTO_LIBC,
  RETURN_ORIENTED_PROGRAMMING, DATA_ONLY};
enum code_ptrs {
  RET_ADDR=300, FUNC_PTR_STACK_VAR, FUNC_PTR_STACK_PARAM,
  FUNC_PTR_HEAP, FUNC_PTR_BSS, FUNC_PTR_DATA,
  LONGJMP_BUF_STACK_VAR, LONGJMP_BUF_STACK_PARAM,
  LONGJMP_BUF_HEAP, LONGJMP_BUF_BSS, LONGJMP_BUF_DATA,
  STRUCT_FUNC_PTR_STACK,STRUCT_FUNC_PTR_HEAP,
  STRUCT_FUNC_PTR_DATA,STRUCT_FUNC_PTR_BSS, VAR_BOF, VAR_IOF, VAR_LEAK};
enum locations {STACK=400, HEAP, BSS, DATA};
enum functions {
  MEMCPY=500, STRCPY, STRNCPY, SPRINTF, SNPRINTF,
  STRCAT, STRNCAT, SSCANF, HOMEBREW};

typedef struct attack_form {
        enum techniques technique;
        enum inject_params inject_param;
        enum code_ptrs code_ptr;
        enum locations location;
        enum functions function;
} ripe_attack_form_t;

typedef struct payload {
        enum inject_params inject_param;
        size_t size;
        void *overflow_ptr; /* Points to code pointer (direct attack) */
                            /* or general pointer (indirect attack)   */
        char *buffer;

        jmp_buf *jmp_buffer;

        uintptr_t stack_jmp_buffer_param;
        size_t offset_to_copied_base_ptr;
        size_t offset_to_fake_return_addr;
        uintptr_t *fake_return_addr;
        uintptr_t *ptr_to_correct_return_addr;
} ripe_payload_t;

typedef struct vulnerable_struct {
        char buffer[256];
        int (*func_ptr)(const char *);
} ripe_vulnerable_struct_t;

#endif // RIPE_TYPES_H
