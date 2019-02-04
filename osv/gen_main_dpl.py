import itertools
import operator

runtime = "hifive"
module = "osv."
policies = ["cfi", "rwx", "stack", "taint", "heap", "threeClass", "none", "testSimple", "testComplex"]

print("module " + module + runtime + ".main:")

print("import:")

for p in policies:
    print("  " + module + p)

print("policy:")

for p in policies:
    print("  " + p + " = " + p + "Pol")

p = sorted(policies)
# list of number of policies
ns = list(range(1,len(p)+1))
# list of combinations for each n
combs = [list(map(sorted,itertools.combinations(p, n))) for n in ns]
# flatten list
l = reduce(operator.concat, combs, [])

for c in l:
    print("  " + "-".join(c) + " = " + " & ".join([ i + "Pol" for i in c]))


