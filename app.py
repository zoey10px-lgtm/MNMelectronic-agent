"""Local M&M website with real YOLO inference and persistent complaint records."""
import base64
import binascii
import hmac
import io
import json
import logging
import os
import re
import secrets
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request, send_file, send_from_directory, session
from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parent
from restore_assets import ensure_assets
ensure_assets()
load_dotenv(ROOT / '.env')
DATA = Path(os.environ.get('MM_DATA_DIR', str(ROOT / 'data')))
MEDIA = DATA / 'media'
MEDIA.mkdir(parents=True, exist_ok=True)
DB = DATA / 'complaints.sqlite3'
SECRET = DATA / 'session.key'
if not SECRET.exists():
    try:
        with SECRET.open('x', encoding='ascii') as f:
            f.write(secrets.token_hex(32))
        SECRET.chmod(0o600)
    except FileExistsError:
        pass

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or SECRET.read_text().strip()
app.config.update(MAX_CONTENT_LENGTH=24 * 1024 * 1024,
                  SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
Image.MAX_IMAGE_PIXELS = 20_000_000
ADMIN_USER = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '').strip() or ('' if os.environ.get('RENDER') else 'MM2026!')
MODEL = None
MODEL_PATH = None
MODEL_LOCK = threading.Lock()


def now():
    return datetime.now(timezone.utc).isoformat()


class _PostgresConnection:
    """Compatibility adapter for the existing parameterized SQLite queries."""
    def __init__(self, connection):
        self.connection = connection

    def execute(self, statement, params=()):
        return self.connection.execute(statement.replace('?', '%s'), params)


@contextmanager
def connect():
    database_url = os.environ.get('DATABASE_URL', '').strip()
    if database_url:
        from psycopg import connect as postgres_connect
        from psycopg.rows import dict_row
        with postgres_connect(database_url, row_factory=dict_row, connect_timeout=10) as connection:
            yield _PostgresConnection(connection)
    else:
        connection = sqlite3.connect(DB, timeout=15)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()


with connect() as c:
    c.execute('CREATE TABLE IF NOT EXISTS records '
              '(id TEXT PRIMARY KEY, owner TEXT, confirmed INTEGER, payload TEXT)')


def owner():
    if 'owner' not in session:
        session['owner'] = uuid.uuid4().hex
    return session['owner']


