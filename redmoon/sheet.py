# 시안 4종 나란히 비교용 시트: python3 sheet.py -> out/compare.html
D = [("A", "파스텔 카드", "레퍼런스 그대로 + 큰 따옴표"),
     ("B", "달 + 영문 이름", "인물 뒤 달, 명조 이름 (추천)"),
     ("C", "미연시 대사창", "대사를 게임 텍스트박스에"),
     ("D", "호감도 게이지", "A + 호감도 바 하나")]
cols = "".join(f'<div class="col"><div class="h"><b>{k}</b>{t}<span>{s}</span></div>'
               f'<img src="draft_{k}.png"></div>' for k, t, s in D)
html = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1760px;background:#f4f2f6;font-family:'Noto Sans CJK KR',sans-serif;color:#3a3340;padding:30px 20px;display:flex;gap:20px}}
.col{{width:415px}} .col img{{width:415px;display:block;border-radius:6px;box-shadow:0 2px 10px #0001}}
.h{{height:70px;font-size:24px;font-weight:700}} .h b{{display:inline-block;width:34px;height:34px;line-height:34px;text-align:center;
border-radius:50%;background:#3a3340;color:#fff;font-size:19px;margin-right:10px}}
.h span{{display:block;font-size:17px;font-weight:400;color:#7a7180;margin:4px 0 0 44px}}
</style></head><body>{cols}</body></html>'''
open("out/compare.html", "w", encoding="utf-8").write(html)
