# python3 build.py  →  out/minimal_*.html (시안) + out/sheet_minimal.html (비교판)
# 렌더: python3 render.py
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- 예시 데이터
DATE, DDAY, TIME, PLACE, ABILITY = 'IY 429. 7.15', 'D-68', '15:00', '기사단 연무장', '시간 정지'
EVENTS = [('D-68', '하계 무술대회'), ('D-55', '루스란, 다프네야 협력 수락'), ('D-49', '다프네야 → 피아체 접촉')]
THOUGHTS = [  # 장면에 있는 인물만
    ('헤드비히', '…보고만 계실 셈인가. 예전처럼 다른 자를 보러 오신 거라면, 차라리 그렇다고 말씀하시지.'),
    ('루스란', '또 재미있는 구경거리를 찾았군. 이번엔 무슨 꿍꿍이지?'),
]
PROSE = '헤드비히의 시선이 연무장 너머, 황제가 선 자리로 천천히 옮겨 갔다. 아무도 그 눈빛의 의미를 묻지 않았다.'

CSS = """
@font-face{font-family:'Gowun Batang';src:url(../fonts/GowunBatang-Regular.ttf);font-weight:400}
@font-face{font-family:'Gowun Batang';src:url(../fonts/GowunBatang-Bold.ttf);font-weight:700}
@font-face{font-family:'Noto Sans KR';src:url(../fonts/NotoSansKR.ttf);font-weight:100 900}
html,body{margin:0;background:#1e1d22}
body{padding:16px 12px 20px;font-family:'Noto Sans KR',sans-serif}
.chat{color:#d6d3cf;font-size:15px;line-height:1.75;margin:0 0 8px;max-width:640px}

.ks{--paper:#faf5ec;--ink:#3b2c27;--sub:#6b584d;--wine:#6e1f30;--gold:#94702f;--rule:#e2d5bf;--edge:#d6c3a0;
  max-width:640px;background:var(--paper);color:var(--ink);border:1px solid var(--edge);border-radius:6px;
  padding:16px 20px 15px;font-family:'Noto Sans KR',sans-serif;box-shadow:0 6px 18px rgba(0,0,0,.3)}
.ks *{box-sizing:border-box}
.ks-date{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.ks-iy{font-family:'Gowun Batang',serif;font-weight:700;font-size:20px;color:var(--wine);line-height:1.3}
.ks-dday{font-size:14px;font-weight:700;color:var(--wine)}
.ks-meta{margin-top:3px;font-size:14px;color:var(--sub);line-height:1.6}
.ks-meta i{font-style:normal;margin:0 6px;color:var(--edge)}
.ks-meta b{font-weight:500;color:var(--wine)}
.ks-rule{height:1px;background:var(--rule);margin:13px 0}
.ks-th{display:flex;gap:14px;align-items:baseline}
.ks-th + .ks-th{margin-top:9px}
.ks-th-name{flex:0 0 58px;font-size:14px;font-weight:700;color:var(--wine);line-height:1.7}
.ks-th p{margin:0;flex:1;min-width:0;font-family:'Gowun Batang',serif;font-size:15.5px;line-height:1.7;color:var(--ink)}
.ks-up-label{font-size:13px;font-weight:700;color:var(--sub);margin-bottom:4px}
.ks-up{list-style:none;margin:0;padding:0}
.ks-up li{display:flex;gap:14px;font-size:14px;line-height:1.75}
.ks-up b{flex:0 0 58px;font-weight:700;color:var(--gold);font-variant-numeric:tabular-nums}
.ks-up b.today{color:var(--wine)}
@media (max-width:480px){
  .ks{padding:14px 15px 13px}
  .ks-iy{font-size:19px}
  .ks-th{gap:12px}
  .ks-th-name,.ks-up b{flex-basis:56px}
}
"""


def card(today_mark, thoughts=THOUGHTS):
    th = ''.join(f'<div class="ks-th"><span class="ks-th-name">{n}</span><p>{t}</p></div>' for n, t in thoughts)
    th_block = f'<div class="ks-rule"></div>{th}' if thoughts else ''
    ev = ''
    for i, (d, t) in enumerate(EVENTS):
        is_today = today_mark and d == DDAY
        ev += f'<li><b class="{"today" if is_today else ""}">{"오늘" if is_today else d}</b><span>{t}</span></li>'
    return (f'<div class="ks"><div class="ks-date"><span class="ks-iy">{DATE}</span><span class="ks-dday">{DDAY}</span></div>'
            f'<div class="ks-meta">{TIME}<i>·</i>{PLACE}<i>·</i>능력 <b>{ABILITY}</b></div>'
            f'{th_block}<div class="ks-rule"></div>'
            f'<div class="ks-up-label">다가올 일</div><ol class="ks-up">{ev}</ol></div>')


VARIANTS = {
    'minimal_a': card(False),
    'minimal_b': card(True),
    'minimal_one': card(False, THOUGHTS[:1]),
    'minimal_none': card(False, []),
}
for name, html in VARIANTS.items():
    open(os.path.join(OUT, f'{name}.html'), 'w', encoding='utf-8').write(
        f'<!doctype html><meta charset="utf-8"><style>{CSS}</style><p class="chat">{PROSE}</p>{html}')

SHEET = """<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:'Noto Sans KR';src:url(../fonts/NotoSansKR.ttf);font-weight:100 900}
body{margin:0;background:#121115;color:#e9e4da;font-family:'Noto Sans KR',sans-serif;padding:28px 32px;width:1180px}
h1{font-size:22px;margin:0 0 4px} .note{color:#a39d95;font-size:14px;margin:0 0 18px;line-height:1.6}
h2{font-size:16px;margin:24px 0 10px;color:#e3c58e}
.row{display:flex;gap:28px;align-items:flex-start}
.col{display:flex;flex-direction:column;gap:6px} .col span{font-size:13px;color:#a39d95}
img{display:block;border-radius:10px;box-shadow:0 0 0 1px #2a2830}
</style><h1>최소 장식 시안 (아이보리 · 와인)</h1>
<p class="note">상자·띠·뱃지·장식선 없이 얇은 테두리와 구분선만. 장면에 있는 인물의 속마음만 나옵니다.<br>
아래 두 안은 '다가올 일'의 오늘 표시만 다릅니다.</p>
<h2>A. 오늘 표시 없음</h2><div class="row">
<div class="col"><span>PC</span><img src="minimal_a_pc.png" style="width:680px"></div>
<div class="col"><span>모바일</span><img src="minimal_a_m.png" style="width:375px"></div></div>
<h2>B. 오늘 표시 (D-숫자 자리에 '오늘')</h2><div class="row">
<div class="col"><span>PC</span><img src="minimal_b_pc.png" style="width:680px"></div>
<div class="col"><span>모바일</span><img src="minimal_b_m.png" style="width:375px"></div></div>
<h2>장면에 인물이 한 명일 때 / 아무도 없을 때 (모바일)</h2><div class="row">
<div class="col"><span>한 명</span><img src="minimal_one_m.png" style="width:375px"></div>
<div class="col"><span>없음 (속마음 칸이 통째로 빠짐)</span><img src="minimal_none_m.png" style="width:375px"></div></div>
"""
open(os.path.join(OUT, 'sheet_minimal.html'), 'w', encoding='utf-8').write(SHEET)
print('built', sorted(f for f in os.listdir(OUT) if f.startswith(('minimal', 'sheet_minimal'))))
