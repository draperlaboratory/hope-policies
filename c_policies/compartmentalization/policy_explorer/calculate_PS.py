#!/usr/bin/python

# This file contains the logic to calculate PS metrics given a CAPMAP.
# Main use case is "python calculate_PS.py <vmlinux> <kmap>".
#
# This is a port for the PIPE variant.
# 
# It computes the privilege set (PS) and privilege set ratio (PSR).

import sys
import copy
import datetime

from CAPMAP import *
from DomainCreator import *
from SyntacticDomains import *

# List of ops, ops_all includes combined readwrite
ops = ["read", "write", "call", "return", "free"]

# When working with (and minimizing) PS, we occasionally require a single number that
# aggregates the various kinds of PS together (refered to as PS_total).
# A knob we can turn is how to weigh the various kinds of PS against each other.
# This simple function simply adds them (all weight of 1); a future exploration
# direction is applying various weighting schemes to guide the algorithms.
def calc_PS_total(PS):
    return PS["read"] + PS["write"] + PS["call"] + PS["return"] + PS["free"]

# Calculate PS_min for a cmap. Returns a dict indexed by op.
# PS_min is the privilege required by the program, so we simply
# follow the CAPMAP to see what was required.
def calculate_PSmin(cmap):
    
    PS_min = {}
    PS_min["read"] = 0
    PS_min["write"] = 0
    PS_min["readwrite"] = 0    
    PS_min["call"] = 0
    PS_min["return"] = 0
    PS_min["free"] = 0

    ps_min_read_sources = {}
    ps_min_write_sources = {}
    
    for node in cmap.dg:

        # Follow outgoing edges. Only instructions have successors.
	# Successors can be obj or instr.
        for obj_node in cmap.dg.successors(node):
            
            size = cmap.get_node_size(obj_node)
        
            edge = cmap.dg.get_edge_data(node, obj_node)
            
            for op in ops:
                PS_min[op] += size if edge[op] > 0 else 0

            # Optional track sources of read/write psmin 
            if edge["read"] > 0:
                obj_ip = cmap.get_node_ip(obj_node)
                if obj_ip not in ps_min_read_sources:
                    ps_min_read_sources[obj_ip] = 0
                ps_min_read_sources[obj_ip] += size

            if edge["write"] > 0:
                obj_ip = cmap.get_node_ip(obj_node)
                if obj_ip not in ps_min_write_sources:
                    ps_min_write_sources[obj_ip] = 0
                ps_min_write_sources[obj_ip] += size            


            #PS_min["readwrite"] += size if (edge["write"] > 0 or edge["read"] > 0) else 0

    '''
    # Optional print top psmin read sources
    ps_min_read = PS_min["read"]
    print("PS_min_read:" + str(ps_min_read))
    print("Top 20 object sources of read PSmin:")
    sorted_sources = sorted(zip(ps_min_read_sources.values(), list(ps_min_read_sources)), reverse=True)

    index = 0
    for (v,k) in sorted_sources:
        percent = float(v) / ps_min_read * 100.0
        if k in cmap.ip_to_func:
            func = cmap.ip_to_func[k]
            print("\t" + k + "(" + func + ") " + str(v) + " (" + str(percent) + "%)")            
        else:
            print("\t" + k + " " + str(v) + " (" + str(percent) + "%)")
        index += 1
        if index > 20:
            break
    # Optional print top psmin write sources
    
    ps_min_write = PS_min["write"]
    print("PS_min_write:" + str(ps_min_write))
    print("Top 20 object sources of write PSmin:")
    sorted_sources = sorted(zip(ps_min_write_sources.values(), list(ps_min_write_sources)), reverse=True)

    index = 0
    for (v,k) in sorted_sources:
        percent = float(v) / ps_min_write * 100.0
        if k in cmap.ip_to_func:
            func = cmap.ip_to_func[k]
            print("\t" + k + "(" + func + ") " + str(v) + " (" + str(percent) + "%)")            
        else:
            print("\t" + k + " " + str(v) + " (" + str(percent) + "%)")
        index += 1
        if index > 20:
            break    
    '''

    return PS_min
            
