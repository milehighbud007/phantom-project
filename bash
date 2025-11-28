#!/usr/bin/env bash
# ============================================================================
# PHANTOM Project Structure Reorganization Script
# ============================================================================

set -e  # Exit on error

PROJECT_ROOT="/home/devpen11/Desktop/phantom-project"
BACKUP_DIR="${PROJECT_ROOT}/backup_$(date +%Y%m%d_%H%M%S)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${PURPLE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                                                            ║${NC}"
echo -e "${PURPLE}║   PHANTOM Project Reorganization                           ║${NC}"
echo -e "${PURPLE}║   Creating Proper Directory Structure                      ║${NC}"
echo -e "${PURPLE}║                                                            ║${NC}"
echo -e "${PURPLE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

cd "$PROJECT_ROOT" || exit 1

# ============================================================================
# STEP 1: Create Backup
# ============================================================================

echo -e "${CYAN}→ Creating backup of current project...${NC}"
mkdir -p "$BACKUP_DIR"
cp -r . "$BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}✓ Backup created at: $BACKUP_DIR${NC}"
echo ""

# ============================================================================
# STEP 2: Create New Directory Structure
# ============================================================================

echo -e "${CYAN}→ Creating directory structure...${NC}"

# Backend directory
mkdir -p backend/{logs,uploads,data,config}

# Frontend directory
mkdir -p frontend/{public,src/{components,services,hooks,types,config}}

# Agents directory
mkdir -p agents

# Tests directory
mkdir -p tests

# Docs directory
mkdir -p docs

# Config directory
mkdir -p config

echo -e "${GREEN}✓ Directory structure created${NC}"
echo ""

# ============================================================================
# STEP 3: Move Existing Files to Backend
# ============================================================================

echo -e "${CYAN}→ Moving Python files to backend/...${NC}"

# Move core Python files
if [ -f "app.py" ]; then
    mv app.py backend/
    echo "  ✓ Moved app.py"
fi

if [ -f "ai_learning_module.py" ]; then
    mv ai_learning_module.py backend/
    echo "  ✓ Moved ai_learning_module.py"
fi

if [ -f "automated_attack_system.py" ]; then
    mv automated_attack_system.py backend/
    echo "  ✓ Moved automated_attack_system.py"
fi

# Move any other Python files
for file in *.py; do
    if [ -f "$file" ] && [ "$file" != "setup.py" ]; then
        mv "$file" backend/ 2>/dev/null || true
    fi
done

# Move JSON knowledge files
mv *.json backend/data/ 2>/dev/null || true

# Move requirements files
mv requirements*.txt backend/ 2>/dev/null || true

echo -e "${GREEN}✓ Python files moved${NC}"
echo ""

# ============================================================================
# STEP 4: Move Virtual Environment
# ============================================================================

echo -e "${CYAN}→ Handling virtual environment...${NC}"

if [ -d "venv" ]; then
    mv venv backend/
    echo -e "${GREEN}✓ Virtual environment moved to backend/${NC}"
else
    echo -e "${YELLOW}○ No virtual environment found (will create new one)${NC}"
fi

echo ""

# ============================================================================
# STEP 5: Create Backend Requirements File
# ============================================================================

echo -e "${CYAN}→ Creating backend/requirements_integrated.txt...${NC}"

cat > backend/requirements_integrated.txt << 'EOF'
# Core Web Framework
flask==3.0.0
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1

# Security & Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pyotp==2.9.0
qrcode==7.4.2

# Metasploit Integration
msgpack==1.0.7
msgpack-python==0.5.6

# Network Tools
python-nmap==0.7.1
scapy==2.5.0
netifaces==0.11.0
requests==2.31.0

# Wireless Tools (Python bindings)
trackerjacker==1.9.0

# Web Sockets
websockets==12.0

# Utilities
pydantic==2.5.0
pydantic-settings==2.1.0
python-dateutil==2.8.2

# Testing (optional)
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
EOF

echo -e "${GREEN}✓ Requirements file created${NC}"
echo ""

# ============================================================================
# STEP 6: Create Frontend Package.json
# ============================================================================

echo -e "${CYAN}→ Creating frontend/package.json...${NC}"

