import os
import json
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter

import pandas as pd


STYLE_NUM_TO_TYPE = {1: "straight", 2: "wave", 3: "natural"}

STYLE_SURVEY_11: List[Tuple[str, List[str]]] = [
    ("살이 찌는 부위와 형태", [
        "상체에 살이 많이 붙는다(등/배/팔뚝/허벅지)",
        "상체가 날씬하고 하체에 살이 붙는다(허벅지/엉덩이)",
        "전체적으로 살이 붙는다, 어깨가 넓고 덩치가 커지는 타입",
    ]),
    ("몸의 두께감", [
        "옆모습이 두툼한 느낌이 든다.",
        "옆모습이 플랫하다",
        "옆모습의 뼈대감이 두툼하다",
    ]),
    ("살의 질감", [
        "살이 단단하고 근육처럼 보임",
        "살이 말랑하고 부드러움",
        "살이 퍼석하고 질긴 느낌",
    ]),
    ("손의 모양", [
        "손등의 살이 두툼하고 뼈가 잘 보이지 않는다",
        "손가락이 가늘고 손의 두께가 얇다",
        "손의 뼈대가 큼직하고 두툼하다",
    ]),
    ("두상", [
        "얼굴에 비해 두상이 작다, 비교적 동글동글",
        "뒤통수가 납작하고 평평한 두상",
        "얼굴에 비해 두상이 크다, 두상이 울퉁불퉁한 편",
    ]),
    ("목", [
        "목이 통통하고 살이 많은 타입, 목이 약간 두껍고 승모근이 많다",
        "목이 가늘고 얇다",
        "목이 튼튼하고 뼈가 두드러짐",
    ]),
    ("쇄골", [
        "쇄골이 많이 도드라지지 않는다",
        "쇄골이 얇고 가늘게 발달",
        "쇄골이 큼직하고 두껍게 발달",
    ]),
    ("어깨", [
        "어깨가 동그랗다",
        "어깨가 가늘고 얇고 쳐져 있다",
        "어깨가 두껍고 큼직, 어깨가 넓은 편, 위로 솟아있는 편",
    ]),
    ("가슴", [
        "가슴이 높고 큰 타입, 유장이 짧아 가슴이 위쪽에 있는 느낌",
        "윗가슴이 꺼져있고 유장이 긴 타입, 버선코 모양이며 플랫한 타입",
        "가슴뼈가 많이 발달되어 있다, 새가슴 타입이다.",
    ]),
    ("엉덩이", [
        "볼록한 오리 궁댕이",
        "물방울 형태",
        "플랫한 타입",
    ]),
    ("허리", [
        "허리가 잘록하지 않거나 아주 약간 잘록하다",
        "허리가 얇고 골반이 큰 타입",
        "허리가 잘록하지 않고 배가 납작한 타입",
    ]),
]


def infer_style_type_from_11_survey(answers: List[int]) -> str:
    c = Counter(answers)
    max_cnt = max(c.values())
    winners = [k for k, v in c.items() if v == max_cnt]
    if len(winners) == 1:
        return STYLE_NUM_TO_TYPE[winners[0]]
    for p in [3, 2, 1]:
        if p in winners:
            return STYLE_NUM_TO_TYPE[p]
    return STYLE_NUM_TO_TYPE[winners[0]]


@dataclass
class Rule:
    when: Dict[str, Any]
    score: float
    reason: str
    hard_filter: bool = False


