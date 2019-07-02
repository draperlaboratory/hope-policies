#!/usr/bin/python3
import argparse
import os
import json
from matplotlib import pyplot as plt
import numpy as np
import pdb

rhealstone_component_names = ["switching",
                              "preempt",
                              "deadlk_base",
                              "deadlk_test",
                              "sem_base",
                              "sem_test",
                              "intertask",
                              "interrupt"]

class RhealstoneComponent():
    def __init__(self, name, policy):
        self.name = name
        self.policy = policy

    def parse_measurements(self):
        directory = "isp-run-rhealstone_{}-osv.frtos.main.{}".format(self.name, self.policy)
        output_path = os.path.join("output", directory)
        uart_log = os.path.join(output_path, "uart.log")
        read_results_flag = False
        json_string = ""
        if not os.path.exists(uart_log):
            raise ValueError('Could Not find uart log: ',uart_log)
        with open(uart_log, 'r') as uart_file:
            for line in uart_file.readlines():
                if 'RESULTS BEGIN' in line:
                    read_results_flag = True
                elif 'RESULTS END' in line:
                    read_results_flag = False
                elif read_results_flag:
                    json_string += line.rstrip()
        try:
            self.result = json.loads(json_string)['rhealstone_result']
        except Exception as e:
            print('JSON Printing')
            print(e)


def calculate_variant(variant_results):
    measure_usecs = float(variant_results['variant_use']['measure_usecs']) - \
                    float(variant_results['variant_no_use']['measure_usecs'])
    return 1.0/(measure_usecs/1000)

def calculate_less_task_switching(result, task_switching):
    measure_usecs = float(result['measure_usecs']) - \
                    float(task_switching['measure_usecs'])
    return 1.0/(measure_usecs/1000)

def calculate_rhealstone(component_measurements):
    """
    In order to combine the six results into a single meaningful
    figure, express all times in seconds and invert them
    arithmetically. There are two related reasons for expressing
    Rhealstone components in terms of frequency per
    second.
     - Performance becomes directly proportional to value
     -- the bigger the number, the better the performance.
     - The Rhealstone metric is then consistent with other industry
       benchmarks such as Whetstones and Dhrystones.

    Expected to recieve a dicionary of rhealstone measurements
    key: rhealstone component name
    value: rhealstone measurment results

    """
    calculations = {}
    # Straight forward calculations
    switching_time = 1.0/(float(component_measurements['switching'].result['measure_usecs'])/1000)
    interrupt_latency = 1.0/(float(component_measurements['interrupt'].result['measure_usecs'])/1000)
    # These aren't as straight forward
    deadlock_result = {'variant_use':component_measurements['deadlk_test'].result,
                        'variant_no_use':component_measurements['deadlk_base'].result}
    semaphore_shuffle_result = {'variant_use':component_measurements['sem_test'].result,
                                 'variant_no_use':component_measurements['sem_base'].result}
    deadlock_break = calculate_variant(deadlock_result)
    semaphore_shuffle = calculate_variant(semaphore_shuffle_result)
    preemption = calculate_less_task_switching(component_measurements['preempt'].result,
                                               component_measurements['switching'].result)
    intertask_latency = calculate_less_task_switching(component_measurements['intertask'].result,
                                                      component_measurements['switching'].result)
    rhealstone = switching_time + interrupt_latency + deadlock_break + semaphore_shuffle + preemption + intertask_latency

    calculations['Task Switching'] = switching_time
    calculations['Interrupt Latency'] = interrupt_latency
    calculations['Deadlock Break'] = deadlock_break
    calculations['Semaphore Shuffle'] = semaphore_shuffle
    calculations['Preemption'] = preemption
    calculations['Intertask Latency'] = intertask_latency
    calculations['Rhealstone'] = rhealstone

    return calculations

def report_print(measurements, calculations):
    separator = "="*(20+2)
    separator += "|"
    separator += "="*(20+2)
    for policy in measurements.keys():
        if measurements[policy] is not None:
            print(' {:^45}'.format("Policy: {}".format(policy)))
            print(' {:^20} | {:^20} '.format("Test", "Rhealstone Score"))
            print(separator)
            print(' {:^20} | {:^20} '.format("Task Switch", calculations[policy]['Task Switching']))
            print(' {:^20} | {:^20} '.format("Inter-task", calculations[policy]['Intertask Latency']))
            print(' {:^20} | {:^20} '.format("Interrupt", calculations[policy]['Interrupt Latency']))
            print(' {:^20} | {:^20} '.format("Deadlock", calculations[policy]['Deadlock Break']))
            print(' {:^20} | {:^20} '.format("Semaphore", calculations[policy]['Semaphore Shuffle']))
            print(' {:^20} | {:^20} '.format("Preemption", calculations[policy]['Preemption']))
            print(separator)
            print(' {:^20} | {:^20} '.format("Rhealstone", calculations[policy]['Rhealstone']))
            print('')

