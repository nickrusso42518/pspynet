#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate NETCONF on IOS-XE and IOS-XR to manage
route targets in an infrastructure as code environment.
"""

from jinja2 import Environment, FileSystemLoader
from yaml import safe_load
from ncclient import manager
from lxml.etree import fromstring, tostring


def save_config_ios(conn):
    """
    Save config on Cisco XE is complex
    Sending custom RPCs can be tricky, see link below
    https://github.com/ncclient/ncclient/issues/182
    """
    save_rpc = '<save-config xmlns="http://cisco.com/yang/cisco-ia"/>'
    save_resp = conn.dispatch(fromstring(save_rpc))
    if save_resp.ok:
        print("Config successfully saved")
    else:
        # Print list of errors as a comma-separated list
        print(f"Errors during save: {','.join(save_resp.errors)}")


def main():
    """
    Execution starts here.
    """

    # Read the hosts file into structured data, may raise YAMLError
    with open("hosts.yml", "r") as handle:
        host_root = safe_load(handle)

    # Iterate over the list of hosts (dicts) defined above
    for host in host_root["host_list"]:

        # Read the variables file into structured data, may raise YAMLError
        with open(f"vars/{host['name']}_vrfs.yml", "r") as handle:
            vrfs = safe_load(handle)

        # Template the configuration changes based on the RT updates
        j2_env = Environment(
            loader=FileSystemLoader("."), trim_blocks=True, autoescape=True
        )
        template = j2_env.get_template(f"templates/{host['platform']}_vpn.j2")
        vrf_config = template.render(data=vrfs["vrfs"])

        # Open a new NETCONF connection to each host using kwargs technique
        connect_params = {
            "host": host["name"],
            "username": "pyuser",
            "password": "pypass",
            "hostkey_verify": False,
            "allow_agent": False,
            "look_for_keys": False,
        }

        # Use the dict above as "keyword arguments" to open netconf session
        with manager.connect(**connect_params) as conn:

            # Gather the current configuration and pretty-print it
            get_vrfs_resp = conn.get_config(
                source="running", filter=("subtree", host["filter"])
            )
            print(tostring(get_vrfs_resp.data_ele, pretty_print=True).decode())

            # Apply the new config by replacing the VRF section.
            # This will delete unspecified VRFs and subcomponents like RTs, etc
            config_resp = conn.edit_config(
                target=host["edit_target"],
                config=vrf_config,
                default_operation=host["operation"],
            )

            if config_resp.ok:
                # Save actions differ between platforms
                # IOS-XR updates the candidate config then commits it
                # IOS/IOS-XE updates the running config then copies to startup
                if host["platform"] == "iosxr":
                    conn.commit()
                elif host["platform"] == "ios":
                    save_config_ios(conn)
                print("VRFs successfully updated")
            else:
                # Print list of errors as a comma-separated list
                print(f"Errors during update: {','.join(config_resp.errors)}")


if __name__ == "__main__":
    main()
