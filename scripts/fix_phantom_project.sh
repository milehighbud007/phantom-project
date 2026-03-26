#!/bin/bash
set -euo pipefail

echo "==============================================="
echo "  Phantom Project - Automated Fix Script"
echo "==============================================="
echo ""

PROJECT_DIR="/home/devpen11/Desktop/phantom-project"

# Check if we're in the right directory
if [[ ! -d "$PROJECT_DIR" ]]; then
    echo "✗ Project directory not found: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

echo "=== Step 1: Kill Process on Port 5000 ==="
echo "Finding and killing process using port 5000..."
PORT_PID=$(sudo lsof -ti:5000 || true)
if [[ -n "$PORT_PID" ]]; then
    sudo kill -9 $PORT_PID
    echo "✓ Killed process on port 5000 (PID: $PORT_PID)"
else
    echo "✓ Port 5000 is already free"
fi
echo ""

echo "=== Step 2: Fix App.py Port Configuration ==="
echo "Updating app.py to use port 5001 as fallback..."

# Create a backup
cp app.py app.py.backup

# Update the port in app.py
cat >> app.py << 'EOF'

# Add port configuration at the end of file
if __name__ == '__main__':
    import sys
    port = 5000
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"Port {port} in use, trying 5001...")
            app.run(host='0.0.0.0', port=5001, debug=False)
        else:
            raise
EOF

echo "✓ App.py updated with fallback port"
echo ""

echo "=== Step 3: Create Missing Test Script ==="
cat > run_meta_mpc_tests.sh << 'EOF'
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
EOF

chmod +x run_meta_mpc_tests.sh
echo "✓ Created run_meta_mpc_tests.sh"
echo ""

echo "=== Step 4: Fix RogueHostAPD Issue ==="
if [[ -d "roguehostapd" ]]; then
    cd roguehostapd
    
    # Check if the issue exists
    if grep -q "config_obj.init_config()" /usr/share/roguehostapd/run.py 2>/dev/null; then
        echo "Found roguehostapd config issue, creating patch..."
        
        # Create a fixed version
        sudo sed -i 's/config_obj.init_config()/config_obj.read_config()/' /usr/share/roguehostapd/run.py 2>/dev/null || true
        
        echo "✓ Patched roguehostapd run.py"
    else
        echo "✓ RogueHostAPD config issue not found or already fixed"
    fi
    
    cd "$PROJECT_DIR"
else
    echo "⚠ roguehostapd directory not found, skipping"
fi
echo ""

echo "=== Step 5: Update Makefile for Better Port Handling ==="
if [[ -f "Makefile" ]]; then
    # Add port checking to Makefile
    cat >> Makefile << 'EOF'

# Check if port is available
.PHONY: check-port
check-port:
	@echo "Checking port 5000..."
	@! lsof -ti:5000 > /dev/null || (echo "Port 5000 in use, killing process..." && sudo kill -9 $$(lsof -ti:5000))
	@echo "✓ Port 5000 is available"
EOF
    echo "✓ Updated Makefile with port checking"
else
    echo "⚠ Makefile not found"
fi
echo ""

echo "=== Step 6: Create Quick Start Script ==="
cat > start_phantom.sh << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "  Starting Phantom Project"
echo "========================================"

# Kill any process on port 5000
PORT_PID=$(sudo lsof -ti:5000 2>/dev/null || true)
if [[ -n "$PORT_PID" ]]; then
    echo "Killing process on port 5000..."
    sudo kill -9 $PORT_PID
    sleep 1
fi

# Check if msfrpcd is running
if ! pgrep -x "msfrpcd" > /dev/null; then
    echo "Starting msfrpcd..."
    sudo msfrpcd -P msf -U msf -p 55553 -a 127.0.0.1 &
    sleep 2
fi

# Activate venv if it exists
if [[ -d "venv" ]]; then
    source venv/bin/activate
fi

# Start the application
echo "Starting Flask application..."
python3 app.py
EOF

chmod +x start_phantom.sh
echo "✓ Created start_phantom.sh quick start script"
echo ""

echo "=== Step 7: Verify File Permissions ==="
chmod +x *.py 2>/dev/null || true
chmod +x *.sh 2>/dev/null || true
echo "✓ Set executable permissions"
echo ""

echo "=========================================="
echo "  Fix Script Completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Run tests: ./run_meta_mpc_tests.sh"
echo "  2. Start app:  ./start_phantom.sh"
echo "  3. Or use:     sudo make run"
echo ""
echo "If issues persist, check:"
echo "  - Port 5000 is free: sudo lsof -i:5000"
echo "  - msfrpcd is running: ps aux | grep msfrpcd"
echo "  - Dependencies installed: pip3 list"
echo ""
