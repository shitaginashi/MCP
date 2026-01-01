import shutil
import time
import subprocess
import argparse
import json
import os
import yaml
from datetime import datetime, timedelta

def get_vitals():
    try:
        # Load Average
        with open('/proc/loadavg', 'r') as f:
            load = f.read().split()[:3]
        
        # CPU Temp
        with open('/sys/class/hwmon/hwmon0/temp2_input', 'r') as f:
            temp_c = int(f.read().strip()) // 1000
            
        # Disk Space (The 1TB Library)
        total, used, free = shutil.disk_usage("/")
        
        # Sentinel Check
        is_busy = subprocess.call(['pgrep', '-f', 'agent_mark2_venv'], stdout=subprocess.DEVNULL) == 0
        
        vitals = {
            "temp": f"{temp_c}°C",
            "load": load,
            "disk": {
                "total": f"{total // (2**30)}GB",
                "used": f"{used // (2**30)}GB",
                "free": f"{free // (2**30)}GB",
                "percent": f"{(used/total)*100:.1f}%"
            },
            "scout_active": is_busy
        }
        print(json.dumps(vitals, indent=4))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

def prime_wol():
    """Ensures the NIC is listening for the Magic Packet."""
    os.system("sudo ethtool -s $(ip route | grep default | awk '{print $5}') wol g")

def initiate_nap(seconds, force=False):
    # 1. Sentinel Safety Check
    is_busy = subprocess.call(['pgrep', '-f', 'agent_mark2_venv'], stdout=subprocess.DEVNULL) == 0
    
    if is_busy and not force:
        print(json.dumps({"status": "rejected", "reason": "Scout active in .venv. Use --force to override."}))
        return

    # 2. Persistence (The Scrolls)
    wake_time = datetime.now() + timedelta(seconds=seconds)
    log_entry = {
        'event': 'sleep',
        'timestamp': datetime.now().isoformat(),
        'intended_wake': wake_time.isoformat(),
        'duration_seconds': seconds
    }
    
    log_path = os.path.expanduser("~/data/power_history.yml")
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a') as f:
            yaml.dump([log_entry], f, default_flow_style=False)
    except Exception as e:
        # Don't let a log failure stop the shutdown, but report it
        pass

    # 3. Hardware Handshake
    print(json.dumps({
        "status": "initiating", 
        "cooldown": "300s", 
        "wake_at": wake_time.strftime('%Y-%m-%d %H:%M:%S')
    }))
    
    prime_wol()
    os.system("sudo hwclock --systohc") # Sync hardware clock to prevent drift
    os.system(f"sudo rtcwake -m no -s {seconds}")
    
    # 4. Thermal Cooldown
    time.sleep(300)
    
    # 5. Final Kill
    os.system("sudo shutdown -h now")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kuro's Echo Interface")
    parser.add_argument('--vitals', action='store_true', help="Get hardware health (JSON)")
    parser.add_argument('--nap', type=int, help="Seconds until next wake-up")
    parser.add_argument('--force', action='store_true', help="Force nap even if busy")
    
    args = parser.parse_args()

    if args.vitals:
        get_vitals()
    elif args.nap is not None:
        initiate_nap(args.nap, args.force)
    else:
        # If no flags, you could call your library reader here
        # echo_library()
        parser.print_help()