#!/usr/bin/env python3
"""Manual smoke tests for the NTP client."""

import sys
import os

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.client import get_current_time

def test_ntp_client():
    """Exercise get_current_time against default and custom servers."""
    print("Testing NTP client functionality...")

    # Test 1: default NTP server (from env)
    try:
        result = get_current_time()
        print("✓ Default NTP server test successful")
        print(f"  NTP server: {result['ntp_server']}")
        print(f"  NTP time: {result['ntp_time']}")
        print(f"  Local system time: {result['local_system_time']}")
        print(f"  Time offset: {result['time_offset']:.3f} seconds")
        print(f"  Response delay: {result['response_delay']:.3f} seconds")
    except Exception as e:
        print(f"✗ Default NTP server test failed: {e}")

    print()

    # Test 2: custom NTP server
    try:
        result = get_current_time("pool.ntp.org")
        print("✓ Custom NTP server test successful")
        print(f"  NTP server: {result['ntp_server']}")
        print(f"  NTP time: {result['ntp_time']}")
    except Exception as e:
        print(f"✗ Custom NTP server test failed: {e}")

    print()

    # Test 3: None falls back to default
    try:
        result = get_current_time(None)
        print("✓ None value test successful, using default server")
    except Exception as e:
        print(f"✗ None value test failed: {e}")

    print()

    # Test 4: whitespace-only string falls back to default
    try:
        result = get_current_time("   ")
        print("✓ Space string test successful, using default server")
    except Exception as e:
        print(f"✗ Space string test encountered unexpected error: {e}")

if __name__ == "__main__":
    test_ntp_client()
