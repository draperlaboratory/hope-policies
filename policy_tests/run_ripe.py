#!/usr/bin/python

# Developed by Nick Nikiforakis to assist the automated testing
# using the RIPE evaluation tool
#
# Released under the MIT license (see file named LICENSE)
#
# This program is part the paper titled
# RIPE: Runtime Intrusion Prevention Evaluator
# Authored by: John Wilander, Nick Nikiforakis, Yves Younan,
#              Mariam Kamkar and Wouter Joosen
# Published in the proceedings of ACSAC 2011, Orlando, Florida
#
# Please cite accordingly.
#
# Modified for RISC-V by John Merrill

import os, sys, subprocess, time, signal, argparse, shutil
from termcolor import colored

code_ptr = ['ret', 'funcptrstackvar', 'funcptrstackparam', 'funcptrheap',
'funcptrbss', 'funcptrdata', 'structfuncptrstack', 'structfuncptrheap',
'structfuncptrdata', 'structfuncptrbss', 'longjmpstackvar', 'longjmpstackparam', 
'longjmpheap', 'longjmpdata', 'longjmpbss','bof', 'iof', 'leak'];

funcs = ['memcpy', 'strcpy', 'strncpy', 'sprintf', 'snprintf', 'strcat',
'strncat', 'sscanf', 'homebrew'];

locations = ['stack','heap','bss','data'];

attacks = ['shellcode', 'returnintolibc', 'rop', 'dataonly'];
techniques = []
output = ''

width = int(os.popen('stty size', 'r').read().split()[1])
color = lambda x,y: colored(x, y, attrs=['bold'])
line = lambda x: color('-'*x, 'white')
bold_line = lambda x: color('='*x, 'white')

def print_attack(cmdargs, status):
	params = cmdargs.split('_')[1:]
	for idx, param in enumerate(params):
		params[idx] = param[2:]
	
	result = ''
	if status == 1:
		result = color('OK', 'green')
	else:
		result = color('FAIL', 'grey')

	print('Technique: ' + params[0])
	print('Attack code: ' + params[1])
	print('{0:50}{1:}'.format('Target Pointer: ' + params[2], 'Result: ' + result))
	print('Location: ' + params[3])
	print('Function: ' + params[4])
	print(line(64))

def is_attack_possible ( attack, tech, loc, ptr, func ):

	if attack == 'shellcode':
		if func != 'memcpy' and func != 'homebrew':
			return 0

	if attack == 'dataonly':
		if ptr not in ['bof', 'iof', 'leak']:
			return 0

		if (ptr == 'iof' or ptr == 'leak') and tech == 'indirect':
			return 0

		if tech == 'indirect' and loc == 'heap':
			return 0
	elif ptr in ['bof', 'iof', 'leak']:
		return 0;

	if attack == 'rop' and tech != 'direct':
		return 0	

	if tech == 'indirect' and ptr == 'longjmpheap' and loc == 'bss':
		if func != 'memcpy' and func != 'strncpy' and func != 'homebrew':
			return 0

	if tech == 'direct':
		if (loc == 'stack' and ptr == 'ret'):
			return 1
		elif attack != 'dataonly' and ptr.find(loc) == -1:
			return 0
		elif ptr == 'funcptrstackparam':
			if func == 'strcat' or func == 'snprintf' or func == 'sscanf' or func == 'homebrew':
				return 0
		elif ptr == 'structfuncptrheap' and attack != 'shellcode' and loc == 'heap':
			if func == 'strncpy':
				return 0
	return 1

                                        

