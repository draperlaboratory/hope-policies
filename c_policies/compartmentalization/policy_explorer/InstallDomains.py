#!/usr/bin/python

# This script runs both the syntatic and clustered domains.
# It installs them into the kernels directory.
# It also creates domain_PS_results.txt containing the PS per cut.

from DomainCreator import *
from SyntacticDomains import *
from calculate_PS import *
from WorkingSets import *

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
def install_domains(subj_domains, obj_domains, name):
    isp_prefix = os.environ['ISP_PREFIX']
    policies_dir = os.path.join(isp_prefix, "policies")
    for f in os.listdir(policies_dir):
        if "compartmentalization" in f:
            policy_dir = os.path.join(policies_dir, f)
            domains_dir = os.path.join(policy_dir, "domains")
            if not os.path.exists(domains_dir):
                os.mkdir(domains_dir)
                print("Note: Created domains dir in compartmentalization policy directory.")
            domain_filename = os.path.join(domains_dir, name + ".domains")
            print_subj_domains(subj_domains, domain_filename)
            print_obj_domains(obj_domains, domain_filename)

if __name__ == '__main__':

    if len(sys.argv) == 2:

        working_sets_filename = sys.argv[1] + ".working_sets"        
        if os.path.exists(working_sets_filename):
            working_sets = load_working_sets(working_sets_filename)
            WS = WorkingSets(working_sets_filename)
        else:
            print("Could not find " + working_sets_filename)
            print("Running with no working sets. Can't use rule clustering.")
            working_sets = None
            WS = none

        prog = sys.argv[1]
        cmap = CAPMAP(prog)
        
        prog_name = os.path.basename(prog)
        
        # Prepare PS file
        results_dir = "results_PS"
        if not os.path.exists(results_dir):
            os.mkdir(results_dir)

        # What constraints do we want to apply?
        #constraints = [(None, None), (cmap.func_to_file, "fileConstr"), (cmap.func_to_dir, "dirConstr")]
        constraints = [(None, None)]
            
        #ps_result_file = open(os.path.join(results_dir, prog_name), "w")
        ps_result_file = open("PSR_results.txt", "a")


        # Create the syntactic domains
        print("Creating syntatic domains...")
        domains = create_syntactic_domains(cmap, prog)
        binary_name = os.path.basename(prog)    
        for cut in domains:
            PSR = calc_PSR_cut(cmap, domains[cut])
            ps_result_file.write(prog_name + " " + cut + " PSR " + str(PSR) + "\n")
            install_domains(domains[cut], cmap.obj_no_cluster, binary_name + "." + cut)
        ps_result_file.flush()


        # Create the size-based domains            
        print("Creating cluster size domains...")
        for size in [512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]:
            for (constraint, name) in constraints:
                condition_name = "C" + str(size)                
                if constraint != None:
                    condition_name += "_" + name                    
                subj_clusters, obj_clusters = cluster_functions(cmap, ClusterStrategy.CLUSTER_SIZE, size, merge_constraint=constraint, WS=None)
                PSR = calc_PSR_cut(cmap, subj_clusters)
                ps_result_file.write(prog_name + " " + condition_name + " PSR " + str(PSR) + "\n") 
                install_domains(subj_clusters, obj_clusters, binary_name + "." + condition_name)
                ps_result_file.flush()

        
        # Create the ratio-based domains            
        print("Creating ratio domains...")
        for ratio in [0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001]:
            condition_name = "R" + str(ratio)
            subj_clusters, obj_clusters = cluster_functions(cmap, ClusterStrategy.CLUSTER_RATIO, ratio)
            PSR = calc_PSR_cut(cmap, subj_clusters)
            ps_result_file.write(prog_name + " " + condition_name + " PSR " + str(PSR) + "\n") 
            install_domains(subj_clusters, obj_clusters, binary_name + "." + condition_name)
            ps_result_file.flush()
        
        # Run the basic rule clustering algorithm
        if working_sets != None:
            for cache_size in [1024, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3200, 3400, 3600, 3800]:
                for (constraint, name) in constraints:
                    condition_name = "Rules" + str(cache_size)                
                    if constraint != None:
                        condition_name += "_" + name
                    print("Running " + condition_name)    
                    subj_clusters, obj_clusters = cluster_functions(cmap, ClusterStrategy.CLUSTER_RULES, cache_size,
                                                 working_sets = working_sets, merge_constraint=constraint, WS=WS)
                    PSR = calc_PSR_cut(cmap, subj_clusters)
                    ps_result_file.write(prog_name + " " + condition_name + " PSR " + str(PSR) + "\n") 
                    install_domains(subj_clusters, obj_clusters, binary_name + "." + condition_name)
                    ps_result_file.flush()
        

    else:

        print("Run with ./InstallDomains.py <vmlinux> <kmap> <working_set_file>")
