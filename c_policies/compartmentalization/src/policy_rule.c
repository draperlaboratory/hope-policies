/* This file contains the compartmentalization micropolicy. 
 *
 * === Subjects and objects ===
 * This policy essentially learns and enforces a static Access Control
 * Matrix. As a result, all "subjects" and "objects" in the system
 * must be labeled in a statically-identifiable way.
 *
 * At the finest granularity, each individual function will be given a
 * unique label (tag). The policy tagger can optionally be supplied with a
 * set of subject definitions, which is simply a mapping of function
 * names to higher-level mappings.  For example, each function could
 * be mapped to "A", "B" or "C" to create a policy with three code
 * compartments. The intention of this feature is to enable external
 * tools (such as uSCOPE, manual partitioning, etc) to create various 
 * compartmentalizations that can flexibly be instantiated as tag policies.
 *
 * Global objects are each given a unique label (tag) that is painted
 * onto their virtual address range. Dynamic objects are a little more
 * involved, given that we must label them in a statically-identifiable
 * way. To accomplish this, this policy assigns a unique identifier to
 * each allocation site (which for FreeRTOS is a call to
 * pvPortMalloc()) and reuses the heap policy machinery in a slightly
 * modified way to color heap objects based on their static call sites
 * (that is, all data allocated by a specific allocation call are
 * grouped together into a single "object"). Some special objects,
 * such as UARTS, etc get a "SPECIAL-UART" object label as specified
 * by the policy initialization. Analogously, Flash or any other
 * kinds of special memory regions are treated the same way.
 *
 * For a given definition of N subjects and M objects, there is then a
 * conceptual static N * M Access Control Matrix, where each cell defines what
 * operations (read, write, call, return) are allowed between those subjects
 * and objects. Note that for calls and returns, subjects are also objects.
 * 
 * == Learning mode and Enforcement mode ==
 * The policy runs in one of two modes: learning mode or enforcement
 * mode.
 *
 * In learning mode, the policy records all observed privileged operations
 * (read, write, call, return) in a hash table (sparse representation
 * of the full N * M table). The granularity of these operations
 * depends on the supplied definitions of subjects and objects as
 * described above.
 * While running, the policy will print out new privileged operations
 * as they are discovered. At the end of an execution, the policy will
 * write out the learned Access Control Matrix in a text representation
 * in the file "result.cmap".
 * 
 * Alternatively, the policy can be run in Enforcement mode by supplying it
 * with an Access Control Matrix file "current.cmap". The policy will 
 * load the supplied Access Control Matrix into the hash table before
 * running. Theoretically, other ways of generated such a matrix
 * (static analysis, etc) could be used instead of the learning mode.
 * When new interactions are encountered in this mode, we can do one
 * of two things. In strict mode (toggled by a #define below), any
 * new interaction is a policy violation and the program will be terminated.
 * Alternatively, if strict mode is turned off, then new interactions
 * are simply printed as warnings. At the end of a such a run, one can
 * choose to update their Access Control Matrix to include these new
 * privileges ("result.cmap") or to keep their "current.cmap".
 *
 * === Context Switching ===
 * This policy keeps tags on the PC, which can cause the policy to
 * break from context switches. This implementation has the preliminary
 * fix for context switching, which involves putting a 'context-switch'
 * tag on the code from portASM.S that saves/restores state to keep
 * the PC tag intact. Needs a little more debugging though.
 *
 * === Tagging ===
 * This policy makes assumptions on the specific ways in which tags
 * are placed in memory. The compartmentalization tagger, "comp_tagger.py"
 * can be found in policy-engine/tagging_tools directory.
 */

// Toggle to turn struct mode on or off
// #define STRICT

#include "policy_meta.h"
#include "policy_rule.h"
#include "policy_meta_set.h"
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <inttypes.h>
#include <limits.h>
#include <string.h>

#include "comp_ht.c"
#include "prefetch_ht.c"
#include "policy_prefetching.c"

