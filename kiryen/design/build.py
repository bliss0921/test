# python3 build.py  →  out/frames/*.svg (테두리 에셋) + out/frame_*.html (시안) + out/sheet_frames.html (비교판)
# 렌더: python3 render.py
#
# 테두리는 '9조각(9-slice)' 이미지다: 모서리 4개는 그대로, 변은 내용 길이에 맞춰 늘어난다.
# CSS: border-image: url(테두리) 40 fill / 30px stretch  (RisuAI에서는 url('{{raw::에셋이름}}'))
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
FR = os.path.join(OUT, 'frames')
os.makedirs(FR, exist_ok=True)

# ---------------------------------------------------------------- 예시 데이터
DATE, DDAY, TIME, PLACE, ABILITY = 'IY 429. 7.15', 'D-68', '15:00', '기사단 연무장', '시간 정지'
EVENTS = [('D-68', '하계 무술대회'), ('D-55', '루스란, 다프네야 협력 수락'), ('D-49', '다프네야 → 피아체 접촉')]
THOUGHTS = [
    ('헤드비히', '…보고만 계실 셈인가. 예전처럼 다른 자를 보러 오신 거라면, 차라리 그렇다고 말씀하시지.'),
    ('루스란', '또 재미있는 구경거리를 찾았군. 이번엔 무슨 꿍꿍이지?'),
]
PROSE = '헤드비히의 시선이 연무장 너머, 황제가 선 자리로 천천히 옮겨 갔다. 아무도 그 눈빛의 의미를 묻지 않았다.'

PAPER, GOLD, WINE = '#faf5ec', '#a8823f', '#6e1f30'

# ---------------------------------------------------------------- 테두리 에셋 (120x120, 모서리 40)


def mirror4(corner):
    """왼쪽 위 모서리 그림을 네 모서리로 복사"""
    return (f'<g>{corner}</g><g transform="translate(120,0) scale(-1,1)">{corner}</g>'
            f'<g transform="translate(0,120) scale(1,-1)">{corner}</g><g transform="translate(120,120) scale(-1,-1)">{corner}</g>')


def svg(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120">{body}</svg>'


# 1. 코너 장식: 둥근 모서리 + 안쪽 아치와 작은 마름모
corner1 = (f'<path d="M40 6 H22 C13 6 6 13 6 22 V40" fill="none" stroke="{GOLD}" stroke-width="1.6"/>'
           f'<path d="M15 34 C15 23 23 15 34 15" fill="none" stroke="{GOLD}" stroke-width="1.2"/>'
           f'<circle cx="15" cy="36" r="2" fill="{GOLD}"/><circle cx="36" cy="15" r="2" fill="{GOLD}"/>'
           f'<rect x="8.8" y="8.8" width="6" height="6" transform="rotate(45 11.8 11.8)" fill="{GOLD}"/>')
FRAME1 = svg(f'<path d="M22 6 H98 C107 6 114 13 114 22 V98 C114 107 107 114 98 114 H22 C13 114 6 107 6 98 V22 C6 13 13 6 22 6 Z" fill="{PAPER}"/>'
             f'<path d="M40 6 H80 M40 114 H80 M6 40 V80 M114 40 V80" stroke="{GOLD}" stroke-width="1.3"/>' + mirror4(corner1))

# 2. 왕실 문장: 얇은 이중선 (위 가운데 태양 문장은 HTML 요소로 따로 얹음)
FRAME2 = svg(f'<rect x="4" y="4" width="112" height="112" rx="3" fill="{PAPER}"/>'
             f'<rect x="4.6" y="4.6" width="110.8" height="110.8" rx="3" fill="none" stroke="{GOLD}" stroke-width="1.2"/>'
             f'<rect x="9" y="9" width="102" height="102" rx="1.5" fill="none" stroke="{GOLD}" stroke-width=".7" opacity=".7"/>')

# 3. 모서리 컷: 모서리를 비스듬히 자른 이중선 + 점
corner3 = (f'<path d="M40 6 H20 L6 20 V40" fill="none" stroke="{GOLD}" stroke-width="1.3"/>'
           f'<path d="M40 11 H22.5 L11 22.5 V40" fill="none" stroke="{GOLD}" stroke-width=".7" opacity=".75"/>'
           f'<circle cx="13" cy="13" r="1.6" fill="{GOLD}"/>')
FRAME3 = svg(f'<path d="M20 6 H100 L114 20 V100 L100 114 H20 L6 100 V20 Z" fill="{PAPER}"/>'
             f'<path d="M40 6 H80 M40 114 H80 M6 40 V80 M114 40 V80" stroke="{GOLD}" stroke-width="1.3"/>'
             f'<path d="M40 11 H80 M40 109 H80 M11 40 V80 M109 40 V80" stroke="{GOLD}" stroke-width=".7" opacity=".75"/>' + mirror4(corner3))

SUN = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28" width="28" height="28">'
       f'<circle cx="14" cy="14" r="12.6" fill="{PAPER}" stroke="{GOLD}" stroke-width="1.1"/>'
       f'<circle cx="14" cy="14" r="3.6" fill="none" stroke="{GOLD}" stroke-width="1.1"/>'
       + ''.join(f'<line x1="14" y1="6.2" x2="14" y2="8.4" stroke="{GOLD}" stroke-width="1" stroke-linecap="round" transform="rotate({a} 14 14)"/>' for a in range(0, 360, 45))
       + '</svg>')

