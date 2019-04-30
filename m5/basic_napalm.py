#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using NAPALM via SSH to interact with multiple
platforms to collect structured data.
"""

from napalm import get_network_driver
from jinja2 import Environment, FileSystemLoader
from yaml import safe_load


def main():
    """
    Execution starts here.
    """

    host_list = [
        {
            "name": "csr",
            "vrf_cmd": "show running-config | section vrf_def",
            "platform": "ios",
        },
        {
            "name": "xrv",
            "vrf_cmd": "show running-config vrf",
            "platform": "iosxr",
        },
    ]

    # Iterate over the list of hosts (dicts) defined above
    for host in host_list:

        # Determine and create the network driver object based on platform
        print(f"Getting {host['platform']} driver")
        driver = get_network_driver(host["platform"])
        device = driver(
            hostname=host["name"], username="pyuser", password="pypass"
        )

        # Open the connection and get the model ID
        print("Opening device and fathering facts")
        device.open()
        facts = device.get_facts()
        print(f"{host['name']} model type: {facts['model']}")

        # Read the YAML file into structured data, may raise YAMLError
        with open(f"vars/{host['name']}_vrfs.yml", "r") as handle:
            vrfs = safe_load(handle)

        # Template the configuration changes based on the RT updates
        j2_env = Environment(
            loader=FileSystemLoader("."), trim_blocks=True, autoescape=True
        )
        template = j2_env.get_template(
            f"templates/basic/{host['platform']}_vpn.j2"
        )
        new_vrf_config = template.render(data=vrfs["vrfs"])

        # Use NAPALM built-in merging to compare and merge RT updates
        # Note that dynamically removing configuration is still a challenge
        # unless NAPALM is explicitly told ...
        device.load_merge_candidate(config=new_vrf_config)
        diff = device.compare_config()
        if diff:
            print(diff)
            print("Committing configuration changes")
            device.commit_config()
        else:
            print("no diff; config up to date")

        # All done; close the connection
        device.close()
        print("OK!")


if __name__ == "__main__":
    main()
