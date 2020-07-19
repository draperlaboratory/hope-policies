#!/usr/bin/python

# The DomainCreator contains algorithms for solving the clustering problems related to uSCOPE,
# specifically (1) clustering functions into subject domains and (2) clustering primitive objects
# into object domains.
#
# This is a port of the uSCOPE DomainCreator for the PIPE variant of the compartmentalizations.

from CAPMAP import *
from calculate_PS import *
import random
import copy

# There are three supported clustering strategies for the subject clusterer:
# 1) CLUSTER_SIZE, in which clusters are build targetting a maximum code size per cluster
# 2) CLUSTER_RATIO, in which there is a cutoff benefit/cost ratio.
# 	Clustering proceeds until there are no merges above ratio.
# 3) CLUSTER_RULES is a new PIPE-specific mode.
# 	It reduces the number of rules per working set to a target level
class ClusterStrategy(Enum):
    CLUSTER_SIZE = 1
    CLUSTER_RATIO = 2
    CLUSTER_RULES = 3

class DomainCreator:

    def __init__(self, cmap):

        # The CAPMAP graph object that we are running clustering algorithms on
        self.cmap = cmap
        
        # A map that records which cluster each function currently belongs to
        self.function_assignment = {}

        # A set of current clusters, stored as lists e.g., clusters[c] = [f1, f2 ... fn]
        self.clusters = {}

        # A map of which objects are accessed by each function per op type
        self.accessed_objs = {}
        for op in ["read", "write", "free"]:
            self.accessed_objs[op] = {}

        # A map of which functions are called by each function
        self.called_funcs = {}

        # Clusters that are done merging
        self.finished_clusters = set()
        
        # A running total of each cluster's current size
        self.cluster_sizes = {}
        
        # A cache of reachable objects from each cluster
        self.reachable_objects_cache = {}
        
        # A cache of reachable subjects from each cluster
        self.reachable_clusters_cache = {}

        # A cache of the calls saved if we merged c1 and c2
        self.external_calls_saved = {}        
        
        # A switch to control how we count cluster size. Values are "instr" or "func".
        # "func" mostly deprecated now.
        self.SIZE_METRIC="instr"

        # A set of working sets, updated as merges happen
        self.current_working_sets = []

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
    
    # Merge two clusters. Logically put c2 into c1.
    # 1) Remove c2 from cluster list, add those functions into c1
    # 2) Update function_assignment
    # 3) Recompute sizes and update caches
    def merge_clusters(self, c1, c2):

        #print("Merging a cluster with " + str(len(self.clusters[c1])) + " functions and a cluster with " + str(len(self.clusters[c2])))
        
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

        self.reachable_clusters_cache[c2] = set()
        self.reachable_clusters_cache[c1] = self.reachable_clusters(c1)

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
        self.total_calls = 0        
        self.object_sizes = {}        
        self.called_funcs = {}
        self.accessed_objs = {}
        for op in ["read", "write", "free"]:
            self.accessed_objs[op] = {}
            self.object_sizes[op] = {}
            
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
                size = self.cmap.dg.node[node]["size"]
                self.object_sizes["read"][obj_ip] = size #* weight[0]
                self.object_sizes["write"][obj_ip] = size #* weight[1]
                self.object_sizes["free"][obj_ip] = size #* weight[2]

        #############################
        ###   Initialize Caches   ###
        #############################
        self.reachable_clusters_cache = {}
        self.reachable_objects_cache = {}        
        for op in ["read", "write", "free"]:
            self.reachable_objects_cache[op] = {}
        self.external_calls_saved = {}
        
        # Initialize reachable_clusters_cache by computing from scratch
        for c in self.clusters:
            for op in ["read", "write", "free"]:
                self.reachable_objects_cache[op][c] = self.reachable_objs(c, op)
            self.reachable_clusters_cache[c] = self.reachable_clusters(c)

        # Initialize external_calls_saved by computing from scratch
        for c1 in self.clusters:
            for c2 in self.reachable_clusters_cache[c1]:
                if not c1 in self.external_calls_saved:
                    self.external_calls_saved[c1] = {}
                self.external_calls_saved[c1][c2] = self.count_external_calls_saved(c1, c2)



    # Calculate the PS change that would occur from merging c1 and c2 together
    def calc_PS_delta_code_merge(self, c1, c2):
        
        # Calculate call/return PS increase: each call instr can now target all instructions in the other cluster
        call_PS = self.cluster_call_ops[c1] * self.cluster_sizes[c2] + self.cluster_call_ops[c2] * self.cluster_sizes[c1]
        
        # Calculate data PS. This is a little more complicated.
        # First determine which objects accessible to each side (represented as sets)
        objs1_read = self.reachable_objects_cache["read"][c1]
        objs1_write = self.reachable_objects_cache["write"][c1]
        objs1_free = self.reachable_objects_cache["free"][c1]

        objs2_read = self.reachable_objects_cache["read"][c2]
        objs2_write = self.reachable_objects_cache["write"][c2]
        objs2_free = self.reachable_objects_cache["free"][c2]

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
            new_for_cluster1_read_size += self.object_sizes["read"][o]
        for o in new_for_cluster1_write:
            new_for_cluster1_write_size += self.object_sizes["write"][o]
        for o in new_for_cluster1_free:
            new_for_cluster1_free_size += self.object_sizes["free"][o]

        new_for_cluster2_read_size = 0
        new_for_cluster2_write_size = 0
        new_for_cluster2_free_size = 0
        for o in new_for_cluster2_read:
            new_for_cluster2_read_size += self.object_sizes["read"][o]
        for o in new_for_cluster2_write:
            new_for_cluster2_write_size += self.object_sizes["write"][o]
        for o in new_for_cluster2_free:
            new_for_cluster2_free_size += self.object_sizes["free"][o]

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
                
        cost = self.calc_PS_delta_code_merge(c1, c2)

        # This merge is a valid candidate merge. Calculate benefit.
        benefit = self.external_calls_saved[c1][c2]

        merge_score = float(benefit) / cost

        return (merge_score, cost, benefit)

    def consider_code_merge_ratio(self, c1, c2, cutoff_ratio):
        
        calls_saved = self.external_calls_saved[c1][c2]
        benefit = float(calls_saved) * 1000000 / self.total_calls
        cost = self.calc_PS_delta_code_merge(c1, c2)
        merge_score = float(benefit) / cost
        # Skip this merge if didn't meet cutoff
        if merge_score < cutoff_ratio:
            merge_score = None
            
        return (merge_score, cost, benefit)

    def consider_code_merge_rules(self, c1, c2):
        benefit = self.calc_working_set_savings_from_merge(self.current_working_sets, c1, c2)
        cost = self.calc_PS_delta_code_merge(c1, c2)
        merge_score = float(benefit) / cost
        return (merge_score, cost, benefit)
        
    
    def cluster_functions(self, cmap, strategy, strategy_param, extra_name="", working_sets = None, cache_target = None, merge_constraint = None):
        
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
        else:
            raise Exception("Unknown strategy.")

        if merge_constraint == cmap.func_to_file:
            condition_name += "fileConstr"
        elif merge_constraint == cmap.func_to_dir:
            condition_name += "dirConstr"

        # Resets data structures and builds called_funcs, accessed_objs, and object sizes
        self.prepare_clustering(cmap)

        # Construct set of clusters available for merging: begin at all clusters
        still_can_merge = set()
        for c in self.clusters:
            still_can_merge.add(c)        

        # Inefficient implementation: consider all merges, keep track of best merge.
        # Then make one best merge, recalculate, and repeat.
        # Each possible merge must produce: cost, benefit, and merge_score
        merge_step = 0
        while True:
            merge_step += 1
            print("Code clustering step " + str(merge_step) + ". Available domains for merging: " + str(len(still_can_merge)))

            # Keep track of best merge we've found this step.
            # At the end, we take the best.
            best_merge = None
            best_benefit = -1            
            best_cost = -1            
            best_merge_score = -1
            benefit = -1
            options_considered = 0           

            # Loop over all possible cluster to cluster merges
            for c1 in still_can_merge:
                
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

                    options_considered += 1
                    
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
                        best_merge_score = merge_score
                        best_benefit = benefit
                        best_cost = cost
                        best_merge = (c1, c2)

            if best_merge == None:
                print("No more valid merges! Done with greedy code clustering.")
                break

            if best_benefit <= 0:
                print("WARNING: best benefit is " + str(best_benefit))

            # Take our best candidate merge and perform the merging.
            # Merge c2 into c1.
            (c1,c2) = best_merge

            # Print the merge?
            print("Merging clusters " + c1 + " and " + c2)
            print("(score = " + str(best_merge_score) +")")
            print("Savings: " + str(best_benefit))            

            rules_saved = self.calc_working_set_savings_from_merge(self.current_working_sets, c1, c2)                
            print("Benefit: " + str(best_benefit) + ",cost=" + str(best_cost) + " saving " + str(rules_saved) + " rules for a score of " + str(best_merge_score) + " of options: " + str(options_considered))
            print(c1 + "=")
            for f in sorted(self.clusters[c1]):
                print("\t" + f)
            print(c2 + "=")
            for f in sorted(self.clusters[c2]):
                print("\t" + f)

            #print("This merge has expected calls saved: " + str(best_benefit) + " with total score = " + str(best_merge_score))
            if working_sets != None:
                self.working_set_replace(self.current_working_sets, c1, c2)
                for ws in list(self.current_working_sets):
                    if len(ws) <= self.cache_size:
                        print("Finished a working set! Deleting. Num working sets = " + str(len(self.current_working_sets)))
                        self.current_working_sets.remove(ws)
                        
            self.merge_clusters(c1,c2)

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
            self.reachable_clusters_cache[cluster_name] = self.reachable_clusters(cluster_name)
            

        clusterfile_name = "cluster_output/clusters_" + condition_name            
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
                    clusterfile.write("\t(src=" + cmap.func_to_dir[f] + "/" + cmap.func_to_file[f]+")")
                    if f in self.cmap.os_functions:
                        clusterfile.write(" [OS]\n")
                    else:
                        clusterfile.write(" [APP]\n")
                        
                clusterfile.write("\tHas privilege to access these objects: (" + str(len(objs)) + ")\n")

                # objs is a set of obj clusters. Might be single elements or actual sets
                for o in sorted(objs):
                    clusterfile.write("\t\t" + o + " ")
                    #if o in self.cmap.object_names:
                    #    name = self.cmap.object_names[o]
                    #else:
                    name = o
                    clusterfile.write(name)
                    clusterfile.write("\n")
                clusterfile.write("\n")
                
        print("Average size: " + str(round(sum(sizes) / len(sizes), 3)))
        print("Maximum size: " + str(max_size))
        sizes = sorted(sizes, reverse=True)
        print("Top sizes: " + str(sizes[0:10]))

        # Sanity check: functions in clusters are right number (i.e., we accounted for all functions)
        total_funcs = 0
        for c in self.clusters:
            for f in self.clusters[c]:
                total_funcs += 1
        if not total_funcs == len(self.cmap.functions):
            raise Exception("Mismatch. Found " + str(total_funcs) + " instead of " + str(len(self.cmap.functions)))
        
        # Function-level map
        print("Done clustering.")        
        func_to_cluster = {}
        for f in self.cmap.functions:
            cluster = self.function_assignment[f]
            func_to_cluster[f] = cluster

        live_clusters = set()
        for f in cmap.live_functions:
            c = func_to_cluster[f]
            live_clusters.add(c)
        print("Number of live clusters: " + str(len(live_clusters)))

        return func_to_cluster


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
            fh.write(f + " " + str(domain_id) + "\n")
            
    def working_set_replace(self, working_sets, new_name, old_name):
        #print("Replacing " + old_name + " with " + new_name)
        number_replaced = 0
        rule_delta = 0
        for ws in working_sets:
            current_size = len(ws)

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
            #if updated_size != current_size:
            #    print("This replacement caused size of working set " + str(current_size) + "->" + str(updated_size))
            rule_delta += (current_size - updated_size)

        return rule_delta

    def calc_working_set_savings_from_merge(self, working_sets, c1, c2):
        # First make a copy of the current working sets
        temp_working_sets = []
        for ws in working_sets:
            temp_working_sets.append(ws.copy())

        # Then calculate delta
        delta = self.working_set_replace(temp_working_sets, c1, c2)
        return delta            

