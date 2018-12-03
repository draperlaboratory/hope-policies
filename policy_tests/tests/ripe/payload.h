#ifndef RIPE_PAYLOAD_H
#define RIPE_PAYLOAD_H

#include <stdbool.h>

#include "ripe_types.h"

/* BUILD_PAYLOAD()                                                  */
/*                                                                  */
/* Simplified example of payload (exact figures are just made up):  */
/*                                                                  */
/*   size      = 31 (the total payload size)                        */
/*   size_sc   = 12 (size of shellcode incl NOP)                    */
/*   size_addr = 4  (size of address to code)                       */
/*   size_null = 1  (size of null termination)                      */
/*                                                                  */
/*    ------------ ----------------- ------------- -                */
/*   | Shell code | Padded bytes    | Address     |N|               */
/*   | including  |                 | back to     |u|               */
/*   | optional   |                 | NOP sled or |l|               */
/*   | NOP sled   |                 | shell code  |l|               */
/*    ------------ ----------------- ------------- -                */
/*    |          | |               | |           | |                */
/*    0         11 12             25 26         29 30               */
/*              /   \             /   \             \               */
/*     size_sc-1     size_sc     /     \             size-size_null */
/*                              /       \                           */
/*  (size-1)-size_addr-size_null         size-size_addr-size_null   */
/*                                                                  */
/* This means that we should pad with                               */
/* size - size_sc - size_addr - size_null = 31-12-4-1 = 14 bytes    */
/* and start the padding at index size_sc                           */
bool build_payload(ripe_payload_t *payload, ripe_attack_form_t attack, char *shellcode, size_t shellcode_length);

/*
RIPE shellcode uses the following instructions:
la <reg>, <addr of shellcode_func()>
jalr <reg>

The first la instruction is disassembled to:
lui <reg>, <upper 20 bits>
addi <reg>, <reg>, <lower 12 bits>

Thus, the shellcode follows the pattern
shown in the following encodings:

LUI: xxxx xxxx xxxx xxxx xxxx xxxx x011 0111
     \                  / \    /\      /
             imm value         reg#  opcode


ADDI: xxxx xxxx xxxx xxxx x000 xxxx x011 0011
      \        / \    /    \    /\      /
        imm value     reg#      reg#  opcode


JALR: 0000 0000 0000 xxxx x000 0000 1110 0111
                     \    /          \      /
                      reg#            opcode

The shellcode is formatted so that:
  1. All instructions are stored to a single string
  1. Byte order is converted to little-endian
*/
void build_shellcode(char *shellcode);

#endif // RIPE_PAYLOAD_H
