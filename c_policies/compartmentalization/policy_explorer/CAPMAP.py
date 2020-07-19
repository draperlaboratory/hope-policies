#!/usr/bin/python

import sys
import networkx as nx
from networkx.drawing.nx_pydot import write_dot
import subprocess
import math
import re
import random
import os
from collections import defaultdict
import copy
from enum import Enum
from elftools.elf.elffile import ELFFile

# This is a modified CAPMAP parser suitable for PIPE compartmentalization
# policies based on the uSCOPE ideas. 

# This class represents a CAPMAP graph. This file contains the logic
# for loading in a .cmap file (or multiple .cmap files), parsing the
# debugging metadata and instruction counts from a matching prog_binary,
# as well as some other operations on the resulting CAPMAP objects.
#
# In the directory in which a prog_binary is stored, it automatially
# checks for a prog_binary_plain file which should be a kernel compiled
# without memorizer. This file is optional but used for accurate
# instruction counts.
#
# If the .cmap file also has a .funcs file or a .baseline file, these
# are optionally read in as function counts and baseline cycles for
# future scaling and overhead calculations.
#
# The first time a .cmap file is loaded, it will automatically be
# compressed into a .cmap.comp file. In future loads, these will
# automatically be detected and loaded instead. This saves a
# tremendous amount of time.
#
# Lots of this file was added bit-by-bit to handle increasing
# complexity as research progressed, some larger refactoring would be
# good now that scope is more known.

# List of operations in uSCOPE; used by this file and others
ops = ["read", "write", "call", "return", "free"]

#### Some classes for CAPMAP graph objects ####

# There are two kinds of nodes in CAPMAP graph
class NodeType(Enum):
    OBJECT = 1
    SUBJECT = 2
    
# Instruction nodes have an InstrType
class InstrType(Enum):
    READ = 1
    WRITE = 2
    CALL = 3
    RETURN = 4
    FREE = 5

# Object nodes have a MemType
class MemType(Enum):
    HEAP = 1
    GLOBAL = 2
    SPECIAL = 3
    
