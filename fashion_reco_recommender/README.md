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
├── outputs/



- src/ : 실행 코드
- data/ : 추천에 필요한 데이터/프로필 파일
- outputs : 실행 결과(JSON) 저장 폴더 (실행 시 자동 생성 가능)
- scripts/ : 스크립트 모음

---

## 2. Requirements

- Python 3.9+
- pandas
- pyarrow (parquet 로드용)

설치:

pip install -r requirements.txt

requirements.txt 예시:
pandas>=2.0.0
pyarrow>=14.0.0

## 3. Data Files

아래 3개 파일이 data/ 폴더에 있어야 실행됩니다.

- data/items_tags.parquet
    > `items_tags.parquet`은 별도의 데이터 전처리/태깅 파이프라인에서 생성된 파일이며,  
    > 본 레포지토리는 생성된 데이터를 입력으로 받아 추천 결과를 생성합니다.

- data/body_profile.json
- data/style_profile.json

## 4. Run

프로젝트 루트에서 실행:

python src/recommender.py


실행 흐름:

1. 체형(body_type) 선택 (번호 또는 문자열)

2. 스타일 설문 11문항 응답 (1=straight, 2=wave, 3=natural)

3. Top-K 입력

4. 추천 결과 출력

5. outputs/sample_outfit.json 저장

## 5. Output

실행이 끝나면 아래 파일이 생성됩니다.
- outputs/sample_outfit.json

예시 

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


## 6. SMPL / Virtual Fitting Integration

다음 규칙으로 로드 가능 

mesh_path = {DATA_ROOT}/filtered_registered_mesh/{mesh_id}/