#!/usr/bin/env bash
set -euo pipefail
python restore_assets.py
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
python verify_checkpoint.py
