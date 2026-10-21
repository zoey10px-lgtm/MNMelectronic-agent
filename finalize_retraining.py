"""Write measured comparisons after the one requested augmented-data run."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
 comparison=json.loads((ROOT/'RETRAINING_COMPARISON.json').read_text(encoding='utf-8'))
 candidate=json.loads((ROOT/'AUGMENTED_MODEL_EVALUATION.json').read_text(encoding='utf-8'))
 previous=json.loads((ROOT/'PRE_RETRAINING_EVALUATION.json').read_text(encoding='utf-8'))
 run=ROOT/candidate['training_run']
 dest=ROOT/'training_history/augmented_retraining';dest.mkdir(parents=True,exist_ok=True)
 for p in run.iterdir():
  if p.is_file() and p.suffix in ('.csv','.yaml','.png','.jpg'):shutil.copy2(p,dest/p.name)
 import csv
 rows=list(csv.DictReader((run/'results.csv').open()))
 comparison['epochs_completed']=len(rows)
 # Protect a previously passing functional photo regression independently
 # from the four-photo validation ranking.
 old_case=previous['challenges'][0]['typed'];new_case=candidate['challenges'][0]['typed']
 regression_ok=(new_case['tp']>=old_case['tp'] and new_case['fp']<=old_case['fp'])
 comparison['previous_photo_regression_passed']=regression_ok
 if comparison['active_model']=='retrained' and not regression_ok:
  shutil.copy2(ROOT/'weights/previous_model.pt',ROOT/'weights/defect_types.pt')
  (ROOT/'MODEL_EVALUATION.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),encoding='utf-8')
  shutil.copytree(ROOT/'evaluation/pre_retraining',ROOT/'evaluation/repaired',dirs_exist_ok=True)
  comparison['active_model']='previous_retained_photo_regression'
 (ROOT/'RETRAINING_COMPARISON.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2),encoding='utf-8')
 lineage=json.loads((ROOT/'TRAINING_LINEAGE.json').read_text(encoding='utf-8'))
 lineage['stages']=[s for s in lineage['stages'] if s['name']!='supplied_augmentation']
 lineage['stages'].append(dict(name='supplied_augmentation',source='weights/previous_model.pt',source_sha256=previous['model_sha256'],epochs_completed=len(rows),training_images=164,unique_originals=14,boxes=186,config='training_history/augmented_retraining/args.yaml',results='training_history/augmented_retraining/results.csv',activation='selected' if comparison['active_model']=='retrained' else 'not_selected'))
 lineage['selected_model_sha256']=hashlib.sha256((ROOT/'weights/defect_types.pt').read_bytes()).hexdigest()
 if comparison['active_model']=='retrained':
  lineage['selected_experiment']='supplied_augmentation'
  for s in lineage['stages']:
   if s['name']!='supplied_augmentation' and s.get('activation')=='selected':s['activation']='previously_selected'
 lineage['note']='Training history preserves the exact paths used during each run. The supplied augmentation contains 164 training views from 14 originals; 4 unchanged heldout originals are separate. App inference uses weights/defect_types.pt, checked against MODEL_EVALUATION.json.'
 (ROOT/'TRAINING_LINEAGE.json').write_text(json.dumps(lineage,ensure_ascii=False,indent=2),encoding='utf-8')
 old=comparison['previous']['val'];new=comparison['retrained']['val']
 active='재학습 모델' if comparison['active_model']=='retrained' else '기존 모델 유지'
 text=f'''# 증강 자료 재학습 결과 (2026-10-21)

받은 MM_augmented_dataset.zip의 사진·라벨을 그대로 사용해 한 번 재학습했습니다.

- 학습 입력: 원본 14장 + 파생 150장 = 164장, 결함 라벨 186개
- 검증 입력: 기존 학습 제외 원본 4장. 파생본으로 검증 세트를 만들지 않았습니다.
- 시작 모델: weights/previous_model.pt (이전 실행 모델)
- 학습 완료: {len(rows)} epoch / 요청 상한 40 epoch, 정체 시 조기 종료
- 입력 640, batch 8, AdamW, 시작 학습률 0.0001, seed 42
- 자료에 증강이 이미 적용되어 추가 온라인 기하·색 증강은 껐습니다.
- 비교 추론: 같은 detector.py, 문턱값 0.25, 위치 일치 IoU 0.5 이상 + 유형 일치

| 같은 검증 원본 4장 | 재학습 전 | 재학습 후 |
|---|---:|---:|
| 위치·유형이 맞은 결함 | {old['tp']} / 4 | {new['tp']} / 4 |
| 놓친 결함 | {old['fn']} | {new['fn']} |
| 추가 오검출 | {old['fp']} | {new['fp']} |
| Precision | {old['precision']:.3f} | {new['precision']:.3f} |
| Recall | {old['recall']:.3f} | {new['recall']:.3f} |

화면 추출 하우징 균열 사진의 별도 회귀 시험: 이전 TP {old_case['tp']}, FP {old_case['fp']} / 재학습 TP {new_case['tp']}, FP {new_case['fp']}.

현재 앱 선택: **{active}**.

학습 완료 후보 파일은 weights/augmented_candidate.pt입니다. 앱이 실행하는 파일은 weights/defect_types.pt이며, MODEL_EVALUATION.json에 해당 파일의 평가와 해시가 연결되어 있습니다.

검증 사진은 4장이고 실물 부품 단위 독립성은 확인되지 않았습니다. 동일 원본의 증강 150장을 독립 원본 150장으로 세지 않습니다. 정상 부품 사진은 없으며 새 결함 유형은 추가하지 않았습니다.

상세 사진별 비교: AUGMENTED_MODEL_REVIEW.html 및 evaluation/augmented_retraining/report.json.
현재 앱 모델의 예측: MODEL_REVIEW.html.
학습 설정과 곡선: training_history/augmented_retraining/.
'''
 (ROOT/'RETRAINING_RESULT.md').write_text(text,encoding='utf-8')
 guide=f'''M&M Electronics 증강 자료 재학습 실행본 6.1

실행: 새 빈 폴더에 압축을 풀고 START.bat (Windows) 또는 START.command (Mac)을 실행합니다.
학습된 모델을 포함했습니다. 첫 실행 시 패키지를 자동 설치합니다.

재학습 자료: 원본 14장 + 증강 150장 = 164장, 라벨 186개.
이전과 같은 검증 원본 4장을 연결했습니다.
학습 완료 {len(rows)} epoch.
검증 위치·유형 일치: 이전 {old['tp']}/4 → 재학습 {new['tp']}/4.
추가 오검출: 이전 {old['fp']} → 재학습 {new['fp']}.
현재 앱 선택: {active}.

파일 안내
RETRAINING_RESULT.md: 이번 재학습의 결과와 비교
RETRAINING_COMPARISON.json: 이전/이후 측정 수치와 선택 근거
AUGMENTED_MODEL_EVALUATION.json: 새 후보 모델의 사진별 예측
MODEL_EVALUATION.json: 현재 앱 모델의 사진별 예측과 해시
AUGMENTED_MODEL_REVIEW.html: 원본 라벨과 재학습 전/후 예측을 눈으로 비교
MODEL_REVIEW.html: 현재 앱 모델의 실제 예측 확인
weights/defect_types.pt: 현재 앱이 실행하는 모델
weights/augmented_candidate.pt: 이번에 재학습한 후보 모델
weights/previous_model.pt: 재학습 전 모델
training_dataset/images/train, labels/train: 받은 증강 학습 자료 164쌍
training_dataset/images/val, labels/val: 그대로 보존한 검증 원본 4쌍
annotations/originals: 제공된 원본 31장 전체
training_history/augmented_retraining: 실제 학습 설정, 기록, 곡선

재학습: TRAIN_4CLASS.bat 또는 TRAIN_4CLASS.command.
학습 경로는 train_augmented.py가 현재 폴더 기준으로 구성합니다.
원본별 학습/검증 구분과 클래스 ID 0~3을 유지합니다.
제품 모델 자동 추정은 등록 사진과 외형 비교이며, 새 제품의 이름은 미식별로 표시합니다.
'''
 for name in ('README.md','READ_THIS_FIRST_KO.txt','README_실행안내.txt','먼저읽기_실행방법.md'):(ROOT/name).write_text(guide,encoding='utf-8')
 history=ROOT/'MODEL_REPORT_BEFORE_AUGMENTATION.md'
 if not history.exists():shutil.copy2(ROOT/'MODEL_REPORT.md',history)
 (ROOT/'MODEL_REPORT.md').write_text(text+'\n이전 수정·평가 이력: MODEL_REPORT_BEFORE_AUGMENTATION.md\n',encoding='utf-8')
 # Human review must show the requested candidate even if production retains old.
 from build_review import main as build
 build('AUGMENTED_MODEL_EVALUATION.json','evaluation/augmented_retraining','AUGMENTED_MODEL_REVIEW.html')
 build()
 html=(ROOT/'MODEL_REVIEW.html').read_text(encoding='utf-8')
 if comparison['active_model']!='retrained':
  html=html.replace('수정 모델의 실제 예측','현재 앱에서 유지한 모델의 실제 예측')
  html=html.replace('<h1>M&M 모델 점검 결과</h1>','<h1>M&M 모델 점검 결과</h1><p>재학습 후보는 기존 모델보다 개선되지 않아 앱은 기존 모델을 유지합니다. 후보의 상세 결과는 RETRAINING_RESULT.md와 evaluation/augmented_retraining/report.json에 있습니다.</p>')
 (ROOT/'MODEL_REVIEW.html').write_text(html,encoding='utf-8')
 print(json.dumps(comparison,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
