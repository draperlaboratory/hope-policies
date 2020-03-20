import os
import errno

def pexName(sim, policies, global_policies, arch, debug):
    name = None
    policy_name = policyName(policies, global_policies, debug)

    if sim == "qemu":
        return "-".join([arch, policy_name, "validator.so"])
    if sim == "vcu118":
        return "-".join([arch, "kernel", "gfe", policy_name])

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
