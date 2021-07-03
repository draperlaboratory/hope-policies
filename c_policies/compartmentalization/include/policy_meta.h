/*
 * Generated header. Modified for compartmentalization policy.
 */

#ifndef POLICY_META_H
#define POLICY_META_H

// A map of which argument fields are being used for which
// purposes. See policy_meta_set.h. Current policy uses three
// arguments, although there is some reuse in cases where it is
// safe. Words 0 and 1 are for membership bits, 2 is for object
// or subject ID, and 3 and 4 are for heap ptr/cell color.
#define SUBJ_INDEX 2
#define OBJ_INDEX 2
#define PC_CONTROL_INDEX 2
#define CELL_COLOR_INDEX 3
#define POINTER_COLOR_INDEX 4

#define opcode_begin				0x1a
#define opcode_end				0x26

#define osv_heap_AntiPointer                    0x18    // QTag ["osv","heap","AntiPointer"]
#define osv_heap_ApplyColor                     0x13    // QTag ["osv","heap","ApplyColor"]
#define osv_heap_Cell                           0x10    // QTag ["osv","heap","Cell"]
#define osv_heap_DelColor                       0x16    // QTag ["osv","heap","DelColor"]
#define osv_heap_ModColor                       0x17    // QTag ["osv","heap","ModColor"]
#define osv_heap_NewColor                       0x15    // QTag ["osv","heap","NewColor"]
#define osv_heap_Pointer                        0x11    // QTag ["osv","heap","Pointer"]
#define osv_heap_RawHeap                        0x12    // QTag ["osv","heap","RawHeap"]
#define osv_heap_RemoveColor                    0x14    // QTag ["osv","heap","RemoveColor"]
#define osv_heap_SpecialCaseVFPRINTF            0x19    // QTag ["osv","heap","SpecialCaseVFPRINTF"]

#define osv_riscv_og_andiGrp                    0x1e    // QGroup ["osv","riscv","og","andiGrp"]
#define osv_riscv_og_arithGrp                   0x20    // QGroup ["osv","riscv","og","arithGrp"]
#define osv_riscv_og_branchGrp                  0x1a    // QGroup ["osv","riscv","og","branchGrp"]
#define osv_riscv_og_csrGrp                     0x24    // QGroup ["osv","riscv","og","csrGrp"]
#define osv_riscv_og_csriGrp                    0x25    // QGroup ["osv","riscv","og","csriGrp"]
#define osv_riscv_og_immArithGrp                0x1f    // QGroup ["osv","riscv","og","immArithGrp"]
#define osv_riscv_og_jumpGrp                    0x1c    // QGroup ["osv","riscv","og","jumpGrp"]
#define osv_riscv_og_jumpRegGrp                 0x1b    // QGroup ["osv","riscv","og","jumpRegGrp"]
#define osv_riscv_og_loadGrp                    0x21    // QGroup ["osv","riscv","og","loadGrp"]
#define osv_riscv_og_loadUpperGrp               0x1d    // QGroup ["osv","riscv","og","loadUpperGrp"]
#define osv_riscv_og_mulDivRemGrp               0x23    // QGroup ["osv","riscv","og","mulDivRemGrp"]
#define osv_riscv_og_privGrp                    0x26    // QGroup ["osv","riscv","og","privGrp"]
#define osv_riscv_og_storeGrp                   0x22    // QGroup ["osv","riscv","og","storeGrp"]

// Compartmentalization function labeling
#define osv_Comp_funcID                         0x27	// Comp.funcID

// Compartmentalization global object labeling
#define osv_Comp_globalID                       0x28	// Comp.globalID

// Compartmentalization control-flow. Decimal encoding because policy_meta.yml uses decimal
// and I'm lazy
#define osv_threeClass_Branch_Instr             46    // QTag ["osv","threeClass","Branch-Instr"]
#define osv_threeClass_Branch_Tgt               43    // QTag ["osv","threeClass","Branch-Tgt"]
#define osv_threeClass_Call_Instr               44    // QTag ["osv","threeClass","Call-Instr"]
#define osv_threeClass_Call_Tgt                 41    // QTag ["osv","threeClass","Call-Tgt"]
#define osv_threeClass_Jumping_Branch           49    // QTag ["osv","threeClass","Jumping-Branch"]
#define osv_threeClass_Jumping_Call             47    // QTag ["osv","threeClass","Jumping-Call"]
#define osv_threeClass_Jumping_NoCFI            51    // QTag ["osv","threeClass","Jumping-NoCFI"]
#define osv_threeClass_Jumping_Return           48    // QTag ["osv","threeClass","Jumping-Return"]
#define osv_threeClass_NoCFI                    50    // QTag ["osv","threeClass","NoCFI"]
#define osv_threeClass_Return_Instr             45    // QTag ["osv","threeClass","Return-Instr"]
#define osv_threeClass_Return_Tgt               42    // QTag ["osv","threeClass","Return-Tgt"]

// Special objects
#define osv_Comp_special_obj_IO                 52	// Comp.special-obj-IO
#define osv_Comp_special_obj_RAM                53	// Comp.special-obj-RAM
#define osv_Comp_special_obj_FLASH              54	// Comp.special-obj-FLASH
#define osv_Comp_special_obj_UART		55	// Comp.special-obj-UART
#define osv_Comp_special_obj_PLIC	 	56	// Comp.special-obj-PLIC
#define osv_Comp_special_obj_ETHERNET	 	57	// Comp.special-obj-PLIC

// A special tag for indicating saving / restoring PC context
#define osv_Comp_context_switch              	58	// Comp.context-switch
#endif // POLICY_META_H