cat > frontend/package.json << 'EOF'
{
  "name": "phantom-frontend",
  "version": "2.0.0",
  "description": "PHANTOM Red Team Operations Console",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.2",
    "lucide-react": "^0.263.1",
    "typescript": "^5.3.3"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "tailwindcss": "^3.3.6"
  }
}
EOF

echo -e "${GREEN}✓ package.json created${NC}"
echo ""

# ============================================================================
# STEP 7: Create Frontend Public HTML
# ============================================================================

echo -e "${CYAN}→ Creating frontend/public/index.html...${NC}"

cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="PHANTOM Red Team Operations Platform" />
    <title>PHANTOM - Red Team C2</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this application.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

echo -e "${GREEN}✓ Frontend HTML created${NC}"
echo ""

# ============================================================================
# STEP 8: Create Frontend Source Files
# ============================================================================

echo -e "${CYAN}→ Creating frontend/src/index.tsx...${NC}"

cat > frontend/src/index.tsx << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

cat > frontend/src/App.tsx << 'EOF'
import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">PHANTOM v2.0</h1>
        <p className="text-xl text-gray-400">Red Team Operations Platform</p>
        <p className="text-sm text-gray-500 mt-4">Frontend Coming Soon...</p>
      </div>
    </div>
  );
}

export default App;
EOF

cat > frontend/src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
EOF

echo -e "${GREEN}✓ Frontend source files created${NC}"
echo ""

# ============================================================================
# STEP 9: Create Test Files
# ============================================================================

echo -e "${CYAN}→ Creating tests/test_backend.py...${NC}"

