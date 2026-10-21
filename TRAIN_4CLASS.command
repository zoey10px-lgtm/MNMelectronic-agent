#!/bin/sh
cd "$(dirname "$0")" || exit 1
python3 one_click.py --train-only