// Policy return codes
const int policyERRORFailure = -2;
const int policyExpFailure = 0;
const int policyImpFailure = -1;
const int policySuccess = 1;

// Are we in enforcement mode or learning mode?
// Set by whether or not we load an initial CAPMAP during initialization.
int enforcement_mode = 0;

// Number of functions and objects found in the defintion files.
// Set on initialization.
int max_func, max_obj;
int event_no = 0;

// There are a couple cases where policy communicates to validator...
extern void rule_analysis_end();

// Policy initialization
struct comp_ht * ht = NULL;

int has_init = 0;
void policy_init(){

  if (has_init == 0){
    printm("Init compartment policy...\n");
    ht = ht_create(HT_SIZE);
    set_max_subjs_objs();
    load_initial_CAPMAP();
    load_prefetching_policy();
    has_init = 1;
  }
}

// At the end of an execution, print out the CAPMAP data to a file.
int has_print_CAPMAP = 0;
int print_CAPMAP(FILE * outfile, int weights){
  
  // Print CAPMAP data for each function
  for (int f = 1; f < max_func; f++){
    print_func_data(ht, f, weights, outfile);
  }
  
}

/* This function contains the logic for the compartmentalization policy. 
 * In "learning mode" it records all observed read/write/call/return operations.
 * In "enforcement mode" it enforces a supplied access control matrix.
 */
