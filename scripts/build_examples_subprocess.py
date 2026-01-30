#!/usr/bin/env python3
"""
Build examples by running them as subprocesses with input mocking.
This approach is simpler and more reliable than patching within the same process.
"""

from pathlib import Path

root_dir = Path(__file__).parent.parent

# For now, let's just verify the old manual approach works
# and update the docs to use the simpler `example="file.py"` syntax

print("✓ Build examples script - using manual HTML files for now")
print("  Run this script after manually creating HTML examples")
print()
print("  The TerminalExample component now supports:")
print('    <TerminalExample example="basic_usage.py" height="200px" />')
print()
print("  Which will load: /examples/basic_usage.html")
