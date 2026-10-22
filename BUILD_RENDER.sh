#!/usr/bin/env bash
set -euo pipefail
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
python download_vice_weights.py
python -c "from model_bundle import verify_bundle; print('VICE_MODEL_VERIFIED', verify_bundle()[0])"
