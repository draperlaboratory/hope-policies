import itertools
import operator

runtime = "frtos"
module = "osv."
global_policies = ["contextswitch"]
local_policies = sorted(["cfi", "rwx", "stack", "taint", "heap", "threeClass", "none", "testSimple", "testComplex", "password", "ppac", "userType", "testContext", "testgenInfoLeak"])
all_policies = global_policies + local_policies

print("module " + module + runtime + ".main:")

print("import:")

for p in all_policies:
    print("  " + module + p)

print("policy:")

# list of number of policies
ns = list(range(0,len(local_policies)+1))
# list of combinations for each n
combs = [list(map(sorted,itertools.combinations(local_policies, n))) for n in ns]
# flatten list
local_subsets = reduce(operator.concat, combs, [])

# list of number of policies
gns = list(range(0,len(global_policies)+1))
# list of combinations for each n
gcombs = [list(itertools.combinations(global_policies, gn)) for gn in gns]
# flatten list
global_subsets = reduce(operator.concat, gcombs, [])

for local_pols in local_subsets:
    for global_pols in global_subsets:
        if global_pols and local_pols:
            print("  " + "-".join(global_pols) + "-" + "-".join(local_pols) + " = " + " & ".join([pol + "Pol" for pol in global_pols]) + " & "+ " & ".join([ pol + "Pol" for pol in local_pols]))
        elif local_pols:
            print("  " + "-".join(local_pols) + " = " + " & ".join([ pol + "Pol" for pol in local_pols]))
        elif global_pols:
            print("  " + "-".join(global_pols) + " = " + " ^ ".join([ pol + "Pol" for pol in global_pols]))


