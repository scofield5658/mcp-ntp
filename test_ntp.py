#!/usr/bin/env python3
"""测试NTP客户端功能"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.client import get_current_time

def test_ntp_client():
    """测试NTP客户端功能"""
    print("Testing NTP client functionality...")

    # 测试1: 使用默认NTP服务器
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

    # 测试2: 使用自定义NTP服务器
    try:
        result = get_current_time("ntp.aliyun.com")
        print("✓ Custom NTP server test successful")
        print(f"  NTP server: {result['ntp_server']}")
        print(f"  NTP time: {result['ntp_time']}")
    except Exception as e:
        print(f"✗ Custom NTP server test failed: {e}")

    print()

    # 测试3: 测试None处理
    try:
        result = get_current_time(None)
        print("✓ None value test successful, using default server")
    except Exception as e:
        print(f"✗ None value test failed: {e}")

    print()

    # 测试4: 测试只包含空格的字符串
    try:
        result = get_current_time("   ")
        print("✓ Space string test successful, using default server")
    except Exception as e:
        print(f"✗ Space string test encountered unexpected error: {e}")

if __name__ == "__main__":
    test_ntp_client()
