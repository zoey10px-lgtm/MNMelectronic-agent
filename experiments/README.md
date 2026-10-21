# 전달받은 실험 코드

아래 명령은 프로젝트 최상위 폴더에서 실행합니다. 상대 경로는 프로젝트 최상위를 기준으로 해석합니다. 현재 앱은 기존 `weights/defect_types.pt`를 계속 사용합니다. 실험을 실행해도 앱 가중치를 자동 교체하지 않습니다.

## E1: 원본 14장과 온라인 증강

```bash
python experiments/e1_full_photo_aug/build_exp_data.py
python experiments/e1_full_photo_aug/train_exp.py E1_orig14_aug100 experiments/e1_full_photo_aug/data_orig/data.yaml 100 on
python experiments/e1_full_photo_aug/eval_exp.py runs/experiments/E1_orig14_aug100/weights/last.pt evaluation/e1_reproduced
```

## 스티커 마스킹 비교

```bash
python experiments/sticker_mask/mask_sticker.py
python experiments/sticker_mask/eval_mask.py
```

E1 모델이 없으면 마스킹 비교는 현재 앱 모델만 평가합니다. E1의 별도 실행 가중치와 결과는 전달받은 code-only ZIP에 없어서 포함하지 않았습니다. 기존 학습 이력에 기록된 당시 절대 경로는 이력 보존을 위해 유지했습니다.
