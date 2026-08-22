"""
naming.py — ② 네이밍 · 카피 담당

담당 기능: 브랜드명 후보 3~5개 + 슬로건 3개
사용 헬퍼: contracts.call_llm(), contracts.extract_json()

[단독 테스트]
    python naming.py
"""

from contracts import call_llm, extract_json


def generate_naming(brief):
    """브랜드명 후보 3~5개를 생성한다.

    Args:
        brief (dict): 브리프

    Returns:
        list[dict] | None
        [{"name_ko": str, "name_en": str, "meaning": str}, ...]
        실패 시 None

    [구현 힌트]
      1. brief의 값들을 넣어 프롬프트 문자열을 만든다.
         - notes에 "이름은 3글자 이내, 영문 표기가 쉬울 것"이 있으니 꼭 반영할 것
      2. 프롬프트 끝에 출력 형식을 못 박는다.
         "설명 없이 JSON 배열만 출력. 각 항목은 name_ko, name_en, meaning 키를 가진다."
      3. "추천하는 순서대로 정렬해줘"를 넣을 것.
         main.py가 [0]번을 대표안으로 쓰기 때문에 순서가 의미를 가진다.
      4. call_llm() 호출 -> extract_json() 파싱
      5. 파싱 실패나 빈 리스트면 None 반환
    """
    # TODO: 구현
    pass


def generate_slogans(brief, brand_name):
    """슬로건 3개를 생성한다.

    Args:
        brief (dict): 브리프
        brand_name (dict): {"name_ko", "name_en", "meaning"} — 확정된 대표 브랜드명

    Returns:
        list[str] | None   (문자열 3개, 실패 시 None)

    [구현 힌트]
      - 브랜드명과 그 의미를 프롬프트에 반드시 포함시킬 것.
        이름을 모르고 쓴 슬로건은 무난하기만 하고 이 브랜드의 것이 아니게 된다.
      - brief["tone"]("차분하고 다정한")을 문장 톤에 반영할 것.
      - 출력 형식: 설명 없이 문자열 3개짜리 JSON 배열
    """
    # TODO: 구현
    pass


if __name__ == "__main__":
    from fixtures import SAMPLE_BRIEF, SAMPLE_NAMING

    print("[네이밍 테스트]")
    result = generate_naming(SAMPLE_BRIEF)
    print(result)

    print("\n[슬로건 테스트]")
    print(generate_slogans(SAMPLE_BRIEF, SAMPLE_NAMING[0]))
