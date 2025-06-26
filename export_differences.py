#!/usr/bin/env python3
"""
Convenience wrapper for scripts/export_differences.py
"""
import sys
import subprocess
from pathlib import Path

if __name__ == "__main__":
    script_path = Path(__file__).parent / "scripts" / "export_differences.py"
    
    # Forward all arguments to the actual script
    cmd = [sys.executable, str(script_path)] + sys.argv[1:]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode) 