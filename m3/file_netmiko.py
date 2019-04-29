#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate SCP file transfer using Netmiko.
"""

import sys
import os
from netmiko import Netmiko, file_transfer


def main(argv):
    """
    Execution starts here.
    """

    # Ensure the file exists before doing anything else
    if not os.path.isfile(argv[1]):
        raise FileNotFoundError(argv[1])

    # Define list of hosts. Notice that "xrv" has a "file_system" key that
    # "csr" does not. Netmiko can sometimes auto-discover file sytems.
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
            "file_system": "disk0:",
        },
    ]

    # Iterate over the list of hosts (list of dictionaries)
    for host in host_list:

        # Initialize the SSH connection
        print(f"Connecting to {host['name']}")
        net_connect = Netmiko(
            host=host["name"],
            username="pyuser",
            password="pypass",
            device_type=host["platform"],
        )

        # Upload the file specified
        print(f"  Uploading {argv[1]} ... ", end="")
        result = file_transfer(
            net_connect,
            source_file=argv[1],
            dest_file=argv[1],
            file_system=host.get("file_system"),
        )

        # Print the resulting details
        print("OK!")
        print(f"  Details: {result}")


if __name__ == "__main__":
    main(sys.argv)
