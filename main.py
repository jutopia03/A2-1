"""
main.py — ① 통합 · 입력 담당 (팀장)

전체 파이프라인:
    brief.json 입력
      -> [1/5] 네이밍  [2/5] 슬로건  [3/5] 스토리  [4/5] 컬러  [5/5] 로고
      -> output/ 에 저장

실행:
    python main.py            실제 API 호출
    python main.py --mock     API 없이 더미 데이터로 전체 흐름 확인

[에러 처리 원칙]
    각 단계를 try/except로 격리한다.
    로고 생성이 실패해도 앞 단계 결과는 brand_result.json에 저장된다.
"""

import json
import os
import sys

from dotenv import load_dotenv

from contracts import ensure_dir, load_brief

load_dotenv()

MOCK = "--mock" in sys.argv


ERRORS = []


def run_step(label, step_name, func, *args):
    """한 단계를 실행하고 실패해도 다음으로 넘어간다.

    실패하면 ERRORS에 단계명을 기록한다.
    함수 자체는 규격대로 None만 반환하므로, 상세 사유는 각 함수가
    print한 메시지로 확인한다. (반환 타입을 늘리지 않기 위한 선택)

    Returns: 함수 반환값 | None
    """
    print(f"{label} ...")
    try:
        result = func(*args)
    except Exception as e:
        print(f"  [오류] {e}")
        ERRORS.append(f"{step_name} 실패 (예외: {type(e).__name__})")
        return None

    if result is None:
        print("  [건너뜀] 결과를 얻지 못했습니다.")
        ERRORS.append(f"{step_name} 실패")
    return result


def main():
    print()
    print("  🌙 AI 브랜드 아이덴티티 생성기")
    print()

    # ── 사용자 입력 ─────────────────────────────────────────
    brief_path = input("  브리프 파일 경로를 입력하세요: ").strip() or "brief.json"
    out_dir = input("  출력 폴더 경로를 입력하세요 (엔터 시 ./output): ").strip() or "./output"
    print()

    try:
        brief = load_brief(brief_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"  [중단] {e}")
        return

    ensure_dir(out_dir)

    # ── 담당 모듈 로드 ──────────────────────────────────────
    if MOCK:
        import fixtures as fx
        generate_naming = lambda b: fx.SAMPLE_NAMING
        generate_slogans = lambda b, n: fx.SAMPLE_SLOGANS
        generate_story = lambda b, n: fx.SAMPLE_STORY
        generate_palette = lambda b: fx.SAMPLE_PALETTE
        from visual import generate_logos, render_palette
        print("  [MOCK 모드] 텍스트는 더미 데이터를 사용합니다.\n")
    else:
        from naming import generate_naming, generate_slogans
        from content import generate_palette, generate_story
        from visual import generate_logos, render_palette

    # ── [1/5] 네이밍 ────────────────────────────────────────
    naming = run_step("  [1/5] 브랜드 네이밍 생성 중", "네이밍 생성",
                      generate_naming, brief)
    if naming:
        for n in naming:
            print(f"    - {n['name_ko']} ({n['name_en']}): {n['meaning']}")

    # 대표안 = 첫 번째 후보. 이후 단계가 이 이름을 기준으로 생성된다.
    # [A안] 네이밍이 실패해도 대체값을 세우고 계속 진행한다.
    #       뒤 단계를 통째로 건너뛰면 결과물이 너무 비어서, 팔레트와 로고라도
    #       나오게 하는 쪽을 택했다.
    brand_name = naming[0] if naming else None
    if brand_name is None:
        print("    [경고] 네이밍이 없어 대체값으로 진행합니다.")
        brand_name = {"name_ko": "(미정)", "name_en": "Brand", "meaning": ""}

    # ── [2/5] 슬로건 ────────────────────────────────────────
    slogans = run_step("  [2/5] 슬로건 생성 중", "슬로건 생성",
                       generate_slogans, brief, brand_name)
    if slogans:
        for s in slogans:
            print(f'    - "{s}"')

    # ── [3/5] 스토리 ────────────────────────────────────────
    story = run_step("  [3/5] 브랜드 스토리 생성 중", "스토리 생성",
                     generate_story, brief, brand_name)
    if story:
        print(f"    - 스토리 생성 완료 ({len(story)}자)")

    # ── [4/5] 컬러 ──────────────────────────────────────────
    palette = run_step("  [4/5] 컬러 팔레트 생성 중", "컬러 팔레트 생성",
                       generate_palette, brief)
    palette_png = None
    if palette:
        m = palette["main"]
        print(f"    - 메인: {m['hex']} ({m['name']})")
        print(f"    - 서브: {', '.join(s['hex'] for s in palette['subs'])}")
        palette_png = run_step("    팔레트 이미지 저장 중", "팔레트 이미지 저장",
                               render_palette, palette, out_dir)
        if palette_png:
            print(f"    - 저장: {palette_png}")

    # ── [5/5] 로고 ──────────────────────────────────────────
    # 팔레트가 없으면 로고 프롬프트에 넣을 색이 없으므로 건너뛴다.
    logos = None
    if palette:
        logos = run_step("  [5/5] 로고 시안 생성 중", "로고 생성",
                         generate_logos, brief, brand_name, palette, out_dir)
        if logos:
            for path in logos:
                print(f"    - 저장: {path}")
    else:
        print("  [5/5] 로고 시안 생성 건너뜀 (컬러 팔레트 없음)")
        ERRORS.append("로고 생성 건너뜀 (컬러 팔레트 없음)")

    # ── 결과 저장 ───────────────────────────────────────────
    result = {
        "brief": brief,
        "naming": naming,
        "selected_name": brand_name,
        "slogans": slogans,
        "story": story,
        "palette": palette,
        "files": {
            "color_palette": palette_png,
            "logos": logos,
        },
        "errors": ERRORS,
    }

    result_path = os.path.join(out_dir, "brand_result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print()
    print(f"  ✅ 완료! {out_dir}/ 폴더를 확인하세요.")
    if ERRORS:
        print(f"  ⚠️  실패한 단계 {len(ERRORS)}건 (brand_result.json의 errors 참고)")
        for e in ERRORS:
            print(f"     - {e}")
    print()


if __name__ == "__main__":
    main()
