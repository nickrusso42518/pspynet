#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using SSH via netmiko to configure network devices.
"""

import yaml
from netmiko import Netmiko
from jinja2 import Environment, FileSystemLoader


def main():
    """
    Execution starts here.
    """

    host_list = [
        {
            "name": "csr",
            "vrf_cmd": "show running-config | section vrf_def",
            "platform": "cisco_ios",
        },
        {
            "name": "xrv",
            "vrf_cmd": "show running-config vrf",
            "platform": "cisco_xr",
        },
    ]

    for host in host_list:
        with open(f"vars/{host['name']}_vrfs.yml", "r") as handle:
            try:
                vrfs = yaml.safe_load(handle)
            except yaml.YAMLError as exc:
                print(exc)

        j2_env = Environment(
            loader=FileSystemLoader("."), trim_blocks=True, autoescape=True
        )
        template = j2_env.get_template(
            f"templates/netmiko/{host['platform']}_vpn.j2"
        )
        new_vrf_config = template.render(data=vrfs)

        net_connect = Netmiko(
            host=host["name"],
            username="pyuser",
            password="pypass",
            device_type=host["platform"],
        )

        print(f"Logged into {net_connect.find_prompt()} successfully")

        print(new_vrf_config.split("\n"))
        result = net_connect.send_config_set(new_vrf_config.split("\n"))
        print(result)

        # term len 0 is automatic
        commands = ["show version | include Software,", host["vrf_cmd"]]
        for command in commands:
            output = net_connect.send_command(command)
            print(output)

        net_connect.disconnect()


if __name__ == "__main__":
    main()
