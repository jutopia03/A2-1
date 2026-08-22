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


def render_palette(palette, out_dir):
    """컬러 팔레트를 PNG 이미지로 시각화해 저장한다.

    Args:
        palette (dict): {"main": {"name": str, "hex": "#RRGGBB"},
                         "subs": [{"name": str, "hex": "#RRGGBB"}, ...]}
        out_dir (str): 출력 폴더 경로

    Returns:
        str | None   저장된 파일 경로 (예: "./output/color_palette.png")

    [구현 힌트]
      - matplotlib으로 색상 블록을 나란히 그리면 된다.
        메인은 크게, 서브는 작게 배치하면 위계가 드러난다.
      - 각 블록 아래에 컬러명(name)과 HEX를 함께 표기할 것.
        예: "Midnight Navy\n#1A237E"
      - name이 영문이라는 전제로 그린다. 혹시 한글이 들어오면 깨지므로
        아래 [함정] 항목의 폰트 설정을 적용할 것.
      - 파일명은 반드시 color_palette.png (제출 체크리스트 항목)
      - plt.savefig() 후 plt.close()를 꼭 호출할 것. 안 하면 메모리에 쌓인다.

      [함정] 한글 폰트
        블록 라벨에 한글을 넣으면 □□□로 깨진다.
        해결 1) 라벨을 HEX 코드(영문/숫자)만 쓴다  <- 가장 간단
        해결 2) matplotlib에 한글 폰트를 지정한다
                plt.rcParams["font.family"] = "Malgun Gothic"  (Windows)
                plt.rcParams["axes.unicode_minus"] = False
    """
    ensure_dir(out_dir)
    # TODO: 구현
    pass


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

    # TODO: 구현
    pass


if __name__ == "__main__":
    from fixtures import SAMPLE_BRIEF, SAMPLE_NAMING, SAMPLE_PALETTE

    print("[팔레트 시각화 테스트]")
    print(render_palette(SAMPLE_PALETTE, "./output"))

    print("\n[로고 생성 테스트]")
    print(generate_logos(SAMPLE_BRIEF, SAMPLE_NAMING[0], SAMPLE_PALETTE, "./output"))
