#include "policy_utils.h"
#include "policy_meta.h"
#include "policy_meta_set.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <inttypes.h>

extern void printm(const char* s, ...);


int meta_args_to_string(const meta_set_t *ts, int i, char *buf, size_t buf_len)
{
    int printed = 0;
    
    switch (i) {
        
      case 16:
        printed = printed;
        // Parsing bug in quasiquoter requires this
        ;
        //printed += snprintf(buf, buf_len - printed, " 0x%x", (unsigned int) ts->tags[3]);
        printed += snprintf(buf, buf_len - printed, " %s", object_defs[ts -> tags[3]]);	
        if (printed >= buf_len)
            return printed;
        break;
        
      case 17:
        printed = printed;
        // Parsing bug in quasiquoter requires this
        ;
        printed += snprintf(buf, buf_len - printed, " 0x%x", (unsigned int) ts->tags[4]);
        if (printed >= buf_len)
            return printed;
        break;

    }
    return printed;
}
int meta_to_string(meta_t tag, const meta_set_t * ts, char *buf, size_t buf_len)
{
    if (buf == NULL || buf_len <= 0)
        return 0;

    
    switch (tag) {
        
      case osv_heap_Cell:
        if (buf_len <= 4) {
            buf[0] = '\0';
            return 1 + 4;
        } else {
            strncpy(buf, "Cell", 1 + 4);
            return 4;
        }
        
      case osv_heap_Pointer:
        if (buf_len <= 7) {
            buf[0] = '\0';
            return 1 + 7;
        } else {
            strncpy(buf, "Pointer", 1 + 7);
            return 7;
        }
        
      case osv_heap_RawHeap:
        if (buf_len <= 7) {
            buf[0] = '\0';
            return 1 + 7;
        } else {
            strncpy(buf, "RawHeap", 1 + 7);
            return 7;
        }
        
      case osv_heap_ApplyColor:
        if (buf_len <= 10) {
            buf[0] = '\0';
            return 1 + 10;
        } else {
            strncpy(buf, "ApplyColor", 1 + 10);
            return 10;
        }
        
      case osv_heap_RemoveColor:
        if (buf_len <= 11) {
            buf[0] = '\0';
            return 1 + 11;
        } else {
            strncpy(buf, "RemoveColor", 1 + 11);
            return 11;
        }
        
      case osv_heap_NewColor:
        if (buf_len <= 8) {
            buf[0] = '\0';
            return 1 + 8;
        } else {
            strncpy(buf, "NewColor", 1 + 8);
            return 8;
        }
        
      case osv_heap_DelColor:
        if (buf_len <= 8) {
            buf[0] = '\0';
            return 1 + 8;
        } else {
            strncpy(buf, "DelColor", 1 + 8);
            return 8;
        }
        
      case osv_heap_ModColor:
        if (buf_len <= 8) {
            buf[0] = '\0';
            return 1 + 8;
        } else {
            strncpy(buf, "ModColor", 1 + 8);
            return 8;
        }
        
      case osv_heap_AntiPointer:
        if (buf_len <= 11) {
            buf[0] = '\0';
            return 1 + 11;
        } else {
            strncpy(buf, "AntiPointer", 1 + 11);
            return 11;
        }
        
      case osv_heap_SpecialCaseVFPRINTF:
        if (buf_len <= 19) {
            buf[0] = '\0';
            return 1 + 19;
        } else {
            strncpy(buf, "SpecialCaseVFPRINTF", 1 + 19);
            return 19;
        }
        
      case osv_riscv_og_branchGrp:
        if (buf_len <= 9) {
            buf[0] = '\0';
            return 1 + 9;
        } else {
            strncpy(buf, "branchGrp", 1 + 9);
            return 9;
        }
        
      case osv_riscv_og_jumpRegGrp:
        if (buf_len <= 10) {
            buf[0] = '\0';
            return 1 + 10;
        } else {
            strncpy(buf, "jumpRegGrp", 1 + 10);
            return 10;
        }
        
      case osv_riscv_og_jumpGrp:
        if (buf_len <= 7) {
            buf[0] = '\0';
            return 1 + 7;
        } else {
            strncpy(buf, "jumpGrp", 1 + 7);
            return 7;
        }
        
      case osv_riscv_og_loadUpperGrp:
        if (buf_len <= 12) {
            buf[0] = '\0';
            return 1 + 12;
        } else {
            strncpy(buf, "loadUpperGrp", 1 + 12);
            return 12;
        }
        
      case osv_riscv_og_andiGrp:
        if (buf_len <= 7) {
            buf[0] = '\0';
            return 1 + 7;
        } else {
            strncpy(buf, "andiGrp", 1 + 7);
            return 7;
        }
        
      case osv_riscv_og_immArithGrp:
        if (buf_len <= 11) {
            buf[0] = '\0';
            return 1 + 11;
        } else {
            strncpy(buf, "immArithGrp", 1 + 11);
            return 11;
        }
        
      case osv_riscv_og_arithGrp:
        if (buf_len <= 8) {
            buf[0] = '\0';
            return 1 + 8;
        } else {
            strncpy(buf, "arithGrp", 1 + 8);
            return 8;
        }
        
      case osv_riscv_og_loadGrp:
        if (buf_len <= 7) {
            buf[0] = '\0';
            return 1 + 7;
        } else {
            strncpy(buf, "loadGrp", 1 + 7);
            return 7;
        }
        
      case osv_riscv_og_storeGrp:
        if (buf_len <= 8) {
            buf[0] = '\0';
            return 1 + 8;
        } else {
            strncpy(buf, "storeGrp", 1 + 8);
            return 8;
        }
        
      case osv_riscv_og_mulDivRemGrp:
        if (buf_len <= 12) {
            buf[0] = '\0';
            return 1 + 12;
        } else {
            strncpy(buf, "mulDivRemGrp", 1 + 12);
            return 12;
        }
        
      case osv_riscv_og_csrGrp:
        if (buf_len <= 6) {
            buf[0] = '\0';
            return 1 + 6;
        } else {
            strncpy(buf, "csrGrp", 1 + 6);
            return 6;
        }
        
      case osv_riscv_og_csriGrp:
        if (buf_len <= 7) {
            buf[0] = '\0';
            return 1 + 7;
        } else {
            strncpy(buf, "csriGrp", 1 + 7);
            return 7;
        }
        
    case osv_riscv_og_privGrp:
      if (buf_len <= 7) {
	buf[0] = '\0';
	return 1 + 7;
      } else {
	strncpy(buf, "privGrp", 1 + 7);
	return 7;
      }
      case osv_threeClass_Call_Tgt:
        if (buf_len <= 8) {
            buf[0] = '\0';
            return 1 + 8;
        } else {
            strncpy(buf, "Call-Tgt", 1 + 8);
            return 8;
        }
        
      case osv_threeClass_Return_Tgt:
        if (buf_len <= 10) {
            buf[0] = '\0';
            return 1 + 10;
        } else {
            strncpy(buf, "Return-Tgt", 1 + 10);
            return 10;
        }
        
      case osv_threeClass_Branch_Tgt:
        if (buf_len <= 10) {
            buf[0] = '\0';
            return 1 + 10;
        } else {
            strncpy(buf, "Branch-Tgt", 1 + 10);
            return 10;
        }
        
      case osv_threeClass_Call_Instr:
        if (buf_len <= 10) {
            buf[0] = '\0';
            return 1 + 10;
        } else {
	  if (ts -> tags[4] != 0){
	    sprintf(buf, "Call-Instr (alloc-%d)", ts -> tags[4]);
	    return strlen(buf);
	  } else {
            strncpy(buf, "Call-Instr", 1 + 10);
            return 10;
	  }
        }
        
      case osv_threeClass_Return_Instr:
        if (buf_len <= 12) {
            buf[0] = '\0';
            return 1 + 12;
        } else {
            strncpy(buf, "Return-Instr", 1 + 12);
            return 12;
        }
        
      case osv_threeClass_Branch_Instr:
        if (buf_len <= 12) {
            buf[0] = '\0';
            return 1 + 12;
        } else {
            strncpy(buf, "Branch-Instr", 1 + 12);
            return 12;
        }
        
      case osv_threeClass_Jumping_Call:
        if (buf_len <= 12) {
            buf[0] = '\0';
            return 1 + 12;
        } else {
            strncpy(buf, "Jumping-Call", 1 + 12);
            return 12;
        }
        
      case osv_threeClass_Jumping_Return:
        if (buf_len <= 14) {
            buf[0] = '\0';
            return 1 + 14;
        } else {
            strncpy(buf, "Jumping-Return", 1 + 14);
            return 14;
        }
        
      case osv_threeClass_Jumping_Branch:
        if (buf_len <= 14) {
            buf[0] = '\0';
            return 1 + 14;
        } else {
            strncpy(buf, "Jumping-Branch", 1 + 14);
            return 14;
        }
        
      case osv_threeClass_NoCFI:
        if (buf_len <= 5) {
            buf[0] = '\0';
            return 1 + 5;
        } else {
            strncpy(buf, "NoCFI", 1 + 5);
            return 5;
        }
        
    case osv_threeClass_Jumping_NoCFI:
      if (buf_len <= 13) {
	buf[0] = '\0';
	return 1 + 13;
      } else {
	strncpy(buf, "Jumping-NoCFI", 1 + 13);
            return 13;
      }
    case osv_Comp_special_obj_IO:
      sprintf(buf, "SPECIAL-IO");
      return strlen(buf);
    case osv_Comp_special_obj_RAM:
      sprintf(buf, "SPECIAL-RAM");
      return strlen(buf);      
    case osv_Comp_special_obj_FLASH:
      sprintf(buf, "SPECIAL-FLASH");
      return strlen(buf);
    case osv_Comp_special_obj_UART:
      sprintf(buf, "SPECIAL-UART");
      return strlen(buf);
    case osv_Comp_special_obj_PLIC:
      sprintf(buf, "SPECIAL-PLIC");
      return strlen(buf);
    case osv_Comp_special_obj_ETHERNET:
      sprintf(buf, "SPECIAL-ETHERNET");
      return strlen(buf);      
    case osv_Comp_context_switch:
      sprintf(buf, "context-switch");
      return strlen(buf);
    case osv_Comp_funcID:
      // If we have defs, use those. Otherwise just print ID.
      if (func_defs != 0){
	sprintf(buf, "func-%s", func_defs[ts -> tags[2]]);	
      } else {
	sprintf(buf, "func-%d", ts -> tags[2]);
      }
      return strlen(buf);
      
    case osv_Comp_globalID:
      // If we have global defs, us those. Otherwise just print ID.
      if (object_defs != 0){
	sprintf(buf, "%s", object_defs[ts -> tags[2]]);	
      } else {
	sprintf(buf, "global-%d", ts -> tags[2]);
      }
      return strlen(buf);
      
    default:
      sprintf(buf, "<unknown tag %x>", tag);
      return strlen(buf);
    }
    return 0;
}
int meta_set_to_string(const meta_set_t *ts, char *buf, size_t buf_len)
{
    char *cursor = buf;
    int consumed = 0;
    
    // These variables keep track of where we are in the buffer and how many
    if (buf == NULL || buf_len <= 0)
        // Check for NULL input or tiny buffers
        return 1;
    if (buf_len <= 2) {
        buf[0] = '\0';
        return 3;
    }
    if (ts == 0) {
        strncpy(buf, "-0-", 4);
        return 4;
    }
    cursor[0] = '{';
    cursor++;
    consumed++;

    if (ts -> tags[2] != 0 || ts ->tags[3] != 0 || ts ->tags[4] != 0){
      char tmpbuff[128];
      sprintf(tmpbuff, "Args: %x %x %x ", ts ->tags[2], ts ->tags[3], ts->tags[4]);
      strcpy(cursor, tmpbuff);
      cursor += strlen(tmpbuff);
    } else {
      strcpy(cursor, "noargs ");
      cursor += strlen("noargs ");
    }
    
    bool one_printed = false;
    
    // This loops over all possible tags, checking if they are present.
    for (int i = 0; i <= MAX_TAG; i++) {
        int index = i / 32;
        int bit = i % 32;
        int meta_chars = 0;
        
        if (ts->tags[index] & 1 << bit) {
            // inlining ts contains because of weird build problem.
            if (one_printed) {
                if (buf_len - consumed < 2) {
                    buf[buf_len - 1] = '\0';
                    return consumed + 3;
                }
                cursor[0] = ',';
                cursor[1] = ' ';
                cursor += 2;
                consumed += 2;
            }
            meta_chars = meta_to_string(i, ts, cursor, buf_len - consumed);
            consumed += meta_chars;
            if (consumed > buf_len) {
                buf[buf_len - 1] = '\0';
                return consumed;
            }
            cursor += meta_chars;
            // print tag arg
            meta_chars = meta_args_to_string(ts, i, cursor, buf_len - consumed);
            consumed += meta_chars;
            if (consumed > buf_len) {
                buf[buf_len - 1] = '\0';
                return consumed;
            }
            cursor += meta_chars;
            one_printed = true;
        }
    }
    if (buf_len - consumed < 2) {
        buf[buf_len - 1] = '\0';
        return consumed + 3;
    }
    cursor[0] = '}';
    cursor[1] = '\0';
    return consumed + 1;
}
void print_meta_set(const meta_set_t *meta_set){
    char name[256];
    meta_set_to_string(meta_set, name, 256);
    printm("%s\n", name);
}


void print_meta_set_debug(meta_t tag){
    print_meta_set((const meta_set_t*)tag);
}


// print the contents of the input vector
void print_debug(const meta_set_t *pc, const meta_set_t *ci, const meta_set_t *rs1, const meta_set_t *rs2, const meta_set_t *rs3, const meta_set_t *mem){
    
    printm("PC: %x:", pc);
    print_meta_set(pc);
    printm("CI: %x:", ci);
    print_meta_set(ci);
    printm("R1: %x:", rs1);
    print_meta_set(rs1);
    printm("R2: %x:", rs2);
    print_meta_set(rs2);
    printm("MEM: %x:", mem);
    print_meta_set(mem);
}


