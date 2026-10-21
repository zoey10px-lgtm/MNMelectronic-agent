"""One-click: setup portable venv, train four classes if needed, launch UI."""
import argparse
import hashlib
import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT=Path(__file__).resolve().parent
VENV=ROOT/'.venv'
PY=VENV/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
REQ=ROOT/'requirements.txt'

def call(args):
    print('>>>', ' '.join(map(str,args)),flush=True)
    subprocess.run([str(a) for a in args],check=True,cwd=ROOT)

def setup():
    if not ((3,10)<=sys.version_info[:2]<=(3,13)):
        raise RuntimeError('Python 3.10~3.13 (64-bit) is required; Python 3.12 recommended.')
    if not PY.is_file():
        print('[1/4] Creating local Python environment...',flush=True)
        venv.EnvBuilder(with_pip=True).create(VENV)
    # Install only if package imports fail; no nonexistent pinned PyTorch versions.
    check=subprocess.run([str(PY),'-c','import torch, ultralytics, flask, waitress, dotenv, cv2, PIL, yaml'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    signature=hashlib.sha256(REQ.read_bytes()).hexdigest()
    stamp=VENV/'mm-requirements.sha256'
    if check.returncode or not stamp.exists() or stamp.read_text()!=signature:
        print('[2/4] Installing PyTorch and YOLO dependencies (internet required once)...',flush=True)
        call([PY,'-m','pip','install','--upgrade','pip'])
        call([PY,'-m','pip','install','-r',REQ])
        call([PY,'-c','import torch, ultralytics, flask, waitress, dotenv; print("Libraries ready")'])
        stamp.write_text(signature)
    else:print('[2/4] Libraries already installed.',flush=True)

def verify_model():
    from model_bundle import verify_bundle
    _,report=verify_bundle()
    print('[3/4] Model and evaluation match. Measured photo holdout:',report['summary']['val'],flush=True)

def train():
    call([PY,ROOT/'train_4class.py','--epochs','40','--batch','8'])
    verify_model()


def start():
    print('[4/4] Launching website on http://127.0.0.1:8000/ ...',flush=True)
    call([PY,ROOT/'serve.py'])

def main():
    from restore_assets import ensure_assets
    ensure_assets()
    arg=argparse.ArgumentParser();arg.add_argument('--train-only',action='store_true');arg.add_argument('--skip-train',action='store_true');args=arg.parse_args()
    setup()
    if args.train_only:
        train()
    else:
        verify_model()
        start()

if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:print('Stopped by user.')
    except Exception as e:
        print('\nERROR:',type(e).__name__,str(e),flush=True)
        sys.exit(1)
