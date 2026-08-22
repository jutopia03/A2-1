"""
content.py — ③ 스토리 · 컬러 담당

담당 기능: 브랜드 스토리 + 컬러 팔레트 추천
사용 헬퍼: contracts.call_llm(), contracts.extract_json()

[단독 테스트]
    python content.py
"""

from contracts import call_llm, extract_json


def generate_story(brief, brand_name):
    """브랜드 스토리를 생성한다. (300자 내외)

    Args:
        brief (dict): 브리프
        brand_name (dict): {"name_ko", "name_en", "meaning"}

    Returns:
        str | None

    [구현 힌트]
      - 탄생 배경 / 철학 / 비전 세 가지를 반드시 포함시킬 것. (과제 요구사항)
      - 브랜드명과 그 의미를 스토리 안에 자연스럽게 녹일 것.
      - "300자 내외"를 프롬프트에 명시하되, 결과 길이를 코드로 검증하면 더 좋다.
      - 이 함수만 JSON이 아니라 순수 텍스트를 반환한다.
        LLM이 따옴표나 "물론이죠!" 같은 서두를 붙이면 .strip()으로 정리할 것.
    """
    # TODO: 구현
    pass


def generate_palette(brief):
    """브랜드에 어울리는 컬러 팔레트를 추천받는다.

    Args:
        brief (dict): 브리프

    Returns:
        dict | None
        {"main": {"name": "Midnight Navy", "hex": "#1A237E"},
         "subs": [{"name": "Moon Gray", "hex": "#B0BEC5"}, ...]}
        실패 시 None

    [구현 힌트]
      - 메인 1개 + 서브 2~3개.
      - 각 색은 name(영문 컬러명)과 hex 두 키를 가진다.
        name은 반드시 영문으로 받을 것. 한글이면 팔레트 PNG에서 글자가 깨진다.
      - 프롬프트에 hex는 "#RRGGBB 6자리 형식"이라고 못 박을 것.
        안 그러면 rgb() 표기나 3자리 축약형이 섞여 들어온다.
      - 파싱 후 hex 형식을 정규식으로 검증하는 걸 권장.
        (^#[0-9A-Fa-f]{6}$)  형식이 깨지면 visual.py에서 그림이 안 그려진다.
      - 이 함수는 brand_name을 받지 않는다. 네이밍과 병렬로 돌리기 위함.
    """
    # TODO: 구현
    pass


if __name__ == "__main__":
    from fixtures import SAMPLE_BRIEF, SAMPLE_NAMING

    print("[스토리 테스트]")
    story = generate_story(SAMPLE_BRIEF, SAMPLE_NAMING[0])
    print(story)
    if story:
        print(f"({len(story)}자)")

    print("\n[컬러 테스트]")
    print(generate_palette(SAMPLE_BRIEF))