int compartmentalization_policy(context_t *ctx, operands_t *ops, results_t *res)
{

  event_no += 1;
  
  /****** Generic setup ******/
  // A few things used by all components of the policy:
  
  // Get function ID and function name of current instruction
  int this_funcID;
  char * func_name = "<unknown>";
  if (ms_contains(ops -> ci, osv_Comp_funcID)){
    this_funcID = ops -> ci -> tags[SUBJ_INDEX];
    if (this_funcID == 0){
      printm("ERROR: funcID 0 on addr %x", ctx -> epc);
      return policyExpFailure;
    }
    func_name = func_defs[this_funcID];
  } else {
    printm("ERROR: running instruction without funcID: %x", ctx -> epc);
    return policyExpFailure;
  }

  // Create shorthands for the operation type
  int is_load = ms_contains(ops -> ci, osv_riscv_og_loadGrp);
  int is_store = ms_contains(ops -> ci, osv_riscv_og_storeGrp);
  int is_return = ms_contains(ops -> ci, osv_threeClass_Return_Instr);  
  int is_call = ms_contains(ops -> ci, osv_threeClass_Call_Instr);
  int is_arith = ms_contains(ops -> ci, osv_riscv_og_immArithGrp) ||
    ms_contains(ops -> ci, osv_riscv_og_arithGrp);  

  /****** Memory access tracking ******/
  
  // Object tracking only relevant to load/store.
  // Lookup the objID being accessed and update CAPMAP.
  if (is_load || is_store){

    // Lookup object that is being accessed
    int this_objID = -1;
    char * obj_name = NULL;

    // Check on the bitfields to see what we know about this object
    int is_heap = ms_contains(ops -> mem, osv_heap_Cell);
    int is_global = ms_contains(ops -> mem, osv_Comp_globalID);
    int is_special_IO = ms_contains(ops -> mem, osv_Comp_special_obj_IO);
    int is_special_RAM = ms_contains(ops -> mem, osv_Comp_special_obj_RAM);
    int is_special_FLASH = ms_contains(ops -> mem, osv_Comp_special_obj_FLASH);
    int is_special_UART = ms_contains(ops -> mem, osv_Comp_special_obj_UART);
    int is_special_PLIC = ms_contains(ops -> mem, osv_Comp_special_obj_PLIC);
    int is_special_ETHERNET = ms_contains(ops -> mem, osv_Comp_special_obj_ETHERNET);
      
    // All heap objects are also global objects, because heap is allocated from a global
    // memory pool called ucHeap. So, the order that we classify objects in matters.
    // Priority is 1) heap, 2) global, 3) special
    
    if (is_heap){
      this_objID = ops -> mem -> tags[CELL_COLOR_INDEX];
      obj_name = object_defs[this_objID];
    } else if (is_global){
      this_objID = ops -> mem -> tags[OBJ_INDEX];
      obj_name = object_defs[this_objID];
    } else if (is_special_IO || is_special_RAM ||
	       is_special_FLASH || is_special_UART ||
	       is_special_PLIC || is_special_ETHERNET){

      // Special objects currently have static, fixed IDs.
      if (is_special_IO)
	this_objID = 1;
      if (is_special_RAM)
	this_objID = 2;
      if (is_special_FLASH)
	this_objID = 3;
      if (is_special_UART)
	this_objID = 4;
      if (is_special_PLIC)
	this_objID = 5;
      if (is_special_ETHERNET)
	this_objID = 6;      
      
      obj_name = object_defs[this_objID];
      
    } else {      
      printm("ERROR: unknown object at addr: %lx from instr %lx", ctx -> bad_addr, ctx -> epc);
      return policyExpFailure;
    }
    
    // We now have a funcID and an objID, do a CAPMAP lookup + update for this mem access
    if (this_funcID != -1 && this_objID != -1){
      
      int edge_type;
      if (is_load)
	edge_type = EDGE_READ;
      else
	edge_type = EDGE_WRITE;

      // Lookup this interaction in CAPMAP
      struct comp_bucket * b = ht_lookup(ht, this_funcID, this_objID, edge_type);      

      // A miss means this is a new memory interaction.
      // Learning mode = add to hash table
      // Enforcement mode = terminate or add and print depending on strictness
      if (b == NULL){
#ifdef STRICT
	if (enforcement_mode){
	  printm("Compartmentalization policy violation: memory access from subject %s to object %s",
		 func_name, obj_name);
	  return policyExpFailure;
	}
#endif	
	if (is_load){
	  printm("New memory interaction: function %s read from object %s", func_name, obj_name);
	} else {
	  printm("New memory interaction: function %s wrote to object %s", func_name, obj_name);
	}
	ht_insert(ht, this_funcID, this_objID, edge_type);	
      }
    }
  }

  /****** Control-flow tracking ******/
  
  // This policy also learns the legal control-flow graph at the function
  // granularity.
  // We do something if:
  // 1) Current executing instruction is a call or return.
  //    In that case, set tags on PC to indicate jumping.
  // 2) Current PC tag is Jumping-Call or Jumping-Return
  //    In that case, log interaction and unset PC tag.
  // Lastly, this policy also colors heap objects based on the
  // static call site to pvPortMalloc(). That subsystem uses
  // tags on the PC, so we set and preserve those here too.
  

  // Log call / returns into hash table
  int is_call_jumping = ms_contains(ops -> pc, osv_threeClass_Jumping_Call);
  int is_return_jumping = ms_contains(ops -> pc, osv_threeClass_Jumping_Return);
  // TODO add require CFI CallTgt ReturnTgt check
  if ((is_call_jumping || is_return_jumping) && this_funcID != -1){

    // Set src and dest
    int src_func = ops -> pc -> tags[PC_CONTROL_INDEX];
    char * src_func_name = func_defs[src_func];
    int dest_func = this_funcID;

    // Set edge type (call or return)
    int edge_type;
    if (is_call_jumping)
      edge_type = EDGE_CALL;
    else
      edge_type = EDGE_RETURN;
	
    // Check to see if we have seen this interaction
    struct comp_bucket * b = ht_lookup(ht, src_func, dest_func, edge_type);

    // A miss means this is a new control-flow interaction.
    // Learning mode = add to hash table
    // Enforcement mode = terminate or add and print depending on strictness
    if (b == NULL){
#ifdef STRICT
      if (enforcement_mode){
	printm("Compartmentalization policy violation: control transfer from subject %s to %s",
	       src_func_name, func_name);
	return policyExpFailure;
      }
#endif       
      if (edge_type == EDGE_CALL) {
	printm("New call interaction: %s -> %s", src_func_name, func_name);
      } else {
	if (src_func == 0){
	  // I haven't debugged this case fully. No unlabeled instructions ever run,
	  // so it looks like PC tag gets clobbered by context switching or something.
	  printm("WARNING: return from NONE. IP=%x", ctx -> epc);
	  return policySuccess;
	}
	printm("New return interaction: %s -> %s", src_func_name, func_name);
      }
      ht_insert(ht, src_func, dest_func, edge_type);
    }
    
    // Cleanup tags for result
    ms_bit_remove(res -> pc, osv_threeClass_Jumping_Call);
    ms_bit_remove(res -> pc, osv_threeClass_Jumping_Return);
    res -> pc -> tags[PC_CONTROL_INDEX] = 0;

    // Keep alloc-ID, which rides on the pointer color slot
    res -> pc -> tags[POINTER_COLOR_INDEX] = ops -> pc -> tags[POINTER_COLOR_INDEX];
    
    res -> pcResult = true;
  }

  // On calls, set the PC tag to indicate that we're jumping and
  // set a field to indicate the source function
  if (is_call && this_funcID != -1){
    ms_bit_add(res -> pc, osv_threeClass_Jumping_Call);
    res -> pc -> tags[PC_CONTROL_INDEX] = this_funcID;

    // If this is a call to an allocator, transfer alloc-id onto PC.
    // If it's a normal call not to an allocator, but happens before
    // allocation routine unsets PC tag, just preserve it.
    if (ops -> ci -> tags[POINTER_COLOR_INDEX] > 0){
      //printm("Calling an allocator! Color = %d", ops -> ci -> tags[POINTER_COLOR_INDEX]);
      res -> pc -> tags[POINTER_COLOR_INDEX] = ops -> ci -> tags[POINTER_COLOR_INDEX];
    } else if (ops -> pc -> tags[POINTER_COLOR_INDEX] != 0){
      res -> pc -> tags[POINTER_COLOR_INDEX] = ops -> pc -> tags[POINTER_COLOR_INDEX];
    }
    
    res -> pcResult = true;
  }

  // Returns are simpler, just set PC tag with appropriate color / preserve PC tag.
  if (is_return && this_funcID != -1){
    // Mark return
    ms_bit_add(res -> pc, osv_threeClass_Jumping_Return);
    res -> pc -> tags[PC_CONTROL_INDEX] = this_funcID;

    // Keep alloc-ID on PC tag
    if (ops -> pc -> tags[POINTER_COLOR_INDEX] != 0){
      res -> pc -> tags[POINTER_COLOR_INDEX] = ops -> pc -> tags[POINTER_COLOR_INDEX];
    }    
    res -> pcResult = true;
  }    

  /****** Handling context switching ******/  

  /*
  int is_context_switch = ms_contains(ops -> ci, osv_Comp_context_switch);
  
  // Handle context swithing. Save PC tags to memory, then try to load them back later.
  // Needs a little more debugging, but does catch these cases properly. Need to clear
  // context-switch tag from stack state as that never gets cleared, etc. See portASM.S
  if (is_context_switch){

    // Case one: If inside context_switch, we hit a store, and current PC is not empty,
    // then copy to mem and add context-switch tag to memory
    
    if (is_store){
      int alloc_id = ops -> pc -> tags[POINTER_COLOR_INDEX];
      int jumping_color = ops -> pc -> tags[PC_CONTROL_INDEX];
      if (alloc_id != 0 || jumping_color != 0){
	
	printm("Inside context switch, had an alloc-ID of %d and jumping color of %d. Saving to mem. PC = %x. Event_no=%d", alloc_id, jumping_color, ctx ->epc, event_no);
	ms_bit_add(res -> rd, osv_Comp_context_switch);
	
	res -> rd -> tags[PC_CONTROL_INDEX] = jumping_color;
	res -> rd -> tags[POINTER_COLOR_INDEX] = alloc_id;

	// Copy over cell color / other properties of the memory cell
	if (ms_contains(ops -> mem, osv_heap_Cell)){
	  ms_bit_add(res -> rd, osv_heap_Cell);
	  res -> rd -> tags[CELL_COLOR_INDEX] = ops -> mem -> tags[CELL_COLOR_INDEX];
	}

	if (ms_contains(ops -> mem, osv_Comp_globalID)){
	  ms_bit_add(res -> rd, osv_Comp_globalID);
	  res -> rd -> tags[OBJ_INDEX] = ops -> mem -> tags[OBJ_INDEX];
	}

	// Clear out tags so this doesn't trigger again
	res -> pc -> tags[POINTER_COLOR_INDEX] = 0; // saved_alloc_id;	
	res -> pc -> tags[PC_CONTROL_INDEX] = 0; //saved_jumping_color;	
	
	// Clear PC tag, we just saved to memory
	res -> rdResult = true;
	
	// Update memory tag, we just added "context-switch" to it and saved stuff
	res -> pcResult = true;
      
      }

    }

    // Case two: If inside context_switch, we hit a load, and the load targets a
    // context-switch word, then load up tag values and clear it up
    // TODO: I'm never clearing the context-switch tag from memory, but if that
    // block gets reallocated it should get cleared. Should come up with something cleaner
    if (is_load){
      int mem_contains_context_switch = ms_contains(ops -> mem, osv_Comp_context_switch);
      if (mem_contains_context_switch){
	int saved_alloc_id = ops -> mem -> tags[POINTER_COLOR_INDEX];
	int saved_jumping_color = ops -> mem -> tags[PC_CONTROL_INDEX];
	printm("Just loaded a saved context switch! Had saved alloc-id of %d and jumping color of %d. PC =%x. Event_no=%d", saved_alloc_id, saved_jumping_color, ctx -> epc, event_no);

	res -> pc -> tags[POINTER_COLOR_INDEX] = saved_alloc_id;	
	res -> pc -> tags[PC_CONTROL_INDEX] = saved_jumping_color;
	res -> pcResult = true;
      }
    }

    return policySuccess;
  }

  */
  
  /****** Heap color maintenance ******/

  // The last major part of this policy has to do with tracking
  // heap colors.
  //
  // Because the compartmentalization policy enforces a *static*
  // access control matrix (the CAPMAP), we label each heap
  // allocation based on the static allocation site that created it.
  // We then learn which pieces of code are allowed access to each
  // of these object classes.
  // 
  // That is, compartmentalization enforces a relationship between
  // *code* and memory, not *pointers* and memory. However,
  // to keep heap regions tagged, we do care about tagging
  // a few special pointers and propagating their colors to
  // make the allocation machinery work.
  
  // NOTE: for load/store, op1 is pointer and op2 is value
  
  // Create some shorthands for being inside ApplyColor/RemoveColor
  // These are the only functions that need pointer propagation to memory
  int is_apply_color = ms_contains(ops -> ci, osv_heap_ApplyColor);
  int is_remove_color = ms_contains(ops -> ci, osv_heap_RemoveColor);
  int inside_apply_remove = is_apply_color || is_remove_color;

  // Tag destruction on registers outside of a few alloc routines:
  // A load outside of ApplyColor and RemoveColor always
  // destroys result register tag.
  if (is_load && !inside_apply_remove){
    res -> rdResult = true;
  }
  // Immediate arith destroys tags on result register
  if (is_arith){
    res -> rdResult = true;
  }
  
  // Inside apply/remove, loads and stores move pointers and leave rest intact
  if (inside_apply_remove){
    
    // Logic for writes:
    // Stores carry pointer tag to memory; leave NewColor and ModColor alone.
    // If writing with ModColor, while inside apply_color, and with a colored
    // pointer to mem tagged RawHeap, then that's a new allocation setup.
    if (is_store){

      // Collect shorthands for tags on written word
      int has_ModColor = ms_contains(ops -> mem, osv_heap_ModColor);
      int has_NewColor = ms_contains(ops -> mem, osv_heap_NewColor);
      int has_Pointer = ms_contains(ops -> mem, osv_heap_Pointer);
      
      // Keep ModColor
      if (has_ModColor){
	ms_bit_add(res -> rd, osv_heap_ModColor);
	res -> rdResult = true;	
      }

      // Keep NewColor
      if (has_NewColor){
	ms_bit_add(res -> rd, osv_heap_NewColor);
	res -> rdResult = true;	
      }

      // Keep global
      if (ms_contains(ops -> mem, osv_Comp_globalID)){
	int globalID = ops -> mem -> tags[OBJ_INDEX];
	ms_bit_add(res -> rd, osv_Comp_globalID);
	res -> rd -> tags[OBJ_INDEX] = globalID;
	res -> rdResult = true;
      }

      // Keep Cell
      if (ms_contains(ops -> mem, osv_heap_Cell)){
	ms_bit_add(res -> rd, osv_heap_Cell);
	res -> rd -> tags[CELL_COLOR_INDEX] = ops -> mem -> tags[CELL_COLOR_INDEX];
	res -> rdResult = true;	
      }

      // Carry pointer to memory
      if (ms_contains(ops -> op2, osv_heap_Pointer)){
	ms_bit_add(res -> rd, osv_heap_Pointer);
	res -> rd -> tags[POINTER_COLOR_INDEX] = ops -> op2 -> tags[POINTER_COLOR_INDEX];
	res -> rdResult = true;
      }

      // Finally, the actual setup rule for an allocated word!
      // Addr must be a colored pointer, value must be ModColor      
      if (is_apply_color){
	if (ms_contains(ops -> op1, osv_heap_Pointer) &&
	    ms_contains(ops -> op2, osv_heap_ModColor)){
	  //printm("Allocating word with (Cell %d)", ops -> op1 -> tags[POINTER_COLOR_INDEX]);
	  if (ops -> op1 -> tags[POINTER_COLOR_INDEX] == 0){
	    printm("ERROR: heap allocation but no color.");
	    //return policyERRORFailure;
	  }
	  ms_bit_add(res -> rd, osv_heap_Cell);
	  res -> rd -> tags[CELL_COLOR_INDEX] = ops -> op1 -> tags[POINTER_COLOR_INDEX];
	  res -> rdResult = true;
	}
      }

      // The rule for clearing a heap cell back to RawHeap
      if (is_remove_color){
	if (ms_contains(ops -> op2, osv_heap_ModColor)){
	  //printm("Freeing word with (Cell %d)", ops -> mem -> tags[CELL_COLOR_INDEX]);
	  //ms_bit_add(res -> rd, osv_heap_RawHeap);
	  ms_bit_add(res -> rd, osv_heap_Cell);
	  res -> rd -> tags[POINTER_COLOR_INDEX] = 0;
	  res -> rdResult = true;
	}
      }
    }

    // Logic for loads:
    // Loading from ModColor and NewColor have special effects.
    // Loading Pointer tags will tag result register.
    if (is_load){
      
      // Handle ModColor
      int accessing_modcolor = ms_contains(ops -> mem, osv_heap_ModColor);
      if (accessing_modcolor){
	ms_bit_add(res -> rd, osv_heap_ModColor);
	res -> rdResult = true;
      }

      // Handle NewColor
      int accessing_newcolor = ms_contains(ops -> mem, osv_heap_NewColor);
      if (accessing_newcolor){
	ms_bit_add(res -> rd, osv_heap_Pointer);
	if (ops -> pc -> tags[POINTER_COLOR_INDEX] != 0){
	  res -> rd -> tags[POINTER_COLOR_INDEX] = ops -> pc -> tags[POINTER_COLOR_INDEX];
	} else {
	  printm("WARNING: color creation, but no PC tag.");
	  res -> rd -> tags[POINTER_COLOR_INDEX] = 0;
	}
	res -> rdResult = true;

	// Clear PC tags
	res -> pcResult = true;
      }
      
      // Handle loading pointer
      if (ms_contains(ops -> mem, osv_heap_Pointer)){
	ms_bit_add(res -> rd, osv_heap_Pointer);
	res -> rd -> tags[POINTER_COLOR_INDEX] = ops -> mem -> tags[POINTER_COLOR_INDEX];
	res -> rdResult = true;
      }
    }
  }

  return policySuccess;  
}