def _match_condition(item: Dict[str, Any], cond: Dict[str, Any]) -> bool:
    for k, v in cond.items():
        if k not in item:
            return False
        iv = item.get(k)
        if isinstance(v, list):
            if iv not in v:
                return False
        else:
            if iv != v:
                return False
    return True


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _extract_profile_map(profile_json: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    if not isinstance(profile_json, dict):
        return {}

    if "profiles" in profile_json and isinstance(profile_json["profiles"], list):
        out = {}
        for p in profile_json["profiles"]:
            if not isinstance(p, dict):
                continue
            pid = p.get("profile_id") or p.get("style_id") or p.get("body_id")
            if pid:
                out[str(pid)] = p
        if out:
            return out

    if "profiles" in profile_json and isinstance(profile_json["profiles"], dict):
        return {k: v for k, v in profile_json["profiles"].items() if isinstance(v, dict)}

    direct = {k: v for k, v in profile_json.items() if isinstance(v, dict)}
    if any(k in direct for k in ["straight", "wave", "natural"]):
        return {k: direct[k] for k in ["straight", "wave", "natural"] if k in direct}

    return {}


def _parse_rules(profile: Dict[str, Any]) -> List[Rule]:
    rules: List[Rule] = []

    rules_raw = profile.get("rules", [])
    if isinstance(rules_raw, list):
        for r in rules_raw:
            if not isinstance(r, dict):
                continue
            when = r.get("when", {})
            if isinstance(when, dict):
                rules.append(
                    Rule(
                        when=when,
                        score=float(r.get("score", 0.0)),
                        reason=str(r.get("reason", "")),
                        hard_filter=bool(r.get("hard_filter", False)),
                    )
                )

    prefer = profile.get("prefer", [])
    if isinstance(prefer, list):
        for r in prefer:
            if isinstance(r, dict) and isinstance(r.get("if"), dict):
                rules.append(
                    Rule(
                        when=r["if"],
                        score=float(r.get("score", 0.0)),
                        reason=str(r.get("reason", "")),
                        hard_filter=False,
                    )
                )

    avoid = profile.get("avoid", [])
    if isinstance(avoid, list):
        for r in avoid:
            if isinstance(r, dict) and isinstance(r.get("if"), dict):
                rules.append(
                    Rule(
                        when=r["if"],
                        score=float(r.get("score", 0.0)),
                        reason=str(r.get("reason", "")),
                        hard_filter=False,
                    )
                )

    micro = profile.get("optional_micro_bonus", [])
    if isinstance(micro, list):
        for r in micro:
            if isinstance(r, dict) and isinstance(r.get("if"), dict):
                rules.append(
                    Rule(
                        when=r["if"],
                        score=float(r.get("score", 0.0)),
                        reason=str(r.get("reason", "")),
                        hard_filter=False,
                    )
                )

    return rules


class RuleBasedRecommender:
    def __init__(self, items_path: str, body_profile_path: str, style_profile_path: str):
        self.items = pd.read_parquet(items_path).fillna("")
        self.body_profiles = _extract_profile_map(_load_json(body_profile_path))
        style_json = _load_json(style_profile_path)
        self.style_profiles = _extract_profile_map(style_json)

        if not self.style_profiles:
            cand = {}
            for k in ["straight", "wave", "natural"]:
                if isinstance(style_json.get(k), dict):
                    cand[k] = style_json[k]
            if cand:
                self.style_profiles = cand

    def recommend(self, body_type: str, style_type: str, top_k: int = 5, min_score: Optional[float] = None):
        if body_type not in self.body_profiles:
            raise ValueError(f"Unknown body_type: {body_type}. Available: {list(self.body_profiles.keys())}")
        if style_type not in self.style_profiles:
            raise ValueError(f"Unknown style_type: {style_type}. Available: {list(self.style_profiles.keys())}")

        body_rules = _parse_rules(self.body_profiles[body_type])
        style_rules = _parse_rules(self.style_profiles[style_type])

        results = []
        for _, row in self.items.iterrows():
            item = row.to_dict()
            combo_score = 0.0
            reasons: List[str] = []
            excluded = False

            for rule in body_rules + style_rules:
                if rule.hard_filter and not _match_condition(item, rule.when):
                    excluded = True
                    break
            if excluded:
                continue

            for rule in body_rules:
                if _match_condition(item, rule.when):
                    combo_score += rule.score
                    if rule.reason:
                        reasons.append(f"[BODY] {rule.reason} (+{rule.score:g})")

            for rule in style_rules:
                if _match_condition(item, rule.when):
                    combo_score += rule.score
                    if rule.reason:
                        reasons.append(f"[STYLE] {rule.reason} (+{rule.score:g})")

            if min_score is not None and combo_score < min_score:
                continue

            out = dict(item)
            out["combo_score"] = float(combo_score)
            out["reasons"] = reasons
            results.append(out)

        results.sort(key=lambda x: x.get("combo_score", 0.0), reverse=True)
        return results[:top_k]


def _input_int_in_set(prompt: str, allowed: set) -> int:
    while True:
        s = input(prompt).strip()
        if s.isdigit() and int(s) in allowed:
            return int(s)
        print(" 1/2/3 중 하나로 입력해줘.")


def _ask_style_type_by_11_survey() -> Tuple[str, List[int]]:
    print("\n=== 스타일 타입 설문 (총 11문항) ===")
    print("각 문항마다 1/2/3 중 하나를 입력하세요. (1=스트레이트, 2=웨이브, 3=네추럴)\n")

    answers: List[int] = []
    for i, (title, choices) in enumerate(STYLE_SURVEY_11, start=1):
        print(f"[{i}/11] {title}")
        for idx, text in enumerate(choices, start=1):
            print(f"  {idx}) {text}")
        ans = _input_int_in_set("선택 (1/2/3): ", {1, 2, 3})
        answers.append(ans)
        print()

    style_type = infer_style_type_from_11_survey(answers)
    print(f" 설문 결과 style_type = {style_type}  (answers={answers})")
    return style_type, answers


def _ask_body_type(available_body_types: List[str]) -> str:
    print("\n=== 체형(body_type) 선택 ===")
    print("아래 목록 중 하나를 그대로 입력하거나, 번호로 선택해줘.\n")
    for i, bt in enumerate(available_body_types, start=1):
        print(f"  {i}) {bt}")

    while True:
        s = input("\nbody_type (번호 또는 문자열): ").strip()
        if s.isdigit():
            idx = int(s)
            if 1 <= idx <= len(available_body_types):
                return available_body_types[idx - 1]
        if s in available_body_types:
            return s
        print(" 목록에 없는 body_type이야.")


def run_cli():
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    items_path = os.path.join(ROOT, "data", "items_tags.parquet")
    body_profile_path = os.path.join(ROOT, "data", "body_profile.json")
    style_profile_path = os.path.join(ROOT, "data", "style_profile.json")


    engine = RuleBasedRecommender(items_path, body_profile_path, style_profile_path)

    body_type = _ask_body_type(sorted(engine.body_profiles.keys()))
    style_type, answers = _ask_style_type_by_11_survey()

    print("\n=== 추천 옵션 ===")
    top_k = int(input("top_k (기본 5): ").strip() or "5")

    recs = engine.recommend(body_type=body_type, style_type=style_type, top_k=top_k)

    print("\n=== 추천 결과 ===")
    if not recs:
        print(" 결과가 비었어.")
        return

    for i, r in enumerate(recs, start=1):
        print(f"\n[{i}] mesh_id={r.get('mesh_id')}  score={r.get('combo_score'):.3f}")
        print(f"    category_main={r.get('category_main')} length={r.get('length')} silhouette={r.get('silhouette')} fit={r.get('fit')}")
        for rs in r.get("reasons", [])[:8]:
            print(f"    - {rs}")

    out_dir = os.path.join(ROOT, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "sample_outfit.json")

    avatar_id = input("\navatar_id (기본 kr_female_20s_01): ").strip() or "kr_female_20s_01"
    age_group = int(input("age_group (기본 20): ").strip() or "20")

    payload = {
        "meta": {"created_at": datetime.now().isoformat(timespec="seconds"), "engine": "rule_based"},
        "avatar": {
            "avatar_id": avatar_id,
            "age_group": age_group,
            "body_type": body_type,
            "style_type": style_type,
            "style_survey_answers": answers,
        },
        "outfits": [
            {
                "rank": i + 1,
                "mesh_id": r.get("mesh_id"),
                "category_main": r.get("category_main"),
                "length": r.get("length"),
                "silhouette": r.get("silhouette"),
                "fit": r.get("fit"),
                "waist_emphasis": r.get("waist_emphasis"),
                "exposure": r.get("exposure"),
                "score": r.get("combo_score"),
                "reasons": r.get("reasons", []),
            }
            for i, r in enumerate(recs)
        ],
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n outputs/sample_outfit.json 저장 완료!\n경로: {out_path}")


if __name__ == "__main__":
    run_cli()
