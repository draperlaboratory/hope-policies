#!/usr/bin/python

# This script runs both the syntatic and clustered domains.
# It installs them into the kernels directory.
# It also creates domain_PS_results.txt containing the PS per cut.

from DomainCreator import *
from SyntacticDomains import *
from calculate_PS import *
from WorkingSets import *

# For making table in paper
from webserver_security_eval import *

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
        fh.write("Subj " + f + " " + str(domain_id) + " " + str(domain_label) + "\n")

def print_obj_domains(domains, name):

    # Convert the string names (e.g., "foo.c", "bar.c") into numbers (e.g., "1", "2")
    domain_ids = {}
    current_id = 7 # First 6 objects reserved for special regions
    for f in domains:
        label = domains[f]
        if not label in domain_ids:
            domain_ids[label] = current_id
            current_id += 1
    
    fh = open(name, "a")

    for f in sorted(list(domains)):
        domain_label = domains[f]
        domain_id = domain_ids[domain_label]
        fh.write("Obj " + f + " " + str(domain_id) + " " + str(domain_label) + "\n")
        #fh.write("Obj " + f + " " + str(7) + " " + "UNIGLOBAL" + "\n")        

# Install these domain files into the policy kernel directory
def install_domains(cmap, subj_domains, obj_domains, name):
    isp_prefix = os.environ['ISP_PREFIX']
    policies_dir = os.path.join(isp_prefix, "policies")
    for f in os.listdir(policies_dir):
        if "compartmentalization" in f:
            policy_dir = os.path.join(policies_dir, f)
            domains_dir = os.path.join(policy_dir, "domains")
            if not os.path.exists(domains_dir):
                os.mkdir(domains_dir)
                print("Note: Created domains dir in compartmentalization policy directory.")
            
            #if cmap.USE_WEIGHTS:
            #    domain_filename = os.path.join(domains_dir, name + ".weighted.domains")
            #else:
            #    domain_filename = os.path.join(domains_dir, name + ".domains")
            domain_filename = os.path.join(domains_dir, name + ".domains")
            print_subj_domains(subj_domains, domain_filename)
            print_obj_domains(obj_domains, domain_filename)


