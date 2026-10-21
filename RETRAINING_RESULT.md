# 증강 자료 재학습 결과 (2026-10-21)

받은 MM_augmented_dataset.zip의 사진·라벨을 그대로 사용해 한 번 재학습했습니다.

- 학습 입력: 원본 14장 + 파생 150장 = 164장, 결함 라벨 186개
- 검증 입력: 기존 학습 제외 원본 4장. 파생본으로 검증 세트를 만들지 않았습니다.
- 시작 모델: weights/previous_model.pt (이전 실행 모델)
- 학습 완료: 24 epoch / 요청 상한 40 epoch, 정체 시 조기 종료
- 입력 640, batch 8, AdamW, 시작 학습률 0.0001, seed 42
- 자료에 증강이 이미 적용되어 추가 온라인 기하·색 증강은 껐습니다.
- 비교 추론: 같은 detector.py, 문턱값 0.25, 위치 일치 IoU 0.5 이상 + 유형 일치

| 같은 검증 원본 4장 | 재학습 전 | 재학습 후 |
|---|---:|---:|
| 위치·유형이 맞은 결함 | 1 / 4 | 1 / 4 |
| 놓친 결함 | 3 | 3 |
| 추가 오검출 | 3 | 0 |
| Precision | 0.250 | 1.000 |
| Recall | 0.250 | 0.250 |

화면 추출 하우징 균열 사진의 별도 회귀 시험: 이전 TP 1, FP 0 / 재학습 TP 1, FP 0.

현재 앱 선택: **재학습 모델**.

학습 완료 후보 파일은 weights/augmented_candidate.pt입니다. 앱이 실행하는 파일은 weights/defect_types.pt이며, MODEL_EVALUATION.json에 해당 파일의 평가와 해시가 연결되어 있습니다.

검증 사진은 4장이고 실물 부품 단위 독립성은 확인되지 않았습니다. 동일 원본의 증강 150장을 독립 원본 150장으로 세지 않습니다. 정상 부품 사진은 없으며 새 결함 유형은 추가하지 않았습니다.

상세 사진별 비교: AUGMENTED_MODEL_REVIEW.html 및 evaluation/augmented_retraining/report.json.
현재 앱 모델의 예측: MODEL_REVIEW.html.
학습 설정과 곡선: training_history/augmented_retraining/.
