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
        print(f"Errors during save: {','.join(save_resp.errors)}")


def main():
    """
    Execution starts here.
    """

    host_list = [
        # {"name": "csr", "platform": "ios"},
        {"name": "xrv", "platform": "iosxr"}
    ]

    # Iterate over the list of hosts (dicts) defined above
    for host in host_list:

        # Read the YAML file into structured data, may raise YAMLError
        with open(f"vars/{host['name']}_vrfs.yml", "r") as handle:
            vrfs = safe_load(handle)

        # Template the configuration changes based on the RT updates
        j2_env = Environment(
            loader=FileSystemLoader("."), trim_blocks=True, autoescape=True
        )
        template = j2_env.get_template(f"templates/{host['platform']}_vpn.j2")
        vrf_config = template.render(data=vrfs["vrfs"])

        # Open a new NETCONF connection to each host
        with manager.connect(
            host=host["name"],
            username="pyuser",
            password="pypass",
            hostkey_verify=False,
        ) as conn:

            # Gather the current configuration and pretty-print it
            get_vrfs_resp = conn.get_config(
                source="running",
                filter=("subtree", "<native><vrf></vrf></native>"),
            )
            print(tostring(get_vrfs_resp.data_ele, pretty_print=True).decode())

            raise ValueError()
            # Apply the new config by replacing the VRF section. This will automatically
            # delete unspecified VRFs and subcomponents like VRFs, etc.
            config_resp = conn.edit_config(target="running", config=vrf_config)
            if config_resp.ok:
                print("VRFs successfully updated")
            else:
                print(f"Errors during update: {','.join(config_resp.errors)}")

            if host["platform"] == "ios":
                save_config_ios(conn)


if __name__ == "__main__":
    main()
