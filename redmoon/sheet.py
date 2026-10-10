# 시안 나란히 비교용 시트: python3 sheet.py -> out/compare.html, out/compare_white.html
SHEETS = {"compare": [("A", "파스텔 카드", "레퍼런스 그대로 + 큰 따옴표"),
     ("B", "달 + 영문 이름", "인물 뒤 달, 명조 이름 (추천)"),
     ("C", "미연시 대사창", "대사를 게임 텍스트박스에"),
     ("D", "호감도 게이지", "A + 호감도 바 하나")],
          "compare_white": [
     ("B", "B (지금)", "카드마다 파스텔 배경"),
     ("W1", "완전 하양", "배경 없음, 대각선 선만"),
     ("W2", "하양 + 달", "색은 인물 뒤 달에만"),
     ("W3", "하양 + 달 + 바닥빛", "W2 + 대각선 따라 옅은 색")],
          "compare_floor": [
     ("W1", "완전 하양", "배경 없음, 대각선 선만"),
     ("W3", "하양 + 달 + 바닥빛", "지난번 W3"),
     ("W4", "하양 + 바닥빛", "W1 + W3의 바닥빛만"),
     ("W5", "하양 + 바닥빛 진하게", "W4에서 바닥빛을 더 높고 진하게")]}
for fname, D in SHEETS.items():
  cols = "".join(f'<div class="col"><div class="h"><b>{k}</b>{t}<span>{s}</span></div>'
               f'<img src="draft_{k}.png"></div>' for k, t, s in D)
  html = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1760px;background:#f4f2f6;font-family:'Noto Sans CJK KR',sans-serif;color:#3a3340;padding:30px 20px;display:flex;gap:20px}}
.col{{width:415px}} .col img{{width:415px;display:block;border-radius:6px;box-shadow:0 2px 10px #0001}}
.h{{height:70px;font-size:24px;font-weight:700}} .h b{{display:inline-block;min-width:34px;padding:0 6px;height:34px;line-height:34px;text-align:center;
border-radius:17px;background:#3a3340;color:#fff;font-size:19px;margin-right:10px}}
.h span{{display:block;font-size:17px;font-weight:400;color:#7a7180;margin:4px 0 0 44px}}
</style></head><body>{cols}</body></html>'''
  open(f"out/{fname}.html", "w", encoding="utf-8").write(html)
