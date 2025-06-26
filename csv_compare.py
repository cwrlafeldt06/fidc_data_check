#!/usr/bin/env python3
"""
Convenience wrapper for cli/csv_compare_cli.py
"""
import sys
import subprocess
from pathlib import Path

if __name__ == "__main__":
    script_path = Path(__file__).parent / "cli" / "csv_compare_cli.py"
    
    # Forward all arguments to the actual script
    cmd = [sys.executable, str(script_path)] + sys.argv[1:]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode) 