def report_plot(measurements, calculations):

    fig, (ax_meas, ax_rheal) = plt.subplots(nrows=1, ncols=2)
    policy_names = [name for name in list(calculations.keys()) if calculations[name] is not None]
    first_component_name = policy_names[0]
    calculation_component_names = list(calculations[first_component_name].keys())
    # Ensure Rhealstone is at end and the rest are sorted
    calculation_component_names.pop(calculation_component_names.index('Rhealstone'))
    calculation_component_names.sort()
    n_groups = len(calculation_component_names)         # number rhealstone components
    component_x = np.arange(n_groups)                   # x locations for the groups
    bar_width = 0.35

    policy_bars = []

    for (p_indx,policy) in enumerate(policy_names):
        offset = bar_width/len(policy_names)
        if (p_indx) <  len(policy_names)/2:
            offset *= -1
        print("policy: {} ({}), offset:{}".format(policy, p_indx, offset))
        # pdb.set_trace()
        calculations_for_policy = []
        for component in calculation_component_names:
            calculations_for_policy.append(calculations[policy][component])
        policy_bars.append(ax_meas.bar(x=component_x+offset,
                                       height=calculations_for_policy,
                                       width=bar_width,
                                       label=policy))
    ax_meas.set_ylabel('Rhealstones per Second')
    ax_meas.set_title('Unweighted Rhealstone Measurement Results')
    ax_meas.set_xticks(component_x)
    ax_meas.set_xticklabels(calculation_component_names)
    ax_meas.xaxis.set_tick_params(rotation=45)
    ax_meas.legend(policy_names)

    n_policy_names = len(policy_names)
    policy_x = np.arange(n_policy_names)
    p_bar_width = 0.35

    rhealstone_bars = []
    rhealstones_y = []

    for p in policy_names:
        rhealstones_y.append(calculations[p]['Rhealstone'])
    ax_rheal.bar(x=policy_x, height=rhealstones_y, width=p_bar_width)
    ax_rheal.set_ylabel('Rhealstones per Second')
    ax_rheal.set_title('Rhealstone Calculations')
    ax_rheal.set_xticks(policy_x)
    ax_rheal.set_xticklabels(policy_names)

    plt.tight_layout()
    plt.show()


def main(component_names, policies):
    """
    The main data to pass around is a dictionary where the top level key
    is the policy, which is paired with another dictionary of rhealstone components
    that have the results and meta data contained in a RhealstoneComponent object
    *- policy:none
    |  |- switching -> RhealstoneComponent
    |  |- [..]
    |  |- interrupt_latency -> RhealstoneComponent
    *- policy: rwx
    |  |- switching -> RhealstoneComponent
    |  |- [..]
    |  |- interrupt_latency -> RhealstoneComponent
    """
    rhealstone_measurements = {}
    rhealstone_calculation = {}
    for policy in policies:
        rhealstone_measurements[policy] = {}
        try:
            for component_name in component_names:
                rhealstone_measurements[policy][component_name] = RhealstoneComponent(name=component_name, policy=policy)
                rhealstone_measurements[policy][component_name].parse_measurements()
            rhealstone_calculation[policy] = calculate_rhealstone(rhealstone_measurements[policy])
        except:
            print('Could Not Parse measurements for policy: {}'.format(policy))
            rhealstone_measurements[policy] = None
            rhealstone_calculation[policy] = None
    report_print(rhealstone_measurements, rhealstone_calculation)
    report_plot(rhealstone_measurements, rhealstone_calculation)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--policies", nargs="+",
                        help="Comma separated list of policies")
    parser.add_argument("-c", "--components", nargs="+",
                        help="Rhealstone Components to parse. If none chosen, all 8 will be searched for")
    args = parser.parse_args()
    components = []
    if args.components:
        components = args.components
    else:
        components = rhealstone_component_names
    pdb.set_trace()
    print(args.policies)
    main(component_names=components, policies=args.policies[0].split(','))
