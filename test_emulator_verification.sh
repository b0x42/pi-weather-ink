#!/bin/bash
# Verification script for EPD-Emulator integration

echo "=== EPD-Emulator Integration Verification ==="
echo

echo "1. Testing with USE_EMULATOR=false (hardware mode, default)"
USE_EMULATOR=false .venv/bin/python -m pytest tests/ -v -k "not emulator"
echo

echo "2. Testing emulator integration tests are skipped by default"
.venv/bin/python -m pytest tests/test_emulator_integration.py -v
echo

echo "3. Verifying emulator availability detection"
.venv/bin/python -c "from emulator_adapter import EMULATOR_AVAILABLE; print(f'Emulator available: {EMULATOR_AVAILABLE}')"
echo

echo "4. Verifying error handling when emulator not installed"
.venv/bin/python << 'PYEOF'
import os
os.environ['USE_EMULATOR'] = 'true'
from display_config import load_display_module
try:
    load_display_module('epd2in13bc')
    print("ERROR: Should have raised ImportError")
except ImportError as e:
    print(f"✓ Correct error: {str(e)[:80]}...")
PYEOF
echo

echo "=== All verification steps completed ==="
echo "NOTE: To test with actual emulator, install EPD-Emulator and run:"
echo "  USE_EMULATOR=true .venv/bin/python -m pytest tests/test_emulator_integration.py -v"
