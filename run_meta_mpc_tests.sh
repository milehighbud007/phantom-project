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
# Test 3: Check Dependencies
########################################
echo "=== TEST 3: Checking Python Dependencies ==="
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

echo "=== ALL TESTS COMPLETED ==="
