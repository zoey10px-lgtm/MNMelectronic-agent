"""Create a local, readable side-by-side evidence report from saved predictions."""
import html,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main(report_name='MODEL_EVALUATION.json', prediction_dir='evaluation/repaired', output_name='MODEL_REVIEW.html'):
 report=json.loads((ROOT/report_name).read_text(encoding='utf-8'))
 baseline=json.loads((ROOT/'PRE_RETRAINING_EVALUATION.json').read_text(encoding='utf-8'))
 blocks=[]
 for c in report['cases']:
  if c['variant']!='full':continue
  ident=c['source_id'];m=c['typed'];role='학습 사진' if c['split']=='train' else '학습 제외 검증 사진'
  preds=', '.join(f"{p['label']} {p['confidence']:.2f}" for p in c['predictions']) or '검출 없음'
  blocks.append(f'''<article><h2>{html.escape(ident)} <small>{role}</small></h2><p>위치·유형 일치 {m['tp']} / 놓침 {m['fn']} / 오검출 {m['fp']} · {html.escape(preds)}</p><div class="photos"><figure><figcaption>등록 정답 라벨</figcaption><img src="annotations/overlays/{ident}.jpg"></figure><figure><figcaption>재학습 전 모델의 실제 예측</figcaption><img src="evaluation/pre_retraining/{ident}__full.jpg"></figure><figure><figcaption>수정 모델의 실제 예측</figcaption><img src="evaluation/repaired/{ident}__full.jpg"></figure></div></article>''')
 ext=report['challenges'][0]
 final=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><title>M&M 모델 점검 결과</title><style>body{{font:15px/1.7 system-ui,sans-serif;max-width:1250px;margin:40px auto;padding:0 20px;color:#16392e;background:#f6f8f5}}h1{{font-size:32px}}article{{margin:28px 0;background:white;border:1px solid #d9e1da;padding:20px;border-radius:12px}}h2{{font-size:19px}}small{{font-weight:400;color:#677c70}}.photos{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}figure{{margin:0}}img{{max-width:100%;height:330px;object-fit:contain;background:#eef3ef}}pre{{white-space:pre-wrap;background:#edf2ec;padding:16px}}@media(max-width:700px){{.photos{{grid-template-columns:1fr}}}}</style><h1>M&M 모델 점검 결과</h1><p>모델이 실제로 예측한 위치와 유형을 정답 자료 옆에 표시했습니다. 저장된 정답 라벨은 모델 예측을 대신하지 않습니다.</p><p>학습 원본 14장 / 검증 원본 4장 · 점수 문턱 0.25 · 위치 일치 IoU 0.5 이상 · 유형도 같을 때 일치로 계산</p><h2>수정 모델 측정 결과</h2><pre>{html.escape(json.dumps(report['summary'],ensure_ascii=False,indent=2))}</pre><p>검증 원본이 4장이고 정상 부품 사진이 없어 전체 사용 환경의 성능을 대표하지 않습니다. 같은 사진의 JPEG·밝기 파생본은 독립 사진 수에 더하지 않았습니다.</p><article><h2>학습에 넣지 않은 하우징 균열 사진</h2><div class="photos"><figure><figcaption>고객 화면에서 추출한 시험 입력</figcaption><img src="evaluation/external_housing.png"></figure><figure><figcaption>재학습 전 모델 예측</figcaption><img src="evaluation/pre_retraining/external_housing.jpg"></figure><figure><figcaption>수정 모델 예측</figcaption><img src="evaluation/repaired/external_housing.jpg"></figure></div><p>위치·유형 일치: {ext['typed']['tp']} / 오검출: {ext['typed']['fp']} / 놓침: {ext['typed']['fn']}</p></article>{''.join(blocks)}<p>상세 원자료: <a href="MODEL_EVALUATION.json">MODEL_EVALUATION.json</a> · <a href="DATA_AUDIT.json">DATA_AUDIT.json</a> · <a href="MODEL_REPORT.md">모델 설명</a></p></html>'''
 final=final.replace('evaluation/repaired/',prediction_dir+'/')
 final=final.replace('수정 모델','재학습 후보 모델' if report_name=='AUGMENTED_MODEL_EVALUATION.json' else '현재 앱 모델')
 final=final.replace('href="MODEL_EVALUATION.json">MODEL_EVALUATION.json',f'href="{report_name}">{report_name}')
 (ROOT/output_name).write_text(final,encoding='utf-8')
if __name__=='__main__':main()
