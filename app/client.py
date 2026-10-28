import ntplib
import time
from datetime import datetime
from .config import NTP_DOMAIN_URL

def get_current_time(ntp_server=None):
    """Fetch the current time from an NTP server."""
    if ntp_server is None or ntp_server.strip() == "":
        ntp_server = NTP_DOMAIN_URL

    # Treat empty / whitespace-only values as unset
    if not ntp_server:
        raise ValueError("NTP server address is not configured. Please set the NTP_DOMAIN_URL environment variable or provide ntp_url in the request header.")

    # Normalize whitespace
    ntp_server = ntp_server.strip()

    try:
        # Create NTP client
        ntp_client = ntplib.NTPClient()

        # Query the NTP server
        response = ntp_client.request(ntp_server, version=3, timeout=5)

        # NTP transmit timestamp
        ntp_time = response.tx_time

        # Convert to local wall clock representation
        local_time = datetime.fromtimestamp(ntp_time)

        # Capture local system time for comparison
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
