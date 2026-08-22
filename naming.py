"""
naming.py — ② 네이밍 · 카피 담당

담당 기능: 브랜드명 후보 3~5개 + 슬로건 3개
사용 헬퍼: contracts.call_llm(), contracts.extract_json()

[단독 테스트]
    python naming.py
"""

from contracts import call_llm, extract_json


def _format_brief(brief):
    """프롬프트에 넣을 브리프 요약 문자열을 만든다.

    두 함수가 같은 형식을 쓰므로 한 곳에서 만든다.
    값을 브리프에서 읽어오기 때문에 brief.json을 바꾸면
    프롬프트도 자동으로 따라 바뀐다. (특정 브랜드에 고정되지 않음)
    """
    return f"""업종: {brief["industry"]}
타겟: {brief["target"]}
키워드: {", ".join(brief["keywords"])}
톤앤매너: {brief.get("tone") or "지정되지 않음"}
경쟁사: {", ".join(brief.get("competitors") or []) or "없음"}
추가 요청사항: {brief.get("notes") or "없음"}"""


def generate_naming(brief):
    """브랜드명 후보 3~5개를 생성한다.

    Args:
        brief (dict): 브랜드 브리프

    Returns:
        list[dict] | None
        [{"name_ko": str, "name_en": str, "meaning": str}, ...]
        실패 시 None
    """
    prompt = f"""다음 브랜드 브리프를 바탕으로 브랜드명 후보를 생성해주세요.

[브랜드 브리프]
{_format_brief(brief)}

[네이밍 조건]
- 브랜드명 후보를 3~5개 생성하세요.
- 위 키워드가 담고 있는 브랜드 이미지를 적절히 반영하세요.
- 위 톤앤매너에 어울리는 어감으로 지어주세요.
- 기억하기 쉽고 발음하기 쉬워야 합니다.
- 경쟁사와 명확히 구별되는 이름을 제안하세요.
- 추가 요청사항이 있다면 반드시 지켜주세요.
- 각 이름에 한글 표기(name_ko)와 영문 표기(name_en)를 모두 붙이세요.
- 각 이름의 의미와 작명 의도를 설명해주세요.
- 가장 추천하는 순서대로 정렬해주세요. (첫 번째 항목이 대표안으로 사용됩니다)

설명이나 마크다운 없이, 아래 JSON 형식으로만 응답하세요.

{{
    "names": [
        {{
            "name_ko": "한글 브랜드명",
            "name_en": "영문 표기",
            "meaning": "이름의 의미와 작명 의도"
        }}
    ]
}}"""

    try:
        text = call_llm(prompt)
        if not text:
            print("❌ 네이밍 생성 실패: LLM 응답이 없습니다.")
            return None

        result = extract_json(text)
        names = result.get("names") if isinstance(result, dict) else result

        if not names:
            print("❌ 네이밍 결과가 비어 있습니다.")
            return None

        # 규격 검증: 필수 키가 있는 항목만 통과시킨다.
        valid = [
            n for n in names
            if isinstance(n, dict) and n.get("name_ko") and n.get("name_en")
        ]
        if not valid:
            print("❌ 네이밍 결과의 형식이 규격과 다릅니다.")
            return None

        for n in valid:
            n.setdefault("meaning", "")

        return valid

    except Exception as e:
        print(f"❌ 네이밍 생성 실패: {e}")
        return None


def generate_slogans(brief, brand_name):
    """슬로건 3개를 생성한다.

    Args:
        brief (dict): 브랜드 브리프
        brand_name (dict): {"name_ko", "name_en", "meaning"} — 확정된 대표 브랜드명

    Returns:
        list[str] | None   실패 시 None
    """
    prompt = f"""다음 브랜드의 슬로건을 생성해주세요.

[브랜드]
브랜드명: {brand_name.get("name_ko", "")} ({brand_name.get("name_en", "")})
이름의 의미: {brand_name.get("meaning", "")}

[브랜드 브리프]
{_format_brief(brief)}

[슬로건 조건]
- 슬로건 3개를 생성하세요.
- 위 톤앤매너를 문장의 분위기에 반영하세요.
- 브랜드명의 의미와 이어지는 문구로 작성하세요.
- 타겟이 자신의 이야기라고 느낄 수 있어야 합니다.
- 짧고 기억하기 쉬운 문장으로 작성하세요.

설명이나 마크다운 없이, 아래 JSON 형식으로만 응답하세요.

{{
    "slogans": ["슬로건 1", "슬로건 2", "슬로건 3"]
}}"""

    try:
        text = call_llm(prompt)
        if not text:
            print("❌ 슬로건 생성 실패: LLM 응답이 없습니다.")
            return None

        result = extract_json(text)
        slogans = result.get("slogans") if isinstance(result, dict) else result

        if not slogans:
            print("❌ 슬로건 결과가 비어 있습니다.")
            return None

        return [s for s in slogans if isinstance(s, str) and s.strip()]

    except Exception as e:
        print(f"❌ 슬로건 생성 실패: {e}")
        return None


if __name__ == "__main__":
    from fixtures import SAMPLE_BRIEF, SAMPLE_NAMING

    print("[네이밍 테스트]")
    result = generate_naming(SAMPLE_BRIEF)
    if result:
        for n in result:
            print(f"  - {n['name_ko']} ({n['name_en']}): {n['meaning']}")

    print("\n[슬로건 테스트]")
    slogans = generate_slogans(SAMPLE_BRIEF, SAMPLE_NAMING[0])
    if slogans:
        for s in slogans:
            print(f'  - "{s}"')