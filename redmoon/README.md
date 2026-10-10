# RED MOON 인물소개 시안

**완성본 이미지: `out/redmoon_full.png`** (건물 → 초이스 → 인물소개 W4 → 누구를 고르시겠습니까)
**봇 소개 HTML: `out/guide.html`** — 아카라이브 편집기 HTML 모드에 그대로 붙여넣기 (아카 HTML 가이드 v6.7.1 규칙: 인라인 스타일만, flex/position 등 미사용, 다크모드 색 가드 포함)
미리보기: `out/guide_preview.png`(PC), `guide_preview_dark.png`(다크 테마 흉내), `guide_preview_mobile.png`(360px). 문구는 `guide.py`에서 수정.

폭 1000px 세로 이미지. 위/아래(타이틀, "누구를 고르시겠습니까?")는 빠진 인물소개 영역만.

| 시안 | 내용 |
|---|---|
| A | 파스텔 카드: 레퍼런스 색 그대로 + 대사 큰 따옴표 + 숫자 대신 영문 이름 |
| B | 달 + 영문 이름: 인물 뒤 파스텔 달 원형, 고운바탕 이름 + 필기체 영문 (추천) |
| C | 미연시 대사창: 대사를 이름표 달린 게임 텍스트박스에 |
| D | 호감도 게이지: A + 호감도 바 하나 (수치는 임시값) |
| W1 | B 흰 배경판: 배경 없음, 대각선 선만 |
| W2 | B 흰 배경판: 색은 인물 뒤 달에만 |
| W3 | B 흰 배경판: W2 + 대각선 아랫변 따라 옅은 색 |
| W4 | B 흰 배경판: W1 + 바닥빛만 (달 없음) |
| W5 | W4에서 바닥빛을 더 높고 진하게 |

비교: `out/compare.png`(A~D), `out/compare_white.png`(B vs 흰 배경판), `out/compare_floor.png`(바닥빛 비교) / 원본: `out/draft_*.png`

## 다시 뽑기
```sh
./get_fonts.sh            # 한 번만 (고운바탕, Cormorant Garamond)
python3 gen.py            # out/draft_*.html 생성
python3 render.py out/draft_B.html out/draft_B.png   # Playwright(Chromium) 스크린샷
python3 sheet.py && python3 render.py out/compare.html out/compare.png   # 비교표
python3 render.py out/draft_W4.html out/draft_W4.png && python3 longpost.py \
  && python3 render.py out/redmoon_full.html out/redmoon_full.png   # 완성본 이미지
python3 guide.py          # out/guide.html (+ lint 결과 출력, 미리보기 html)
```
글 내용·색은 `gen.py`의 `CHARS`, 카드 높이·대각선 기울기는 `BIG`, `SLOPE`에서 바꾸면 됨.