# Wrapper around making a new clustering object and using it once as a possible use case.
def cluster_functions(cmap, strategy, strategy_param, extra_name="", working_sets = None, cache_target = None, merge_constraint = None):

    # Make sure output dir exists
    if not os.path.exists("cluster_output"):
        os.mkdir("cluster_output")
    
    clusterer = DomainCreator(cmap)

    subj_clusters = clusterer.cluster_functions(cmap, strategy, strategy_param, extra_name=extra_name,
                                                working_sets = working_sets, cache_target = cache_target,
                                                merge_constraint = merge_constraint)

    return subj_clusters



# One way to reduce the number of working sets we have to crunch at runtime
# is to only take "unique" working sets, say that don't overlap 90% with
# an existing ws.
def add_working_set_if_unique(working_sets, new_ws):

    # One precheck: any WS with "CU_start" we are going to skip
    # This WS will be huge and only runs once
    for rule in new_ws:
        if "[CU_start.S]" in rule:
            return

    if len(new_ws) == 0:
        return

    # Next, we will try to prune out repetitive WSs
    
    # How picky are we about saying a ws is "new"?
    cutoff_ratio = 0.75
    
    is_unique = True

    for ws in working_sets:
        total = len(new_ws)
        overlapping = 0
        for rule in new_ws:
            if rule in ws:
                overlapping += 1
        ratio = float(overlapping) / total
        if float(overlapping) / total >= cutoff_ratio:
            is_unique = False

    if is_unique:
        working_sets.append(new_ws)


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
                add_working_set_if_unique(working_sets, current_set)
                #working_sets.append(current_set)            
            current_set = set()
            read_sets += 1
            continue
        current_set.add(l)

    num_sets = len(working_sets)
    print("We read " + str(read_sets) + " working sets, taking " + str(num_sets) + " as unique WSs.")

    print("Length of WSs: " + str(sorted(working_set_lengths)))
    print(" **** serious pruning and refining of WSs needed! *** ")
    
    '''
    for ws in working_sets:
        print("A working set: " + str(len(ws)))
        for rule in sorted(ws):
            print("\t" + rule)
    '''
    return working_sets

    '''
    if len(working_sets) > 2:
        return working_sets[len(working_sets)-2:len(working_sets)-1]    
    else:
        return working_sets
    '''
if __name__ == '__main__':

    if len(sys.argv) == 2:

        # Check for working sets file
        working_sets_filename = sys.argv[1] + ".working_sets"
        if os.path.exists(working_sets_filename):
            working_sets = load_working_sets(working_sets_filename)
        else:
            print("Could not find " + working_sets_filename)
            print("Running with no working sets. Can't use rule clustering.")
            working_sets = None

        # Load in CAPMAP            
        cmap = CAPMAP(sys.argv[1])
        
        # Run the rule clustering variant
        for cache_size in [1024]:
            for cache_target in [0.76, 0.8, 0.85, 0.9, 0.95, 1.0]:
                working_set_clusters = cluster_functions(cmap, ClusterStrategy.CLUSTER_RULES, cache_size,
                                                         working_sets = working_sets, cache_target=cache_target)

        # Run the basic rule clustering algorithm
        for cache_size in [1024, 1100, 1200, 1300, 1400, 1500, 1600]:
                working_set_clusters = cluster_functions(cmap, ClusterStrategy.CLUSTER_RULES, cache_size,
                                                         working_sets = working_sets)
                
        
    else:

        print("Run with ./DomainCreator.py <vmlinux> <kmap> <working_set_file>")
