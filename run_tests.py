#!/usr/bin/env python3
"""
Test Runner
Unified entry point for running various tests
"""
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run command and display results"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
        else:
            print(f"❌ {description} - Failed (code: {result.returncode})")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Niu Niu Statistics Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    success_count = 0
    total_count = 0
    
    # Unit tests
    if args.unit or args.all or True:  # Default to unit tests
        unit_tests = [
            (["python3", "tests/test_dice_parser.py"], "Dice Parser Unit Test"),
            (["python3", "tests/test_niu_niu_engine.py"], "Niu Niu Engine Unit Test"),
        ]
        
        print(f"\n🔧 Running unit tests...")
        for cmd, desc in unit_tests:
            total_count += 1
            if run_command(cmd, desc):
                success_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Test Summary")
    print(f"{'='*60}")
    print(f"Total tests: {total_count}")
    print(f"Passed: {success_count}")
    print(f"Failed: {total_count - success_count}")
    print(f"Success rate: {success_count/total_count*100:.1f}%" if total_count > 0 else "No tests run")
    
    if success_count == total_count:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())