"""
contracts.py — 팀 공용 규격 및 헬퍼

[중요] 이 파일은 팀장만 수정합니다.
       내용을 바꿔야 하면 팀 채널에 먼저 공유하고 합의한 뒤에 수정하세요.

──────────────────────────────────────────────────────────────
■ 함수 규격 (STEP 1에서 합의됨)

  naming.py
    generate_naming(brief)                          -> list[dict] | None
    generate_slogans(brief, brand_name)             -> list[str]  | None

  content.py
    generate_story(brief, brand_name)               -> str        | None
    generate_palette(brief)                         -> dict       | None

  visual.py
    render_palette(palette, out_dir)                -> str        | None
    generate_logos(brief, brand_name, palette, out_dir) -> list[str] | None

■ 공통 규칙 3가지 (반드시 지킬 것)

  1. 실패하면 예외를 던지지 말고 None을 반환한다.
     에러 메시지는 함수 안에서 print로 출력한다.
     → API 하나가 실패해도 프로그램 전체가 죽지 않게 하기 위함.

  2. brand_result.json 조립은 팀장이 main.py에서 한다.
     각자는 자기 함수의 반환값까지만 책임진다.

  3. 파일을 만드는 함수는 저장까지 마치고 '경로 문자열'을 반환한다.

■ 데이터 모양 (실제 예시)

  brief         {"industry": str, "target": str, "keywords": list[str],
                 "tone": str, "competitors": list[str], "notes": str}

  naming 항목   {"name_ko": "소소담", "name_en": "Sosodam",
                 "meaning": "소소한 일상에 자연을 담다"}

  brand_name    naming 리스트의 항목 1개 (main.py에서 naming[0]을 넘김)

  palette       {"main": {"name": "Forest Green", "hex": "#2E7D32"},
                 "subs": [{"name": "Sage",  "hex": "#81C784"},
                          {"name": "Cream", "hex": "#E8F5E9"}]}
                 → hex는 필수, name은 영문 컬러명 (팔레트 PNG 라벨과
                   콘솔 출력에 쓰인다. 한글로 받으면 그림에서 깨진다.)
──────────────────────────────────────────────────────────────
"""

import json
import os
import re

# ── 브리프 필수 필드 ────────────────────────────────────────
REQUIRED_FIELDS = ["industry", "target", "keywords"]


def load_brief(path):
    """브리프 JSON을 읽고 필수 필드를 검증한다.

    Returns: dict
    Raises:  FileNotFoundError, ValueError  (여기서는 예외를 던진다.
             브리프가 없으면 애초에 아무것도 못 하므로 즉시 중단하는 게 맞다.)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"브리프 파일을 찾을 수 없습니다: {path}")

    with open(path, "r", encoding="utf-8") as f:
        brief = json.load(f)

    missing = [k for k in REQUIRED_FIELDS if not brief.get(k)]
    if missing:
        raise ValueError(f"브리프에 필수 항목이 비어 있습니다: {', '.join(missing)}")

    return brief


# ── LLM 응답에서 JSON만 뽑아내는 헬퍼 ────────────────────────
def extract_json(text):
    """LLM 응답 문자열에서 JSON 부분만 잘라내 파싱한다.

    LLM은 이런 식으로 응답하는 일이 잦다:
        ```json
        {"main": "#2E7D32"}
        ```
        위와 같이 추천드립니다!
    이 함수는 백틱과 앞뒤 설명을 제거하고 순수 JSON만 파싱한다.

    Returns: dict | list | None   (파싱 실패 시 None)
    """
    if not text:
        return None

    # 1) 코드펜스 제거
    cleaned = re.sub(r"```(?:json)?", "", text).strip()

    # 2) 그대로 파싱 시도
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3) 가장 바깥쪽 { } 또는 [ ] 구간만 잘라내서 재시도
    for opener, closer in (("{", "}"), ("[", "]")):
        start = cleaned.find(opener)
        end = cleaned.rfind(closer)
        if start != -1 and end != -1 and start < end:
            try:
                return json.loads(cleaned[start:end + 1])
            except json.JSONDecodeError:
                continue

    print("  [경고] LLM 응답을 JSON으로 파싱하지 못했습니다.")
    return None


# ── LLM 호출 헬퍼 (3명이 공용으로 사용) ──────────────────────
def call_llm(prompt, temperature=0.9):
    """LLM에 프롬프트를 보내고 응답 텍스트를 받는다.

    Returns: str | None   (실패 시 None, 에러 메시지는 여기서 출력)

    [담당자 안내]
      각자 이 함수를 다시 만들지 마세요. 그대로 가져다 쓰면 됩니다.
      naming / content 담당은 프롬프트 작성과 extract_json 처리에만
      집중하면 됩니다.

    [공급자 변경]
      기본은 Google Gemini입니다. 다른 API를 쓰기로 하면
      아래 블록만 팀장이 교체합니다. 함수 이름과 반환 타입은 그대로.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("  [오류] GEMINI_API_KEY가 없습니다. .env 파일을 확인하세요.")
        return None

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(temperature=temperature),
        )
        return response.text

    except Exception as e:
        print(f"  [오류] LLM 호출 실패: {e}")
        return None


# ── 출력 폴더 준비 ──────────────────────────────────────────
def ensure_dir(path):
    """출력 폴더가 없으면 만든다. 경로를 그대로 반환."""
    os.makedirs(path, exist_ok=True)
    return path
