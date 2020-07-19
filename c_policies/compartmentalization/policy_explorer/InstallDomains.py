#!/usr/bin/python

# This script runs both the syntatic and clustered domains.
# It installs them into the kernels directory.
# It also creates domain_PS_results.txt containing the PS per cut.

from DomainCreator import *
from SyntacticDomains import *
from calculate_PS import *

# Install these domain files into the policy kernel directory
def install_domains(domains, name):
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
            print_subj_domains(domains, domain_filename)
        
            

if __name__ == '__main__':

    if len(sys.argv) == 2:

        working_sets_filename = sys.argv[1] + ".working_sets"        
        if os.path.exists(working_sets_filename):
            working_sets = load_working_sets(working_sets_filename)
        else:
            print("Could not find " + working_sets_filename)
            print("Running with no working sets. Can't use rule clustering.")
            working_sets = None

        # Check for coresidency file
        '''
        coresidency_filename = sys.argv[1] + ".coresidency"
        if os.path.exists(coresidency_filename):
            coresidency = load_rule_frequencies(coresidency_filename)
        else:
            print("Running with no rule frequencies. Could not find " + coresidency_filename)
            coresidency = None
        '''
        
        prog = sys.argv[1]
        cmap = CAPMAP(prog)
        
        prog_name = os.path.basename(prog)
        
        # Prepare PS file
        results_dir = "results_PS"
        if not os.path.exists(results_dir):
            os.mkdir(results_dir)
            
        #ps_result_file = open(os.path.join(results_dir, prog_name), "w")
        ps_result_file = open("PSR_results.txt", "a")

        # Create the syntactic domains
        print("Creating syntatic domains...")
        domains = create_syntactic_domains(cmap, prog)
        binary_name = os.path.basename(prog)    
        for cut in domains:
            PSR = calc_PSR_cut(cmap, domains[cut])
            ps_result_file.write(prog_name + " " + cut + " PSR " + str(PSR) + "\n")
            install_domains(domains[cut], binary_name + "." + cut)
        ps_result_file.flush()

        '''
        # Create the size-based domains            
        print("Creating cluster size domains...")
        for size in [512, 1024, 2048, 4096, 8192, 16384, 32768]:
            for (constraint, name) in [(None, None), (cmap.func_to_file, "fileConstr"), (cmap.func_to_dir, "dirConstr")]:
                condition_name = "C" + str(size)                
                if constraint != None:
                    condition_name += "_" + name                    
                subj_clusters = cluster_functions(cmap, ClusterStrategy.CLUSTER_SIZE, size, merge_constraint=constraint)
                PSR = calc_PSR_cut(cmap, subj_clusters)
                ps_result_file.write(prog_name + " " + condition_name + " PSR " + str(PSR) + "\n") 
                install_domains(subj_clusters, binary_name + "." + condition_name)
                ps_result_file.flush()
        '''
        
        '''
        # Create the ratio-based domains            
        print("Creating ratio domains...")
        for ratio in [0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001]:
            condition_name = "R" + str(ratio)
            subj_clusters = cluster_functions(cmap, ClusterStrategy.CLUSTER_RATIO, ratio)
            PSR = calc_PSR_cut(cmap, subj_clusters)
            ps_result_file.write(prog_name + " " + condition_name + " PSR " + str(PSR) + "\n") 
            install_domains(subj_clusters, binary_name + "." + condition_name)
            ps_result_file.flush()
        '''
        
        # Run the basic rule clustering algorithm
        if working_sets != None:
            for cache_size in [1024, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3200, 3400, 3600, 3800]:
                for (constraint, name) in [(None, None), (cmap.func_to_file, "fileConstr"), (cmap.func_to_dir, "dirConstr")]:
                    condition_name = "Rules" + str(cache_size)                
                    if constraint != None:
                        condition_name += "_" + name
                    print("Running " + condition_name)    
                    clusters = cluster_functions(cmap, ClusterStrategy.CLUSTER_RULES, cache_size,
                                                 working_sets = working_sets, merge_constraint=constraint)
                    PSR = calc_PSR_cut(cmap, clusters)
                    ps_result_file.write(prog_name + " " + condition_name + " PSR " + str(PSR) + "\n") 
                    install_domains(clusters, binary_name + "." + condition_name)
                    ps_result_file.flush()
        
        '''
        # Run the coresidency variant
        for cache_size in [1024]:
            for cache_target in [0.97, 0.98, 0.99]:
                condition_name = "Cores" + str(cache_target)
                print("Running " + condition_name)
                clusters = cluster_functions(cmap, ClusterStrategy.CLUSTER_RULES, cache_size,
                                                         working_sets = working_sets, coresidency = coresidency, cache_target=cache_target)
                PSR = calc_PSR_cut(cmap, clusters)
                ps_result_file.write(prog_name + " " + condition_name + " PSR " + str(PSR) + "\n") 
                install_domains(clusters, binary_name + "." + condition_name)
                ps_result_file.flush()        
        '''        


    else:

        print("Run with ./InstallDomains.py <vmlinux> <kmap> <working_set_file>")
