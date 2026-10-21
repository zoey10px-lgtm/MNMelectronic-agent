#!/bin/bash
cd "$(dirname "$0")" || exit 1
export PYTHONUTF8=1
python3 one_click.py
read -r -p "Server stopped. Press Enter to close. "