for name, data in (('frame_corner', FRAME1), ('frame_crest', FRAME2), ('frame_cut', FRAME3), ('crest_sun', SUN)):
    open(os.path.join(FR, f'{name}.svg'), 'w', encoding='utf-8').write(data)

CSS = """
@font-face{font-family:'Gowun Batang';src:url(../fonts/GowunBatang-Regular.ttf);font-weight:400}
@font-face{font-family:'Gowun Batang';src:url(../fonts/GowunBatang-Bold.ttf);font-weight:700}
@font-face{font-family:'Noto Sans KR';src:url(../fonts/NotoSansKR.ttf);font-weight:100 900}
html,body{margin:0;background:#1e1d22}
body{padding:16px 12px 20px;font-family:'Noto Sans KR',sans-serif}
.chat{color:#d6d3cf;font-size:15px;line-height:1.75;margin:0 0 8px;max-width:640px}

.ks{--ink:#3b2c27;--sub:#6b584d;--wine:#6e1f30;--gold:#94702f;--rule:#e2d5bf;--edge:#d6c3a0;
  position:relative;max-width:640px;color:var(--ink);font-family:'Noto Sans KR',sans-serif;
  border:30px solid transparent;border-image:var(--frame) 40 fill / 30px stretch;padding:0 6px;
  filter:drop-shadow(0 6px 14px rgba(0,0,0,.35))}
.ks *{box-sizing:border-box}
.ks-crest{position:absolute;left:50%;top:-40.5px;width:28px;height:28px;margin-left:-14px;background:var(--crest) center/contain no-repeat}
.ks-has-crest{margin-top:14px}
.ks-date{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.ks-iy{font-family:'Gowun Batang',serif;font-weight:700;font-size:20px;color:var(--wine);line-height:1.3}
.ks-dday{font-size:14px;font-weight:700;color:var(--wine)}
.ks-meta{margin-top:3px;font-size:14px;color:var(--sub);line-height:1.6}
.ks-meta i{font-style:normal;margin:0 6px;color:var(--edge)}
.ks-meta b{font-weight:500;color:var(--wine)}
.ks-ab{white-space:nowrap}
.ks-rule{height:1px;background:var(--rule);margin:13px 0}
.ks-th{display:flex;gap:14px;align-items:baseline}
.ks-th + .ks-th{margin-top:9px}
.ks-th-name{flex:0 0 58px;font-size:14px;font-weight:700;color:var(--wine);line-height:1.7}
.ks-th p{margin:0;flex:1;min-width:0;font-family:'Gowun Batang',serif;font-size:15.5px;line-height:1.7;color:var(--ink)}
/* 배치 1: 이름 위, 속마음 아래 */
.lay-stack .ks-th{display:block}
.lay-stack .ks-th + .ks-th{margin-top:12px}
.lay-stack .ks-th-name{display:block;line-height:1.4;margin-bottom:2px}
/* 배치 2: 이름을 문장 맨 앞에 붙여 쓰기 (줄바꿈은 왼쪽 끝부터) */
.ks-runin{margin:0;font-family:'Gowun Batang',serif;font-size:15.5px;line-height:1.75;color:var(--ink)}
.ks-runin + .ks-runin{margin-top:8px}
.ks-runin b{font-family:'Noto Sans KR',sans-serif;font-size:14px;font-weight:700;color:var(--wine);margin-right:9px}
/* 배치 3: 속마음 먼저, 이름은 오른쪽 아래에 */
.ks-quote{margin:0}
.ks-quote + .ks-quote{margin-top:12px}
.ks-quote p{margin:0;font-family:'Gowun Batang',serif;font-size:15.5px;line-height:1.75;color:var(--ink)}
.ks-quote span{display:block;text-align:right;margin-top:2px;font-size:13.5px;font-weight:700;color:var(--wine)}
.ks-up-label{font-size:13px;font-weight:700;color:var(--sub);margin-bottom:4px}
.ks-up{list-style:none;margin:0;padding:0}
.ks-up li{display:flex;gap:14px;font-size:14px;line-height:1.75}
.ks-up b{flex:0 0 58px;font-weight:700;color:var(--gold);font-variant-numeric:tabular-nums}
@media (max-width:480px){
  .ks{border-width:24px;border-image-width:24px;padding:0 2px}
  .ks-crest{top:-35.2px}
  .ks-iy{font-size:19px}
  .ks-th{gap:12px}
  .ks-th-name,.ks-up b{flex-basis:56px}
}
"""