# Calculate the PS_mono for a kmap. Returns a dict indexed by op.
# This represents all the privilege in the system with no separation.
# At a high level, it's the number of instructions that can perform an
# op times the number of bytes that are accessible.
# This interpretation assumes that we might use an operation on anything
# (might call data, might write code, etc).
# Parameterizable by whether or not we model Write XOR Execute (WXORE),
# and simple CFI which tightens the above interpretation.
# LIVE means remove dead code, which has an impact on privilege.
def calculate_PSmono(cmap):

    # Should dead code contribute to PS mono?
    LIVE=False
    
    PS_mono = {}
    
    # Count up number of each kind of operation and
    # the total size of all instructions themselves
    total_instr_size = 0
    num_reads = 0
    num_writes = 0
    num_calls = 0
    num_returns = 0    
    num_frees = 0

    # Also count entry points. Assume 1 per func.
    total_entry_points = 0
    total_return_points = 0
    
    for f in cmap.functions:
        
        # Skip if we're removing dead and this is dead
        if LIVE and not f in cmap.live_functions:
            continue
        
        num_reads += cmap.instr_count_map[f]["read"]
        num_writes += cmap.instr_count_map[f]["write"]
        num_calls += cmap.instr_count_map[f]["call"]
        num_returns += cmap.instr_count_map[f]["return"]
        num_frees += cmap.instr_count_map[f]["free"]
        total_instr_size += cmap.instr_count_map[f]["size"]
        total_return_points += cmap.instr_count_map[f]["call"] # one valid return point per call
        total_entry_points += 1

    #print("Total reads: " + str(num_reads))
    #print("Total writes: " + str(num_writes))
    #print("Total calls: " + str(num_calls))
    #print("Total returns: " + str(num_returns))
    #print("Total free: " + str(num_frees))
    
    # Count up the size of data objects.
    total_data_size = 0
    total_global_size = 0
    total_heap_size = 0
    total_special_size = 0
    for node in cmap.dg:
        if node[0] == NodeType.OBJECT:
            size = cmap.get_node_size(node)
            obj_name = cmap.get_node_ip(node)
            total_data_size += size
            if "heap_" in obj_name:
                total_heap_size += size
            elif "global_" in obj_name:
                total_global_size += size
            else:
                total_special_size += size
            
    #print("Total data size : " + str(total_data_size))
    #print("\tTotal heap size: " + str(total_heap_size))
    #print("\tTotal global size: " + str(total_global_size))
    #print("\tTotal special size: " + str(total_special_size))        
    #print("Total instr size : " + str(total_instr_size))
    
    # Finally, compute PSmono
    # In the PIPE case, there is CFI so that part includes the valid entry and return points
    # Assuming W^X policy, which can be expressed using existing rules (already tags differentiating code/data)

    #print("PS mono breakdown:")
    #print("Num reads: " + str(num_reads) + ", readable data bytes: " + str(total_data_size))
    #print("Num calls: " + str(num_calls) + ", num entry points: " + str(total_entry_points))
    #print("Num returns: " + str(num_returns) + ", num return points: " + str(total_return_points))    
    
    PS_mono["readwrite"] = 0 #(num_writes + num_reads) * total_data_size
    PS_mono["read"] = num_reads * total_data_size
    PS_mono["write"] = num_writes * total_data_size
    PS_mono["free"] = 0 # TODO: add privilege for freeing?
    PS_mono["call"] = num_calls * total_entry_points
    PS_mono["return"] = num_returns * total_return_points
    return PS_mono

