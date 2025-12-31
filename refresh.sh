#!/bin/bash

# 1. Enter the environment
source ~/agent_mark2_venv/bin/activate

echo "--- DOMINA SYNC INITIALIZED ---"

# 2. Project Audits (Sage/Core-Ledger)
# Add any new projects here as they are created
echo "[1/3] Auditing Projects..."
python3 ~/agents/ledger.py --project painter
python3 ~/agents/ledger.py --project ledger

# 3. Quarterly Integrity Check (Cerberus)
echo "[2/3] Checking Schedule Integrity..."
# Cerberus runs internally within Painter, but we can trigger 
# a standalone health check here if needed in the future.

# 4. Interface Refresh
echo "[3/3] Restarting Painter UI..."
# Find and kill existing painter process to free the port
pkill -f painter.py
nohup python3 ~/agents/painter.py > /dev/null 2>&1 &

echo "--- SYNC COMPLETE: Dashboard Live at Port 5000 ---"