def admin_only(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if not session.get('admin'):
            return jsonify(error='관리자 로그인이 필요합니다.'), 401
        return fn(*a, **kw)
    return wrapper


@app.before_request
def same_origin():
    if request.method in ('POST', 'PATCH', 'DELETE') and request.headers.get('Origin'):
        if urlsplit(request.headers['Origin']).netloc != request.host:
            abort(403)


@app.after_request
def private_cache(response):
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.errorhandler(413)
def too_large(_):
    return jsonify(error='첨부 파일이 너무 큽니다. 사진을 줄여주세요.'), 413


@app.errorhandler(500)
def server_error(_):
    return jsonify(error='서버 처리 중 오류가 발생했습니다. START 창의 오류를 확인해주세요.'), 500


def display_model_path(path):
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return path.name


def model_info():
    """Expose the actual available weights instead of implying 4-class accuracy."""
    candidates = [ROOT / 'weights' / 'exp-4.pt']
    return {'available_weights': [str(p.relative_to(ROOT)) for p in candidates if p.is_file()],
            'active_weights': display_model_path(MODEL_PATH),
            'active_classes': list(MODEL.names.values()) if MODEL is not None else [],
            'evaluation': evaluation_info(),
            'type_classifier_active': MODEL is not None and set(MODEL.names.values()) ==
            {'fracture', 'dent', 'porosity', 'missing_feature'}}


def evaluation_info():
    import hashlib
    path = ROOT / 'MODEL_EVALUATION.json'
    if not path.is_file() or MODEL_PATH is None:
        return {'status': 'not_evaluated'}
    if MODEL_PATH.name == 'exp-4.pt' or os.environ.get('MM_MODEL_PATH'):
        return {'status': 'vice_model_external_validation_pending', 'universal_generalization_verified': False}
    report = json.loads(path.read_text(encoding='utf-8'))
    digest = hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest()
    if report.get('model_sha256') != digest:
        return {'status': 'model_changed_evaluation_required'}
    return {'status': report['assessment'], 'summary': report['summary'],
            'universal_generalization_verified': report['universal_generalization_verified'],
            'unsupported_types': report['unsupported_types']}


def load_model():
    global MODEL, MODEL_PATH
    if MODEL is None:
        import torch
        from ultralytics import YOLO
        import ultralytics.utils.torch_utils as tu
        tu.NUM_THREADS = min(4, os.cpu_count() or 1)
        torch.set_num_threads(min(4, os.cpu_count() or 1))
        from model_bundle import verify_bundle
        path, report = verify_bundle()
        loaded = YOLO(str(path))
        if list(loaded.names.values()) != report['class_names']:
            raise RuntimeError('Loaded model class mapping differs from its evaluation.')
        MODEL, MODEL_PATH = loaded, path
    return MODEL


def _overlap(a, b):
    x1=max(a[0],b[0]); y1=max(a[1],b[1]); x2=min(a[2],b[2]); y2=min(a[3],b[3])
    intersection=max(0,x2-x1)*max(0,y2-y1)
    ar1=max(0,a[2]-a[0])*max(0,a[3]-a[1]); ar2=max(0,b[2]-b[0])*max(0,b[3]-b[1])
    return intersection/(ar1+ar2-intersection+1e-9)


def inspect(image):
    from detector import detect
    model = load_model()
    with MODEL_LOCK:
        return detect(model, image)


def decode_photo(photo):
    if not isinstance(photo, dict):
        raise ValueError('사진 형식을 확인해주세요.')
    data = photo.get('url', '')
    if not isinstance(data, str) or not data.startswith(('data:image/jpeg;base64,',
            'data:image/png;base64,', 'data:image/webp;base64,')):
        raise ValueError('JPG, PNG, WEBP 사진만 사용할 수 있습니다.')
    try:
        raw = base64.b64decode(data.split(',', 1)[1], validate=True)
        if len(raw) > 8 * 1024 * 1024:
            raise ValueError('사진 한 장의 크기를 줄여주세요.')
        im = Image.open(io.BytesIO(raw))
        if im.format not in ('JPEG', 'PNG', 'WEBP') or im.width * im.height > 20_000_000:
            raise ValueError('이미지 형식 또는 해상도를 확인해주세요.')
        im.load()
        return ImageOps.exif_transpose(im).convert('RGB')
    except (binascii.Error, UnidentifiedImageError, OSError, Image.DecompressionBombError) as e:
        raise ValueError('사진 파일을 읽을 수 없습니다.') from e


def text(d, key, length):
    return str(d.get(key) or '').strip()[:length]


def read_record(cid):
    with connect() as c:
        return c.execute('SELECT * FROM records WHERE id=?', (cid,)).fetchone()


@app.get('/')
def homepage():
    return send_file(ROOT / 'templates' / 'index.html')


@app.get('/health')
def health():
    from language_service import configuration
    return jsonify(ok=True, database_backend='postgresql' if os.environ.get('DATABASE_URL') else 'sqlite', application='MM_Electronics_YOLO', revision='6.1',
                   model_loaded=MODEL is not None, language=configuration(), **model_info())


@app.get('/api/label-cases')
def label_cases():
    from label_engine import RECORDS, public_case
    return jsonify([public_case(r) for r in RECORDS])


@app.get('/sample-photo')
def sample_photo():
    kind = request.args.get('type', 'fracture')
    if kind not in ('fracture', 'dent', 'porosity', 'missing_feature'):
        abort(404)
    return send_file(ROOT / 'sample_photos' / f'{kind}.jpg')


@app.get('/annotations/')
def annotation_review():
    return send_file(ROOT / 'annotations' / 'review.html')


@app.get('/annotations/<path:name>')
def annotation_assets(name):
    return send_from_directory(ROOT / 'annotations', name)


@app.post('/api/documents/preprocess')
def preprocess_document_upload():
    upload = request.files.get('file')
    if upload is None or not upload.filename:
        return jsonify(error='Select a document.'), 400
    filename = Path(upload.filename).name
    extension = Path(filename).suffix.lower()
    if extension not in ('.pdf', '.docx', '.txt'):
        return jsonify(error='Only PDF, DOCX and TXT are supported.'), 400
    data = upload.read(12 * 1024 * 1024 + 1)
    if len(data) > 12 * 1024 * 1024:
        return jsonify(error='Maximum document size is 12 MB.'), 413
    try:
        if extension == '.txt':
            result = {'filename': filename, 'type': 'txt',
                      'text': data.decode('utf-8-sig')[:30000], 'images': [], 'image_count': 0}
        else:
            from document_preprocessor import preprocess_document
            result = preprocess_document(filename, data)
    except (ValueError, UnicodeDecodeError) as exc:
        return jsonify(error=str(exc)), 400
    images = result.pop('images')
    result['image_previews'] = ['data:image/jpeg;base64,' + base64.b64encode(item).decode('ascii') for item in images]
    result['text_length'] = len(result['text'])
    return jsonify(result)


@app.post('/api/analyze')
def analyze():
    d = request.get_json(silent=True)
    if not isinstance(d, dict):
        return jsonify(error='문의 내용을 확인해주세요.'), 400
    product, message = text(d, 'product', 20), text(d, 'message', 1800)
    document_text = text(d, 'document_text', 30000)
    document_name = text(d, 'document_name', 200)
    language = d.get('language', 'ko')
    if language not in ('ko', 'en', 'vi'):
        language = 'ko'
    photos = d.get('photos', [])
    if not isinstance(photos, list) or len(photos) > 3:
        return jsonify(error='사진은 최대 3장까지 첨부할 수 있습니다.'), 400
    if product not in ('A156', 'A176', 'A276', 'A376', 'AUTO') or (not photos and len(message) < 10 and len(document_text) < 10):
        return jsonify(error='제품을 선택하고 사진 또는 10자 이상의 문의 내용을 입력해주세요.'), 400
    if not message:
        message = '첨부 문서의 품질 문제 분석을 요청합니다.' if document_text else '첨부 사진의 결함 의심 영역 검사를 요청합니다.'
    try:
        images = [decode_photo(p) for p in photos]
    except ValueError as e:
        return jsonify(error=str(e)), 400
    from visual_matcher import guess_product
    product_guesses = [guess_product(im) for im in images]
    if product == 'AUTO':
        from label_engine import index, pixels
        exact_matches = [index()[0].get(pixels(im)) for im in images]
        exact_products = [m[0]['product_model'] for m in exact_matches if m]
        reliable = exact_products or [g['model'] for g in product_guesses if g['model']]
        product = max(set(reliable),key=reliable.count) if reliable else 'UNKNOWN'
        if product == 'UNKNOWN':
            mentioned = set(re.findall(r'(?<![A-Z0-9])A[\s-]*(156|176|276|376)(?!\d)', message.upper()))
            if len(mentioned) == 1:
                product = 'A' + mentioned.pop()
    cid = 'MM-' + datetime.now(timezone.utc).strftime('%Y%m%d') + '-' + uuid.uuid4().hex[:12].upper()
    media_dir = MEDIA / cid
    original, findings = [], []
    try:
        media_dir.mkdir()
        for i, image in enumerate(images):
            from label_engine import lookup, similar_cases
            known, label_marked = lookup(image, product)
            is_map = known and known['annotation_status'] == 'inspection_location_map'
            boxes, marked, weak, modes = ([], image.copy(), [], []) if is_map else inspect(image)
            image.save(media_dir / f'{i}_original.jpg', quality=95)
            marked.save(media_dir / f'{i}_detected.jpg', quality=95)
            if label_marked:
                label_marked.save(media_dir / f'{i}_labels.jpg', quality=95)
                known['annotated_image'] = f'/api/media/{cid}/{i}_labels.jpg'
            original.append({'name': text(photos[i], 'name', 120),
                             'url': f'/api/media/{cid}/{i}_original.jpg'})
            findings.append({'detections': boxes, 'detection_count': len(boxes),
                             'image_width': image.width, 'image_height': image.height,
                             'product_recognition': product_guesses[i],
                             'low_confidence_candidates': weak, 'search_passes': modes,
                             'registered_label': known,
                             'interpretation_mode': 'model_prediction_with_reference' if known else 'new_photo',
                             'inference_status': 'skipped_location_map' if is_map else 'complete',
                             'training_membership': known.get('split') if known else None,
                             'similar_label_cases': [] if known else similar_cases(image, boxes, product),
                             'annotated_image': f'/api/media/{cid}/{i}_detected.jpg'})
    except Exception:
        import shutil
        shutil.rmtree(media_dir, ignore_errors=True)
        logging.exception('YOLO inference failed')
        return jsonify(error='사진 분석에 실패했습니다. 서버 창의 오류를 확인해주세요.'), 503
    from retrieve import retrieve
    source_types = sorted({b['class_name'] for im in findings
                           for b in (im.get('registered_label') or {}).get('labels', [])
                           if not im['registered_label']['product_mismatch']})
    from interpretation import CLASSES
    total = sum(f['detection_count'] for f in findings)
    predicted_types = sorted({b['label'] for f in findings for b in f['detections']
                              if b['label'] in CLASSES})
    query = message + '\n' + document_text[:6000] + ' ' + ' '.join(CLASSES[t]['ko'] for t in predicted_types)
    references = retrieve(query, model=product if product in ('A156','A176','A276','A376') else None, k=5, include_examples=True,
                          category=predicted_types[0] if len(predicted_types) == 1 else None)
    vision = {'status': 'complete' if photos else 'no_photo', 'model': str(MODEL_PATH.relative_to(ROOT)) if MODEL_PATH else None,
              'revision': '6.1', 'photo_product_estimate': product_guesses, 'class_names': list(MODEL.names.values()) if MODEL else [],
              'predicted_types': predicted_types, 'type_classifier_active': bool(predicted_types) or (MODEL is not None and set(MODEL.names.values()) == set(CLASSES)),
              'source_label_types': source_types, 'evaluation': evaluation_info(),
              'interpretation_method': 'YOLO predictions from detector.py; source annotations are separate reference data; GPT receives YOLO metadata only, never original images',
              'confidence_threshold': 0.25, 'detection_count': total, 'images': findings,
              'message': (f'YOLO가 결함 {total}곳을 검출하고 유형 {len(predicted_types)}종을 예측했습니다.' if predicted_types else f'YOLO가 결함 의심 영역 {total}곳을 검출했습니다. 유형 모델이 없어 세부 유형은 미확정입니다.') if total else
                         ('검출된 영역이 없습니다. 정상 판정은 아니며 담당자 확인이 필요합니다.' if photos
                          else '사진이 없어 이미지 검사를 진행하지 않았습니다.')}
    from language_service import generate
    language_result = generate(product, message + ('\n\n[Attached document: ' + document_name + ']\n' + document_text[:10000] if document_text else ''), text(d, 'category', 80),
                               [], vision, references, language)  # Text-only GPT; YOLO owns image detection.
    category_names = {'scratch': '표면 스크래치', 'dent': '찍힘·변형', 'fracture': '균열 의심',
                      'porosity': '기공·표면 공동', 'missing_feature': '재료·형상 결손',
                      'assembly_gap': '조립 벌어짐', 'dimension': '치수·조립 문제',
                      'coating': '도장·코팅 불량', 'contamination': '이물질·오염',
                      'shipping': '배송·포장 문제', 'other': '기타 문의', 'unclear': '추가 확인'}
    chosen_category = text(d, 'category', 80)
    if chosen_category in ('', '사진 검사') and language_result.get('status') == 'complete':
        chosen_category = category_names[language_result['category']]
    analysis = {'vision': vision, 'language': language_result,
                'references': [{'id': r['id'], 'kind': r['kind'], 'text': r['text'],
                                'authority': r['authority'],
                                'synthetic': r['synthetic']} for r in references]}
    payload = {'id': cid, 'createdAt': now(), 'product': product,
               'message': message, 'document_name': document_name, 'document_text': document_text, 'category': chosen_category or '사진 검사',
               'lot': text(d, 'lot', 80), 'name': text(d, 'name', 80), 'language': language,
               'email': text(d, 'email', 150), 'photos': original,
               'analysis': analysis, 'status': '접수 대기',
               'priority': {'low': '낮음', 'normal': '보통', 'high': '높음', 'urgent': '긴급'}.get(language_result.get('priority'), '보통'),
               'history': [],
               'admin_summary': language_result.get('summary', '') if language_result.get('status') == 'complete' else '',
               'recommended_actions': language_result.get('next_actions', []) if language_result.get('status') == 'complete' else [],
               'ai_category': language_result.get('category') if language_result.get('status') == 'complete' else None,
               'ai_review_required': language_result.get('needs_human_review', True)}
    with connect() as c:
        c.execute('INSERT INTO records VALUES (?,?,0,?)',
                  (cid, owner(), json.dumps(payload, ensure_ascii=False)))
    return jsonify(id=cid, analysis=analysis), 201


@app.post('/api/complaints/<cid>/confirm')
def confirm(cid):
    row = read_record(cid)
    if not row or row['owner'] != session.get('owner'):
        return jsonify(error='이 브라우저에서 분석한 문의를 먼저 선택해주세요.'), 404
    payload = json.loads(row['payload'])
    if not row['confirmed']:
        payload['status'] = '접수 완료'
        payload['history'].append({'at': now(), 'text': '고객이 품질 문의를 최종 접수했습니다.'})
        with connect() as c:
            c.execute('UPDATE records SET confirmed=1,payload=? WHERE id=?',
                      (json.dumps(payload, ensure_ascii=False), cid))
    return jsonify(ok=True, id=cid)


@app.get('/api/complaints/<cid>/status')
def status(cid):
    row = read_record(cid)
    if not row or not row['confirmed']:
        return jsonify(error='등록된 접수번호가 없습니다.'), 404
    p = json.loads(row['payload'])
    return jsonify({k: p[k] for k in ('id', 'createdAt', 'product', 'category', 'status')})


@app.get('/api/media/<cid>/<name>')
def media(cid, name):
    row = read_record(cid)
    if not row or not (session.get('admin') or row['owner'] == session.get('owner')):
        abort(404)
    allowed = {f'{i}_{kind}.jpg' for i in range(3) for kind in ('original', 'detected', 'labels')}
    if name not in allowed:
        abort(404)
    return send_file(MEDIA / cid / name)


@app.get('/api/admin/me')
def me():
    return jsonify(authenticated=bool(session.get('admin')))


@app.post('/api/admin/login')
def login():
    if not ADMIN_PASSWORD:
        return jsonify(error='관리자 계정 설정을 확인해주세요.'), 503
    d = request.get_json(silent=True) or {}
    if not (hmac.compare_digest(str(d.get('username', '')).encode(), ADMIN_USER.encode()) and
            hmac.compare_digest(str(d.get('password', '')).encode(), ADMIN_PASSWORD.encode())):
        return jsonify(error='아이디 또는 비밀번호를 확인해주세요.'), 401
    session['admin'] = True
    return jsonify(ok=True)


@app.post('/api/admin/logout')
def logout():
    session.pop('admin', None)
    return jsonify(ok=True)


@app.get('/api/admin/complaints')
@admin_only
def records():
    with connect() as c:
        rows = c.execute('SELECT payload FROM records WHERE confirmed=1').fetchall()
    return jsonify(sorted([json.loads(row['payload']) for row in rows],
                          key=lambda p: p['createdAt'], reverse=True))


@app.patch('/api/admin/complaints/<cid>')
@admin_only
def update(cid):
    d = request.get_json(silent=True) or {}
    status, priority = d.get('status'), d.get('priority')
    if status not in ('접수 완료', '검토 중', '조치 중', '처리 완료', '보류') or priority not in ('낮음', '보통', '높음', '긴급'):
        return jsonify(error='상태 또는 우선순위를 확인해주세요.'), 400
    row = read_record(cid)
    if not row or not row['confirmed']:
        abort(404)
    p = json.loads(row['payload'])
    for key, value, label in [('status', status, '처리 상태'), ('priority', priority, '우선순위')]:
        if p[key] != value:
            p['history'].append({'at': now(), 'text': f'{label}: {p[key]} → {value}'})
            p[key] = value
    with connect() as c:
        c.execute('UPDATE records SET payload=? WHERE id=?', (json.dumps(p, ensure_ascii=False), cid))
    return jsonify(ok=True)


if __name__ == '__main__':
    from waitress import serve
    load_model()
    serve(app, host='127.0.0.1', port=int(os.environ.get('PORT', '8000')), threads=4)
