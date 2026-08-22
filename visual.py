"""
visual.py — ④ 비주얼 담당

담당 기능: 컬러 팔레트 시각화(matplotlib) + AI 로고 시안 생성
필요 패키지: matplotlib, requests (또는 사용하는 이미지 API의 SDK)

[단독 테스트]
    python visual.py
    -> fixtures의 더미 팔레트로 테스트하므로 다른 팀원을 기다릴 필요 없음

[주의] 이미지 생성 API 키는 팀장이 관리합니다.
       .env의 IMAGE_API_KEY를 읽어 쓰고, 코드에 직접 적지 마세요.
"""

import os

from contracts import ensure_dir

# ── 개발용 안전장치 ─────────────────────────────────────
# 로고는 호출할 때마다 과금된다. 프롬프트를 다듬는 동안에는
# LOGO_COUNT를 1로 두고, 최종 확인 때만 2~3으로 올린다. (미션 요구사항 2~3장)
LOGO_COUNT = 3          # 생성할 시안 수 (최종 제출 시 2 이상)
LOGO_SIZE = "1024x1024"

def render_palette(palette, out_dir):
    """컬러 팔레트를 PNG 이미지로 시각화해 저장한다.

    Returns: str | None   저장된 파일 경로
    """
    ensure_dir(out_dir)

    import re

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    # ── 입력 검증 ────────────────────────────────────────
    if not palette or "main" not in palette:
        print("  [오류] 팔레트 데이터가 비어 있습니다.")
        return None

    colors = [palette["main"]] + palette.get("subs", [])

    # hex 형식이 올바른 색만 남긴다
    valid = []
    for c in colors:
        hex_code = (c.get("hex") or "").strip()
        if re.fullmatch(r"#[0-9A-Fa-f]{6}", hex_code):
            valid.append({"name": c.get("name") or "Unknown", "hex": hex_code})
        else:
            print(f"  [경고] HEX 형식이 잘못되어 건너뜁니다: {hex_code}")

    if not valid:
        print("  [오류] 그릴 수 있는 색이 하나도 없습니다.")
        return None

    # ── 그리기 ───────────────────────────────────────────
    main_color = valid[0]
    sub_colors = valid[1:]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 5)
    ax.axis("off")                      # 축·눈금·테두리 모두 숨김

    # 메인: 왼쪽에 크게
    ax.add_patch(Rectangle((0.3, 1.2), 3.6, 3.0, facecolor=main_color["hex"]))
    ax.text(2.1, 0.9, main_color["name"], ha="center", fontsize=13, weight="bold")
    ax.text(2.1, 0.45, main_color["hex"], ha="center", fontsize=11, color="#555555")

    # 서브: 오른쪽에 작게 나란히
    if sub_colors:
        width = 4.4 / len(sub_colors)
        for i, c in enumerate(sub_colors):
            x = 4.4 + i * width
            ax.add_patch(Rectangle((x + 0.1, 2.0), width - 0.2, 2.2,
                                   facecolor=c["hex"]))
            cx = x + width / 2
            ax.text(cx, 1.7, c["name"], ha="center", fontsize=10)
            ax.text(cx, 1.35, c["hex"], ha="center", fontsize=9, color="#555555")

    # ── 저장 ─────────────────────────────────────────────
    out_path = os.path.join(out_dir, "color_palette.png")
    try:
        plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    except Exception as e:
        print(f"  [오류] 팔레트 이미지 저장 실패: {e}")
        return None
    finally:
        plt.close()

    return out_path

def _build_logo_prompt(brief, brand_name, palette, concept):
    """로고 이미지 생성용 영문 프롬프트를 조립한다.

    Args:
        concept (str): 시안별 컨셉 지시문 (심볼형 / 워드마크형 / 결합형)

    Returns: str
    """
    name_en = brand_name.get("name_en") or "Brand"
    meaning = brand_name.get("meaning") or ""
    keywords = ", ".join(brief.get("keywords", []))
    tone = brief.get("tone", "")

    main = palette["main"]
    subs = ", ".join(f"{s['name']} ({s['hex']})" for s in palette.get("subs", []))

    return (
        f"A minimal vector logo for a brand named '{name_en}'. "
        f"{concept} "
        f"Brand concept: {meaning}. "
        f"Keywords: {keywords}. Mood: {tone}. "
        f"Main color {main['name']} ({main['hex']}); accent colors {subs}. "
        f"Flat design, clean geometric shapes, plain white background, "
        f"no photograph, no gradient mesh, no extra text."
    )

