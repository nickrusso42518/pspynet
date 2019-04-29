#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using NAPALM via SSH to interact with multiple
platforms to collect structured data.
"""

from pprint import pprint
from napalm import get_network_driver
from parse_rt import parse_rt_ios, parse_rt_iosxr


def get_rt_parser(platform):
    """
    Selects the proper parsing function based on the specific platform.
    Note it does not call the function, just returns it for calling later.
    """
    if platform.lower() == "ios":
        return parse_rt_ios
    if platform.lower() == "iosxr":
        return parse_rt_iosxr

    raise ValueError(platform)


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
        # {
        # "name": "xrv",
        # "vrf_cmd": "show running-config vrf",
        # "platform": "iosxr",
        # },
    ]
    for host in host_list:
        print(f"Getting {host['platform']} driver")
        driver = get_network_driver(host["platform"])
        device = driver(
            hostname=host["name"], username="pyuser", password="pypass"
        )
        print("Opening device")
        device.open()
        facts = device.get_facts()
        # print(facts)
        print(f"{host['name']} model type: {facts['model']}")

        output = device.cli([host["vrf_cmd"]])
        # pprint(output)

        parse_rt = get_rt_parser(host["platform"])
        vrf_data = parse_rt(output[host["vrf_cmd"]])
        pprint(vrf_data)

        # merge config
        device.load_merge_candidate(
            config="hostname test\nno interface Ethernet2\ndescription bla"
        )
        print(device.compare_config())
        # device.commit_config()
        # device.discard_config()

        device.close()


if __name__ == "__main__":
    main()
