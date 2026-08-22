"""
fixtures.py — 병렬 개발용 가짜 데이터

[왜 필요한가]
  visual.py는 palette가 있어야 일을 시작할 수 있는데,
  palette는 content.py가 만듭니다.
  이 파일이 없으면 비주얼 담당은 콘텐츠 담당이 끝날 때까지 대기해야 합니다.

[사용법]
  각자 자기 파일을 단독 테스트할 때 import해서 씁니다.

    from fixtures import SAMPLE_PALETTE, SAMPLE_BRIEF
    render_palette(SAMPLE_PALETTE, "./output")

  main.py는 --mock 옵션으로 API 없이 전체 흐름을 돌려볼 수 있습니다.

[주의]
  확정 후 아무도 수정하지 않습니다. 값이 바뀌면 서로의 테스트 결과가 어긋납니다.
"""

SAMPLE_BRIEF = {
    "industry": "야간 근무자를 위한 디카페인 음료 브랜드",
    "target": "교대 근무로 수면 리듬이 깨진 간호사와 개발자",
    "keywords": ["회복", "밤", "리듬"],
    "tone": "차분하고 다정한",
    "competitors": ["스타벅스 디카페인", "티젠"],
    "notes": "이름은 3글자 이내, 영문 표기가 쉬울 것",
}

SAMPLE_NAMING = [
    {
        "name_ko": "밤결",
        "name_en": "Bamgyeol",
        "meaning": "밤의 결을 따라 흐르는 회복의 리듬",
    },
    {
        "name_ko": "쉼표",
        "name_en": "Shimpyo",
        "meaning": "긴 문장 같은 하루에 찍는 짧은 쉼표",
    },
    {
        "name_ko": "온새",
        "name_en": "Onsae",
        "meaning": "따뜻하게(온) 새로워지는 시간",
    },
]

SAMPLE_SLOGANS = [
    "밤에도 당신의 리듬으로",
    "깨어 있는 밤, 쉬어 가는 한 잔",
    "잠들지 않아도 쉴 수 있으니까",
]

SAMPLE_STORY = (
    "밤결은 어느 대학병원 야간 병동에서 시작되었습니다. "
    "새벽 세 시, 커피 말고는 기댈 것이 없던 간호사들의 휴게실이 브랜드의 출발점이었습니다. "
    "깨어 있어야 하지만 무너지고 싶지 않은 사람들에게 필요한 것은 각성이 아니라 회복이라고 믿습니다. "
    "밤결은 카페인 대신 몸의 리듬을 존중하는 방식으로 밤을 함께 지킵니다. "
    "언젠가 모든 야간 근무자가 자신의 리듬을 되찾는 날까지, 밤결은 그 곁에 조용히 놓여 있겠습니다."
)

SAMPLE_PALETTE = {
    "main": {"name": "Midnight Navy", "hex": "#2C3E6B"},
    "subs": [
        {"name": "Moon Gray", "hex": "#7B8FC7"},
        {"name": "Dawn Mist", "hex": "#E8EAF2"},
    ],
}
