# RED MOON 인물소개 시안

**완성본: `out/redmoon_full.png`** (건물 → 초이스 → 인물소개 W4 → 누구를 → 봇 이용 안내서)
봇 소개 별지 서식만: `out/form.png` (내용은 `longpost.py`의 `SECTIONS`)

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
  && python3 render.py out/form.html out/form.png out/redmoon_full.html out/redmoon_full.png   # 완성본
```
글 내용·색은 `gen.py`의 `CHARS`, 카드 높이·대각선 기울기는 `BIG`, `SLOPE`에서 바꾸면 됨.