def init_test_dir(attack, tech, loc, ptr, func):

        test_name = attack + '_' + tech + '_' + loc + '_' + ptr + '_' + func + ".ripe"

        # make ./ripe/test & ./ripe/test/build
        test_dir = os.path.join(os.path.join(os.getcwd(),"ripe"),test_name)
        safemkdir(os.path.join(test_dir,"build"))

        # destination sources dir contains c sources & headers 
        test_srcdir = os.path.join(test_dir, "srcs")
        safemkdir(test_srcdir)
        
        # runtime specific code
        shutil.copytree(os.getenv("ISP_PREFIX")+"/hifive_bsp", os.path.join(test_dir, "build/bsp"))
        shutil.copy(os.path.join("template", "hifive.makefile"), os.path.join(test_dir, "build/Makefile"))
        shutil.copyfile(os.path.join("template", "hifive-mem.h"), os.path.join(test_srcdir, "mem.h"));

        # pytest code run wrappers
        shutil.copy(os.path.join("template", "runQEMU.py"), os.path.join(test_dir, "runQEMU.py"))

        # generic test code 
        shutil.copy(os.path.join("template", "hifive.c"), test_srcdir)
        shutil.copy(os.path.join("template", "test.h"), test_srcdir)
        shutil.copy(os.path.join("template", "test_status.c"), test_srcdir)
        shutil.copy(os.path.join("template", "test_status.h"), test_srcdir)

        # test specific code
        for f in os.listdir(os.path.join("tests", "ripe")):
                shutil.copy(os.path.join("tests", "ripe", f), test_srcdir)

        # and makefile                
        mf_cflags = 'CFLAGS += '
        mf_cflags += '-DATTACK_TECHNIQUE=\\\"'+tech+'\\\" '
        mf_cflags += '-DATTACK_INJECT_PARAM=\\\"'+attack+'\\\" '
        mf_cflags += '-DATTACK_CODE_PTR=\\\"'+ptr+'\\\" '
        mf_cflags += '-DATTACK_LOCATION=\\\"'+loc+'\\\" '
        mf_cflags += '-DATTACK_FUNCTION=\\\"'+func+'\\\"'
        
        with open(os.path.join(test_srcdir, "Makefile"), "w") as f:
                f.write(mf_cflags)

        # create entity for file elements
        entDir = os.path.abspath("../entities")
        entFile = "ripe" + ".entities.yml"
        srcEnt = os.path.join(entDir, entFile)
        destEnt = os.path.join(test_dir, entFile.replace('/', '-'))
        if os.path.isfile(srcEnt):
                shutil.copyfile(srcEnt, destEnt)
        else:
                shutil.copyfile(os.path.join(entDir, "empty.entities.yml"), destEnt)

        # debug config script
        gs = gdbScriptQemu(test_dir)
        #print("GDB Script: {}".format(test_dir))
        with open(os.path.join(test_dir,'.gdbinit'), 'w+') as f:
                f.write(gs)

        # compile the test
        shutil.copyfile(os.path.join("template", "test.makefile"), os.path.join(test_dir, "Makefile"))
        subprocess.Popen(["make"], stdout=open(os.path.join(test_dir, "build/build.log"), "w+"), stderr=subprocess.STDOUT, cwd=test_dir).wait()
        # subprocess.Popen(["make"], stdout=open(os.path.join(test_dir, "build/build.log"), "w+"), cwd=test_dir).wait()
        
        # check that build succeeded
        assert os.path.isfile(os.path.join(test_dir, "build", "main"))


def run_tests(policy, attack, tech, loc, ptr, func):

        global run_cmd
        global total_ok
        global total_fail
        global total_np

        # assuming attack is possible here

        # location of test 
        test_name = attack + '_' + tech + '_' + loc + '_' + ptr + '_' + func + ".ripe"
        test_dir = os.path.join(os.path.join(os.getcwd(),"ripe"),test_name)
        pol_test_dir = os.path.join(test_dir, policy.split('.')[-1]) 

        # make test-specific directory
        safemkdir(pol_test_dir)

        # get copy of the policy
        subprocess.Popen(["cp", "-r", os.path.join(os.path.join(os.getcwd(), 'kernel_dir/kernels'), policy), pol_test_dir], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT).wait()
        
        # simulator config script -- ONLY NEEDED FOR RENODE
#        rs = rescScriptHifive(pol_test_dir, policy)
        #print("Renode Script: {}".format(test_dir))
