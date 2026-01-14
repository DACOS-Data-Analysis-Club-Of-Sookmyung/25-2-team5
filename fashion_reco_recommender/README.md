# Fashion Recommender (Rule-based)

체형(`body_type`) + 11문항 스타일 타입 설문(1/2/3 다수결) 기반으로  
`items_tags.parquet`에서 Top-K 의류를 추천하고 `outputs/sample_outfit.json`을 생성하는 룰 기반 추천 시스템입니다.

---

## 1. Project Structure

fashion_reco_recommender/
├── src/
│   └── recommender.py
├── data/
│   ├── items_tags.parquet
│   ├── body_profile.json
│   ├── style_profile.json
│   └── items_index.csv
├── outputs/ # 실행 후 sample_outfit.json 생성
├── requirements.txt
└── README.md
```

- 'src/' : 실행 코드
- 'data/' : 추천에 필요한 데이터/프로필 파일
- 'outputs' : 실행 결과(JSON) 저장 폴더 (실행 시 자동 생성 가능)

---

## 2. Requirements

- Python 3.9+
- pandas
- pyarrow (parquet 로드용)

설치:

```bash
pip install -r requirements.txt
```

> `items_tags.parquet`을 읽기 위해 `pyarrow`가 필요합니다.

---

## 3. Data Files

아래 3개 파일이 'data/' 폴더에 있어야 실행됩니다.

- data/items_tags.parquet
    - 별도의 데이터 전처리/태깅 파이프라인에서 생성된 파일이며,  
    본 레포지토리는 생성된 데이터를 입력으로 받아 추천 결과를 생성합니다.

- data/body_profile.json
- data/style_profile.json

---

## 4. Run

### 4-1) 레포 다운로드

**ZIP 다운로드**
1. GitHub 레포 → `Code` → `Download ZIP`
2. 압축 해제 후 폴더로 이동

---

### 4-2) 레포 루트에서 터미널 열기

반드시 아래 폴더(루트)에서 실행해야 합니다.

예시:
```
.../fashion_reco_recommender/
```
여기서 `data/`, `src/`, `requirements.txt`가 보여야 정상입니다.

---

### 4-3) (선택) 한글 깨짐 방지 (Windows PowerShell)

```powershell
chcp 65001
```

---

### 4-4) 패키지 설치

```bash
pip install -r requirements.txt
```

---

### 4-5) 대화형 실행 (CLI)

```powershell
python -m src.recommender
```

> `recommender.py`는 대화형(CLI) 방식으로 입력을 받습니다.

---

## 5. 실행 흐름

실행하면 아래 순서대로 질문이 나옵니다.

1. 체형(body_type) 선택 (번호 또는 문자열)

2. 스타일 설문 11문항 응답 (1=straight, 2=wave, 3=natural)

3. Top-K 입력

4. avatar_id / age_group 입력 (기본값 사용 가능)

5. 추천 결과 생성 및 저장

---

## 6. Output

실행이 끝나면 아래 파일이 생성됩니다.
- outputs/sample_outfit.json

JSON 예시 

{
  "meta": {
    "created_at": "2026-01-14T16:10:00",
    "engine": "rule_based"
  },
  "avatar": {
    "avatar_id": "kr_female_20s_01",
    "age_group": 20,
    "body_type": "hourglass",
    "style_type": "straight",
    "style_survey_answers": [1,1,1,1,1,1,1,1,1,1,1]
  },
  "outfits": [
    {
      "rank": 1,
      "mesh_id": "...",
      "category_main": "dress",
      "length": "midi",
      "silhouette": "a_line",
      "fit": "regular",
      "waist_emphasis": "high",
      "exposure": "low",
      "score": 1.23,
      "reasons": ["[BODY] ...", "[STYLE] ..."]
    }
  ]
}


## 7. SMPL / Virtual Fitting Integration

다음 규칙으로 로드 가능 

mesh_path = {DATA_ROOT}/filtered_registered_mesh/{mesh_id}/