# CAPMAP represented as a digraph. Nodes are either:
#   - A kernel object, as denoted by the tuple of (NodeType.OBJECT, MemType, alloc_ip)
#   - An instruction, denoted by the tuple (NodeType.SUBJECT, instruction_type, access_ip)
# This class reads in a .cmap file and creates a CAPMAP object containing a networkx graph.
class CAPMAP:

    # Init function does the following operations in this order:
    # 1) It extracts info from the prog_binary using "nm", "objdump", etc
    # 2) It parses a single cmap file or a whole directory of cmap files
    # 3) It does some post-processing and cleaning
    def __init__(self, prog_binary, verbose=1):

        ### Define some class variables ###
        self.prog_binary = prog_binary
        self.prog_binary_name = os.path.basename(prog_binary)
        self.re_kernel = re.compile('.*/hope-src[a-z\-]*/(.*)$')
        self.kmap_file = prog_binary + ".weighted.cmap"
        self.kmap_name = os.path.basename(self.kmap_file)
        self.kmap_dir = os.path.dirname(self.prog_binary)
        #self.symbol_table = {}
        #self.symbol_table_sizes = {}
        #self.symbol_table_names = {}
        #self.symbol_table_src_files = {}
        #self.object_names = {}
        #self.object_names_display = {}        
        self.verbose = verbose
        self.functions = set()
        self.live_functions = set()
        self.os_functions = set()
        self.instr_count_map = {}
        self.dg = nx.DiGraph();
        self.clear_maps()

        ### Extract info about prog_binary ###
        self.read_instructions_and_get_info()

        ### Parse cmap files ###
        # If passed a specific cmap file, load that file.
        # If passed a directory, iterate over all cmaps in that directory.
        print("File: " + self.kmap_file)
        if os.path.isfile(self.kmap_file):
            print("Loading from one file: " + self.kmap_file)
            self.from_single_file = True
            self.parse_to_digraph(self.kmap_file)
        else:
            print("Currently does not support multiple files!")
            sys.exit()

        #### Post processing ###
        self.set_object_sizes()
        self.build_object_ownership_maps()
        self.calc_live_functions()

    # Helper function for clearing class variables
    def clear_maps(self):
        self.ip_to_file = {}
        self.ip_to_func = {}
        self.ip_to_dir = {}
        self.ip_to_topdir = {}        
        self.ip_to_mono = {}
        self.ip_to_ip = {}        
        self.func_to_file = {}        
        self.func_to_func = {}        
        self.func_to_dir = {}
        self.func_to_topdir = {}
        self.func_to_mono = {}
        self.file_to_funcs = {}        
        self.file_to_dir = {}
        self.file_to_topdir = {}
        self.obj_no_cluster = {}
        #self.obj_owner_func = {}
        #self.obj_owner_file = {}
        #self.obj_owner_dir = {}
        #self.obj_owner_topdir = {}
                
    # This is the core logic for reading in a .cmap file. Has been
    # growing steadily to handle increasing complexity in Memorizer
    # data, should probably be refactored.  Reads a .cmap file and
    # creates a networkx graph.
    def parse_to_digraph(self, fn):

        # Parse this cmap into a local graph. Merge into full dg afterwards, this design
        # allows loading in multiple capmaps as long as based on same prog_binary.
        this_dg = nx.DiGraph()
        num_instr = 0
        num_obj = 0
        current_func = None
        current_subj_node = None
        
        # Open .cmap file, process line by line
        with open(fn, "r") as file:

            # Track the current object
            obj = None

            for line in file:
                
                # Skip comments
                if line[0] == "#":
                    continue

                # Break line into fields
                myline = line.strip().split()

                # Lines with field are a new function
                if len(myline) == 1:
                    current_func = myline[0]
                    func_node  = (NodeType.SUBJECT, current_func)

                    # The "functions" that correspond to entire compilation units for asm code won't have code sizes
                    # Currently inserting dummy data for these. TODO extract real data for asm.
                    if not current_func in self.instr_count_map:
                        self.functions.add(current_func)
                        #print("ASM subject: " + current_func)
                        self.instr_count_map[current_func] = {}
                        self.instr_count_map[current_func]["total"] = 0
                        self.instr_count_map[current_func]["size"] = 50
                        self.instr_count_map[current_func]["read"] = 1
                        self.instr_count_map[current_func]["write"] = 1
                        self.instr_count_map[current_func]["call"] = 1
                        self.instr_count_map[current_func]["return"] = 1
                        self.instr_count_map[current_func]["free"] = 0
                    
                    if not this_dg.has_node(func_node):
                        # Add node, set current node to this node
                        this_dg.add_node(func_node, size=1) #size=self.instr_count_map[current_func]["size"])
                        
                    current_subj_node = func_node
                        
                # Lines with 2 fields are an access from the current_func
                elif len(myline) == 3:

                    # Skip accesses to obj if none object
                    if current_func == None:
                        raise Exception("Parsing error: read access line without current active func.")

                    # Parse fields
                    op_type = myline[0].lower()
                    obj_target = myline[1]
                    weight = int(myline[2])

                    # Make the node for the target obj or func if not already in graph
                    if op_type in ["read", "write"]:
                        obj_node = (NodeType.OBJECT, obj_target)
                        if not this_dg.has_node(obj_node):
                            this_dg.add_node(obj_node, size=0)
                            #print("Adding object node!" + obj_target)
                    elif op_type in ["call", "return"]:
                        obj_node = (NodeType.SUBJECT, obj_target)
                        if not this_dg.has_node(obj_node):
                            this_dg.add_node(obj_node, size=1) #size=self.instr_count_map[obj_target]["size"])
                            #print("Adding subject node!" + obj_target)
                    else:
                        raise Exception("Invalid op type: " + op_type)    

                    # Setup weights for this edge. We add all types as 0 to make future computations easier
                    reads = weight if op_type == "read" else 0                    
                    writes = weight if op_type == "write" else 0
                    calls = weight if op_type == "call" else 0
                    returns = weight if op_type == "return" else 0
                    frees = 0
                    
                    # Add new edge or add weights to existing edge
                    if (not this_dg.has_edge(current_subj_node, obj_node)):
                        #print("Adding edge " + current_subj_node[1] + " " + obj_node[1])
                        this_dg.add_edge(current_subj_node, obj_node,
                                         read = reads, write = writes,
                                         call = calls,free = frees)

                        # Have to add this way, "return" is a Python keyword
                        this_dg.get_edge_data(current_subj_node, obj_node)["return"] = 0

                    else:
                        edge = this_dg.get_edge_data(current_subj_node, obj_node)
                        edge["read"] += reads
                        edge["write"] += writes
                        edge["call"] += calls
                        edge["return"] += returns
                        edge["free"] += frees

                # Lines with only 3 fields are call/ret
                else:
                    raise Exception("Invalid line type while parsing. Make sure to run on weighted cmap.")

        # Add this graph onto running total
        self.add_capmap(this_dg, fn)
        
    # This function extracts lots of info from the prog_binary.
    #
    # It calls objdump on the prog_binary and parses through the asm file.
    # The main output of this function is the self.instr_count_map,
    # which contains the number of read/write/call/return/free instructions
    # in each function, as well as the self.ip_to_X which maps debug info
    # to instruction addresses.
    def read_instructions_and_get_info(self):

        prog_binary = self.prog_binary

        # Attempt to locate objdump...
        ISP_PREFIX = os.environ["ISP_PREFIX"]
        objdump = os.path.join(ISP_PREFIX, "riscv32-unknown-elf", "bin", "objdump")
        if not os.path.isfile(objdump):
            raise Exception("WARNING: could not find objdump. Looked for " + objdump)
        
        
        if self.verbose:
            print("Extracting info from " + prog_binary + ". This takes a few minutes...")

        # Reset the maps, which may have been populated with info from the plain prog_binary
        self.ip_to_func = {}
        self.ip_to_file = {}
        self.ip_to_ip = {}
        self.ip_to_dir = {}
        self.ip_to_topdir = {}
        self.ip_to_mono = {}
        self.func_to_func = {}
        self.func_to_file = {}
        self.func_to_dir = {}
        self.func_to_topdir = {}
        self.func_to_mono = {}
        self.file_to_funcs = {}        
        self.file_to_dir = {}
        self.file_to_topdir = {}
        
        asm_output = prog_binary + ".asm"
        if not os.path.isfile(asm_output):
            os.system(objdump + " -d " + prog_binary + " > " + asm_output)
                    
        # Populate some of the metadata maps from DWARF metadata
        self.get_dwarf_info()

        # Read through the .asm a second time.
        # Construct mappings for each instruction to func, file, dir, etc
        # Also record number of operations of each type in each function
        # (removed) Lastly, try to associate globals
        with open(asm_output) as fh:
            
            funcname = None
            filename = None
            dirname = None
            topdirname = None
            
            for line in fh:
                line = line.strip()

                # This is the section that follows the .text section, so we end here
                if "section .altinstr" in line:
                    break                
                
                # Each new function, lookup metadata from addr2line
                if ">:" in line and "<." not in line:
                    addr = line.split()[0]
                    #funcname = self.ip_to_func[addr]
                    funcname = line.split()[1][1:-2]
                    #filename = self.ip_to_file[addr]
                    #dirname = self.ip_to_dir[addr]
                    #topdirname = self.ip_to_topdir[addr]
                    self.functions.add(funcname)
                    #print("Parsing new function:" + funcname)                    

                    if not funcname in self.instr_count_map:
                        self.instr_count_map[funcname] = {}
                        self.instr_count_map[funcname]["total"] = 0
                        self.instr_count_map[funcname]["size"] = 0                        
                        self.instr_count_map[funcname]["read"] = 0
                        self.instr_count_map[funcname]["write"] = 0                        
                        self.instr_count_map[funcname]["call"] = 0
                        self.instr_count_map[funcname]["return"] = 0
                        self.instr_count_map[funcname]["free"] = 0
                        self.instr_count_map[funcname]["writers"] = set()
                    continue

                if line == "":
                    continue
                
                if funcname != None:

                    # Store info about this isntr                    
                    addr = line.split()[0][:-1]
                    
                    #self.ip_to_mono[addr] = "mono"
                    #self.ip_to_topdir[addr] = topdirname
                    #self.ip_to_dir[addr] = dirname
                    #self.ip_to_file[addr] = filename
                    #self.ip_to_func[addr] = funcname
                    #self.ip_to_ip[addr] = addr

                    # This occured in my plain prog_binary. Not sure what it's from, but removing
                    if "..." in line:
                        continue                    
                    
                    # Parse line into addr, bytes, opcode, regs
                    line_chunks = line.split("\t")
                    num_chunks = len(line_chunks)
                    # First skip some garbage:
                    if num_chunks == 1 and ("<." in line) or ("Disassembly of" in line):
                        pass
                    # Then parse out the valid line types:
                    elif num_chunks == 3:
                        addr = line_chunks[0][:-1]
                        instr_bytes = line_chunks[1]
                        opcode = line_chunks[2]
                        operands = ""
                    elif num_chunks == 4:
                        addr = line_chunks[0][:-1]
                        instr_bytes = line_chunks[1]
                        opcode = line_chunks[2]
                        operands = line_chunks[3]
                    else:
                        raise Exception("Could not parse line: " + line.strip() + str(line_chunks))

                    # Count up op types. Muuuch easier for RISC ISA :)
                    if opcode in ["sb", "sh", "sw"]:
                        self.instr_count_map[funcname]["write"] += 1
                    elif opcode in ["lb", "lbu", "lh", "lhu", "lw", "lwu"]:
                        self.instr_count_map[funcname]["read"] += 1
                    elif opcode in ["ret"]:
                        self.instr_count_map[funcname]["return"] += 1
                    elif opcode in ["jal", "jalr"]:
                        self.instr_count_map[funcname]["call"] += 1
                    
                    num_bytes = 4 #len(instr_bytes.split())
                    self.instr_count_map[funcname]["size"] += num_bytes
                    self.instr_count_map[funcname]["total"] += 1
                    

        '''
        # Optional: print out the extracted operation counts
        for f in self.instr_count_map:
            print("Function " + f + " had:")
            for op in ["read", "write", "call", "return", "free"]:
                print("\t" + str(self.instr_count_map[f][op]) + " " + op)
        '''

    # Set sizes for all objects
    def set_object_sizes(self):

        # First, load globals from the symbol table
        self.load_sizes_symbol_table()

        # Next, set sizes of the things that are not globals.
        # This includes:
        # 1) Heap objects
        # 2) The SPECIAL memory regions
        # 3) The "STACK" special object
        # 4) The "UNKNOWN" objects that we get from some mem regions with no debug info
        # 5) The special case of the <none> object, which does not actually exist...
        no_sizes = set()
        for node in self.dg:
            if node[0] == NodeType.OBJECT:
                obj_name = self.get_node_ip(node)
                size = self.dg.node[node]["size"]
                new_size = None

                # One special case is that in our FreeRTOS, the heap is drawn from globals.
                # We don't want to double-count, so set this as a moderate sized object
                if obj_name == "global_ucHeap":
                    self.dg.node[node]["size"] = 1000

                # Otherwise set size based on some simple logic
                if size == 0:

                    if "heap_" in obj_name:
                        new_size = 500
                    elif "special-" in obj_name:
                        new_size = 1000
                    elif "STACK" == obj_name:
                        new_size = 1000
                    elif "UNKNOWN" in obj_name:
                        new_size = 1000
                    elif "<none>" == obj_name:
                        new_size = 0

                    if new_size == None:
                        raise Exception("Failed to set size for obj " + obj_name)

                    self.dg.node[node]["size"] = new_size

        # Print out the object sizes
        print("Printing object sizes!")
        output = set()
        total_size = 0
        for node in self.dg:
            if node[0] == NodeType.OBJECT:
                obj_name = self.get_node_ip(node)
                size = self.dg.node[node]["size"]
                total_size += size
                #output.add(obj_name + " " + str(size))

        # Print object sizes and percents
        #for node in self.dg:
        #    if node[0] == NodeType.OBJECT:
        #        obj_name = self.get_node_ip(node)
        #        size = self.dg.node[node]["size"]
        #        percent = str(float(size) / total_size * 100.0)[0:8] + "%"
        #        output.add((size, str(size) + " " + percent + " " + obj_name))
        #for (size, line) in sorted(output, reverse=True):
        #    print(line)
        
        # NUKE: set all sizes to 1
        print("Warning: using size of 1")
        for node in self.dg:
            if node[0] == NodeType.OBJECT:
                obj_name = self.get_node_ip(node)
                self.dg.node[node]["size"] = 1

        
    # Load sizes of all global objects from the symbol table using nm
    def load_sizes_symbol_table(self):
        
        prog_binary = self.prog_binary

        # Attempt to locate objdump...
        ISP_PREFIX = os.environ["ISP_PREFIX"]
        nm = os.path.join(ISP_PREFIX, "riscv32-unknown-elf", "bin", "nm")
        if not os.path.isfile(nm):
            raise Exception("WARNING: could not find objdump. Looked for " + objdump)

        nm_output = prog_binary + ".nm"
        print("Putting NM output at: " + nm_output)        
        # Run nm if it's not there
        if not os.path.isfile(nm_output):
            os.system("nm " + prog_binary + " -l -S -v  > " + nm_output)

        loaded_globals = {}
            
        with open(nm_output) as fh:
            addr = ""
            size = ""
            symbol_kind = ""
            name = ""
            src = ""

            for line in fh:
                line = line.strip()

                parts = line.split()
                if len(parts) in [4,5]:
                    addr = parts[0]
                    size = parts[1]
                    symbol_kind = parts[2]
                    name = parts[3]
                    #src = parts[4] # some don't have src field... for now we are not using anyways

                    if symbol_kind in ["b", "B", "d", "D", "r", "R"]:
                        size = int(size, 16)
                        #print("Found global " + name + " at addr " + addr + " of size " + str(size))
                        loaded_globals["global_" + name] = size

        # Now scan the graph and set sizes!
        set_sizes = 0
        for node in self.dg:
            if node[0] == NodeType.OBJECT:
                obj_name = self.get_node_ip(node)
                if obj_name in loaded_globals:
                    size = loaded_globals[obj_name]
                    #print("Setting size of " + obj_name + " in graph to " + str(size))
                    self.dg.node[node]["size"] = size
                    set_sizes += 1
                    
        print("Set the sizes of " + str(set_sizes) + " globals!")
            
    # Instead of using addr2line like uSCOPE variant, use DWARF for more reliable data scraping.
    # Populates the ip_to_X maps.
    def get_dwarf_info(self):

        OS_labels = ["FreeRTOS/Source", "FreeRTOS-Plus/Source"]
        
        # Open ELF
        with open(self.prog_binary, 'rb') as elf_file:

            ef = ELFFile(elf_file)

            # See if we have DWARF info. Currently required
            if not ef.has_dwarf_info():
                raise Exception('  file has no DWARF info')
                return

            dwarfinfo = ef.get_dwarf_info()

            for CU in dwarfinfo.iter_CUs():
                
                current_dir = ""
                current_file = ""
                current_func = ""
                
                for DIE in CU.iter_DIEs():
                    try:
                        if str(DIE.tag) == "DW_TAG_compile_unit":
                            
                            # Get name of compilation unit
                            current_CU = DIE.attributes["DW_AT_name"].value.decode("utf-8")
                            current_CU = os.path.normpath(current_CU)

                            # Extract syntatic cut info
                            current_dir = os.path.dirname(current_CU)
                            current_file = os.path.basename(current_CU)

                            # Anything that ends in .S is assembly and so doesn't actually have 'functions'...
                            # As a result, for any .S compilation unit, just insert a dummy CU func
                            if current_file[-2:] == ".S":
                                func_name = "CU_" + current_file
                                self.func_to_func[func_name] = func_name
                                self.func_to_file[func_name] = current_file
                                self.func_to_dir[func_name ] = current_dir
                                for label in OS_labels:
                                    if label in current_dir:
                                        self.os_functions.add(func_name)
                                
                        # We only care about functions (subprograms)
                        if str(DIE.tag) == "DW_TAG_subprogram":

                            if not ("DW_AT_name" in DIE.attributes and "DW_AT_low_pc" in DIE.attributes):
                                #print(str(DIE))
                                #print("Skipping a subprogram DIE.")
                                continue

                            func_name = DIE.attributes["DW_AT_name"].value.decode("utf-8")
                            func_name = str(func_name)
                            self.func_to_func[func_name] = func_name
                            self.func_to_file[func_name] = current_file
                            self.func_to_dir[func_name] = current_dir
                            for label in OS_labels:
                                if label in current_dir:
                                    self.os_functions.add(func_name)
                                    #print("OS func: " + func_name + " in " + current_dir)
                            

                    except Exception as e:
                        print(e)
                        #print(traceback.print_exc())
                        #print("error: " + str(Exception.print_exc()))
        
    # Add a single dg into an aggregate running dg of all loaded CAPMAPs.
    def add_capmap(self, dg, fn):

        number_calls = 0
        added_obj_nodes = 0
        added_instr_nodes = 0
        added_edges = {}
        for op in ops:
            added_edges[op] = 0

        size = int(os.path.getsize(fn) / (1024 * 1024))
        print("Processing " + os.path.split(fn)[1] + " (" + str(size) + "MB)")

        for node in dg:

            # If I don't have this node, add it and set attributes
            if not node in self.dg:
                self.dg.add_node(copy.deepcopy(node))
                for prop in ["size", "allocator", "va", "slab_cache", "name", "weight"]:
                    if prop in dg.node[node]:
                        self.dg.node[node][prop] = dg.node[node][prop]
                if node[0] == NodeType.OBJECT:
                    added_obj_nodes += 1
                else:
                    added_instr_nodes += 1

            # Loop over successors to get edges
            for objnode in dg.successors(node):
                
                # If didn't have other vertex, add as well
                if not objnode in self.dg:
                    self.dg.add_node(copy.deepcopy(objnode))
                    for prop in ["size", "allocator", "va", "slab_cache", "name", "weight"]:
                        if prop in dg.node[objnode]:
                            self.dg.node[objnode][prop] = dg.node[objnode][prop]

                    if objnode[0] == NodeType.OBJECT:
                        added_obj_nodes += 1
                    else:
                        added_instr_nodes += 1

                # Next, either add new edge or just add weights onto existing edge.
                edge_data = dg.get_edge_data(node, objnode)
                number_calls += edge_data["call"]
                if not self.dg.has_edge(node, objnode):
                    self.dg.add_edge(node, objnode,
                                     read = edge_data["read"],
                                     write = edge_data["write"],
                                     call = edge_data["call"],
                                     free = edge_data["free"])
                    self.dg.get_edge_data(node, objnode)["return"] = edge_data["return"]

                    for op in ops:
                        if edge_data[op] > 0:
                            added_edges[op] += 1
                else:
                    for op in ops:
                        self.dg.get_edge_data(node, objnode)[op] += edge_data[op]
                        
        total_added = added_obj_nodes + added_instr_nodes
        if self.verbose:
            print("\tTotal calls: " + str(number_calls))
            print("\tAdded object nodes: " + str(added_obj_nodes))
            print("\tAdded subj nodes: " + str(added_instr_nodes))
            for op in ops:
                print("\tAdded " + op + " edges: " + str(added_edges[op]))
                total_added += added_edges[op]
            print("\tTotal added from " + os.path.split(fn)[1] + ": " + str(total_added))

    # This function computes a set called live_functions.
    # A function is live if it has call or return edges. This set it used for:  
    # 1) to be able to calculate PS effects of removing dead code,
    # 2) As an optimization for the code clusterer to save compute time
    def calc_live_functions(self):
        for node in self.dg:
            if node[0] == NodeType.SUBJECT:
                func_name = self.get_node_label(node)
                for obj_node in self.dg.successors(node):
                    if obj_node[0] == NodeType.SUBJECT:
                        dest_func = obj_node[1]
                        self.live_functions.add(func_name)
                        self.live_functions.add(dest_func)
                    else:
                        self.live_functions.add(func_name)
        if self.verbose:
            print("Total functions: " + str(len(self.functions)))
            print("Live functions: " + str(len(self.live_functions)))

    # Only building no clustering map for the PIPE variant
    def build_object_ownership_maps(self):
        for node in self.dg:
            if node[0] == NodeType.OBJECT:
                obj_name = self.get_node_ip(node)
                self.obj_no_cluster[obj_name] = obj_name            

    # Returns a set of all the subject clusters given a clustering map
    def get_subjects(self, subj_clusters):
        subjects = set()
        for f in subj_clusters:
            subj_cluster = subj_clusters[f]
            subjects.add(subj_cluster)
        return subjects

    # Returns a set of all the object clusters given a clustering map
    def get_objects(self, obj_clusters):
        objects = set()
        for o in obj_clusters:
            node_cluster = obj_clusters[node_ip]
            objects.add(node_cluster)
        return objects

    def get_node_label(self, node):
        return node[1]

    # Get an graph object from its objaddr/ip
    # Slow, could make map for O(1) lookups
    def get_object(self, objaddr):
        for o in self.dg:
            if o[0] == NodeType.OBJECT:
                if self.get_node_ip(o) == objaddr:
                    return o
        return None

    # Get the size of a node. It's either an instruction or a data object
    def get_node_size(self,node):
        return self.dg.node[node]["size"]

    # Get the address of a node
    def get_node_ip(self,node):
        return node[1]
    
if __name__ == '__main__':

    if len(sys.argv) > 1:
        print("Opening CAPMAP for " + sys.argv[1])
        cmap = CAPMAP(sys.argv[1])
    else:
        print("python CAPMAP.py <binary> <kmap>")
