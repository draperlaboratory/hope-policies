#!/usr/bin/python3

import sys
import os
import re
import test_groups
import argparse

from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
from xml.dom import minidom

start_pattern = "Start time: [0-9]*us"
end_pattern = "End time: [0-9]+us"
time_pattern = "[0-9]+"

def get_output_dir(runtime, sim, policy, test):
    policy_full_name = ".".join(["osv", runtime, "main", policy])
    dir_name = "-".join(["isp", "run", test, policy_full_name, sim])
    result = os.path.join("output", dir_name)

    if not os.path.isdir(result):
        return None
    return result


def get_duration_msec(output_dir):
    uart_filename = os.path.join(output_dir, "uart.log")
    uart_file = open(uart_filename, "r")
    uart = uart_file.read()
    uart_file.close()

    start_matches = re.findall(start_pattern, uart)
    if not start_matches:
        return 0
    start_str = start_matches[0]

    end_matches = re.findall(end_pattern, uart)
    if not end_matches:
        return 0
    end_str = end_matches[0]

    start_time = int(re.findall(time_pattern, start_str)[0])
    end_time = int(re.findall(time_pattern, end_str)[0])

    return end_time - start_time


def generate_report(runtime, sim, policies, tests):
    top = Element("performance_tests")

    skipped = []
    for test in tests:
        test_node = SubElement(top, "test")
        test_node.text = test

        policy_durations = {}
        for policy in policies:
            output_dir = get_output_dir(runtime, sim, policy, test)
            if output_dir is None:
                skipped.append((test, policy))
                continue
            msec = get_duration_msec(output_dir)
            if msec == 0:
                skipped.append((test, policy))
                continue
            
            sec = float(msec)/1000000
            policy_durations[policy] = sec

        if not policy_durations:
            continue
        base_time = policy_durations['none']
        print("Test: {}".format(test))
        print("  Baseline time: {}".format(base_time))
        base_time_node = SubElement(test_node, "base_time")
        base_time_node.text = str(base_time)
        for policy in policies:
            if policy == 'none':
                continue
            policy_time = policy_durations[policy]
            overhead = ((policy_time - base_time) / base_time) * 100
            print("  Policy: {}".format(policy))
            print("    total time: {}".format(policy_durations[policy]))
            print("    overhead: {}%".format(overhead))

            policy_node = SubElement(test_node, "policy")
            policy_node.text = policy
            policy_time_node = SubElement(policy_node, "time")
            policy_time_node.text = str(policy_durations[policy])
            policy_overhead_node = SubElement(policy_node, "overhead")
            policy_overhead_node.text = str(overhead)
        print("")

    print("Tests skipped: {}".format(len(skipped)))
    return top

def get_tests(test_arg):
    # "TESTS" as passed on the command line may be the names
    #   of individual tests, or the name of a group of tests
    #   defined in test_groups.py. The latter is the default
    #   in a case in which a group is given the same name as
    #   a test        

    # look up any test groups
    tests = []
    for t in test_arg:
        if t not in test_groups.test_groups:
            tests.append(t)
        else:
            tests.extend(test_groups.test_groups[t].tests)

    # unique (avoid duplicate work) & alphabetical (for XDIST)
    tests = sorted(list(set(tests))) 
    return tests


def pretty_xml(node):
    rough_string = tostring(node, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def main():
    runtime = sys.argv[1]
    sim = sys.argv[2]
    policy_list = sys.argv[3]
    test_list = sys.argv[4]

    parser = argparse.ArgumentParser(description="Generate performance report for policy tests")
    parser.add_argument("-r", "--runtime", type=str, required=True)
    parser.add_argument("-s", "--sim", type=str, required=True)
    parser.add_argument("-p", "--policies", type=str, required=True, help='''
    comma-separated list of policies e.g. rwx,stack,heap,heap-rwx-stack
    ''')
    parser.add_argument("-t", "--tests", type=str, required=True, help='''
    comma-separated list of tests or test groups e.g. bare OR hello_works_1,coremark
    ''')
    parser.add_argument("-o", "--output", type=str, help='''
    output xml file for report. Default is: performance-test-<runtime>-<sim>.xml
    ''')
    parser.add_argument("-c", "--compose", action="store_true", help='''
    Also test composite of all standalone policies
    ''')
    args = parser.parse_args()

    policies = args.policies.split(",")
    if "none" not in policies:
        policies.append('none')

    if args.compose:
        standalone_policies = []
        for policy in policies:
            if "-" not in policy and policy != "none":
                standalone_policies.append(policy)
        if len(standalone_policies) > 1:
            standalone_policies = sorted(standalone_policies)
            policies.append("-".join(standalone_policies))

    test_arg = args.tests.split(",")
    tests = get_tests(test_arg)

    output_path = "-".join(["performance", "test", args.runtime, args.sim]) + ".xml"
    if args.output:
        output_path = args.output
    output_file = open(output_path, "w")

    report = generate_report(args.runtime, args.sim, policies, tests)

    output_file.write(pretty_xml(report))
    output_file.close()

if __name__ == "__main__":
    main()

