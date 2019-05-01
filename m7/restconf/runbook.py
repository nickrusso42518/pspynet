#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate using Nornir with IOS-XE RESTCONF API
for infrastructure as code. This is a very modern approach.
"""

import logging
import requests
from nornir import InitNornir
from nornir.plugins.tasks.apis import http_method
from nornir.plugins.functions.text import print_result


def manage_rt(task):
    """
    This is a grouped task that runs once per host. This
    iteration happens inside nornir automatically. Anytime
    'task.run()' is invoked, a new result is automatically added to
    the MultiResult assembled on a per-host basis. If the grouped
    task returns anything, that object is stored in MultiResult[0]
    and all subsequent results are stored thereafter.
    """

    base_url = f"https://{task.host.hostname}/restconf/"
    vrf_target = "data/Cisco-IOS-XE-native:native/Cisco-IOS-XE-native:vrf"
    get_headers = {"Accept": "application/yang-data+json"}

    print("Retrieving VRF config ... ")
    get_config_result = task.run(
        task=http_method,
        method="get",
        url=base_url + vrf_target,
        auth=("pyuser", "pypass"),
        headers=get_headers,
        verify=False,
    )
    print(get_config_result[0].result)

    print("Updating VRF config ... ", end="")
    put_post_headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json, application/yang-data.errors+json",
    }
    task.run(
        task=http_method,
        method="put",
        url=base_url + vrf_target,
        auth=("pyuser", "pypass"),
        headers=put_post_headers,
        verify=False,
        json=task.host["body"],
    )
    print("OK!")

    print("Saving running config ... ", end="")
    task.run(
        task=http_method,
        method="post",
        url=base_url + "operations/cisco-ia:save-config",
        auth=("pyuser", "pypass"),
        headers=put_post_headers,
        verify=False,
    )
    print("OK!")


def main():
    """
    Execution begins here.
    """

    # Disable SSL warnings in a test environment
    # This is the only reason we had to import "requests"
    requests.packages.urllib3.disable_warnings()

    # Initialize nornir and invoke the grouped task.
    nornir = InitNornir()
    result = nornir.run(task=manage_rt)

    # Use Nornir-supplied function to pretty-print the result
    # to see a recap of all actions taken. Standard Python logging
    # levels are supported to set output verbosity.
    print_result(result, severity_level=logging.WARNING)


if __name__ == "__main__":
    main()