const int ruleLogMax = 2;
char *ruleLog[3];
int ruleLogIdx = 0;
void logRuleEval(const char *ruleDescription)
{
    if (ruleLogIdx < ruleLogMax) {
        ruleLog[ruleLogIdx] = ruleDescription;
        if (ruleLogIdx <= ruleLogMax)
            ruleLogIdx++;
    }
}
void logRuleInit()
{
    ruleLogIdx = 0;
    ruleLog[ruleLogMax] = "additional rules omitted...";
}
const char *nextLogRule(int *idx)
{
    if (*idx < ruleLogIdx)
        return ruleLog[(*idx)++];
    return 0;
}

int eval_policy(context_t *ctx, operands_t *ops, results_t *res)
{

  // Init if we haven't yet
  policy_init();
    
  int evalResult = policyImpFailure;
  
  evalResult = compartmentalization_policy(ctx, ops, res);

  // If prefetching is enabled, and we hit a rule trigger in the lookup table, then insert the prefetched rule now too.
  // TODO: this logic really should be asynchronous, so need to think about timing models, etc
  if (prefetching_enabled){
    struct prefetch_bucket * result = ht_lookup_prefetch(prefetch_ht, ops);
    if (result != NULL){
      //printm("Hit a prefetch!");
      prefetch_rule(result -> prefetch_ops, result -> prefetch_res);
    } else {
      //printm("No prefetch.");
    }
  }  
  
  if (evalResult != policySuccess)
    return evalResult;
  return policySuccess;
}

