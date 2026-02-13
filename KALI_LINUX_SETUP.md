# ReconX Enterprise ASM - Kali Linux Installation Guide

## Quick Setup (One Command)

```bash
bash kali_setup.sh
```

This script will:
- ✓ Update system packages
- ✓ Install all system dependencies (nmap, nikto, dnsutils, etc.)
- ✓ Create Python virtual environment
- ✓ Install all Python packages
- ✓ Verify all dependencies
- ✓ Create helper scripts for running the server
- ✓ Generate status check and stop scripts

## What Gets Installed

### System Tools
- nmap, nikto, masscan, sqlmap
- whois, dnsutils, net-tools
- git, curl, wget, tmux, screen
- Build essentials (gcc, make, etc.)

### Python Packages (from requirements.txt)
- FastAPI 0.129.0
- Uvicorn 0.40.0
- SQLAlchemy 2.0.46
- Pydantic 2.12.5
- NetworkX, Requests, PyYAML
- pytest, pytest-asyncio
- And 30+ more dependencies

## Manual Installation Steps

If the script doesn't work, follow these manual steps:

### Step 1: Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 2: Install Python & Git
```bash
sudo apt-get install -y python3 python3-pip python3-venv python3-dev build-essential git
```

### Step 3: Install Scanning Tools
```bash
sudo apt-get install -y nmap nikto masscan whois dnsutils net-tools netcat
```

### Step 4: Setup Project
```bash
git clone -b db_setup --single-branch https://github.com/thompson005/kali-ASM.git kali-linux-asm
cd kali-linux-asm
python3 -m venv .venv
source .venv/bin/activate
```

### Step 5: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Verify Installation
```bash
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
```

Access at: `http://localhost:8000`

## Starting the Server (3 Options)

### Option 1: Interactive (Stop with Ctrl+C)
```bash
bash start_server.sh
```

### Option 2: Background (Survives SSH disconnect)
```bash
bash start_server_bg.sh
```

Check logs:
```bash
tail -f server.log
```

Stop it:
```bash
bash stop_server.sh
```

### Option 3: Persistent tmux Session (Recommended)
```bash
bash start_server_tmux.sh
```

Reattach later:
```bash
tmux attach-session -t reconx
```

## Useful Commands

### Check Server Status
```bash
bash check_status.sh
```

### View Active Processes
```bash
ps aux | grep uvicorn
```

### Check Port 8000
```bash
lsof -i :8000
```

### Kill Process on Port 8000
```bash
lsof -ti:8000 | xargs kill -9
```

## Troubleshooting

### Python Not Found
```bash
sudo apt-get install python3 python3-pip python3-venv
```

### nmap/nikto Not Found
```bash
sudo apt-get install nmap nikto
```

### Port 8000 Already in Use
```bash
lsof -ti:8000 | xargs kill -9
```

### Permission Denied on Script
```bash
chmod +x kali_setup.sh start_server.sh start_server_bg.sh start_server_tmux.sh check_status.sh stop_server.sh
```

### Virtual Environment Corrupted
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Accessing the Application

**URL**: `http://localhost:8000`

**Dashboard**: See real-time scan results, findings, and compliance data
**Assessments**: Browse vulnerability assessment results
**Reports**: Generate and export CSV reports
**Compliance**: View OWASP, CIS, NIST compliance scores
**Alerts**: Real-time vulnerability alerts
**Settings**: Configure scan parameters and API keys

## Support

For issues, check:
1. `server.log` - Application logs
2. `bash check_status.sh` - Server health
3. `bash stop_server.sh` && `bash start_server_tmux.sh` - Restart server

---

**Create Date**: February 13, 2026  
**Compatible**: Kali Linux | Debian | Ubuntu  
**Python**: 3.11+  
**License**: See LICENSE file
