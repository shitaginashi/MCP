import os
import socket
import platform
import time

def heartbeat():
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)
    uptime = os.popen('uptime -p').read().strip()
    
    print(f"--- Mark 2 Agent Reporting ---")
    print(f"Status: OPERATIONAL")
    print(f"Host: {hostname} ({ip_addr})")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Uptime: {uptime}")
    print(f"------------------------------")

if __name__ == "__main__":
    while True:
        heartbeat()
        # Sleep for 60 seconds so we don't spam the console
        time.sleep(60)