// We have extern func_defs and object_defs which get supplied
// by policy compilation down the road. Calculate the max index
// into these, they always end with blank "" entry.
void set_max_subjs_objs(){

  // Calculate the highest function number
  max_func = 0;
  if (func_defs == NULL){
    printm("ERROR: undefined function defs.");
  }
  char * curr_func_name = func_defs[0];
  while (curr_func_name != NULL){
    max_func++;
    curr_func_name = func_defs[max_func];
    if (strcmp(curr_func_name, "") == 0){
      break;
    }
  }
  if (max_func == 0){
    printm("ERROR: no function defs.");
  }

  // Calculate highest object number
  max_obj = 0;
  if (object_defs == NULL){
    printm("ERROR: undefined object defs.");
  }
  char * curr_obj_name = object_defs[0];
  while (curr_obj_name != NULL){
    max_obj++;
    curr_obj_name = object_defs[max_obj];
    if (strcmp(curr_obj_name, "") == 0){
      break;
    }
  }
  if (max_obj == 0){
    printm("ERROR: no object defs.");
  }

  printm("Loaded %d subject definitions and %d object definitions.",
	 max_func,
	 max_obj);

}

// On program termination, dump the current CAPMAP out to result.cmap file
void policy_terminate(){

  // Trigger the rule analysis ending
  rule_analysis_end();
  
  if (enforcement_mode){
    printm("Ran in enforcement mode. Encountered %d new CAPMAP entries compared to initial CAPMAP file.", ht -> new_additions);
    if (ht -> new_additions > 0){
      printm("***Copy this capmap file to save these additions***");
    }
  }
  
  printm("Program terminated. Writing out CAPMAP to file.");
  
  FILE * outfile;
  outfile = fopen("result.cmap", "w");
  print_CAPMAP(outfile, 0);
  fclose(outfile);
  outfile = fopen("result_weighted.cmap", "w");
  print_CAPMAP(outfile, 1);
  fclose(outfile);
}


