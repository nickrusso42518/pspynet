#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using Nornir to introduce orchestration and
concurrency, as well as inventory management.
"""

from nornir import InitNornir
from nornir.plugins.tasks.networking import (
    napalm_cli,
    napalm_get,
    napalm_configure,
)
from nornir.plugins.tasks.text import template_file
from nornir.plugins.functions.text import print_result
from parse_rt import get_rt_parser, rt_diff


def manage_rt(task):
    """
    This is a grouped task that runs once per host. This
    iteration happens inside nornir automatically. Anytime
    'task.run()' is invoked, a new result is automatically added to
    the MultiResult assembled on a per-host basis. If the grouped
    task returns anything, that object is stored in MultiResult[0]
    and all subsequent results are stored thereafter.
    """

    # TASK 1: Gather facts using NAPALM to get model ID
    task1_result = task.run(task=napalm_get, getters=["get_facts"])
    model = task1_result[0].result["get_facts"]["model"]
    print(f"{task.host.hostname} model type: {model}")

    # TASK 2: Collect the VRF running configuration
    # Note that using "task=netmiko_send_command" is another option
    task2_result = task.run(task=napalm_cli, commands=[task.host["vrf_cmd"]])
    output = task2_result[0].result[task.host["vrf_cmd"]]

    # Determine the parser and perform parsing. This is a huge advantange
    # of using Nornir ... you can run arbitrary Python code wherever you want!
    parse_rt = get_rt_parser(task.host.platform)
    vrf_data = parse_rt(output)
    rt_updates = rt_diff(task.host["vrfs"], vrf_data)

    # TASK 3: Create the template of config to add
    task3_result = task.run(
        task=template_file,
        template=f"{task.host.platform}_vpn.j2",
        path="templates/",
        data=rt_updates,
    )
    new_vrf_config = task3_result[0].result

    # TASK 4: Configure the devices using NAPALM
    task4_result = task.run(task=napalm_configure, configuration=new_vrf_config)

    if task4_result[0].result:
        print(task4_result[0].result.diff)
    else:
        print("no diff; config up to date")

def main():
    """
    Execution begins here.
    """

    # Initialize nornir and invoke the grouped task.
    nornir = InitNornir()
    result = nornir.run(task=manage_rt)

    # Use Nornir-supplied function to pretty-print the result
    # to see a recap of all actions taken. Standard Python logging
    # levels are supported to set output verbosity.
    print_result(result)


if __name__ == "__main__":
    main()
