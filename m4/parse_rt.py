#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Develop VRF configuration parsers for IOS-XE and IOS-XR.
These are focused on route-targets and not general-purpose VRF fields.
"""

import re


def parse_rt_ios(text):
    """
    Parses blocks of VRF text into indexable dictionary entries. This
    typically feeds into the rt_diff function to be tested against the
    intended config.
    """
    vrf_list = ["vrf" + s for s in text.strip().split("vrf") if s]
    return_dict = {}
    for vrf in vrf_list:
        # Parse the VRF name from the definition line
        name_regex = re.compile(r"vrf\s+definition\s+(?P<name>\S+)")
        name_match = name_regex.search(vrf)
        sub_dict = {}
        vrf_dict = {name_match.group("name"): sub_dict}

        # Parse the RT imports into a list of strings
        rti_regex = re.compile(r"route-target\s+import\s+(?P<rti>\d+:\d+)")
        rti_matches = rti_regex.findall(vrf)
        sub_dict.update({"route_import": rti_matches})

        # Parse the RT exports into a list of strings
        rte_regex = re.compile(r"route-target\s+export\s+(?P<rte>\d+:\d+)")
        rte_matches = rte_regex.findall(vrf)
        sub_dict.update({"route_export": rte_matches})

        # Append dictionary to return list
        return_dict.update(vrf_dict)

    return return_dict


def parse_rt_iosxr(text):
    """
    Parses blocks of VRF text into indexable dictionary entries. This
    typically feeds into the rt_diff function to be tested against the
    intended config.
    """
    vrf_list = ["vrf" + s for s in text.strip().split("vrf") if s]
    return_dict = {}
    for vrf in vrf_list:
        # Parse the VRF name from the definition line
        name_regex = re.compile(r"^vrf\s+(?P<name>\S+)")
        name_match = name_regex.search(vrf)
        sub_dict = {}
        vrf_dict = {name_match.group("name"): sub_dict}

        rti_regex = re.compile(r"import\s+route-target(.+?)!", re.DOTALL)
        rti_matches = rti_regex.findall(vrf, re.DOTALL)
        if rti_matches:
            rti_list = [s.strip() for s in rti_matches[0].strip().split("\n")]
        else:
            rti_list = []
        sub_dict.update({"route_import": rti_list})

        rte_regex = re.compile(r"export\s+route-target(.+?)!", re.DOTALL)
        rte_matches = rte_regex.findall(vrf, re.DOTALL)
        if rte_matches:
            rte_list = [s.strip() for s in rte_matches[0].strip().split("\n")]
        else:
            rte_list = []
        sub_dict.update({"route_export": rte_list})

        # Append dictionary to return list
        return_dict.update(vrf_dict)

    return return_dict
