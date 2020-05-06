#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate NETCONF on IOS-XE and IOS-XR coupled
with Nornir to collect and store VRF configuration to disk.
"""

from nornir import InitNornir
from nornir.plugins.tasks.data import load_yaml
from nornir.plugins.tasks.text import template_file
from nc_tasks import netconf_edit_config, netconf_commit, netconf_custom_rpc


def manage_config(task):
    """
    Custom task to wrap complex infra-as-code steps:
      1. Load vars from YAML file
      2. Render jinja2 template to get XML text
      3. Send NETCONF edit_config RPC to perform updates
      4. Save configuration to non-volatile memory
    """

    vars_file = f"vars/{task.host.name}_vrfs.yaml"
    task1_result = task.run(task=load_yaml, file=vars_file)
    vrfs = task1_result[0].result

    path = "templates"
    template = f"{task.host.platform}_vpn.j2"
    task2_result = task.run(
        task=template_file, path=path, template=template, data=vrfs["vrfs"]
    )

    new_vrf_config = task2_result[0].result
    task3_result = task.run(
        task=netconf_edit_config,
        target=task.host["edit_target"],
        config=new_vrf_config,
        default_operation=task.host.get("operation"),
    )
    config_resp = task3_result[0].result

    if config_resp.ok:
        if task.host.platform == "iosxr":
            task4_result = task.run(task=netconf_commit)
        elif task.host.platform == "ios":
            rpc_text = '<save-config xmlns="http://cisco.com/yang/cisco-ia"/>'
            task4_result = task.run(task=netconf_custom_rpc, rpc_text=rpc_text)

        if task4_result[0].result.ok:
            print(f"{task.host.name}: VRFs successfully updated")

    else:
        print(f"{task.host.name}: Errors: {','.join(config_resp.errors)}")


def main():
    """
    Execution begins here.
    """

    # Initialize Nornir and run the manage_config custom task
    nornir = InitNornir()
    nornir.run(task=manage_config)


if __name__ == "__main__":
    main()