def generate_logos(brief, brand_name, palette, out_dir):
    """AI 이미지 생성 API로 로고 시안 2~3개를 만들어 PNG로 저장한다.

    Args:
        brief (dict): 브리프
        brand_name (dict): {"name_ko", "name_en", "meaning"}
        palette (dict): {"main": {"name", "hex"}, "subs": [{"name", "hex"}, ...]}
        out_dir (str): 출력 폴더 경로

    Returns:
        list[str] | None   저장된 파일 경로 리스트
                           (예: ["./output/logo_01.png", "./output/logo_02.png"])

    [구현 힌트]
      - 프롬프트에 넣을 재료 4가지:
          1) brand_name["name_en"]  <- 한글보다 영문을 쓸 것.
             이미지 생성 모델은 한글 글자를 거의 못 그린다.
          2) brand_name["meaning"]  <- 시각적 컨셉의 힌트
          3) palette["main"]["hex"] <- HEX를 그대로 프롬프트에 넣어도 잘 먹는다
             palette["main"]["name"] <- 컬러명을 같이 넣으면 색 재현이 더 정확해진다
          4) brief["keywords"]      <- 회복 / 밤 / 리듬
      - "minimal vector logo, flat design, white background" 같은 스타일 지시어를
        붙이면 로고다운 결과가 나온다. 사진처럼 나오면 스타일 지시어가 부족한 것.
      - 시안 2~3개는 서로 다른 컨셉으로 뽑을 것.
        (예: 심볼 중심 / 워드마크 중심 / 결합형)
      - 파일명은 logo_01.png, logo_02.png ... (제출 체크리스트 항목)

      [에러 처리]
        3장 중 1장만 실패해도 나머지는 저장하고 리스트로 반환할 것.
        전부 실패했을 때만 None을 반환한다.
        한 장씩 try/except로 감싸는 것이 핵심.

      [비용 주의]
        테스트할 때마다 실제 호출이 나간다.
        프롬프트를 다듬는 동안에는 호출 수를 1장으로 줄여두고 작업할 것.
    """
    ensure_dir(out_dir)

    api_key = os.getenv("IMAGE_API_KEY")
    if not api_key:
        print("  [오류] IMAGE_API_KEY가 없습니다. .env 파일을 확인하세요.")
        return None

    # (위쪽 ensure_dir / api_key 검사는 그대로)

    from openai import OpenAI

    # 시안별 컨셉 — 서로 다른 방향으로 뽑는다
    concepts = [
        "Abstract symbol mark only, no letters.",
        f"Wordmark logotype spelling '{brand_name.get('name_en', 'Brand')}' in a clean sans-serif.",
        "Combination mark: a small symbol placed above the brand name.",
    ]

    client = OpenAI(api_key=api_key)
    saved = []

    for i in range(min(LOGO_COUNT, len(concepts))):
        prompt = _build_logo_prompt(brief, brand_name, palette, concepts[i])
        out_path = os.path.join(out_dir, f"logo_{i + 1:02d}.png")

        try:
            result = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size=LOGO_SIZE,
                n=1,
            )

            # 응답에서 이미지 데이터를 꺼낸다 (base64 또는 URL)
            item = result.data[0]

            if getattr(item, "b64_json", None):
                import base64
                image_bytes = base64.b64decode(item.b64_json)
            else:
                import requests
                resp = requests.get(item.url, timeout=60)
                resp.raise_for_status()
                image_bytes = resp.content

            # 바이너리 모드로 저장 ("wb"의 b가 핵심)
            with open(out_path, "wb") as f:
                f.write(image_bytes)

            saved.append(out_path)

        except Exception as e:
            print(f"  [오류] 로고 {i + 1}번 생성 실패: {e}")
            continue

    if not saved:
        print("  [오류] 로고를 한 장도 생성하지 못했습니다.")
        return None

    return saved

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    from fixtures import SAMPLE_BRIEF, SAMPLE_NAMING, SAMPLE_PALETTE

    print("[팔레트 시각화 테스트]")
    print(render_palette(SAMPLE_PALETTE, "./output"))

    print("\n[로고 생성 테스트]")
    print(generate_logos(SAMPLE_BRIEF, SAMPLE_NAMING[0], SAMPLE_PALETTE, "./output"))
