pointers = ['ret', 'funcptrstackvar', 'funcptrstackparam', 'funcptrheap',
'funcptrbss', 'funcptrdata', 'structfuncptrstack', 'structfuncptrheap',
'structfuncptrdata', 'structfuncptrbss', 'longjmpstackvar', 'longjmpstackparam', 
'longjmpheap', 'longjmpdata', 'longjmpbss','bof', 'iof', 'leak']

functions = ['memcpy', 'strcpy', 'strncpy', 'sprintf', 'snprintf', 'strcat',
'strncat', 'sscanf', 'homebrew']

locations = ['stack','heap','bss','data']

attacks = ['shellcode', 'returnintolibc', 'rop', 'dataonly']

techniques = ['direct', 'indirect']


def violates_heap_policy(attack, technique, location, pointer, function):
    if location is 'heap':
        return True
    return False

def violates_composite_policy(attack, technique, location, pointer, function):
    return violates_heap_policy(attack, technique, location, pointer, function) or \
        violates_stack_policy(attack, technique, location, pointer, function)   or \
        violates_rwx_policy(attack, technique, location, pointer, function)     or \
        violates_three_class_policy(attack, technique, location, pointer, function)

def violates_stack_policy(attack, technique, location, pointer, function):
    if pointer is 'ret':
        return True
    return False


def violates_three_class_policy(attack, technique, location, pointer, function):
    if pointer is 'ret':
        return True
    if attack in ['rop', 'shellcode']:
        return True
    return False


def violates_rwx_policy(attack, technique, location, pointer, function):
    if attack is 'shellcode':
        return True
    return False


class RIPEPolicy:
    def __init__(self, name, is_violation):
        self.name = name
        self.is_violation = is_violation


class RIPEPolicyConfig:
    def __init__(self, attack, technique, location, pointer, function, policies):
        self.attack = attack
        self.technique = technique
        self.location = location
        self.pointer = pointer
        self.function = function
        self.policies = []
        for policy in policies:
            if policy.is_violation(
                    self.attack,
                    self.technique,
                    self.location,
                    self.pointer,
                    self.function):
                self.policies.append(policy.name)

    def __iter__(self):
        yield self.attack
        yield self.technique
        yield self.location
        yield self.pointer
        yield self.function
        yield self.policies

def is_attack_possible(attack, technique, location, pointer, function):
    # temporarily disabling broken longjmp parameters
    if 'longjmp' in pointer:
        return False

    if attack is 'shellcode':
        if function not in ['memcpy', 'homebrew']:
            return False

    if attack is 'dataonly':
        if pointer not in ['bof', 'iof', 'leak']:
            return False

        if (pointer is 'iof' or pointer is 'leak') and technique is 'indirect':
            return False

        if technique is 'indirect' and location is 'heap':
            return False
    elif pointer in ['bof', 'iof', 'leak']:
        return False

    if attack is 'rop' and technique is not 'direct':
        return False	

    if technique is 'indirect' and pointer is 'longjmpheap' and location is 'bss':
        if function is not 'memcpy' and function is not 'strncpy' and function is not 'homebrew':
            return False

    if technique == 'direct':
        if (location is 'stack' and pointer is 'ret'):
            return True
        elif attack is not 'dataonly' and location not in pointer:
            return False
        elif pointer == 'funcptrstackparam':
            if function is 'strcat' or function is 'snprintf' or function is 'sscanf' or function is 'homebrew':
                return False
        elif pointer is 'structfuncptrheap' and attack is not 'shellcode' and location is 'heap':
            if function is 'strncpy':
                return False

    return True


def generate_ripe_policy_configs(techniques, attacks, locations, code_ptr, funcs, policies):
    ripe_policy_configs = []

    for attack in attacks:
        for tech in techniques:
            for loc in locations:
                for ptr in code_ptr:
                    for func in funcs:
                        if is_attack_possible(attack, tech, loc, ptr, func):
                            config = RIPEPolicyConfig(attack, tech, loc, ptr, func, policies)
                            ripe_policy_configs.append(tuple(config))

    return ripe_policy_configs


def main():
    global techniques
    global attacks
    global locations
    global pointers

    policies = [
        RIPEPolicy('osv.hifive.main.heap', violates_heap_policy),
        RIPEPolicy('osv.hifive.main.stack', violates_stack_policy),
        RIPEPolicy('osv.hifive.main.threeClass', violates_three_class_policy),
        RIPEPolicy('osv.hifive.main.rwx', violates_rwx_policy),
        RIPEPolicy('osv.hifive.main.heap-rwx-stack-threeClass', violates_composite_policy),
    ]

    configs = generate_ripe_policy_configs(techniques, attacks, locations, pointers, ['memcpy'], policies)

    print "class RipeConfigs:"
    print "    configs= ["
    for config in configs:
        print "      " + str(config) + ","
    print "    ]"
        
if __name__ == "__main__":
    main()
