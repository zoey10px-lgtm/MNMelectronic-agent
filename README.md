# M&M Electronics — 통합 중간점검 실행본

기존 전체 패키지의 웹 화면·원본·라벨·증강 데이터·학습 가중치에 제공받은 코드와 실험 스크립트를 합친 실행본입니다. 추가 학습 없이 실행할 수 있습니다.

## GitHub에 올리기

ZIP을 풀고 이 README와 `app.py`, `requirements.txt`, `weights/`, `templates/`가 있는 폴더의 **내용 전체**를 저장소 최상위에 올립니다. ZIP 파일 자체를 올리는 방식으로는 서버가 실행되지 않습니다. `.env.example`은 설정 예시이고 실제 비밀번호·API 키를 담은 `.env`는 커밋하지 않습니다.

## 내 컴퓨터에서 실행

- Windows: Python 3.12 설치 후 `START.bat` 실행.
- Mac: Python 3.12 설치 후 `START.command` 실행.
- 이미 의존성을 설치했다면 `python serve.py`.
- 주소: http://127.0.0.1:8000/#support

## Render에서 중간점검

| 설정 | 값 |
|---|---|
| 서비스 종류 | Web Service / Python |
| Root Directory | 이 README가 저장소 최상위면 비워둠 |
| Build Command | `bash BUILD_RENDER.sh` |
| Start Command | `python serve.py` |
| Health Check Path | `/health` |
| Python | `PYTHON_VERSION=3.12.12` |
| 환경변수 | `OPENAI_API_KEY`, `ADMIN_PASSWORD`, `SECRET_KEY`를 서비스 환경에서 설정. `ADMIN_USERNAME=admin`, `OPENAI_MODEL=gpt-5.4-mini` |

`BUILD_RENDER.sh`는 CPU용 PyTorch를 먼저 설치합니다. 서버는 클라우드에서 `0.0.0.0:$PORT`로 실행하며 브라우저를 자동으로 열지 않습니다. 기존 서비스에서도 위 Build/Start 설정을 맞춥니다. 저장소의 `assets/`에는 원본·가중치·학습 자료가 묶여 있으며 빌드 시 자동 복원됩니다. 모든 묶음과 복원 파일의 SHA-256을 검증합니다.

문의 기록과 첨부 사진은 `data/`에 저장됩니다. 재배포 후에도 기록을 보존하려면 영구 저장 경로를 `MM_DATA_DIR`로 지정합니다. 관리자 계정은 `.env.example`을 참고합니다.

## 중간점검 순서

1. 홈페이지에서 한국어·영어·베트남어 전환과 고객지원 화면 확인.
2. `sample_photos/`의 사진을 업로드하고 YOLO의 박스·유형 출력 확인.
3. 문의 접수 확정 후 접수 번호·조회·관리자 화면 확인.
4. 새 사진과 기존 등록 사진을 각각 테스트. 등록 라벨과 실제 모델 예측은 화면에서 구분됩니다.
5. `MODEL_REVIEW.html`, `MODEL_REPORT.md`, `CHECKPOINT_VERIFICATION.json`으로 현재 상태 확인.

## 포함 파일

| 경로 | 내용 |
|---|---|
| `templates/index.html` | 기존 회사 홈페이지와 고객지원·관리자 UI |
| `app.py`, `serve.py` | Flask API·문의 DB·Waitress 서버 |
| `weights/defect_types.pt` | 앱이 실제로 사용하는 학습 가중치 |
| `weights/`의 나머지 파일 | 이전·후보·사전학습 가중치 |
| `annotations/originals/` | 원본 사진 31장 |
| `annotations/records.json` | 사진별 라벨과 학습·검증 구분 |
| `training_dataset/` | 증강 학습 164장·검증 4장과 YOLO 라벨 |
| `rag/` | 제품·문의 참고 자료 |
| `data_pipeline/` | 전달받은 증강·라벨 확인 코드 |
| `experiments/` | 전달받은 별도 실험 코드. 실행 경로를 현재 폴더 기준으로 정리 |
| `training_history/`, `evaluation/` | 기존 학습 이력과 평가 결과 |
| `MERGE_REPORT.json` | 파일별 통합 기록과 원본 ZIP 해시 |

## 현재 모델의 측정 범위

현재 가중치의 기존 검증 기록은 원본 4장 중 위치·유형 일치 1개, 추가 오검출 0개입니다. 이번 작업은 파일 통합과 실행 점검이며 재학습을 수행하지 않았습니다. 긁힘·조립 벌어짐은 현재 네 개 학습 클래스에 포함되지 않습니다. OpenAI API를 통해 사진 관찰, 문의 분류, 권장 조치와 답변 초안을 생성합니다. YOLO 검출 결과와 API 관찰은 구분해 표시합니다. API 키가 없거나 요청에 실패해도 로컬 검사와 문의 접수는 유지됩니다.

학습은 `TRAIN_4CLASS.bat` 또는 `python train_augmented.py`로 별도 실행합니다. 학습 파생본과 검증 원본의 분리를 유지합니다. 실험 재현 방법은 `experiments/README.md`에 있습니다.

## API 키 입력

Render의 서비스 Environment에서 `OPENAI_API_KEY`에 본인의 키를 입력하고 저장·재배포합니다. 키는 GitHub 또는 브라우저 코드에 넣지 않습니다. 모델은 `OPENAI_MODEL`로 바꿀 수 있습니다. `/health`의 `language.configured`로 설정 여부만 확인할 수 있습니다. 실제 API 호출 성공 여부는 사진·문의 분석 결과에서 확인합니다.

운영 서버의 관리자 로그인은 `ADMIN_PASSWORD` 설정 후 활성화됩니다. 한국어·영어·베트남어는 상단 언어 선택에서 전환합니다. 고객이 선택한 언어로 API 답변을 생성하며, 관리자 화면에도 답변 초안과 확인할 사항을 저장합니다.
