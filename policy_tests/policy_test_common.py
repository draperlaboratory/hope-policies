import os
import errno

def pexName(sim, policies, global_policies, arch, debug, processor=None):
    name = None
    policy_name = policyName(policies, global_policies, debug)

    if sim == "qemu":
        return "-".join([arch, policy_name, "validator.so"])
    if sim == "vcu118" or sim == "iveia":
        if not processor:
            return None
        return "-".join(["kernel", "gfe", processor, policy_name])

    return None


def policyName(policies, global_policies, debug):
    all_policies = sorted(global_policies) + sorted(policies)
    policy_name = "-".join(all_policies)
    if debug:
        return "-".join([policy_name, "debug"])
    return policy_name


def is64Bit(arch):
    if arch == 'rv64':
        return True
    return False


def getExtraArg(extra, arg_name):
    extra_args = extra.split(",")
    for arg in extra_args:
        arg_key = "+" + arg_name + "="
        if arg_key in arg:
            return arg.strip(arg_key)

    return None