#        filenm = policy+".main.resc"
#        with open(os.path.join(pol_test_dir,filenm), 'w+') as f:
#                f.write(rs)

        # configure validator
        doValidatorCfg(policy, pol_test_dir)#, rule_cache, rule_cache_size)

        # build makefile 
        mf = ripeHifiveMakefile(policy)
        #print("Makefile: {}".format(test_dir))
        with open(os.path.join(pol_test_dir,'Makefile'), 'w+') as f:
                f.write(mf)
        
        # RUN THE TEST

        # run tagging tools
        safemkdir(os.path.join(pol_test_dir, "bininfo"))
        subprocess.Popen(["make", "inits"], stdout=open(os.path.join(pol_test_dir, "inits.log"), "w"), stderr=subprocess.STDOUT, cwd=pol_test_dir).wait()

        # Check for tag information
        assert os.path.isfile(os.path.join(pol_test_dir, "bininfo", "main.taginfo"))
        # assert os.path.isfile(os.path.join(pol_test_dir, "bininfo", "main.text"))
        # assert os.path.isfile(os.path.join(pol_test_dir, "bininfo", "main.text.tagged"))

        # run test
        subprocess.Popen(["make", "qemu", "POLICY={}".format(policy)], stdout=open(os.path.join(pol_test_dir, "sim.log"), "w+"), stderr=subprocess.STDOUT, cwd=pol_test_dir).wait()

        # check for successful attack
        with open(os.path.join(pol_test_dir, 'uart.log'), 'r') as log:
	        if log.read().find('success') != -1:
                        return "Attack Success!"

        # check for successful defense
        with open(os.path.join(pol_test_dir, 'pex.log'), 'r') as log:
                if log.read().find('Policy Violation') != -1:
                        return "Violation Detected!"

        return "ERROR"

def ripeHifiveMakefile(policy):
    return """
PYTHON ?= python3

inits:
	gen_tag_info -d ./{p} -t ./bininfo/main.taginfo -b ../build/main -e ./{p}/{p}.entities.yml ../ripe.entities.yml

renode:
	$(PYTHON) runRenode.py

renode-console:
	renode {p}.main.resc

qemu:
	$(PYTHON) -u ../runQEMU.py {p}

qemu-console:
	$(PYTHON) -u ../runQEMU.py {p} -d

gdb:
	riscv32-unknown-elf-gdb -q -iex "set auto-load safe-path ./" ../build/main

clean:
	rm -rf *.o *.log bininfo/*
""".format(p=policy)

def gdbScriptQemu(dir):
    return """

define metadata
   help metadata
end

document metadata
Metadata related commnads:
   pvm      - print violation message
   env-m    - get the env metadata
   reg-m n  - get register n metadata
   csr-m a  - get csr metadata at addr a
   mem-m a  - get mem metadata at addr a
Watchpoints halt simulation when metadata changes
   env-mw   - set watch on the env metadata
   reg-mw n - set watch on register n metadata
   csr-mw a - set watch on csr metadata at addr a
   mem-mw a - set watch on mem metadata at addr a
end

define pvm
   monitor pvm
end

document pvm
   Command to print last policy violation info
   Only captures the last violation info.
end

define env-m
   monitor env-m
end

document env-m
   get environment metadata
end

define reg-m
   monitor reg-m
end

document reg-m
   get register metadata
end

define csr-m
   monitor csr-m $arg0
end
document csr-m
   get csr metadata at addr
end

define mem-m
   monitor mem-m $arg0
end
document mem-m
   get mem metadata at addr
end

define env-mw
   monitor env-mw
end
document env-mw
   set watch on the env metadata
end

define reg-mw
   monitor reg-mw $arg0
end
document reg-mw
   set watch on register metadata
end

define csr-mw
   monitor csr-mw $arg0
end
document csr-mw
   set watch on csr metadata at addr
end

define mem-mw
   monitor mem-mw $arg0
end
document mem-mw
   set watch on mem metadata at addr
end



define hook-stop
   pvm
end

set confirm off
target remote :3333
break main
continue
""".format(path = os.path.join(os.getcwd(), dir))

def doValidatorCfg(policy, dirPath):#, rule_cache, rule_cache_size):
        soc_cfg = "hifive_e_cfg.yml"

        validatorCfg =  """\
---
   policy_dir: {policyDir}
   tags_file: {tagfile}
   soc_cfg_path: {soc_cfg}
""".format(policyDir=os.path.join(os.getcwd(), dirPath, policy),
           tagfile=os.path.join(os.getcwd(), dirPath, "./bininfo/main.taginfo"),
           soc_cfg=os.path.join(os.getcwd(), dirPath, policy, "soc_cfg", soc_cfg))

