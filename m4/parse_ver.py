#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Develop software version ID parsers for IOS-XE and IOS-XR.
One generic parser can easily cover both versions. These are focused
on just the version ID and not general information.
"""

import re


def parse_ver(text):
    """
    Parses the software version from IOS XE and IOS XR platforms and returns
    a dictionary with the "version" key and a string value of the version ID.
    """

    # Define the regex first using a raw string. Matches both "XE" and "XR"
    # using a character class. Captures the version into a dictionary with
    # a key named "version" for easy reference.
    version_regex = re.compile(
        r"Cisco\s+IOS\s+X[ER]\s+Software,\s+Version\s+(?P<version>\S+)"
    )

    # Attempt to match the regex against the specific input.
    version_match = version_regex.search(text)

    # Return just the string value from the match, assuming it succeeded.
    if version_match:
        return version_match.group("version")

    # If there was no match, return None to indicate no match.
    return None