# There are two main modes that InstallDomains can run in:
# 1) a batch mode where it creates many domains
# 2) a single-target mode where it builds one policy; allows external parallelism
if __name__ == '__main__':

    if len(sys.argv) in [2,5]:

        full_pack=False

        if full_pack:
            print(" *** INFO: This is a full-packing run! ***")
        
        # In all cases, load up CMAP and prepare
        working_sets_filename = sys.argv[1] + ".working_sets"
        if os.path.exists(working_sets_filename):
            working_sets = load_working_sets(working_sets_filename)
            WS = WorkingSets(working_sets_filename, full_pack=full_pack)
        else:
            print("Could not find " + working_sets_filename)
            print("Running with no working sets. Can't use rule clustering.")
            working_sets = None
            WS = None

        #weight = None
        #if len(sys.argv) == 3:
        #    weight = sys.argv[2]
        #    if weight == "weighted":
        #        print("This is a weighted run!")

        prog = sys.argv[1]
        cmap = CAPMAP(prog, weight=True)
        prog_name = os.path.basename(prog)
        
        # What constraints do we want to apply?
        # This installs the OS domains into the cmap
        domains = create_syntactic_domains(cmap, prog)
        binary_name = os.path.basename(prog)
            
        ###### batch mode ######
        if len(sys.argv) == 2:
            
            print("Running in batch mode.")
            size_domains = False
            ratio_domains = False
            rule_domains = False

            constraints = [(None, None, None), ("OSConstr", cmap.func_to_OS, cmap.obj_owner_OS),
                           ("dirConstr", cmap.func_to_dir, cmap.obj_owner_dir), ("fileConstr", cmap.func_to_file, cmap.obj_owner_file)]
            constraints = [(None, None, None)]

            #ps_result_file = open(os.path.join(results_dir, prog_name), "w")
            if cmap.USE_WEIGHTS:
                ps_result_file = open("PSR_results_weighted.txt", "a")
            else:
                ps_result_file = open("PSR_results_unweighted.txt", "a")


            for cut in domains:
                # Take the raw obj_no_cluster and smoosh it down to equivalence classes
                # Preserve the func because we use that for working set generation and want lables intact.
                if cut != "func":
                    obj_clusters = optimize_object_mapping(cmap, domains[cut], cmap.obj_no_cluster)
                else:
                    obj_clusters = cmap.obj_no_cluster
                # Alternatively, just use raw objects:
                #obj_clusters = cmap.obj_no_cluster
                PSR = calc_PSR_cut(cmap, domains[cut], obj_clusters)
                OR = calc_OR_cut(cmap, domains[cut], obj_clusters, domains["func"])
                ps_result_file.write(prog_name + " " + cut + " " + str(PSR) + " " + str(OR) + "\n")
                install_domains(cmap, domains[cut], obj_clusters, binary_name + "." + cut)
            ps_result_file.flush()

            # Create the size-based domains
            if size_domains:
                print("Creating cluster size domains...")
                for size in [256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144]:
                #for size in [8192, 131072]:
                    for (name, subj_constr, obj_constr) in constraints:
                        condition_name = "C" + str(size)                
                        if name != None:
                            condition_name += "_" + name        
                        subj_clusters, obj_clusters, success = cluster_functions(cmap, ClusterStrategy.CLUSTER_SIZE, size, merge_constraint=(subj_constr, obj_constr), WS=None)
                        # Optimize down object clusters to equivalence classes
                        obj_clusters = optimize_object_mapping(cmap, subj_clusters, obj_clusters)
                        PSR = calc_PSR_cut(cmap, subj_clusters, obj_clusters)
                        OR = calc_OR_cut(cmap, subj_clusters, obj_clusters, domains["func"])
                        ps_result_file.write(prog_name + " " + condition_name + " " + str(PSR) + " " + str(OR) + "\n")
                        install_domains(cmap, subj_clusters, obj_clusters, binary_name + "." + condition_name)
                        ps_result_file.flush()


            # Create the ratio-based domains
            if ratio_domains:
                print("Creating ratio domains...")
                for ratio in [0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001]:
                    condition_name = "R" + str(ratio)
                    subj_clusters, obj_clusters, success = cluster_functions(cmap, ClusterStrategy.CLUSTER_RATIO, ratio)
                    PSR = calc_PSR_cut(cmap, subj_clusters, obj_clusters)
                    OR = calc_OR_cut(cmap, subj_clusters, obj_clusters, domains["func"])
                    ps_result_file.write(prog_name + " " + condition_name + " " + str(PSR) + " " + str(OR) + "\n") 
                    install_domains(cmap, subj_clusters, obj_clusters, binary_name + "." + condition_name)
                    ps_result_file.flush()

            # Run the basic rule clustering algorithm
            if rule_domains:
                if working_sets != None:
                    #for cache_size in [1024, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3200, 3400, 3600, 3800]:
                    #for cache_size in [1024] + range(1100, 4100, 100):
                    for cache_size in [1024]:
                        for (name, subj_constr, obj_constr) in constraints:
                            condition_name = "Rules" + str(cache_size)                
                            if name != None:
                                condition_name += "_" + name
                            if WS.full_pack:
                                condition_name += "_fullpack"
                                
                            print("Running " + condition_name)
                            subj_clusters, obj_clusters, success = cluster_functions(cmap, ClusterStrategy.CLUSTER_RULES, cache_size,
                                                                            working_sets = working_sets, merge_constraint=(subj_constr,obj_constr), WS=WS)
                            PSR = calc_PSR_cut(cmap, subj_clusters, obj_clusters)
                            OR = calc_OR_cut(cmap, subj_clusters, obj_clusters, domains["func"])
                            print("OR: " + str(OR))
                            ps_result_file.write(prog_name + " " + condition_name + " " + str(PSR) + " " + str(OR) + "\n")
                            install_domains(cmap, subj_clusters, obj_clusters, binary_name + "." + condition_name)
                            ps_result_file.flush()
        else:
            print("Running in single-target mode")

            strategy = sys.argv[2]
            param = sys.argv[3]
            constr = sys.argv[4]

            # Prepare PS output dir
            results_dir = "PSR_results"
            if not os.path.exists(results_dir):
                os.mkdir(results_dir)            

            # Parse strategy
            if strategy == "size":
                strategy = ClusterStrategy.CLUSTER_SIZE
                condition_name = "C" + param
                WS=None
                param_list = None
            elif strategy == "ratio":
                strategy = ClusterStrategy.CLUSTER_RATIO
                condition_name = "R" + param
                WS=None
                param_list = None
            elif strategy == "rules":
                strategy = ClusterStrategy.CLUSTER_RULES
                condition_name = "Rules" + param
                param_list = [1024] + range(1100, 6100, 100)
            elif strategy == "syntactic":
                print("Doing syntactic")
                for cut in domains:
                    # Apply object smooshing to the syntactic domains
                    # Preserve the func domains for raw tracing
                    if cut != "func":
                        obj_clusters = optimize_object_mapping(cmap, domains[cut], cmap.obj_no_cluster)
                    else:
                        obj_clusters = cmap.obj_no_cluster
                        
                    PSR = calc_PSR_cut(cmap, domains[cut], obj_clusters)
                    OR = calc_OR_cut(cmap, domains[cut], obj_clusters, domains["func"])
                    ps_result_file = open(os.path.join(results_dir, prog_name + "_" + cut), "w")                    
                    ps_result_file.write(prog_name + " " + cut + " " + str(PSR) + " " + str(OR) + " True\n")
                    install_domains(cmap, domains[cut], obj_clusters, binary_name + "." + cut)
                sys.exit()
                
            else:
                raise Exception("Unrecognized strategy " + strategy)

            # Parse strategy parameter
            param = int(param)

            # Parse constraint choice
            if constr == "None":
                merge_constraint=(None, None)
            elif constr == "OS":
                merge_constraint=(cmap.func_to_OS, cmap.obj_owner_OS)
                condition_name += "_OSConstr"
            elif constr == "dir":
                merge_constraint=(cmap.func_to_dir, cmap.obj_owner_dir)
                condition_name += "_dirConstr"
            elif constr == "file":
                merge_constraint=(cmap.func_to_file, cmap.obj_owner_file)
                condition_name += "_fileConstr"
            else:
                raise Exception("Unrecognized constraint " + constr)

            if WS != None and WS.full_pack:
                condition_name += "_fullpack"

            # To force monotonicity, trying to adjust targets one by one as they are reached
            # requires passing in full list...
            if param_list != None:
                print("This is a monotonic run!")

            print("Warning: Not using param list")
            
            param_list = None
            if full_pack:
                print("For full packing case, remove param list")
                param_list = None
            
            # Now that parameters are parsed, run this one clustering
            subj_clusters, obj_clusters, success = cluster_functions(cmap, strategy, param, working_sets = working_sets,
                                                                     merge_constraint=merge_constraint, WS=WS, param_list = param_list)


            print("Webserver security eval:" )
            webserver_security_eval(cmap, subj_clusters)
            
            if strategy == ClusterStrategy.CLUSTER_SIZE:
                print("Applying object smoothing, is a cluster size domain.")
                obj_clusters = optimize_object_mapping(cmap, subj_clusters, obj_clusters)
                
            # Calculate PS results
            PSR = calc_PSR_cut(cmap, subj_clusters, obj_clusters)
            OR = calc_OR_cut(cmap, subj_clusters, obj_clusters, domains["func"])

            # Write PS results out, save domains into domain dir
            ps_result_file = open(os.path.join(results_dir, prog_name + "_" + condition_name), "w")
            ps_result_file.write(prog_name + " " + condition_name + " " + str(PSR) + " " + str(OR) + " " + str(success) + "\n")
            install_domains(cmap, subj_clusters, obj_clusters, binary_name + "." + condition_name)            
                   
    else:
        print("Run with ./InstallDomains.py <vmlinux> <kmap> <working_set_file>")
