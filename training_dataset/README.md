# MM 전자부품 결함 증강 데이터셋

- 원본 14장 (sha256 검증 통과) + 파생 150장 = 학습 이미지 164장, 박스 186개
- 클래스: 0 fracture, 1 dent, 2 porosity, 3 missing_feature (원본 라벨 그대로, 신규 클래스 없음)
- 학습 세트에 홀드아웃 검증 원본은 포함하지 않음. 재학습 실행본에서는 기존 원본 4장(A156_reference_10, A176_reference_06, A276_reference_02, A376_reference_02)을 images/val 및 labels/val에 그대로 연결했음. 검증 사진은 증강하지 않음.
- 정상 부품 사진 없음: 라벨 없는 이미지를 정상으로 지정하지 않음

## 구성
images/train, labels/train (YOLO), annotations_coco.json, manifest.csv/json (source_image_id·시드·변환값),
augmentation_config.json, dataset.yaml, overlays/ (라벨 검수 시트), augment.py, make_overlays.py

## 재현
python augment.py MM_Augmentation_Training_Data.json out_dir   # 시드 20261021 고정

## 박스 처리 기준
- 사각형 4개 꼭짓점을 같은 아핀 행렬로 변환 후 외접 박스 사용 (회전 시 박스가 약간 커짐)
- 가시 면적 < 60% 또는 한 변 < 8px 인 박스가 하나라도 생기면 그 샘플 전체를 버리고 다시 뽑음 (이미지에 결함이 남았는데 라벨만 빠지는 경우 방지)
- 빈 영역은 회색(114) 고정 채움 (반사 채움은 라벨 없는 결함 복제 위험)

## 주의
- 같은 source_image_id의 파생본은 모두 학습 세트에만 둘 것. 파생본을 무작위로 train/val 분할하지 말고 source_image_id 단위로 나눌 것
- 검증은 홀드아웃 원본으로만 수행
- 원본 라벨은 factory_verified=false (육안 라벨) 상태