#    if (rule_cache):
#        validatorCfg += """\
#   rule_cache:
#      name: {rule_cache_name}
#      capacity: {rule_cache_size}
#        """.format(rule_cache_name=rule_cache, rule_cache_size=rule_cache_size)

        filenm = policy+".validator_cfg.yml"
        with open(os.path.join(dirPath,filenm), 'w') as f:
                f.write(validatorCfg)

def safemkdir(directory):
        try:
                os.makedirs(directory)
        except OSError as e:
                if e.errno != errno.EEXIST:
                        raise
                
# parse args
parser = argparse.ArgumentParser(description='frontend for RIPE')
parser.add_argument('-t', help='Techniques [direct | indirect | both] (both by default)', default='both')
parser.add_argument('-l', help='Memory location [stack | heap | data | bss]', default=None)
parser.add_argument('-c', help="""
Code pointer to overwrite: [ret |
funcptrstackvar | funcptrstackparam | funcptrheap | funcptrbss| funcptrdata |
structfuncptrstack | structfuncptrheap | structfuncptrdata | structfuncptrbss |
longjmpstackvar | longjmpstackparam | longjmpheap | longjmpdata | longjmpbss |
bof | iof | leak]
""")
parser.add_argument('-a', help='Attack method [shellcode | returnintolibc | rop | dataonly]', default=None)
parser.add_argument('-f', help='Run tests with all functions (memcpy() only by default)', default=False, action='store_true')
parser.add_argument('-r', help='Simulator command', default='spike pk', action='store_true')
parser.add_argument('-o', help='Send output to file (default stdout)', nargs=1)
args = parser.parse_args()

print args

if args.t == 'both':
	techniques = ['direct','indirect'];
else:
	techniques = [args.t]

if not args.f:
	funcs = ['memcpy']

if args.l is not None:
        locations = [args.l]

if args.c is not None:
        code_ptr = [args.c]

if args.a is not None:
        attacks = [args.a]

if args.r:
	run_cmd = args.r

if args.o:
	color = lambda x,y:x
	sys.stdout = open(args.o[0], 'w')

print bold_line(width)
print color('RIPE: The Runtime Intrusion Prevention Evaluator for RISCV', 'white')
print bold_line(width)

start_time = time.time()

policies = os.listdir(os.path.join("kernel_dir", "kernels"))
none_pol = [x for x in policies if x.find("none") != -1][0]
not_none_pols = [x for x in policies if x.find("none") == -1]

for attack in attacks:
	for tech in techniques:
		for loc in locations:
			for ptr in code_ptr:
				for func in funcs:
	                                if is_attack_possible (attack, tech, loc, ptr, func):
                                                print("Test config: "+attack+","+tech+","+loc+","+ptr+","+func)
                                                init_test_dir(attack, tech, loc, ptr, func)
                                                out = run_tests(none_pol, attack, tech, loc, ptr, func)
                                                print("  Baseline - "+out)
                                                if out == "Attack Success!":
                                                        print("  Applicable policies (violation detection expected):")
                                                        for policy in [p for p in not_none_pols if p.find(loc) != -1]:
                                                                out = run_tests(policy, attack, tech, loc, ptr, func)
                                                                print("    "+policy+" - "+out)
                                                        print("  Other policies (attack success expected):")
                                                        for policy in [p for p in not_none_pols if p.find(loc) == -1]:
                                                                out = run_tests(policy, attack, tech, loc, ptr, func)
                                                                print("    "+policy+" - "+out)
                                                
# do summary
#total_attacks = total_ok + total_fail;
#end_time = time.time() - start_time
#avg_time = end_time / (total_attacks)

#print color('SUMMARY\n', 'white') + line(64)
#print 'Total ' + color('OK', 'green') + ': ' + str(total_ok)
#print 'Total ' + color('FAIL', 'grey') + ': ' + str(total_fail)
#print 'Total Attacks Executed: ' + str(total_attacks)
#print 'Total time elapsed: ' + str(int(end_time / 60)) + 'm ' + str(int(end_time % 60)) + 's'
#print 'Average time per attack: ' + '{0:.2f}'.format(avg_time) + 's'
