#!/usr/bin/python
# This tool creates syntactic domains using DWARF metadata about each function
# It creates (1) Compilation Unit, (2) Directory, and (3) File domains.

from InstallDomains import *

import sys
import shutil
import os.path
import subprocess
from elftools.elf.elffile import ELFFile
from elftools.elf.constants import SH_FLAGS
from elftools.common.py3compat import itervalues
from elftools.dwarf.locationlists import LocationEntry
from elftools.dwarf.descriptions import describe_form_class


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
        mono_domains = {}
        
        for CU in dwarfinfo.iter_CUs():
            current_CU = ""
            current_dir = ""
            current_file = ""
            current_OS = ""
            current_mono = "1"
            
            for DIE in CU.iter_DIEs():
                #print(str(DIE))
                try:
                    if str(DIE.tag) == "DW_TAG_compile_unit":
                        # Get name of compilation unit
                        comp_dir = DIE.attributes["DW_AT_comp_dir"].value.decode("utf-8")
                        name = DIE.attributes["DW_AT_name"].value.decode("utf-8")
                        current_CU = os.path.normpath(os.path.join(comp_dir, name))
                        #print("Got CU: " + current_CU)

                        if "hope-src/" in current_CU:
                            current_CU = current_CU.split("hope-src/")[1]
                        
                        # Extract syntatic cut info
                        current_dir = os.path.dirname(current_CU)
                        current_file = os.path.basename(current_CU)
                        #print("CU: " + current_CU + ", dir=" + current_dir + ",file=" + current_file)

                        # For the OS cut, determine if this is Application, OS, or compiler
                        current_OS = classify_OS(current_CU)
                        #print("Type: " + current_OS)
                        is_lib = False
                        for l in compiler_labels:
                            if l in current_CU:
                                is_lib = True
                            
                        # Anything that ends in .S is assembly and so doesn't actually have 'functions'...
                        # As a result, for any .S compilation unit, just insert a dummy CU func
                        # Also just making a new domain for each CU...
                        if current_file[-2:] == ".S": # or is_lib:
                            func_name = "CU_" + current_file

                            mono_domains[func_name] = current_mono
                            OS_domains[func_name] = current_OS
                            CU_domains[func_name] = current_CU                            
                            dir_domains[func_name] = current_dir
                            file_domains[func_name] = current_file
                            func_domains[func_name] = func_name

                            # Insert the OS domain into the cmap
                            cmap.func_to_OS[func_name] = current_OS
                            
                    # We only care about functions (subprograms)
                    if str(DIE.tag) == "DW_TAG_subprogram":

                        if not ("DW_AT_name" in DIE.attributes and "DW_AT_low_pc" in DIE.attributes):
                            #print(str(DIE))
                            #print("Skipping a subprogram DIE.")
                            continue

                        func_name = DIE.attributes["DW_AT_name"].value.decode("utf-8")
                        declared_file = DIE.attributes["DW_AT_decl_file"]
                        func_display_name = str(func_name)

                        mono_domains[func_name] = current_mono                        
                        CU_domains[func_name] = current_CU
                        dir_domains[func_name] = current_dir
                        file_domains[func_name] = current_file
                        OS_domains[func_name] = current_OS
                        func_domains[func_name] = func_name
                        
                        cmap.func_to_OS[func_name] = current_OS
                        
                except Exception as e:
                    print(e)
                    #print(traceback.print_exc())
                    #print("error: " + str(Exception.print_exc()))

        domains = {}
        domains["mono"] = mono_domains
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


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: run with one argument, the program to create syntactic domains from.")
        sys.exit()

    print("RUnning on : " + sys.argv[1])
    cmap = CAPMAP(sys.argv[1])        
    prog = sys.argv[1]
    
    if not os.path.exists(prog):
        print("Error: can not find " + prog)
        sys.exit()

    print("Creating syntactic domains...")    
    domains = create_syntactic_domains(cmap, prog)
    print("Done.")
