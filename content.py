"""
content.py — ③ 스토리 · 컬러 담당

담당 기능: 브랜드 스토리 + 컬러 팔레트 추천
사용 헬퍼: contracts.call_llm(), contracts.extract_json()

[단독 테스트]
    python content.py
"""

import re

from contracts import call_llm, extract_json


## ---------------------------------------------------------
## 브랜드 스토리 생성
## ---------------------------------------------------------
## 브랜드 브리프와 생성된 브랜드명을 바탕으로
## 약 300자의 브랜드 스토리를 생성한다.
##
## 성공: str
## 실패: None
##
## 팀 규칙:
## - API 호출은 contracts.call_llm()을 사용한다.
## - 오류가 발생하면 함수 내부에서 메시지를 출력한다.
## - 예외를 외부로 전달하지 않고 None을 반환한다.
## ---------------------------------------------------------

def generate_story(brief, brand_name):
    """브랜드 스토리를 생성한다. (300자 내외)

    Args:
        brief (dict): 브리프
        brand_name (dict): {"name_ko", "name_en", "meaning"}

    Returns:
        str | None
    """

    try:
        ## 브랜드 브리프와 브랜드명을 프롬프트에 전달한다.
        prompt = f"""
당신은 전문 브랜드 전략가입니다.

다음 브랜드 브리프와 브랜드명을 바탕으로 브랜드 스토리를 작성해주세요.

[브랜드 브리프]
업종: {brief.get("industry", "")}
타겟: {brief.get("target", "")}
키워드: {", ".join(brief.get("keywords", []))}
톤앤매너: {brief.get("tone", "")}
경쟁사: {", ".join(brief.get("competitors", []))}
추가 요청사항: {brief.get("notes", "")}

[브랜드명]
한글명: {brand_name.get("name_ko", "")}
영문명: {brand_name.get("name_en", "")}
의미: {brand_name.get("meaning", "")}

[작성 조건]
1. 한국어로 작성해주세요.
2. 300자 내외로 작성해주세요.
3. 브랜드의 탄생 배경을 포함해주세요.
4. 브랜드가 추구하는 철학을 포함해주세요.
5. 브랜드가 앞으로 제공하고자 하는 가치와 비전을 포함해주세요.
6. 브랜드명과 브랜드명의 의미를 스토리에 자연스럽게 녹여주세요.
7. 브리프의 "차분하고 다정한" 톤앤매너를 반영해주세요.
8. 야간 근무자의 피로와 깨진 수면 리듬을 이해하고,
   카페인 대신 편안한 회복의 시간을 제공하는 브랜드라는 점을 자연스럽게 표현해주세요.
9. 제목, 인사말, 설명 없이 스토리 본문만 출력해주세요.
"""

        ## contracts.py의 공통 LLM 호출 함수 사용
        response = call_llm(prompt)

        ## API 응답이 없으면 실패 처리
        if not response:
            print("❌ 브랜드 스토리 생성 실패: LLM 응답이 없습니다.")
            return None

        ## 순수 텍스트로 정리
        story = response.strip()

        ## AI가 불필요한 따옴표로 감싼 경우 제거
        if story.startswith('"') and story.endswith('"'):
            story = story[1:-1].strip()

        ## 빈 응답 확인
        if not story:
            print("❌ 브랜드 스토리 생성 실패: 결과가 비어 있습니다.")
            return None

        ## 300자 내외인지 확인
        ## "내외"이므로 너무 엄격하게 300자만 허용하지 않는다.
        if len(story) < 200 or len(story) > 400:
            print(
                f"⚠️ 브랜드 스토리 길이가 300자 내외를 벗어났습니다. "
                f"현재 {len(story)}자입니다."
            )

        return story

    except Exception as e:
        ## 함수 내부에서 오류를 처리하고 None 반환
        print(f"❌ 브랜드 스토리 생성 실패: {e}")
        return None


## ---------------------------------------------------------
## 컬러 팔레트 생성
## ---------------------------------------------------------
## 브랜드 브리프를 바탕으로 메인 컬러 1개와
## 서브 컬러 2~3개를 추천받는다.
##
## 성공:
## {
##     "main": {
##         "name": "Midnight Navy",
##         "hex": "#1A237E"
##     },
##     "subs": [
##         {
##             "name": "Moon Gray",
##             "hex": "#B0BEC5"
##         },
##         ...
##     ]
## }
##
## 실패:
## None
##
## 중요:
## - 이 함수는 brand_name을 받지 않는다.
## - 네이밍과 병렬 실행할 수 있도록 독립적으로 동작한다.
## ---------------------------------------------------------