def card(frame, crest=False, thoughts=THOUGHTS, head=None, layout='grid', lang='en'):
    date, dday, time, place, ability = head or (DATE, DDAY, TIME, PLACE, ABILITY)
    lab_ab, lab_up = ('Ability', 'Upcoming') if lang == 'en' else ('능력', '다가올 일')
    if layout == 'runin':
        th = ''.join(f'<p class="ks-runin"><b>{n}</b>{t}</p>' for n, t in thoughts)
    elif layout == 'quote':
        th = ''.join(f'<div class="ks-quote"><p>{t}</p><span>— {n}</span></div>' for n, t in thoughts)
    else:
        th = ''.join(f'<div class="ks-th"><span class="ks-th-name">{n}</span><p>{t}</p></div>' for n, t in thoughts)
    th_block = f'<div class="ks-rule"></div>{th}' if thoughts else ''
    ev = ''.join(f'<li><b>{d}</b><span>{t}</span></li>' for d, t in (EVENTS if lang == 'ko' else [('D-68', 'Summer Martial Tournament'), ('D-55', 'Ruslan agrees to work with Daphneya'), ('D-49', 'Daphneya → Piache')]))
    style = f"--frame:url('frames/{frame}.svg')" + (";--crest:url('frames/crest_sun.svg')" if crest else '')
    return (f'<div class="ks lay-{layout}{" ks-has-crest" if crest else ""}" style="{style}">' + ('<div class="ks-crest"></div>' if crest else '')
            + f'<div class="ks-date"><span class="ks-iy">{date}</span><span class="ks-dday">{dday}</span></div>'
            f'<div class="ks-meta">{time}<i>·</i>{place}<i>·</i><span class="ks-ab">{lab_ab} <b>{ability}</b></span></div>'
            f'{th_block}<div class="ks-rule"></div>'
            f'<div class="ks-up-label">{lab_up}</div><ol class="ks-up">{ev}</ol></div>')


EN_HEAD = ('IY 429. 7.15', 'D-68', '15:00', 'Knights\' Training Grounds', 'Time Stop')
EN_THOUGHTS = [
    ('Hedwig', 'So you only intend to watch. If you came for someone else again, I would rather you just said so.'),
    ('Ruslan', 'Found another amusing spectacle, have we? What scheme is it this time?'),
]
VARIANTS = {
    'lay_stack': card('frame_cut', layout='stack', lang='ko'),
    'lay_runin': card('frame_cut', layout='runin', lang='ko'),
    'lay_quote': card('frame_cut', layout='quote', lang='ko'),
    'lay_runin_en': card('frame_cut', layout='runin', lang='en', thoughts=EN_THOUGHTS, head=EN_HEAD),
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
</style><h1>이름 · 속마음 배치 세 가지</h1>
<p class="note">이름 아래 빈 공간이 없도록 바꾼 세 가지입니다. 한국어 설정이면 라벨이 '능력 · 다가올 일', 영어 설정이면 'Ability · Upcoming'.</p>
<h2>1. 이름 위, 속마음 아래 (줄바꿈)</h2><div class="row">
<div class="col"><span>PC</span><img src="lay_stack_pc.png" style="width:680px"></div>
<div class="col"><span>모바일</span><img src="lay_stack_m.png" style="width:375px"></div></div>
<h2>2. 이름을 문장 맨 앞에 붙여 쓰기 — 줄이 넘어가면 왼쪽 끝부터</h2><div class="row">
<div class="col"><span>PC</span><img src="lay_runin_pc.png" style="width:680px"></div>
<div class="col"><span>모바일</span><img src="lay_runin_m.png" style="width:375px"></div></div>
<h2>3. 속마음 먼저, 이름은 오른쪽 아래 (편지 서명처럼)</h2><div class="row">
<div class="col"><span>PC</span><img src="lay_quote_pc.png" style="width:680px"></div>
<div class="col"><span>모바일</span><img src="lay_quote_m.png" style="width:375px"></div></div>
<h2>참고: 2번을 영어 설정으로 (모바일) — 라벨·원작 이벤트 이름까지 영어</h2><div class="row">
<div class="col"><img src="lay_runin_en_m.png" style="width:375px"></div></div>
"""
open(os.path.join(OUT, 'sheet_layout.html'), 'w', encoding='utf-8').write(SHEET)
print('built', sorted(os.listdir(OUT)))
