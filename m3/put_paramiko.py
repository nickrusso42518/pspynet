#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using SSH via paramiko to configure network devices.
"""

import time
import yaml
import paramiko
from jinja2 import Environment, FileSystemLoader


def send_cmd(conn, command):
    """
    Given an open connection and a command, issue the command and wait
    500 ms for the command to be processed.
    """
    output = conn.send(command + "\n")
    time.sleep(0.5)
    return output


def get_output(conn):
    """
    Given an open connection, read all the data from the buffer and
    decode the byte string as UTF-8.
    """
    return conn.recv(65535).decode("utf-8")


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
            f"templates/paramiko/{host['platform']}_vpn.j2"
        )
        new_vrf_config = template.render(data=vrfs)

        conn_params = paramiko.SSHClient()
        conn_params.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn_params.connect(
            hostname=host["name"],
            port=22,
            username="pyuser",
            password="pypass",
            look_for_keys=False,
            allow_agent=False,
        )

        conn = conn_params.invoke_shell()
        time.sleep(0.5)  # need for XRv, prompt is slow

        print(f"Logged into {get_output(conn).strip()} successfully")

        send_cmd(conn, new_vrf_config)

        commands = [
            "terminal length 0",
            "show version | include Software,",
            host["vrf_cmd"],
        ]
        for command in commands:
            send_cmd(conn, command)
            print(get_output(conn))


if __name__ == "__main__":
    main()