def generate_palette(brief):
    """브랜드에 어울리는 컬러 팔레트를 추천받는다.

    Args:
        brief (dict): 브리프

    Returns:
        dict | None
    """

    try:
        ## 브랜드 브리프를 프롬프트에 전달한다.
        prompt = f"""
당신은 전문 브랜드 디자이너입니다.

다음 브랜드 브리프를 분석하여 브랜드에 어울리는 컬러 팔레트를 추천해주세요.

[브랜드 브리프]
업종: {brief.get("industry", "")}
타겟: {brief.get("target", "")}
키워드: {", ".join(brief.get("keywords", []))}
톤앤매너: {brief.get("tone", "")}
경쟁사: {", ".join(brief.get("competitors", []))}
추가 요청사항: {brief.get("notes", "")}

[컬러 선정 조건]
1. 메인 컬러는 정확히 1개를 선택해주세요.
2. 서브 컬러는 2~3개를 선택해주세요.
3. 각 색상은 반드시 name과 hex 두 가지 정보를 가져야 합니다.
4. name은 반드시 영문 컬러명으로 작성해주세요.
5. hex는 반드시 "#RRGGBB" 형식의 6자리 HEX 코드로 작성해주세요.
6. 브랜드의 업종, 타겟, 키워드, 톤앤매너를 고려해주세요.
7. 서로 조화로운 컬러 조합을 선택해주세요.
8. 야간 근무자를 위한 브랜드라는 특성을 고려하여
   편안함, 회복, 밤, 안정감을 느낄 수 있는 색상을 추천해주세요.

반드시 아래 JSON 형식으로만 출력해주세요.

{{
    "main": {{
        "name": "Midnight Navy",
        "hex": "#1A237E"
    }},
    "subs": [
        {{
            "name": "Moon Gray",
            "hex": "#B0BEC5"
        }},
        {{
            "name": "Soft Lavender",
            "hex": "#D1C4E9"
        }}
    ]
}}
"""

        ## contracts.py의 공통 LLM 호출 함수 사용
        response = call_llm(prompt)

        ## API 응답이 없으면 실패 처리
        if not response:
            print("❌ 컬러 팔레트 생성 실패: LLM 응답이 없습니다.")
            return None

        ## AI 응답을 JSON으로 변환
        palette = extract_json(response)

        ## JSON 변환 실패
        if not palette:
            print("❌ 컬러 팔레트 생성 실패: JSON 파싱에 실패했습니다.")
            return None

        ## -------------------------------------------------
        ## 컬러 팔레트 결과 구조 검증
        ## -------------------------------------------------

        ## 최상위 구조 확인
        if not isinstance(palette, dict):
            print("❌ 컬러 팔레트 형식이 올바르지 않습니다.")
            return None

        ## main과 subs 존재 여부 확인
        if "main" not in palette or "subs" not in palette:
            print("❌ 컬러 팔레트에 main 또는 subs가 없습니다.")
            return None

        ## main은 dictionary인지 확인
        if not isinstance(palette["main"], dict):
            print("❌ main 컬러 형식이 올바르지 않습니다.")
            return None

        ## main에 name과 hex가 있는지 확인
        if "name" not in palette["main"] or "hex" not in palette["main"]:
            print("❌ main 컬러에 name 또는 hex가 없습니다.")
            return None

        ## main 컬러명은 문자열인지 확인
        if not isinstance(palette["main"]["name"], str):
            print("❌ main 컬러명이 올바르지 않습니다.")
            return None

        ## main HEX 형식 검증
        if not re.match(
            r"^#[0-9A-Fa-f]{6}$",
            palette["main"]["hex"]
        ):
            print(
                f"❌ main 컬러의 HEX 코드가 올바르지 않습니다: "
                f"{palette['main']['hex']}"
            )
            return None

        ## subs가 리스트인지 확인
        if not isinstance(palette["subs"], list):
            print("❌ subs 컬러는 리스트 형식이어야 합니다.")
            return None

        ## 서브 컬러는 2~3개
        if not 2 <= len(palette["subs"]) <= 3:
            print("❌ 서브 컬러는 2~3개여야 합니다.")
            return None

        ## 각각의 서브 컬러 검증
        for color in palette["subs"]:

            ## dictionary인지 확인
            if not isinstance(color, dict):
                print("❌ 서브 컬러 형식이 올바르지 않습니다.")
                return None

            ## name과 hex가 있는지 확인
            if "name" not in color or "hex" not in color:
                print("❌ 서브 컬러에 name 또는 hex가 없습니다.")
                return None

            ## 컬러명은 문자열인지 확인
            if not isinstance(color["name"], str):
                print("❌ 서브 컬러명이 올바르지 않습니다.")
                return None

            ## HEX 코드 형식 검증
            if not re.match(
                r"^#[0-9A-Fa-f]{6}$",
                color["hex"]
            ):
                print(
                    f"❌ 서브 컬러의 HEX 코드가 올바르지 않습니다: "
                    f"{color['hex']}"
                )
                return None

        ## 모든 검증을 통과하면 palette 반환
        return palette

    except Exception as e:
        ## 함수 내부에서 오류를 처리하고 None 반환
        print(f"❌ 컬러 팔레트 생성 실패: {e}")
        return None


## ---------------------------------------------------------
## 단독 테스트
## ---------------------------------------------------------

if __name__ == "__main__":
    from fixtures import SAMPLE_BRIEF, SAMPLE_NAMING

    print("[스토리 테스트]")
    story = generate_story(SAMPLE_BRIEF, SAMPLE_NAMING[0])
    print(story)

    if story:
        print(f"({len(story)}자)")

    print("\n[컬러 테스트]")
    print(generate_palette(SAMPLE_BRIEF))