import os
from dotenv import load_dotenv

load_dotenv()

def get_env(key: str, default=None):
    return os.getenv(key, default)

# NTP服务器配置
NTP_DOMAIN_URL = get_env("NTP_DOMAIN_URL", "cn.ntp.org.cn")
