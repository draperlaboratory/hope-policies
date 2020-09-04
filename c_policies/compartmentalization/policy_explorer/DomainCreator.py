#!/usr/bin/python

# The DomainCreator contains algorithms for solving the clustering problems related to uSCOPE,
# specifically (1) clustering functions into subject domains and (2) clustering primitive objects
# into object domains.
#
# This is a port of the uSCOPE DomainCreator for the PIPE variant of the compartmentalizations.

import random
import copy
import itertools

from CAPMAP import *
from calculate_PS import *
from WorkingSets import *

# DomainCreator supports three strategiies
class ClusterStrategy(Enum):
    CLUSTER_SIZE = 1
    CLUSTER_RATIO = 2
    CLUSTER_RULES = 3

# Datatype for tracking the two merge types
class MergeType(Enum):
    MERGE_SUBJ = 1
    MERGE_OBJ = 2

class DomainCreator:

    def __init__(self, cmap):

        # The CAPMAP graph object that we are running clustering algorithms on
        self.cmap = cmap
        
        # A map that records which cluster each function currently belongs to
        self.function_assignment = {}

        # A set of current clusters, stored as lists e.g., clusters[c] = [f1, f2 ... fn]
        self.clusters = {}

        # A running total of each cluster's current size
        self.cluster_sizes = {}        

        # A map that records which cluster each object is in
        self.obj_cluster_to_objs = {}

        # A map that records which object cluster each object is in
        self.obj_assignment = {}

        # A map that records the size of each object cluster
        self.object_cluster_sizes = {}

        # A map of which objects are accessed by each function per op type
        self.accessed_objs = {}

        # A map of which object clusters are accessed by each function
        self.accessing_clusters = {}        

        # A map of which functions are called by each function
        self.called_funcs = {}

        # Clusters that are done merging
        self.finished_clusters = set()
                
        # A cache of reachable objects from each cluster
        self.reachable_objects_cache = {}

        # A cache of reachable objects from each cluster
        self.reachable_object_clusters_cache = {}        
        
        # A cache of reachable subjects from each cluster
        self.reachable_clusters_cache = {}

        # A cache of the calls saved if we merged c1 and c2
        self.external_calls_saved = {}        
        
        # A switch to control how we count cluster size. Values are "instr" or "func".
        # "func" mostly deprecated now.
        self.SIZE_METRIC="instr"

        # A set of working sets, updated as merges happen
        self.current_working_sets = []


    # Reset and initialize data structures before clustering.
    # 1) Creates the initial clustering assignment, one func per cluster
    # 		Clusters get their initial sizes and opcounts from CAPMAP
    # 2) Builds called_funcs, accessible_objs, and obj_sizes for use later
    # 3) Initializes caches by computing from scratch
    def prepare_clustering(self, cmap):
        
        ##################################################
        ###   Create initial clusters and init stats   ###
        ##################################################
        self.clusters = {}
        self.finished_clusters = set()        
        self.function_assignment = {}        
        self.cluster_sizes = {}
        self.cluster_call_ops = {}
        self.cluster_read_ops = {}
        self.cluster_write_ops = {}
        self.cluster_free_ops = {}
        self.smallest_cluster_size = None        
        for f in self.cmap.live_functions:
            cluster_name = "[" + f + "]"
            self.clusters[cluster_name] = [f]
            self.function_assignment[f] = cluster_name
            function_size = int(self.cmap.instr_count_map[f]["size"])
            self.cluster_sizes[cluster_name] = function_size
            self.cluster_read_ops[cluster_name] = self.cmap.instr_count_map[f]["read"]
            self.cluster_write_ops[cluster_name] = self.cmap.instr_count_map[f]["write"]
            self.cluster_free_ops[cluster_name] = self.cmap.instr_count_map[f]["free"]
            self.cluster_call_ops[cluster_name] = self.cmap.instr_count_map[f]["call"] + \
                                                  self.cmap.instr_count_map[f]["return"]
            if self.smallest_cluster_size == None or function_size < self.smallest_cluster_size:
                self.smallest_cluster_size = function_size
        print("Minimum cluster size: " + str(self.smallest_cluster_size))


        ###########################################################
        ###   Build called_funcs, accessed_objs and obj_sizes   ###
        ###########################################################
        # called_funcs maps each func to funcs that it calls
        # accessed_objs maps each func to objects it accesses
        # obj_sizes maps each obj to its size for each op type (to include weight)
        # Initialize obj_cluster_to_objs as reflexive
        self.total_calls = 0
        self.object_sizes = {}
        self.object_cluster_sizes = {}
        self.called_funcs = {}
        self.accessed_objs = {}
        for op in ["read", "write", "free"]:
            self.accessed_objs[op] = {}
            self.object_sizes[op] = {}
            self.object_cluster_sizes[op] = {}
        obj_id = 0
        for node in self.cmap.dg:
            if node[0] == NodeType.SUBJECT:
                this_func = cmap.get_node_label(node)
                # Init if new func
                if not this_func in self.accessed_objs["read"]:
                    for op in ["read", "write", "free"]:
                        self.accessed_objs[op][this_func] = set()
                    self.called_funcs[this_func] = {}
                for obj_node in self.cmap.dg.successors(node):
                    edge = self.cmap.dg.get_edge_data(node, obj_node)
                    obj_label = obj_node[1]
                    if obj_node[0] == NodeType.SUBJECT:
                        called_func = obj_label
                        if not called_func in self.called_funcs[this_func]:
                            self.called_funcs[this_func][called_func] = 0
                        self.called_funcs[this_func][called_func] += edge["call"] + edge["return"]
                        self.total_calls += edge["call"] + edge["return"]
                    elif obj_node[0] == NodeType.OBJECT:
                        for op in ["read", "write", "free"]:
                            if edge[op] > 0:
                                self.accessed_objs[op][this_func].add(obj_label)
            elif node[0] == NodeType.OBJECT:
                obj_ip = self.cmap.get_node_ip(node)
                
                # Set object size
                size = self.cmap.dg.node[node]["size"]
                self.object_sizes["read"][obj_ip] = size #* weight[0]
                self.object_sizes["write"][obj_ip] = size #* weight[1]
                self.object_sizes["free"][obj_ip] = size #* weight[2]

                # Initialize object cluster
                obj_cluster_name = "[" + str(obj_ip) + "]"
                obj_id += 1
                self.obj_cluster_to_objs[obj_cluster_name] = set()
                self.obj_cluster_to_objs[obj_cluster_name].add(obj_ip)
                self.object_cluster_sizes["read"][obj_cluster_name] = size
                self.object_cluster_sizes["write"][obj_cluster_name] = size
                self.object_cluster_sizes["free"][obj_cluster_name] = size
                self.obj_assignment[obj_ip] = obj_cluster_name
                
                self.accessing_clusters[obj_cluster_name] = set()
                for subj_node in self.cmap.dg.predecessors(node):
                    accessing_func = cmap.get_node_label(subj_node)
                    accessing_cluster = self.function_assignment[accessing_func]
                    #print(accessing_func + " accesses " + obj_ip)
                    self.accessing_clusters[obj_cluster_name].add(accessing_cluster)

        #############################
        ###   Initialize Caches   ###
        #############################
        self.reachable_clusters_cache = {}
        self.reachable_objects_cache = {}        
        for op in ["read", "write", "free"]:
            self.reachable_objects_cache[op] = {}
            self.reachable_object_clusters_cache[op] = {}            
        self.external_calls_saved = {}
        
        # Initialize reachable_clusters_cache by computing from scratch
        for c in self.clusters:
            for op in ["read", "write", "free"]:
                self.reachable_objects_cache[op][c] = self.reachable_objs(c, op)
                self.reachable_object_clusters_cache[op][c] = self.reachable_obj_clusters(c, op)
            self.reachable_clusters_cache[c] = self.reachable_clusters(c)

        # Initialize external_calls_saved by computing from scratch
        for c1 in self.clusters:
            for c2 in self.reachable_clusters_cache[c1]:
                if not c1 in self.external_calls_saved:
                    self.external_calls_saved[c1] = {}
                self.external_calls_saved[c1][c2] = self.count_external_calls_saved(c1, c2)
        
    # Given a cluster, return which other clusters can be called from that cluster
    def reachable_clusters(self, c):
    
        # First, find all functions called by functions in this cluster
        all_called_funcs = set()
        for f in self.clusters[c]:
            if f in self.called_funcs:
                for called_f in self.called_funcs[f]:
                    all_called_funcs.add(called_f)

        # Then, take union of all of these clusters
        all_called_clusters = set()
        for f in all_called_funcs:
            cluster = self.function_assignment[f]
            if cluster != c and not cluster in self.finished_clusters:
                all_called_clusters.add(cluster)
        return all_called_clusters

    # Given a cluster, return a set of all objects accessed by that cluster
    def reachable_objs(self, c, op):

        reachable_objs = set()

        for f in self.clusters[c]:
            if f in self.accessed_objs[op]:
                for o in self.accessed_objs[op][f]:
                    reachable_objs.add(o)

        return reachable_objs


    # Given a cluster, return a set of all objects accessed by that cluster
    def reachable_obj_clusters(self, c, op):

        reachable_obj_clusters = set()

        for f in self.clusters[c]:
            if f in self.accessed_objs[op]:
                for o in self.accessed_objs[op][f]:
                    obj_cluster = self.obj_assignment[o]
                    reachable_obj_clusters.add(obj_cluster)

        return reachable_obj_clusters   

    # Merge two objects together. Logically put o2 into o1.
    # Reachable clusters are not affected, so we are only concerned
    # about reachable objects. The goal is correctness  not speed,
    # so let's simply recompute the object caches.
    def merge_object_clusters(self, o1, o2):

        #print("Merging obj cluster " + o1 + " with " + o2)
        #print(o1 + " size=" + str(len(self.obj_cluster_to_objs[o1])))
        #print(o2 + " size=" + str(len(self.obj_cluster_to_objs[o2])))        
        
        # Transfer over the objects
        for o in self.obj_cluster_to_objs[o2]:
            self.obj_assignment[o] = o1
            self.obj_cluster_to_objs[o1].add(o)
        del self.obj_cluster_to_objs[o2]

        # Update the accessing functions
        self.accessing_clusters[o1] = self.accessing_clusters[o1].union(self.accessing_clusters[o2])
        del self.accessing_clusters[o2]
        
        # Update the object cluster sizes
        for op in ["read", "write", "free"]:
            self.object_cluster_sizes[op][o1] += self.object_cluster_sizes[op][o2]
            del self.object_cluster_sizes[op][o2]

        # Recompute all object clusters that have o1 or o2 in them...
        # Should be able to replace with accessing_clusters to speed up
        for c in self.reachable_clusters_cache:
            for op in ["read", "write", "free"]:            
                if o1 in self.reachable_object_clusters_cache[op][c] or o2 in self.reachable_object_clusters_cache[op][c]:
                    self.reachable_object_clusters_cache[op][c] = self.reachable_obj_clusters(c, op)
        
    # Merge two clusters. Logically put c2 into c1.
    # 1) Remove c2 from cluster list, add those functions into c1
    # 2) Update function_assignment
    # 3) Recompute sizes and update caches
    # This doesn't have to be fast, as actual commited merges are rather rare.
    # As a result, currently it sloppily rebuilds caches from scratch after changes.
    def merge_clusters(self, c1, c2):

        #print("Merging a cluster with " + str(len(self.clusters[c1])) + " functions and a cluster with " + str(len(self.clusters[c2])))

        # Transfer over functions between clusters
        for f in self.clusters[c2]:
            self.function_assignment[f] = c1
            self.clusters[c1].append(f)

        # Update sizes and operation counts as a result of the merge
        self.cluster_sizes[c1] += self.cluster_sizes[c2]
        self.cluster_sizes[c2] = 0
        self.cluster_read_ops[c1] += self.cluster_free_ops[c2]
        self.cluster_write_ops[c1] += self.cluster_write_ops[c2]
        self.cluster_free_ops[c1] += self.cluster_free_ops[c2]                
        self.cluster_read_ops[c2] = 0
        self.cluster_write_ops[c2] = 0
        self.cluster_free_ops[c2] = 0
        self.cluster_call_ops[c1] += self.cluster_call_ops[c2]
        self.cluster_call_ops[c2] = 0

        # Clear out cluster c2
        self.clusters[c2] = []
        
        # Update caches
        for op in ["read", "write", "free"]:
            self.reachable_objects_cache[op][c2] = set()
            self.reachable_objects_cache[op][c1] = self.reachable_objs(c1,op)
            self.reachable_object_clusters_cache[op][c2] = set()
            self.reachable_object_clusters_cache[op][c1] = self.reachable_obj_clusters(c1,op)

        self.reachable_clusters_cache[c2] = set()
        self.reachable_clusters_cache[c1] = self.reachable_clusters(c1)

        # Update the accessing clusters from each object cluster
        # Replace c2 with c1 in reachable clusters
        for obj_cluster in self.accessing_clusters:
            if c2 in self.accessing_clusters[obj_cluster]:
                self.accessing_clusters[obj_cluster].remove(c2)
                self.accessing_clusters[obj_cluster].add(c1)

        # Now rebuild other parts of the caches that are affected by this merge.
        # 1) C2 should have no reachable, already set above.
        # 2) C1 should be recomputed now that C2 is in it, as done above.
        # 3) Reachable clusters changed because new edges, recalculate those now.
        for c in self.reachable_clusters_cache:            
            # Skip the ones we just merged
            if c == c1 or c == c2:
                continue
            # Add new reachability from the merge
            if c2 in self.reachable_clusters_cache[c]:
                self.reachable_clusters_cache[c] = self.reachable_clusters(c)
        
        # Lastly, we need to update the external_calls_saved to each reachable cluster.

        # Update the counts on each edge outgoing from C1
        self.external_calls_saved[c1] = {}
        for new_cluster in self.reachable_clusters_cache[c1]:
            self.external_calls_saved[c1][new_cluster] = self.count_external_calls_saved(c1, new_cluster)

        # And also edges pointing back in. Reachability not a mirror so it's not just opposite of above
        for search_cluster in self.clusters:
            if search_cluster == c1 or search_cluster == c2:
                continue
            # If we find c1, update it
            if c1 in self.reachable_clusters_cache[search_cluster]:
                self.external_calls_saved[search_cluster][c1] = self.count_external_calls_saved(search_cluster, c1)

    # Count the number of calls that are currently external between c1 and c2
    def count_external_calls_saved(self, c1, c2):

        total_external_calls_saved = 0
        
        # That includes c1 -> c2
        for f1 in self.clusters[c1]:
            if f1 in self.called_funcs:
                for f2 in self.called_funcs[f1]:
                    f2_cluster = self.function_assignment[f2]
                    if f2_cluster == c2:
                        total_external_calls_saved += self.called_funcs[f1][f2]

        # and c2 -> c1
        for f1 in self.clusters[c2]:
            if f1 in self.called_funcs:
                for f2 in self.called_funcs[f1]:
                    f2_cluster = self.function_assignment[f2]
                    if f2_cluster == c1:
                        total_external_calls_saved += self.called_funcs[f1][f2]

        return total_external_calls_saved


    # Calculate the PS change that would occur from merging o1 and o2 together
    # New clusters can get access to the other objects in the object / operation types
    # after a merge takes place.
    # One pass looked good, TODO another debug pass.
    def calc_PS_delta_object_merge(self, o1, o2):

        data_PS = 0

        '''
        print("Calculating delta PS from merging " + o1 + " and " + o2)
        print("cluster1:")
        for o in self.obj_cluster_to_objs[o1]:
            print("\t" + o)
        print("cluster2:")
        for o in self.obj_cluster_to_objs[o2]:
            print("\t" + o)
        '''
        
        # For efficiency, quickly grab just the clusters that matter
        clusters_involved = self.accessing_clusters[o1]
        clusters_involved = clusters_involved.union(self.accessing_clusters[o2])

        # Then loop over them and compute PS changes
        for op in ["read", "write", "free"]:
            for c in clusters_involved:
                o1_in_c = o1 in self.reachable_object_clusters_cache[op][c]
                o2_in_c = o2 in self.reachable_object_clusters_cache[op][c]

                # If both clusters either have or don't have, then no change in pass
                if (o1_in_c and o2_in_c) or (not o1_in_c and not o2_in_c):
                    continue

                # Now pick which cluster is getting access
                if o2_in_c:
                    new_obj = o1
                else:
                    new_obj = o2

                # Count the number of ops
                num_ops = 0
                if op == "read":
                    num_ops = self.cluster_read_ops[c]
                elif op == "write":
                    num_ops = self.cluster_write_ops[c]
                elif op == "free":
                    num_ops = self.cluster_free_ops[c]

                PS_increase = num_ops * self.object_cluster_sizes[op][new_obj]

                #if PS_increase > 0:
                #    print("\tPS inreasing by " + str(PS_increase) + "for cluster" + c + " from op " + op + " to obj cluster " + new_obj)
                
                data_PS += PS_increase
                    
        return data_PS
        
    
    # Calculate the PS change that would occur from merging c1 and c2 together
    def calc_PS_delta_code_merge(self, c1, c2):
        
        # Calculate call/return PS increase: each call instr can now target all instructions in the other cluster
        call_PS = self.cluster_call_ops[c1] * self.cluster_sizes[c2] + self.cluster_call_ops[c2] * self.cluster_sizes[c1]
        
        # Calculate data PS. This is a little more complicated.
        # First determine which object clusters are accessible to each side (represented as sets)
        objs1_read = self.reachable_object_clusters_cache["read"][c1]
        objs1_write = self.reachable_object_clusters_cache["write"][c1]
        objs1_free = self.reachable_object_clusters_cache["free"][c1]

        objs2_read = self.reachable_object_clusters_cache["read"][c2]
        objs2_write = self.reachable_object_clusters_cache["write"][c2]
        objs2_free = self.reachable_object_clusters_cache["free"][c2]

        # Next, union these together, then subtract out to determine what will be new
        union_read = objs1_read.union(objs2_read)
        union_write = objs1_write.union(objs2_write)
        union_free = objs1_free.union(objs2_free)

        new_for_cluster1_read = union_read.difference(objs1_read)
        new_for_cluster1_write = union_write.difference(objs1_write)
        new_for_cluster1_free = union_free.difference(objs1_free)

        new_for_cluster2_read = union_read.difference(objs2_read)
        new_for_cluster2_write = union_write.difference(objs2_write)
        new_for_cluster2_free = union_free.difference(objs2_free)

        # Recheck objects cache. TODO: fix up for the op type checks
        '''
        if random.random() < 0.01:
            count1 = len(objs1)
            recalc_cache = self.reachable_objs(c1)
            #print("Object cache recheck: " + str(count1) + " " + str(len(recalc_cache)))
            if count1 != len(recalc_cache):
                print("Object recalc error :/")                        
        '''

        # Lastly, calculate PS updates by introduced num bytes for each op type to each side
        new_for_cluster1_read_size = 0
        new_for_cluster1_write_size = 0
        new_for_cluster1_free_size = 0
        for o in new_for_cluster1_read:
            new_for_cluster1_read_size += self.object_cluster_sizes["read"][o]
        for o in new_for_cluster1_write:
            new_for_cluster1_write_size += self.object_cluster_sizes["write"][o]
        for o in new_for_cluster1_free:
            new_for_cluster1_free_size += self.object_cluster_sizes["free"][o]

        new_for_cluster2_read_size = 0
        new_for_cluster2_write_size = 0
        new_for_cluster2_free_size = 0
        for o in new_for_cluster2_read:
            new_for_cluster2_read_size += self.object_cluster_sizes["read"][o]
        for o in new_for_cluster2_write:
            new_for_cluster2_write_size += self.object_cluster_sizes["write"][o]
        for o in new_for_cluster2_free:
            new_for_cluster2_free_size += self.object_cluster_sizes["free"][o]

        # Now multiply each new amount of added bytes times the op count of the new cluster
        data_PS = self.cluster_read_ops[c1] * new_for_cluster1_read_size + \
                  self.cluster_write_ops[c1] * new_for_cluster1_write_size + \
                  self.cluster_free_ops[c1] * new_for_cluster1_free_size + \
                  self.cluster_read_ops[c2] * new_for_cluster2_read_size + \
                  self.cluster_write_ops[c2] * new_for_cluster2_write_size + \
                  self.cluster_free_ops[c2] * new_for_cluster2_free_size
        
        return data_PS + call_PS


    # Calculate the cost and benefit of a code merge for the CLUSTER_SIZE algorithm   
    def consider_code_merge_size(self, c1, c2, cluster_size):

        # First question: is this a valid merge? Can only merge if don't violate size constraint
        if self.SIZE_METRIC == "func":
            if (len(self.clusters[c1]) + len(self.clusters[c2])) > cluster_size:
                return (None, None, None)
        elif self.SIZE_METRIC == "instr":
            if self.cluster_sizes[c1] + self.cluster_sizes[c2] > cluster_size:
                return (None, None, None)

        # This merge is a valid candidate merge. Calculate benefit.
        benefit = self.external_calls_saved[c1][c2]

        if benefit <= 0:
            return (None, None, 0)
            
        cost = self.calc_PS_delta_code_merge(c1, c2)

        merge_score = float(benefit) / cost

        return (merge_score, cost, benefit)

    def consider_code_merge_ratio(self, c1, c2, cutoff_ratio):
        
        calls_saved = self.external_calls_saved[c1][c2]
        benefit = float(calls_saved) * 1000000 / self.total_calls
        if benefit <= 0:
            return (None, None, 0)
        
        cost = self.calc_PS_delta_code_merge(c1, c2)
        merge_score = float(benefit) / cost
        # Skip this merge if didn't meet cutoff
        if merge_score < cutoff_ratio:
            merge_score = None
            
        return (merge_score, cost, benefit)

    def consider_code_merge_rules(self, c1, c2):

        benefit = self.WS.CalcSaved_Merge(c1,c2)
        if benefit <= 0:
            return (None, None, 0)
        
        cost = self.calc_PS_delta_code_merge(c1, c2)
        merge_score = float(benefit) / cost
        return (merge_score, cost, benefit)

    def consider_object_merge_rules(self, o1, o2):

        benefit = self.WS.CalcSaved_Merge(o1,o2)
        if benefit <= 0:
            return (None, None, 0)
        
        cost = self.calc_PS_delta_object_merge(o1, o2)
        #print("Cost of merging " + o1 + " and " + o2 + ":" + str(cost) + "benefit=" + str(benefit))
        merge_score = float('inf') if cost == 0 else float(benefit) / cost
        return (merge_score, cost, benefit)

    
    def cluster_functions(self, cmap, strategy, strategy_param, extra_name="", working_sets = None, cache_target = None, merge_constraint = None, WS=None):
        
        # Banner for this clustering run. Display the chosen config options.
        print("Running code clustering algorithm. Parameters:")
        
        if strategy == ClusterStrategy.CLUSTER_SIZE:
            print("Clustering strategy: cluster_size")
            cluster_size = strategy_param
            condition_name = "C" + str(cluster_size)
            print("Cluster_size=" + str(cluster_size))
        elif strategy == ClusterStrategy.CLUSTER_RATIO:
            print("Clustering strategy: cluster_ratio")
            cutoff_ratio = strategy_param
            cutoff_ratio_str = '{0:.10f}'.format(strategy_param)
            condition_name = "R" + cutoff_ratio_str
            print("Ratio_minimum=" + cutoff_ratio_str)
        elif strategy == ClusterStrategy.CLUSTER_RULES:
            max_rules = strategy_param
            self.cache_size = max_rules
            condition_name = "Rules" + str(max_rules)
            print("Clustering strategy: clustering rules to cache size " + str(max_rules))
            if working_sets == None:
                raise Exception("Can't run rule clustering with no working sets.")
            self.current_working_sets = []
            for ws in working_sets:
                self.current_working_sets.append(ws.copy())
            if WS != None:
                self.WS = WS
                self.WS.Reset(self.cache_size)
        else:
            raise Exception("Unknown strategy.")

        if merge_constraint == cmap.func_to_file:
            condition_name += "fileConstr"
        elif merge_constraint == cmap.func_to_dir:
            condition_name += "dirConstr"
        elif merge_constraint == None:
            pass
        else:
            raise Exception("Unknown merge constraint.")

        # Resets data structures and builds called_funcs, accessed_objs, and object sizes
        self.prepare_clustering(cmap)

        # Construct set of clusters available for merging: begin at all clusters
        still_can_merge = set()
        for c in self.clusters:
            still_can_merge.add(c)        

        print("Len of still_can_merge: " + str(len(still_can_merge)))
        # Inefficient implementation: consider all merges, keep track of best merge.
        # Then make one best merge, recalculate, and repeat.
        # Each possible merge must produce: cost, benefit, and merge_score
        merge_step = 0
        while True:
            merge_step += 1
            print("Clustering step " + str(merge_step) + ". Available domains for merging: " + str(len(still_can_merge)))

            # Keep track of best merge we've found this step.
            # At the end, we take the best.
            best_merge = None
            merge_type = None
            merge_score = None
            best_benefit = -1            
            best_cost = -1            
            best_merge_score = -1
            benefit = -1

            # Loop over all possible clusters to look at pairs of objects we might want to merge
            # Note: we don't actually have to get this list from still_can_merge... that has some assumptions
            obj_merges_considered = 0
            for c in still_can_merge:
                
                # Exit early if we get a free move
                if merge_score == float('inf'):
                    break

                ###############################################
                ######### Consider merging objects ############
                ###############################################
                for op in ["read", "write"]:

                    # Currently, object merges only done for the rule clustering algo.
                    # To add to ratio / cluster_size, need a heuristic for perf improvement
                    if strategy != ClusterStrategy.CLUSTER_RULES:
                        continue
                    
                    # Grab all the combinations of pairs of objects that we could merge
                    reachable_obj_clusters = self.reachable_object_clusters_cache[op][c]

                    # Prune out objects not in working sets (these can't save us anything)
                    # Also prune out non-globals, currently tagging tools do not support.
                    for o in list(reachable_obj_clusters):
                        if not WS.PresentInWorkingSets(o):
                            reachable_obj_clusters.remove(o)
                        elif not o[0:8] == "[global_":
                            reachable_obj_clusters.remove(o)

                    # Then, construct all pairs of pruned list and check stats
                    obj_pairs = list(itertools.combinations(reachable_obj_clusters, r=2))
                    for (o1,o2) in obj_pairs:
                        # Tagging tools currently only support merging two globals together
                        #if o1[0:8] == "[global_" and o2[0:8] == "[global_":
                            
                        (merge_score, cost, benefit) = self.consider_object_merge_rules(o1, o2)
                            
                        obj_merges_considered += 1

                        # If this merge is better than anything we have yet, update best
                        if merge_score != None and \
                           (best_merge == None or merge_score > best_merge_score) and \
                           benefit > 0:
                            merge_type = MergeType.MERGE_OBJ
                            best_merge_score = merge_score
                            best_benefit = benefit
                            best_cost = cost
                            best_merge = (o1, o2)
                            if merge_score == float('inf'):
                                #print("\tFound a free move, early exit.")
                                break            

            ###############################################
            ######### Consider merging subjects ###########
            ###############################################
                                
            # Loop over all possible cluster to cluster merges
            subj_merges_considered = 0            
            for c1 in still_can_merge:

                # Exit early if we get a free move
                if merge_score == float('inf'):
                    break
                
                for c2 in self.reachable_clusters_cache[c1]:

                    if not c2 in still_can_merge:
                        continue

                    if merge_constraint != None:
                        constraint1 = merge_constraint[self.clusters[c1][0]]
                        constraint2 = merge_constraint[self.clusters[c2][0]]
                        if constraint1 != constraint2:
                            continue

                    # For FreeRTOS case, *must* keep OS code and application code separate
                    c1_is_os = self.clusters[c1][0] in cmap.os_functions
                    c2_is_os = self.clusters[c2][0] in cmap.os_functions

                    if c1_is_os != c2_is_os:
                        continue

                    subj_merges_considered += 1
                    
                    # When using CLUSTER_SIZE strategy, discard any moves that would violate size limit
                    # merge_score is computed as a function of calls between clusters
                    if strategy == ClusterStrategy.CLUSTER_SIZE:
                        
                        (merge_score, cost, benefit) = self.consider_code_merge_size(c1, c2, cluster_size)
                        if merge_score == None:
                            continue

                    elif strategy == ClusterStrategy.CLUSTER_RATIO:

                        (merge_score, cost, benefit) = self.consider_code_merge_ratio(c1, c2, cutoff_ratio)
                        if merge_score == None:
                            continue

                    # Onto the first draft of the rule clustering algo!
                    elif strategy == ClusterStrategy.CLUSTER_RULES:

                        (merge_score, cost, benefit) = self.consider_code_merge_rules(c1, c2)

                    # If this merge is better than anything we have yet, update best
                    if merge_score != None and \
                       (best_merge == None or merge_score > best_merge_score) and \
                       benefit > 0:
                        merge_type = MergeType.MERGE_SUBJ
                        best_merge_score = merge_score
                        best_benefit = benefit
                        best_cost = cost
                        best_merge = (c1, c2)


            #######################################################
            ######### Pick the best move and perform it ###########
            #######################################################
                
            if best_merge == None:
                print("\tNo more valid merges! Done with greedy code clustering.")
                break

            if best_benefit <= 0:
                print("WARNING: best benefit is " + str(best_benefit))
                break

            if merge_type == MergeType.MERGE_SUBJ:
                
                print("\tPicked a subject merge that cycle. Considered " + str(subj_merges_considered) + " such options.")
                # Take our best candidate merge and perform the merging.
                # Merge c2 into c1.
                (c1,c2) = best_merge
                # Print the merge?
                print("\tMerging clusters " + c1 + " and " + c2)
                #print("\t(score = " + str(best_merge_score) +")")
                #print("\tSavings: " + str(best_benefit))            
                
                rules_saved = self.calc_working_set_savings_from_merge(self.current_working_sets, c1, c2)
                print("\tBenefit: " + str(best_benefit) + ",cost=" + str(best_cost) + " saving " + str(rules_saved) + " rules for a score of " + str(best_merge_score))
                #print(c1 + "=")
                #for f in sorted(self.clusters[c1]):
                #    print("\t" + f)
                #    print(c2 + "=")
                #    for f in sorted(self.clusters[c2]):
                #        print("\t" + f)

                #print("This merge has expected calls saved: " + str(best_benefit) + " with total score = " + str(best_merge_score))
                '''
                if working_sets != None:
                    current_over = 0
                    for ws in self.current_working_sets:
                        if len(ws) > self.cache_size:
                            current_over += len(ws) - self.cache_size
                    print("Total over, before: " + str(current_over))
                    print("Savings guess new algo: " + str(self.WS.CalcSaved_Merge(c1,c2)))
                    print("Savings guess current algo: " + str(self.calc_working_set_savings_from_merge(self.current_working_sets, c1, c2)))
                    self.working_set_replace(self.current_working_sets, c1, c2)
                    over_after = 0
                    for ws in self.current_working_sets:
                        if len(ws) > self.cache_size:
                            over_after += len(ws) - self.cache_size
                    saved = current_over - over_after
                    print("Total after: " + str(over_after) + ", saved=" + str(saved))
                    for ws in list(self.current_working_sets):
                        if len(ws) <= self.cache_size:
                            print("Finished a working set! Deleting. Num working sets = " + str(len(self.current_working_sets)))
                            self.current_working_sets.remove(ws)
                '''
                
                self.merge_clusters(c1,c2)
                if WS != None:
                    self.WS.PerformMerge(c1,c2)

                self.finished_clusters.add(c2)

                # C2 is gone now, remove from list
                still_can_merge.remove(c2)

                # If C1 is full, or close enough that even the smallest merge would go over,
                # then remove that too.
                if strategy == ClusterStrategy.CLUSTER_SIZE:
                    if self.SIZE_METRIC == "func":
                        if len(self.clusters[c1]) >= cluster_size:
                            print("Cluster " + c1 + " is full.")
                            still_can_merge.remove(c1)
                            self.finished_clusters.add(c1)
                    if self.SIZE_METRIC == "instr":
                        if (self.cluster_sizes[c1] + self.smallest_cluster_size) >= cluster_size:
                            print("Cluster " + c1 + " is full.")
                            still_can_merge.remove(c1)
                            self.finished_clusters.add(c1)

            elif merge_type == MergeType.MERGE_OBJ:
                (o1,o2) = best_merge
                print("\tPicked an object merge that cycle. Considered " + str(obj_merges_considered) + " such options.")
                print("\tMerging " + o1 + " with " + o2)
                rules_saved = self.calc_working_set_savings_from_merge(self.current_working_sets, o1, o2)
                print("\tBenefit: " + str(best_benefit) + ",cost=" + str(best_cost) + " saving " + str(rules_saved) + " rules for a score of " + str(best_merge_score))
                self.merge_object_clusters(o1,o2)
                if WS != None:
                    self.WS.PerformMerge(o1,o2)
            else:
                raise Exception("Merge_type error.")
                
        # Add in the dead functions now, one per cluster. We skipped these earlier to not slow
        # down the clustering. However, we want final map to be complete.
        # Make list of dead functions, we skip these in clustering and add them back at the end
        dead_functions = set()
        for f in self.cmap.functions:
            if not f in self.cmap.live_functions:
                dead_functions.add(f)
        print("Number of functions: " + str(len(self.cmap.functions)) + ", live=" + str(len(self.cmap.live_functions)) + ", dead=" + str(len(dead_functions)))        
        dead_clusters = set()
        for f in dead_functions:
            cluster_name = "[" + f + "_dead]"
            dead_clusters.add(cluster_name)
            self.clusters[cluster_name] = [f]
            self.function_assignment[f] = cluster_name
            self.cluster_sizes[cluster_name] = int(self.cmap.instr_count_map[f]["size"])
            still_can_merge.add(cluster_name)
            self.cluster_read_ops[cluster_name] = self.cmap.instr_count_map[f]["read"]
            self.cluster_write_ops[cluster_name] = self.cmap.instr_count_map[f]["write"]
            self.cluster_free_ops[cluster_name] = self.cmap.instr_count_map[f]["free"]            
            self.cluster_call_ops[cluster_name] = self.cmap.instr_count_map[f]["call"] + self.cmap.instr_count_map[f]["return"]
            for op in ["read", "write", "free"]:
                self.reachable_objects_cache[op][cluster_name] = self.reachable_objs(cluster_name, op)
                self.reachable_object_clusters_cache[op][cluster_name] = self.reachable_obj_clusters(cluster_name, op)
            self.reachable_clusters_cache[cluster_name] = self.reachable_clusters(cluster_name)
            
        # Write out these clusters to an output file for future reference
        self.write_clusters(condition_name, extra_name)

        # Sanity check: functions in clusters are right number (i.e., we accounted for all functions)
        total_funcs = 0
        for c in self.clusters:
            for f in self.clusters[c]:
                total_funcs += 1
        if not total_funcs == len(self.cmap.functions):
            raise Exception("Mismatch. Found " + str(total_funcs) + " instead of " + str(len(self.cmap.functions)))

        # Done! Make and return our domains
        
        # Make subj domains
        print("Done clustering.")        
        func_to_cluster = {}
        for f in self.cmap.functions:
            cluster = self.function_assignment[f]
            func_to_cluster[f] = cluster

        # Some debug output
        live_clusters = set()
        for f in cmap.live_functions:
            c = func_to_cluster[f]
            live_clusters.add(c)
        print("Number of live clusters: " + str(len(live_clusters)))            

        # Make object domains
        obj_to_cluster = {}
        for o in self.obj_assignment:
            cluster = self.obj_assignment[o]
            obj_to_cluster[o] = cluster

        return (func_to_cluster, obj_to_cluster)

    
    def write_clusters(self, condition_name, extra_name):

        # Make sure output dir exists
        if not os.path.exists("cluster_output"):
            os.mkdir("cluster_output")
        
        clusterfile_name = "cluster_output/" + self.cmap.prog_binary_name + "_" + condition_name
        if extra_name != "":
            clusterfile_name += "_" + extra_name        
        clusterfile = open(clusterfile_name, "w")

        clusterfile.write("Final clusters:\n")
        index = 0
        sizes = []
        max_size = 0

        full_clusters = []
        empty_clusters = []

        for c in self.clusters:
            if len(self.clusters[c]) > 1:
                full_clusters.append(c)
            else:
                empty_clusters.append(c)
            
        for c in full_clusters + empty_clusters:
            objs = self.reachable_objects_cache["read"][c].union(self.reachable_objects_cache["write"][c])
            obj_clusters = self.reachable_object_clusters_cache["read"][c].union(self.reachable_object_clusters_cache["write"][c])            
            
            if len(self.clusters[c]) >= 2 or len(objs) > 0:
                if len(self.clusters[c]) > 1:
                    sizes.append(self.cluster_sizes[c])
                if self.cluster_sizes[c] > max_size:
                    max_size = self.cluster_sizes[c]
                index += 1            
                clusterfile.write("Compartment " + str(index) + "\n")
                clusterfile.write("\tContains these functions: (count=" + str(len(self.clusters[c])) + ",size=" + str(self.cluster_sizes[c]) +" bytes)\n")
                for f in sorted(self.clusters[c]):
                    clusterfile.write("\t\t" + f + " (" + str(int(self.cmap.instr_count_map[f]["size"])) +" bytes)")
                    clusterfile.write("\t(src=" + self.cmap.func_to_dir[f] + "/" + self.cmap.func_to_file[f]+")")
                    if f in self.cmap.os_functions:
                        clusterfile.write(" [OS]\n")
                    else:
                        clusterfile.write(" [APP]\n")
                        
                clusterfile.write("\tHas privilege to access these objects: (" + str(len(objs)) + ")\n")

                # Write out the object clusters
                written_objs = set()
                # objs is a set of obj clusters. Might be single elements or actual sets
                for oc in sorted(obj_clusters):
                    objs_in_cluster = self.obj_cluster_to_objs[oc]
                    if len(objs_in_cluster) <= 1:
                        for o in objs_in_cluster:
                            written_objs.add(o)
                            clusterfile.write("\t\t" + o + "\n")
                    else:
                        clusterfile.write("\t\tCluster:\n")
                        for o in objs_in_cluster:
                            written_objs.add(o)
                            if o in objs:
                                clusterfile.write("\t\t\t" + o + " [X]\n")
                            else:
                                clusterfile.write("\t\t\t" + o + " [ ]\n")
                                
                # Then write out the singleton objects
                for o in objs:
                    if o not in written_objs:
                        clusterfile.write("\t\t" + o + "\n")
                clusterfile.write("\n")

        clusterfile.write("Object clusters: \n")
        
        index = 0
        for obj_cluster in self.obj_cluster_to_objs:
            num_objs = len(self.obj_cluster_to_objs[obj_cluster])
            if num_objs > 1:
                index += 1
                size = self.object_cluster_sizes["read"][obj_cluster]
                clusterfile.write("\tObject cluster " + str(index) + ", size=" + str(size) + "\n")
                for o in self.obj_cluster_to_objs[obj_cluster]:
                    clusterfile.write("\t\t" + o + "\n")
                    
        if len(sizes) > 0:
            print("Average size: " + str(round(sum(sizes) / len(sizes), 3)))
            print("Maximum size: " + str(max_size))
            sizes = sorted(sizes, reverse=True)
            print("Top sizes: " + str(sizes[0:10]))


    def print_subj_domains(self, domain_filename):
        # Convert the string names (e.g., "foo.c", "bar.c") into numbers (e.g., "1", "2")
        domain_ids = {}
        current_id = 1
        for f in self.function_assignment:
            label = self.function_assignment[f]
            if not label in domain_ids:
                domain_ids[label] = current_id
                current_id += 1

        fh = open(domain_filename, "w")

        for f in sorted(list(self.function_assignment)):
            domain_label = self.function_assignment[f]
            domain_id = domain_ids[domain_label]
            fh.write("S " + f + " " + str(domain_id) + "\n")

    def print_obj_domains(self, domain_filename, obj_clusters):
        domain_ids = {}
        current_id = 1
        for o in obj_clusters:
            label = obj_clusters[o]
            if not label in domain_ids:
                domain_ids[label] = current_id
                current_id += 1

        fh = open(domain_filename, "a")

        for o in sorted(list(obj_clusters)):
            domain_label = obj_clusters[o]
            domain_id = domain_ids[domain_label]
            fh.write("O" + f + " " + str(domain_id) + "\n")        
            
    def working_set_replace(self, working_sets, new_name, old_name, debug=False):
        #print("Replacing " + old_name + " with " + new_name)
        number_replaced = 0
        rule_delta = 0
        ws_id = 0
        for ws in working_sets:

            ws_id += 1
            current_size = len(ws)

            if debug:
                ws_backup = set(ws)
                
            # Figure out which rules are going to be replaced
            replacements = set()
            for rule in ws:
                if old_name in rule:
                    replacements.add(rule)

            # Perform the replacements
            for rule in replacements:
                ws.remove(rule)
                new_rule = rule.replace(old_name, new_name)
                ws.add(new_rule)
                number_replaced += 1
                
            updated_size = len(ws)

            if debug:
                rules_removed = ws_backup.difference(set(ws))
                for r in rules_removed:
                    print("Removed this rule " + r + " in WS " + str(ws_id))
            #if updated_size != current_size:
            #    print("This replacement caused size of working set " + str(current_size) + "->" + str(updated_size))
            rule_delta += (current_size - updated_size)

        return rule_delta

    def calc_working_set_savings_from_merge(self, working_sets, c1, c2, debug=False):
        # First make a copy of the current working sets
        temp_working_sets = []
        for ws in working_sets:
            temp_working_sets.append(ws.copy())

        # Then calculate delta
        delta = self.working_set_replace(temp_working_sets, c1, c2, debug)
        return delta            

