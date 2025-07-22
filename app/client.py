import ntplib
import time
from datetime import datetime
from .config import NTP_DOMAIN_URL

def get_current_time(ntp_server=None):
    """从NTP服务器获取当前时间"""
    if ntp_server is None or ntp_server.strip() == "":
        ntp_server = NTP_DOMAIN_URL

    # 处理空串和None的情况
    if not ntp_server:
        raise ValueError("NTP server address is not configured. Please set the NTP_DOMAIN_URL environment variable or provide ntp_url in the request header.")

    # 去除首尾空格
    ntp_server = ntp_server.strip()

    try:
        # 创建NTP客户端
        ntp_client = ntplib.NTPClient()

        # 从NTP服务器获取时间
        response = ntp_client.request(ntp_server, version=3, timeout=5)

        # 获取NTP时间戳
        ntp_time = response.tx_time

        # 转换为本地时间
        local_time = datetime.fromtimestamp(ntp_time)

        # 获取本地时间作为对比
        local_system_time = datetime.now()

        return {
            "ntp_server": ntp_server,
            "ntp_timestamp": ntp_time,
            "ntp_time": local_time.isoformat(),
            "local_system_time": local_system_time.isoformat(),
            "time_offset": ntp_time - time.time(),
            "response_delay": response.delay
        }

    except ntplib.NTPException as e:
        raise Exception(f"NTP Request Failed (NTPException): {str(e)}")
    except Exception as e:
        raise Exception(f"NTP Request Failed (Other Error): {str(e)}")
