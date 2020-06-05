#!/usr/bin/python
# This tool creates syntactic domains using DWARF metadata about each function
# It creates (1) Compilation Unit, (2) Directory, and (3) File domains.

import sys
import shutil
import os.path
import subprocess
from elftools.elf.elffile import ELFFile
from elftools.elf.constants import SH_FLAGS
from elftools.common.py3compat import itervalues
from elftools.dwarf.locationlists import LocationEntry
from elftools.dwarf.descriptions import describe_form_class


# For the OS / Application cut, these are the tags for considering something in OS:
OS_labels = ["FreeRTOS/Source", "FreeRTOS-Plus/Source"]

compiler_labels = ["newlib"]

def create_syntactic_domains(cmap, elf_filename):

    # Open ELF
    with open(elf_filename, 'rb') as elf_file:

        ef = ELFFile(elf_file)

        # See if we have DWARF info. Currently required
        if not ef.has_dwarf_info():
            raise Exception('  file has no DWARF info')
            return

        dwarfinfo = ef.get_dwarf_info()

        OS_domains = {}
        CU_domains = {}
        dir_domains = {}
        file_domains = {}
        func_domains = {}
        
        for CU in dwarfinfo.iter_CUs():
            current_CU = ""
            current_dir = ""
            current_file = ""
            current_OS = ""
            
            for DIE in CU.iter_DIEs():
                #print(str(DIE))
                try:
                    if str(DIE.tag) == "DW_TAG_compile_unit":
                        # Get name of compilation unit
                        current_CU = DIE.attributes["DW_AT_name"].value.decode("utf-8")
                        current_CU = os.path.normpath(current_CU)

                        # Extract syntatic cut info
                        current_dir = os.path.dirname(current_CU)
                        current_file = os.path.basename(current_CU)

                        # For the OS cut, determine if this is application or OS
                        current_OS = "App"
                        for l in OS_labels:
                            if l in current_CU:
                                current_OS = "FreeRTOS"

                        is_lib = False
                        if "newlib/libc" in current_CU:
                            is_lib = True

                        # Anything that ends in .S is assembly and so doesn't actually have 'functions'...
                        # As a result, for any .S compilation unit, just insert a dummy CU func
                        # Also just making a new domain for each CU...
                        if current_file[-2:] == ".S" or is_lib:
                            func_name = "CU_" + current_file
                            
                            OS_domains[func_name] = current_OS
                            CU_domains[func_name] = current_CU                            
                            dir_domains[func_name] = current_dir
                            file_domains[func_name] = current_file
                            func_domains[func_name] = func_name
                            
                    # We only care about functions (subprograms)
                    if str(DIE.tag) == "DW_TAG_subprogram":

                        if not ("DW_AT_name" in DIE.attributes and "DW_AT_low_pc" in DIE.attributes):
                            #print(str(DIE))
                            #print("Skipping a subprogram DIE.")
                            continue

                        func_name = DIE.attributes["DW_AT_name"].value.decode("utf-8")
                        declared_file = DIE.attributes["DW_AT_decl_file"]
                        func_display_name = str(func_name)
                        
                        CU_domains[func_name] = current_CU
                        dir_domains[func_name] = current_dir
                        file_domains[func_name] = current_file
                        OS_domains[func_name] = current_OS
                        func_domains[func_name] = func_name
                        
                except Exception as e:
                    print(e)
                    #print(traceback.print_exc())
                    #print("error: " + str(Exception.print_exc()))

        domains = {}
        domains["func"] = func_domains
        domains["file"] = file_domains        
        domains["dir"] = dir_domains
        domains["os"] = OS_domains

        # Fix up syntactic domains by adding all missing functions not in DWARF
        # with simple reflexive mappings.
        for cut in domains:
            for f in cmap.functions:
                if not f in domains[cut]:
                    #print("Adding in " + f)
                    domains[cut][f] = f
                         
        return domains

# Install these domain files into the policy kernel directory
def install_domains(domains, name):
    isp_prefix = os.environ['ISP_PREFIX']
    kernels_dir = os.path.join(isp_prefix, "kernels")
    for f in os.listdir(kernels_dir):
        if "compartmentalization" in f:
            kernel_dir = os.path.join(kernels_dir, f)
            domains_dir = os.path.join(kernel_dir, "domains")
            if not os.path.exists(domains_dir):
                os.mkdir(domains_dir)
                print("Note: Created domains dir in kernel directory.")
            domain_filename = os.path.join(domains_dir, name + ".domains")
            print_subj_domains(domains, domain_filename)
        
def print_subj_domains(domains, name):

    # Convert the string names (e.g., "foo.c", "bar.c") into numbers (e.g., "1", "2")
    domain_ids = {}
    current_id = 1
    for f in domains:
        label = domains[f]
        if not label in domain_ids:
            domain_ids[label] = current_id
            current_id += 1
    
    fh = open(name, "w")

    for f in sorted(list(domains)):
        domain_label = domains[f]
        domain_id = domain_ids[domain_label]
        fh.write(f + " " + str(domain_id) + " " + str(domain_label) + "\n")
                    

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: run with one argument, the program to create syntacic domains from.")
        sys.exit()

    prog = sys.argv[1]
    
    if not os.path.exists(prog):
        print("Error: can not find " + prog)
        sys.exit()

    print("Creating syntactic domains...")    
    domains = create_syntactic_domains(prog)
    print("Done.")
       
