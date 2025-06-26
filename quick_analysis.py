#!/usr/bin/env python3
"""
Convenience wrapper for scripts/quick_analysis.py
"""
import sys
import subprocess
from pathlib import Path

if __name__ == "__main__":
    script_path = Path(__file__).parent / "scripts" / "quick_analysis.py"
    
    # Forward all arguments to the actual script
    cmd = [sys.executable, str(script_path)] + sys.argv[1:]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode) 