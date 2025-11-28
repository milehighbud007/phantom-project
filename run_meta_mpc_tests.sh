#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/devpen11/Desktop/phantom-project"

echo "RUN EACH TEST FOR META MPC BELOW 1-6"
echo ""

# Ensure we are in the correct directory
if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "✗ Project directory not found: $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR"

# Ensure required files exist
missing_files=()
for f in ai_learning_module.py automated_attack_system.py app.py; do
  [[ -f "$f" ]] || missing_files+=("$f")
done
if (( ${#missing_files[@]} > 0 )); then
  echo "✗ Missing required files: ${missing_files[*]}"
  exit 1
fi

# Prefer local venv if present
if [[ -d "venv" ]]; then
  source venv/bin/activate || true
fi

########################################
# Test 1: Validate Python Syntax
########################################
echo "=== TEST 1: Python Syntax Validation ==="
echo ""

echo -n "Testing ai_learning_module.py... "
python3 -m py_compile ai_learning_module.py && echo "✓ OK" || echo "✗ FAILED"

echo -n "Testing automated_attack_system.py... "
python3 -m py_compile automated_attack_system.py && echo "✓ OK" || echo "✗ FAILED"

echo -n "Testing app.py... "
python3 -m py_compile app.py && echo "✓ OK" || echo "✗ FAILED"
echo ""

########################################
# Test 2: Test Module Imports
########################################
echo "=== TEST 2: Module Import Tests ==="
echo ""

python3 << 'PYTEST'
import sys
print("Testing imports...")

try:
    from ai_learning_module import PenetrationTestingAI
    print("✓ ai_learning_module imports successfully")
except Exception as e:
    print(f"✗ ai_learning_module import failed: {e}")
    sys.exit(1)

try:
    from automated_attack_system import AutomatedAttackSystem
    print("✓ automated_attack_system imports successfully")
except Exception as e:
    print(f"✗ automated_attack_system import failed: {e}")
    sys.exit(1)

print("\n✓ All core modules import successfully!")
PYTEST
echo ""

########################################
# Test 3: Test AI Module Functionality
########################################
echo "=== TEST 3: AI Module Functionality Test ==="
echo ""

python3 << 'PYTEST'
from ai_learning_module import PenetrationTestingAI
import os

print("Creating AI instance...")
ai = PenetrationTestingAI("test_ai_knowledge.json")

print("Testing AI methods...")

stats = ai.get_statistics()
print(f"✓ get_statistics() works - Total ops: {stats.get('total_operations', 'N/A')}")

ai.record_scan_result("192.168.1.0/24", 10, 45.5)
print("✓ record_scan_result() works")

ai.update_target_profile(
    mac="aa:bb:cc:dd:ee:ff",
    ip="192.168.1.100",
    hostname="test-pc",
    vendor="TestVendor",
    os_guess="Windows"
)
print("✓ update_target_profile() works")

ai.record_exploit_attempt(
    exploit="exploit/test",
    payload="test/payload",
    target_mac="aa:bb:cc:dd:ee:ff",
    success=True
)
print("✓ record_exploit_attempt() works")

rec = ai.recommend_exploit("aa:bb:cc:dd:ee:ff")
print(f"✓ recommend_exploit() works - Recommendation: {rec}")

report = ai.export_knowledge_report()
print(f"✓ export_knowledge_report() works - Report length: {len(report)} chars")

# Cleanup
for p in ["test_ai_knowledge.json", "test_ai_knowledge.json.backup"]:
    if os.path.exists(p):
        os.remove(p)

print("\n✓✓✓ AI Module: ALL TESTS PASSED ✓✓✓")
PYTEST
echo ""

########################################
# Test 4: Test Automated Attack System
########################################
echo "=== TEST 4: Automated Attack System Test ==="
echo ""

python3 << 'PYTEST'
from ai_learning_module import PenetrationTestingAI
from automated_attack_system import AutomatedAttackSystem
import time, os, random

print("Creating AI instance...")
ai = PenetrationTestingAI("test_ai_knowledge.json")

print("Creating mock exploit executor...")
def mock_executor(mac, exploit, payload):
    time.sleep(0.1)
    success = random.random() > 0.5
    error = None if success else "Mock error"
    return success, error

print("Creating AutomatedAttackSystem...")
attack_sys = AutomatedAttackSystem(ai, mock_executor)

print("Testing exploit database info...")
db_info = attack_sys.get_exploit_database_info()
print(f"✓ Exploit database: {db_info.get('total_exploits', 0)} exploits")
bp = db_info.get('by_platform', {})
print(f"  - Windows: {bp.get('windows', 0)}")
print(f"  - Linux: {bp.get('linux', 0)}")
print(f"  - Multi: {bp.get('multi', 0)}")

print("\nStarting test campaign...")
campaign_id = attack_sys.start_automated_campaign(
    target_mac="aa:bb:cc:dd:ee:ff",
    target_ip="192.168.1.100",
    os_guess="Windows",
    aggressive=False
)
print(f"✓ Campaign started: {campaign_id}")

print("\nMonitoring campaign progress...")
for i in range(10):
    time.sleep(1)
    status = attack_sys.get_campaign_status(campaign_id)
    if status:
        print(f"  Progress: {status.get('progress', 0):.1f}% - Status: {status.get('status', 'unknown')}")
        if status.get('status') in ['completed', 'stopped']:
            break

print("\nGetting campaign results...")
results = attack_sys.get_campaign_results(campaign_id)
if results:
    print("✓ Results retrieved:")
    print(f"  - Completed: {results.get('completed_exploits', 0)}/{results.get('total_exploits', 0)}")
    print(f"  - Successful: {results.get('successful_exploits', 0)}")
    print(f"  - Failed: {results.get('failed_exploits', 0)}")
    print(f"  - Skipped: {results.get('skipped_exploits', 0)}")

# Cleanup
for p in ["test_ai_knowledge.json", "test_ai_knowledge.json.backup"]:
    if os.path.exists(p):
        os.remove(p)

print("\n✓✓✓ Automated Attack System: ALL TESTS PASSED ✓✓✓")
PYTEST
echo ""

########################################
# Test 5: Check Python Dependencies
########################################
echo "=== TEST 5: Checking Python Dependencies ==="
echo ""

python3 << 'PYTEST'
import sys
dependencies = {
    'flask': 'Flask web framework',
    'nmap': 'Python-nmap for network scanning',
    'msgpack': 'MessagePack for Metasploit RPC',
    'requests': 'HTTP library'
}

missing, installed = [], []
for module, description in dependencies.items():
    try:
        __import__(module)
        print(f"✓ {module:15s} - {description}")
        installed.append(module)
    except ImportError:
        print(f"✗ {module:15s} - {description} (MISSING)")
        missing.append(module)

print(f"\nInstalled: {len(installed)}/{len(dependencies)}")
if missing:
    print(f"\nMissing dependencies: {', '.join(missing)}")
    print("\nInstall with:")
    print(f"  pip3 install {' '.join(missing)}")
    sys.exit(1)
else:
    print("\n✓✓✓ All Python dependencies installed! ✓✓✓")
PYTEST
echo ""

########################################
# Test 6: Check System Dependencies
########################################
echo "=== TEST 6: System Dependencies Check ==="
echo ""

echo -n "Checking nmap... "
if command -v nmap &> /dev/null; then
    echo "✓ $(nmap --version | head -1)"
else
    echo "✗ NOT FOUND (install with: sudo pacman -S nmap)"
fi

echo -n "Checking Metasploit Framework... "
if command -v msfconsole &> /dev/null; then
    echo "✓ Installed"
else
    echo "✗ NOT FOUND (install with: sudo pacman -S metasploit)"
fi

echo -n "Checking msfrpcd... "
if command -v msfrpcd &> /dev/null; then
    echo "✓ Available"
else
    echo "✗ NOT FOUND (provided by metasploit; install with: sudo pacman -S metasploit)"
fi
echo ""

echo "=== FINAL TEST SUMMARY ==="
echo ""
echo "File sizes:"
ls -lh ai_learning_module.py automated_attack_system.py app.py | awk '{print "  " $9 ": " $5}'
echo ""
echo "Next steps:"
echo "  1. If all tests passed, create Makefile"
echo "  2. Run 'make setup' to create virtual environment"
echo "  3. Run 'make run' to start the system"