// Small helper function for load_initial_CAPMAP()
// Converts a string to subjectID
int subject_name_to_ID(char * funcName){
  int i;
  for (i = 0; i < max_func; i++){
    if (strcmp(funcName, func_defs[i]) == 0){
      return i;
    }
  }
  printm("ERROR: could not match subject %s. Wrong CAPMAP.",
	 funcName);
  exit(EXIT_FAILURE);
}

// Small helper function for load_initial_CAPMAP()
// Converts a string to objectID
int object_name_to_ID(char * objectName){
  int i;
  for (i = 0; i < max_obj; i++){
    if (strcmp(objectName, object_defs[i]) == 0){
      return i;
    }
  }
  printm("ERROR: could not match object %s. Wrong CAPMAP.",
	 objectName);
  exit(EXIT_FAILURE);
}

// On initialization, look for "current.cmap" file for an existing
// CAPMAP.  If there isn't one, we are in "learning" mode and will
// simply learn new interactions and create a result.cmap file at the
// end. If we do load an initial CAPMAP, then we are in "enforcement"
// mode.
void load_initial_CAPMAP(){
  
  FILE * infile = fopen("current.cmap", "r");

  if (infile == NULL){
    printm("Did not load an initial CAPMAP. Learning mode.");
    enforcement_mode = 0;
    ht -> initialized = 1;
    return;
  } else {
    printm("Found an initial CAPMAP file. Enforcement mode.");
#ifdef STRICT
    printm("Strict is enabled! Any new interactions will be policy violations.");
#else
    printm("Strict is disabled. New interactions are allowed but printed to sim.log");
#endif
    enforcement_mode = 1;
  }

  // CAPMAP files (with extension .cmap) are simple text file with two line types.
  // A line that starts with a token indicates a new subject (e.g., function).
  // A line that begins with a tab and then two space-separated tokens indicates a
  // privilege belonging to that function.
  // For example, the following represents a function foo() that can read object1 and
  // call bar():
  //
  // foo
  // 	Call bar
  //	Read object1
  //
  // We simply parse these, convert to numeric identifiers from the subject and
  // object defintions, then insert into initial hashtable.

  // Variables for line parsing
  char * line = NULL;  
  int length;

  // Variables for token parsing within a line
  char funcName[256], objectName[256], operationType[32];

  // Variables for tracking current subject and object id
  int funcID = -1;
  int objID = -1;
  
  while (getline(&line, &length, infile) != -1){
    
    // This line is a function, set current funcID
    if (line[0] != '\t'){
      sscanf(line, "%s", funcName);
      funcID = subject_name_to_ID(funcName);
    } else {
      // Otherwise the line is an operation type then a target object
      int read = sscanf(line, "%s %s", operationType, objectName);
      if (read == 0){
	printm("No match, breaking.");
	break;
      }

      // Convert operationType string to Edge type
      int edge_type = -1;
      if (strcmp(operationType, "Read") == 0){
	edge_type = EDGE_READ;
      } else if (strcmp(operationType, "Write") == 0){
	edge_type = EDGE_WRITE;
      } else if (strcmp(operationType, "Call") == 0){
	edge_type = EDGE_CALL;
      } else if (strcmp(operationType, "Return") == 0){
	edge_type = EDGE_RETURN;
      } else {
	printm("ERROR: failed to parse operation type %s", operationType);
	exit(EXIT_FAILURE);
      }

      // Convert object (code or data) to an object ID
      if (edge_type == EDGE_READ || edge_type == EDGE_WRITE){
	objID = object_name_to_ID(objectName);
      } else {
	objID = subject_name_to_ID(objectName);
      }

      // Insert into initial hashtable
      void * r = (void *) ht_lookup(ht, funcID, objID, edge_type);
      if (r != NULL){
	printm("Warning: already loaded that entry. Redudant CAPMAP file.");
      } else {
	ht_insert(ht, funcID, objID, edge_type);
      }
    }
  }
  
  // getline() automatically mallocs a line. Free it now.
  free(line);

  printm("Loaded up %d initial CAPMAP entries.", ht -> stored_objects);
  
  // Clear new addition count for enforcement mode
  ht -> new_additions = 0;
  ht -> initialized = 1;
}