cat > tests/test_backend.py << 'EOF'
"""
Basic tests for PHANTOM backend
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_import_modules():
    """Test that core modules can be imported"""
    try:
        import ai_learning_module
        import automated_attack_system
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")

def test_ai_module_creation():
    """Test AI module instantiation"""
    from ai_learning_module import PenetrationTestingAI
    
    ai = PenetrationTestingAI("test_knowledge.json")
    assert ai is not None
    
    # Cleanup
    import os
    if os.path.exists("test_knowledge.json"):
        os.remove("test_knowledge.json")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
EOF

echo -e "${GREEN}✓ Test files created${NC}"
echo ""

# ============================================================================
# STEP 10: Move Makefiles
# ============================================================================

echo -e "${CYAN}→ Organizing Makefiles...${NC}"

# Move master Makefile to root
if [ -f "master Makefile" ]; then
    # Backup current Makefile if exists
    if [ -f "Makefile" ]; then
        mv Makefile Makefile.simple.backup
        echo "  ✓ Backed up simple Makefile"
    fi
    
    mv "master Makefile" Makefile
    echo "  ✓ Activated master Makefile"
fi

# Move old makefiles to backup
mkdir -p old_makefiles
mv Makefile.old* old_makefiles/ 2>/dev/null || true
mv Makefile.bak old_makefiles/ 2>/dev/null || true
mv Makefile.simple.backup old_makefiles/ 2>/dev/null || true

echo -e "${GREEN}✓ Makefiles organized${NC}"
echo ""

# ============================================================================
# STEP 11: Create README
# ============================================================================

echo -e "${CYAN}→ Creating README.md...${NC}"

cat > README.md << 'EOF'
# PHANTOM v2.0

**Penetration & Hacking Automation Network Threat Operations Manager**

Colorado Tech University - Jack Cole Dissertation Project

## 🎯 Overview

PHANTOM is a comprehensive red team operations platform integrating:
- Enterprise C2 Framework (FastAPI)
- Metasploit Automation
- AI Learning System
- Wireless Attack Suite
- Network Reconnaissance
- React-based Operator Console

## 🚀 Quick Start

```bash
# 1. Install dependencies
sudo make install

# 2. Setup environment
sudo make setup

# 3. Start PHANTOM
sudo make run
```

## 📁 Project Structure

```
phantom-project/
├── backend/              # Python backend (Flask + FastAPI)
│   ├── app.py           # Main Flask application
│   ├── ai_learning_module.py
│   ├── automated_attack_system.py
│   └── venv/            # Python virtual environment
├── frontend/            # React frontend console
│   ├── src/
│   └── public/
├── agents/              # C2 agents
├── tests/               # Test suite
├── config/              # Configuration files
├── docs/                # Documentation
└── Makefile            # Build automation

```

## 🔧 Commands

```bash
make help              # Show all commands
make status            # Check system status
make start-msfrpcd     # Start Metasploit RPC
make wireless-check    # Check wireless interface
make test              # Run tests
make clean             # Clean up
```

## ⚠️ Legal Notice

This tool is for **AUTHORIZED SECURITY TESTING ONLY**. Ensure you have:
- Written authorization
- Documented scope
- Proper consent

## 📖 Documentation

See `docs/` directory for full documentation.

## 👨‍🎓 Author

Jack Cole - Colorado Tech University
Cybersecurity Dissertation Project

---

**For Educational and Authorized Security Testing Only**
EOF

echo -e "${GREEN}✓ README created${NC}"
echo ""

# ============================================================================
# STEP 12: Create .gitignore
# ============================================================================

echo -e "${CYAN}→ Creating .gitignore...${NC}"

cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite
*.sqlite3

# AI Knowledge
*_knowledge.json
*_knowledge.json.backup

# Logs
*.log
logs/
*.pid

# Node
node_modules/
npm-debug.log*
build/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Sensitive
config/secrets.py
*.key
*.pem

# Backups
backup_*/
old_makefiles/
*.backup
*.bak
EOF

echo -e "${GREEN}✓ .gitignore created${NC}"
echo ""

# ============================================================================
# STEP 13: Create Config Files
# ============================================================================

echo -e "${CYAN}→ Creating configuration files...${NC}"

cat > config/default.py << 'EOF'
"""
Default configuration for PHANTOM
"""

# Server Configuration
BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = 8000
FRONTEND_PORT = 3000

# Metasploit RPC
MSF_RPC_HOST = "127.0.0.1"
MSF_RPC_PORT = 55552
MSF_RPC_USER = "msf"
MSF_RPC_PASS = "kali"

# Database
DATABASE_URL = "sqlite:///./backend/data/c2_database.db"
# For production use PostgreSQL:
# DATABASE_URL = "postgresql://c2_user:SecurePassword123@localhost/c2_database"

# Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Security
SECRET_KEY = "CHANGE_THIS_IN_PRODUCTION"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Wireless
WIRELESS_INTERFACE = "wlan1"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "backend/logs/phantom.log"
EOF

echo -e "${GREEN}✓ Configuration files created${NC}"
echo ""

# ============================================================================
# STEP 14: Update Backend Files Paths
# ============================================================================

echo -e "${CYAN}→ Updating file paths in backend files...${NC}"

# Update app.py to use new paths
if [ -f "backend/app.py" ]; then
    sed -i 's|metasploit_ai_knowledge.json|data/metasploit_ai_knowledge.json|g' backend/app.py 2>/dev/null || true
    echo "  ✓ Updated app.py paths"
fi

echo -e "${GREEN}✓ Paths updated${NC}"
echo ""

# ============================================================================
# STEP 15: Create Run Script
# ============================================================================

echo -e "${CYAN}→ Creating run_tests.sh...${NC}"

cat > run_tests.sh << 'EOF'
#!/usr/bin/env bash
# Quick test script

cd "$(dirname "$0")"

echo "Running PHANTOM tests..."
cd tests && python3 -m pytest -v --cov=../backend
EOF

chmod +x run_tests.sh

echo -e "${GREEN}✓ Run script created${NC}"
echo ""

# ============================================================================
# FINAL SUMMARY
# ============================================================================

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✓ REORGANIZATION COMPLETE                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}📁 New Directory Structure:${NC}"
echo ""
tree -L 2 -I 'venv|node_modules|__pycache__|backup_*' 2>/dev/null || ls -la
echo ""

echo -e "${YELLOW}📋 Next Steps:${NC}"
echo ""
echo -e "  1. ${CYAN}make help${NC}             - View all available commands"
echo -e "  2. ${CYAN}sudo make install${NC}     - Install system dependencies"
echo -e "  3. ${CYAN}sudo make setup${NC}       - Setup environment"
echo -e "  4. ${CYAN}make status${NC}           - Check system status"
echo -e "  5. ${CYAN}sudo make run${NC}         - Start PHANTOM platform"
echo ""

echo -e "${YELLOW}💾 Backup Location:${NC}"
echo -e "  ${CYAN}$BACKUP_DIR${NC}"
echo ""

echo -e "${GREEN}✓ Your project is now properly organized!${NC}"
echo ""
