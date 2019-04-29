#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: The pytest functions for ensuring software version ID parsers
for IOS-XE and IOS-XR are functional. Run with "-s" to see outputs.
"""

import parse_ver


def test_parse_version_ios():
    """
    Defines unit tests for the Cisco IOS XE version string.
    """

    # Create and display some test data
    version_output = """
        Cisco IOS XE Software, Version 16.09.02
        Cisco IOS Software [Fuji], Virtual XE Software (more_junk)
        Technical Support: http://www.cisco.com/techsupport
        Copyright (c) 1986-2018 by Cisco Systems, Inc.
        Compiled Mon 05-Nov-18 19:26 by mcpre
    """
    print(version_output)

    # Perform parsing, print structured data, and validate
    version_data = parse_ver.parse_ver(version_output)
    print(version_data)
    assert version_data == "16.09.02"


def test_parse_version_iosxr():
    """
    Defines unit tests for the Cisco IOS XR version string.
    """

    # Create and display some test data
    version_output = """
        Cisco IOS XR Software, Version 6.3.1
        Copyright (c) 2013-2017 by Cisco Systems, Inc.
        Build Information:
         Built By     : ahoang
         Built On     : Wed Sep 13 18:30:01 PDT 2017
    """
    print(version_output)

    # Perform parsing, print structured data, and validate
    version_data = parse_ver.parse_ver(version_output)
    print(version_data)
    assert version_data == "6.3.1"
