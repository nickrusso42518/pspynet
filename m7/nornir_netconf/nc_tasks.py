#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Collection of Nornir-oriented tasks that wrap existing
ncclient methods. This mimics the look and feel of Netmiko/NAPALM
methods for consistency.
"""


from nornir.core.task import Result
from lxml.etree import fromstring


def netconf_custom_rpc(task, rpc_text, **kwargs):
    """
    Nornir task to issue a custom NETCONF RPC given an XML-formatted string
    and additional keyword arguments.
    """

    conn = task.host.get_connection("netconf", task.nornir.config)
    result = conn.dispatch(fromstring(rpc_text), **kwargs)
    return Result(host=task.host, result=result)


def netconf_get(task, **kwargs):
    """
    Nornir task to issue a NETCONF get RPC with optional keyword arguments.
    """

    conn = task.host.get_connection("netconf", task.nornir.config)
    result = conn.get(**kwargs)
    return Result(host=task.host, result=result)


def netconf_get_config(task, source="running", **kwargs):
    """
    Nornir task to issue a NETCONF get_config RPC with optional keyword
    arguments. Assumes the source datastore is "running" by default.
    """

    conn = task.host.get_connection("netconf", task.nornir.config)
    result = conn.get_config(source=source, **kwargs)
    return Result(host=task.host, result=result)
