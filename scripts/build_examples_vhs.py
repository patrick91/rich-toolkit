#!/usr/bin/env python3
"""
Build examples using VHS (https://github.com/charmbracelet/vhs).

This script generates MP4 videos of terminal demos by running VHS tape files.
The tapes script the interaction with Rich Toolkit examples.

Usage:
    uv run python scripts/build_examples_vhs.py

Requirements:
    - VHS (installed via flake.nix)
    - FFmpeg (installed via flake.nix)
"""

import subprocess
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
tapes_dir = root_dir / "examples" / "tapes"
output_dir = root_dir / "website" / "content" / "examples"


def build_example(tape_file: Path) -> bool:
    """
    Build a single example by running its VHS tape file.

    Args:
        tape_file: Path to the .tape file

    Returns:
        True if successful, False otherwise
    """
    print(f"📹 Recording {tape_file.stem}...")

    try:
        # Run VHS with the tape file
        result = subprocess.run(
            ["vhs", str(tape_file)],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout per example
        )

        if result.returncode != 0:
            print(f"  ❌ Failed to record {tape_file.stem}")
            print(f"  Error: {result.stderr}")
            return False

        # Check if the output file was created
        output_file = output_dir / f"{tape_file.stem}.mp4"
        if output_file.exists():
            size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"  ✅ Created {output_file.name} ({size_mb:.2f} MB)")
            return True
        else:
            print(f"  ❌ Output file not found: {output_file}")
            return False

    except subprocess.TimeoutExpired:
        print(f"  ❌ Timeout recording {tape_file.stem}")
        return False
    except FileNotFoundError:
        print("  ❌ VHS not found. Make sure it's installed:")
        print("     Run: direnv allow  (to load flake.nix)")
        print("     Or install manually: https://github.com/charmbracelet/vhs")
        sys.exit(1)
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def build_all_examples():
    """Build all example videos from tape files."""
    if not tapes_dir.exists():
        print(f"❌ Tapes directory not found: {tapes_dir}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(exist_ok=True, parents=True)

    # Find all tape files
    tape_files = sorted(tapes_dir.glob("*.tape"))

    if not tape_files:
        print(f"❌ No .tape files found in {tapes_dir}")
        sys.exit(1)

    print("🎬 Building example videos with VHS")
    print(f"Tapes directory: {tapes_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Found {len(tape_files)} tape files")
    print()

    # Build each example
    success_count = 0
    for tape_file in tape_files:
        if build_example(tape_file):
            success_count += 1
        print()

    # Summary
    print("━" * 50)
    print(f"✅ Successfully built {success_count}/{len(tape_files)} examples")

    if success_count < len(tape_files):
        sys.exit(1)


if __name__ == "__main__":
    build_all_examples()
