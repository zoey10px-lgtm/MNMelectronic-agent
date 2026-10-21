"""Explanations derived from predicted class and measured image coordinates."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLASSES = {c['name']: c for c in json.loads((ROOT/'class_catalog.json').read_text(encoding='utf-8'))['classes']}


def describe_detection(box, width, height):
    result = dict(box)
    name = result['label']
    meta = CLASSES.get(name)
    x1, y1, x2, y2 = result['box_xyxy']
    cx, cy = (x1+x2)/2/width, (y1+y2)/2/height
    h = '왼쪽' if cx < 1/3 else '오른쪽' if cx > 2/3 else '가운데'
    v = '위쪽' if cy < 1/3 else '아래쪽' if cy > 2/3 else '중앙'
    position = f'사진 기준 {h} {v}'
    result.update(location_ko=position,
                  box_xyxy_normalized=[x1/width, y1/height, x2/width, y2/height],
                  cause=None, interpretation_source='class_catalog_and_box_coordinates',
                  type_status='predicted' if meta else 'unconfirmed')
    if meta:
        result.update(label_ko=meta['ko'], label_en=meta['en'], label_vi=meta['vi'],
                      explanation=f"{position}에서 {meta['ko']} 영역을 검출했습니다. {meta['appearance']}",
                      recommended_checks=meta['checks'])
    else:
        result.update(label_ko='결함 의심 · 유형 미확정', label_en='Suspected defect; type unconfirmed',
                      label_vi='Nghi khuyết tật; chưa xác định loại',
                      explanation=f'{position}에서 결함 의심 영역을 찾았습니다. 검출된 위치의 세부 유형은 미확정입니다. 아래 라벨 사례와 실제 형상을 비교해 확인하세요.',
                      recommended_checks=['표시 부위를 확대한 사진과 다른 각도 사진으로 실제 형상을 확인하세요.'])
    return result
