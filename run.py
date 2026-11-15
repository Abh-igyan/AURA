#!/usr/bin/env python3
"""
AURA Launch Script
Runs the Streamlit dashboard locally.
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    app_path = Path(__file__).parent / "app.py"
    print("=" * 60)
    print("🚀 Launching AURA: Autonomous Flight Surgeon Dashboard")
    print("   NASA Space Apps Challenge 2026 Prototype")
    print(f"   Target: {app_path}")
    print("=" * 60)
    
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[+] AURA Cockpit terminated cleanly.")

if __name__ == "__main__":
    main()
