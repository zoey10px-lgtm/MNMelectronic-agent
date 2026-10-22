"""Fetch an approved Vice checkpoint during deployment; verify full SHA-256."""
import hashlib
import os
from pathlib import Path
from urllib.parse import urlsplit
import requests

DEST=Path(__file__).resolve().parent/'weights'/'exp-4.pt'
DEFAULT_SHA='d522fc938cd3478d1deafe536fc9d438f91a9b7024ddede307d7c78d7a4846c9'

def run():
    url=os.environ.get('MM_MODEL_DOWNLOAD_URL','').strip()
    expected=os.environ.get('MM_MODEL_SHA256',DEFAULT_SHA).strip().lower()
    if not url:
        print('Vice download URL not set; existing weights remain active')
        return
    if urlsplit(url).scheme!='https':
        raise RuntimeError('MM_MODEL_DOWNLOAD_URL must be an HTTPS URL')
    DEST.parent.mkdir(parents=True, exist_ok=True)
    tmp=DEST.with_suffix('.pt.download')
    try:
        digest=hashlib.sha256()
        with requests.get(url,stream=True,timeout=(15,120)) as response:
            response.raise_for_status()
            with tmp.open('wb') as out:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        digest.update(chunk)
                        out.write(chunk)
        if digest.hexdigest()!=expected:
            raise RuntimeError('Vice checkpoint SHA-256 mismatch')
        tmp.replace(DEST)
        print('Vice checkpoint ready:', DEST.name)
    finally:
        tmp.unlink(missing_ok=True)

if __name__=='__main__':
    run()
