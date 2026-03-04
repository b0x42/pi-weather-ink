#!/usr/bin/env bash
# Reset a stuck Waveshare e-Paper display by clearing it and putting it to sleep.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load DISPLAY_MODEL from ~/.env (same as the installer uses)
if [[ -f "$HOME/.env" ]]; then
    DISPLAY_MODEL=$(grep -oP '^DISPLAY_MODEL="\K[^"]+' "$HOME/.env" || true)
fi
DISPLAY_MODEL="${DISPLAY_MODEL:-epd2in13bc}"

echo "Resetting e-Paper display (model: $DISPLAY_MODEL)..."

python3 -c "
from waveshare_epd.${DISPLAY_MODEL} import EPD
epd = EPD()
epd.init()
epd.Clear()
epd.sleep()
print('Display cleared and put to sleep.')
"