# Calculate the PS of a particular set of subj and obj groups
# The PIPE variant does not have unmediation, so this is much simpler than the uSCOPE case
def calculate_PScut(cmap, subject_clusters, object_clusters, return_sum = True):
    
    LIVE=False
    
    # Calculating the PS for a cut efficiently involves pre-computing some intermediate state
    # This includes:
    # 1) Precomputing the number of entry points and return points per cluster
    # 2) An accessible_size map that stores the amount of object data a cluster has access to
    # 3) A cluster_op_count map that stores how many ops of each kind are in each cluster
    #
    # After calculating these things, we can compute the PS of each cluster, then sum

    # Make a list of clusters
    clusters = set()
    for f in cmap.functions:
        cluster = subject_clusters[f]
        if not cluster in clusters:
            clusters.add(cluster)
            
    #### Step 1: Calculate the number of entry and return points per cluster ###
    entry_points_per_cluster = {}
    return_points_per_cluster = {}
    for f in cmap.functions:

        # Add to cluster size
        cluster = subject_clusters[f]
        if not cluster in entry_points_per_cluster:
            entry_points_per_cluster[cluster] = 0
            return_points_per_cluster[cluster] = 0

        entry_points_per_cluster[cluster] += 1
        return_points_per_cluster[cluster] += cmap.instr_count_map[f]["call"]

    ### Step 2: Calculate size of each object cluster ###
    # Next, build a size map for each object cluster
    obj_cluster_sizes = {}
    for node in cmap.dg:
        if node[0] == NodeType.OBJECT:
            obj_ip = cmap.get_node_ip(node)
            obj_cluster = object_clusters[obj_ip]
            if not obj_cluster in obj_cluster_sizes:
                obj_cluster_sizes[obj_cluster] = 0
            obj_cluster_sizes[obj_cluster] += cmap.get_node_size(node)
        
    # Print sizes
    '''
    print("Obj cluster sizes:")
    for c in sorted(obj_cluster_sizes):
        print("obj_cluster_sizes[" + c + "]= " + str(obj_cluster_sizes[c]))
    '''
    
    ### Step 3: Calculate accessible objs and size of each op by cluster ###
    accessible_objs = {}
    for node in cmap.dg:
        if node[0] == NodeType.SUBJECT:
            
            func_name = cmap.get_node_ip(node)
            subj_cluster = subject_clusters[func_name]
            
            if not subj_cluster in accessible_objs:
                accessible_objs[subj_cluster] = {}
                for op in ops:
                    accessible_objs[subj_cluster][op] = set()

            for obj_node in cmap.dg.successors(node):

                if obj_node[0] == NodeType.SUBJECT:
                    obj_cluster = subject_clusters[cmap.get_node_ip(obj_node)]
                elif obj_node[0] == NodeType.OBJECT:
                    obj_cluster = object_clusters[cmap.get_node_ip(obj_node)]

                edge = cmap.dg.get_edge_data(node, obj_node)                    
                for op in ops:
                    if edge[op] > 0:
                        accessible_objs[subj_cluster][op].add(obj_cluster)

    # Next, we can calculate the accessible number of bytes from each cluster by op type
    # Store in dict indexed by cluster name and op type
    accessible_size = {}
    for subj_cluster in clusters:
        
        accessible_size[subj_cluster] = {}
        
        for op in ops:
            accessible_size[subj_cluster][op] = 0
            
        if subj_cluster in accessible_objs:

            for op in ops:
                
                for obj_cluster in accessible_objs[subj_cluster][op]:

                    # For read/write/free, the size is the sum of the object cluster
                    # For call/return, the size is the size of the code
                    if op in ["read", "write", "free"]:
                        accessible_size[subj_cluster][op] += obj_cluster_sizes[obj_cluster]
                    elif op == "call":
                        accessible_size[subj_cluster][op] += entry_points_per_cluster[obj_cluster]
                    elif op == "return":
                        accessible_size[subj_cluster][op] += return_points_per_cluster[obj_cluster]
                        
                #accessible_size[subj_cluster]["readwrite"] += accessible_size[subj_cluster]["read"] + accessible_size[subj_cluster]["write"]

    '''
    print("Unmediated accessible size: ")
    for subj_cluster in accessible_size:
        for op in accessible_size[subj_cluster]:
            if accessible_size[subj_cluster][op] > 0:
                print("accessible_size[" + subj_cluster + "][" + op + "]=" + str(accessible_size[subj_cluster][op]))
    '''
    
    # Step 4: Count the number of operations of each kind in each cluster
    # Store in dict indexed by operation type and cluster name
    # cluster_op_counts[cluster][op] = N
    cluster_op_counts = {}
    for f in cmap.functions:
        
        subj_cluster = subject_clusters[f]
        if subj_cluster not in cluster_op_counts:
            cluster_op_counts[subj_cluster] = {}
            for op in ops:
                cluster_op_counts[subj_cluster][op] = 0
            cluster_op_counts[subj_cluster]["functions"] = 0

        # Skip if we're removing dead and this is dead
        if LIVE and not f in cmap.live_functions:
            continue
        
        cluster_op_counts[subj_cluster]["read"] += cmap.instr_count_map[f]["read"]
        cluster_op_counts[subj_cluster]["write"] += cmap.instr_count_map[f]["write"]
        cluster_op_counts[subj_cluster]["call"] += cmap.instr_count_map[f]["call"]
        cluster_op_counts[subj_cluster]["return"] += cmap.instr_count_map[f]["return"]
        cluster_op_counts[subj_cluster]["free"] += cmap.instr_count_map[f]["free"]
        cluster_op_counts[subj_cluster]["functions"] += 1 

    # Print instr count map
    '''
    for s in sorted(cluster_op_counts):
        d = cluster_op_counts[s]
        #print(s + ": read=" + str(d["read"]) + ",write=" + str(d["write"]) + ",call=" + str(d["call"]) + ",return=" + str(d["return"]) + ",free=" + str(d["free"]))
        print(s + ": " + str(d["read"]) + "," + str(d["write"]) + "," + str(d["call"]) + "," + str(d["return"]) + "," + str(d["free"]))
    '''

    # Step 5: With these data structures built, we can efficiently compute PS.
    # We know the size of each subject cluster and object cluster.
    # We know the number of ops of each type in each subject cluster.
    # And we know the accessible size for each operation type for each cluster
    
    PS_cut = {}
    PS_cut["read"] = {}
    PS_cut["write"] = {}
    PS_cut["readwrite"] = {}
    PS_cut["call"] = {}
    PS_cut["return"] = {}
    PS_cut["free"] = {} 

    # The PS from each cluster is the number of operations of that type multiplied by the size as calculated above
    for subj_cluster in cluster_op_counts:
        PS_cut["read"][subj_cluster] = cluster_op_counts[subj_cluster]["read"] * accessible_size[subj_cluster]["read"]
        PS_cut["write"][subj_cluster] = cluster_op_counts[subj_cluster]["write"] *accessible_size[subj_cluster]["write"]
        PS_cut["free"][subj_cluster] = cluster_op_counts[subj_cluster]["free"] * accessible_size[subj_cluster]["free"]
        PS_cut["call"][subj_cluster] = cluster_op_counts[subj_cluster]["call"] * accessible_size[subj_cluster]["call"]
        PS_cut["return"][subj_cluster] = cluster_op_counts[subj_cluster]["return"] * accessible_size[subj_cluster]["return"]        
    
    # We now have PS_cut calculated broken down by subj_cluster
    # We can either return this raw, or sum up all subj together
    if return_sum:
        PS_all = {}
        PS_all["read"] = 0
        PS_all["write"] = 0
        PS_all["call"] = 0
        PS_all["return"] = 0        
        PS_all["free"] = 0      

        for subj_cluster in clusters:
            for op in ops:
                PS_all[op] += PS_cut[op][subj_cluster]
    
        return PS_all
    
    else:
        return PS_cut
    
def calc_PSR_cut(cmap, cut):
    PS_mono = calc_PS_total(calculate_PSmono(cmap))
    PS_cut = calc_PS_total(calculate_PScut(cmap, cut, cmap.obj_no_cluster, return_sum=True))
    PSR = float(PS_cut) / PS_mono
    return PSR
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Default behavior for this file: read a kmap and compute: mono,min,dirs,files,funcs
        cmap = CAPMAP(sys.argv[1])
        print("PS min: " + str(calculate_PSmin(cmap)))
        print("PS mono: " + str(calculate_PSmono(cmap)))

        syntactic_domains = create_syntactic_domains(sys.argv[1])

        # Print out PSRs for the syntactic cuts
        for cut in syntactic_domains:
            PSR = calc_PSR_cut(cmap, syntactic_domains[cut])
            print("PSR for " + cut + ":" + str(PSR))
        
    else:
        print("Use python calculate_PS.py <vmlinux> <kmap> to run on a .kmap")
