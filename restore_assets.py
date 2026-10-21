"""Restore checksum-verified binary assets from the GitHub deployment bundle."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent


def ensure_assets(root=ROOT):
    root = Path(root).resolve()
    manifest_path = root/'assets/manifest.json'
    if not manifest_path.is_file():
        return {'status': 'already_unpacked'}
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    expected_marker = hashlib.sha256(raw).hexdigest()
    marker = root/'.assets-ready'
    if marker.is_file() and marker.read_text() == expected_marker and all(
            (root/entry['path']).is_file() and (root/entry['path']).stat().st_size == entry['size']
            for entry in manifest['files']):
        return {'status': 'ready', 'files': len(manifest['files'])}
    expected = {entry['path']: entry for entry in manifest['files']}
    with tempfile.TemporaryDirectory(prefix='mm-assets-') as temp:
        archive = Path(temp)/'assets.zip'
        archive_hash = hashlib.sha256()
        with archive.open('wb') as output:
            for part in manifest['parts']:
                source = root/'assets'/part['name']
                digest = hashlib.sha256()
                with source.open('rb') as inp:
                    while block := inp.read(1024*1024):
                        digest.update(block)
                        archive_hash.update(block)
                        output.write(block)
                if digest.hexdigest() != part['sha256']:
                    raise RuntimeError('Asset bundle part checksum mismatch: '+part['name'])
        if archive_hash.hexdigest() != manifest['archive_sha256']:
            raise RuntimeError('Asset bundle checksum mismatch')
        with zipfile.ZipFile(archive) as bundle:
            if set(bundle.namelist()) != set(expected):
                raise RuntimeError('Asset bundle members differ from manifest')
            for info in bundle.infolist():
                rel = Path(info.filename)
                if rel.is_absolute() or '..' in rel.parts:
                    raise RuntimeError('Invalid asset path')
                target = root/rel
                if not target.resolve().is_relative_to(root):
                    raise RuntimeError('Asset target escapes the project')
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary = target.with_name(target.name+'.restoring')
                digest = hashlib.sha256()
                try:
                    with bundle.open(info) as inp, temporary.open('wb') as out:
                        while block := inp.read(1024*1024):
                            digest.update(block)
                            out.write(block)
                    entry = expected[info.filename]
                    if temporary.stat().st_size != entry['size'] or digest.hexdigest() != entry['sha256']:
                        raise RuntimeError('Restored asset checksum mismatch: '+info.filename)
                    os.replace(temporary, target)
                finally:
                    temporary.unlink(missing_ok=True)
    marker.write_text(expected_marker)
    return {'status': 'restored', 'files': len(expected)}


if __name__ == '__main__':
    print(json.dumps(ensure_assets()))
