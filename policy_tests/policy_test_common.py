import os
import errno

def pexName(sim, policies, global_policies, debug):
    name = None
    policy_name = policyName(policies, global_policies, debug)

    if sim == "qemu":
        return "-".join(["rv32", policy_name, "validator.so"])
    if sim == "vcu118":
        return "-".join(["kernel", "gfe", policy_name])

    return None


def policyName(policies, global_policies, debug):
    all_policies = sorted(global_policies) + sorted(policies)
    policy_name = "-".join(all_policies)
    if debug:
        return "-".join(policy_name, "debug")
    return policy_name


def is64Bit(arch):
    if arch == 'rv64':
        return True
    return False


def outputDir(runtime, sim, arch):
    return os.path.join(os.path.abspath("build"), runtime, sim, arch)
