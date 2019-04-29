#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using SSH via paramiko to get information from
the network and write it to a file for future reference.
"""

import time
import paramiko


def send_cmd(conn, command):
    """
    Given an open connection and a command, issue the command and wait
    500 ms for the command to be processed.
    """
    conn.send(command + "\n")
    time.sleep(0.5)


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

    host_dict = {
        "csr": "show running-config | section vrf_definition",
        "xrv": "show running-config vrf",
    }
    for hostname, vrf_cmd in host_dict.items():
        conn_params = paramiko.SSHClient()
        conn_params.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn_params.connect(
            hostname=hostname,
            port=22,
            username="pyuser",
            password="pypass",
            look_for_keys=False,
            allow_agent=False,
        )

        conn = conn_params.invoke_shell()
        time.sleep(0.5)  # need for XRv, prompt is slow

        print(f"Logged into {get_output(conn).strip()} successfully")

        commands = [
            "terminal length 0",
            "show version | include Software,",
            vrf_cmd,
        ]

        concat_output = ""
        for command in commands:
            send_cmd(conn, command)
            concat_output += get_output(conn)

        with open(f"{hostname}.txt", "w") as handle:
            handle.write(concat_output)


if __name__ == "__main__":
    main()
