#!/bin/bash
# PHANTOM Installation Script

echo "Installing PHANTOM Makefile..."

# Backup old Makefile
if [ -f Makefile ]; then
    cp Makefile Makefile.backup.$(date +%s)
    echo "✓ Old Makefile backed up"
fi

# The new Makefile content will be here
# (You'll paste the artifact content)

echo "✓ PHANTOM Makefile installed"
echo ""
echo "Quick start:"
echo "  sudo make run     - Start PHANTOM"
echo "  make help         - Show all commands"
echo "  make info         - Show project info"