# Wrapper around making a new clustering object and using it once as a possible use case.
def cluster_functions(cmap, strategy, strategy_param, extra_name="", working_sets = None, cache_target = None, merge_constraint = None, WS=None):
    
    clusterer = DomainCreator(cmap)

    subj_clusters, obj_clusters = clusterer.cluster_functions(cmap, strategy, strategy_param, extra_name=extra_name,
                                                working_sets = working_sets, cache_target = cache_target,
                                                merge_constraint = merge_constraint, WS=WS)

    return (subj_clusters, obj_clusters)

# Load in a working sets file.
# The format for this file is a token BEGIN and then all the rules in that set
# Right now we just take the last few sets, too slow to run on all
def load_working_sets(filename):
    print("Loading working sets from " + filename)
    f = open(filename, "r")
    current_set = None
    working_sets = []
    working_set_lengths = []
    read_sets = 0
    for l in f.readlines():
        l = l.strip()
        if l == "BEGIN":
            if current_set != None:
                working_set_lengths.append(len(current_set))
                working_sets.append(current_set)            
            current_set = set()
            read_sets += 1
            continue
        current_set.add(l)

    # Add the last set too
    if current_set != None and len(current_set) > 0:
        working_sets.append(current_set)
        
    num_sets = len(working_sets)
    print("We read " + str(read_sets) + " working sets, taking " + str(num_sets) + " as unique WSs.")

    '''
    for ws in working_sets:
        print("A working set: " + str(len(ws)))
        for rule in sorted(ws):
            print("\t" + rule)
    '''
    
    return working_sets



if __name__ == '__main__':

    if len(sys.argv) == 2:

        # Check for working sets file
        working_sets_filename = sys.argv[1] + ".working_sets"
        if os.path.exists(working_sets_filename):
            working_sets = load_working_sets(working_sets_filename)
            WS = WorkingSets(working_sets_filename)
        else:
            print("Could not find " + working_sets_filename)
            print("Running with no working sets. Can't use rule clustering.")
            working_sets = None
            WS=None

        # Load in CAPMAP            
        cmap = CAPMAP(sys.argv[1])

        '''
        print("Creating cluster size domains...")
        for size in [4096]:
                condition_name = "C" + str(size)                
                subj_clusters = cluster_functions(cmap, ClusterStrategy.CLUSTER_SIZE, size, WS=WS)
        '''

        print("Creating rule-cluster domains...")
        for cache_size in [2000]: #[1024]:
            condition_name = "Rules" + str(cache_size)
            subj_clusters, obj_clusters = cluster_functions(cmap, ClusterStrategy.CLUSTER_RULES, cache_size, working_sets=working_sets, WS=WS)
        
    else:

        print("Run with ./DomainCreator.py <vmlinux>")
