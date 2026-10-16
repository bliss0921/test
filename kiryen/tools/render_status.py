import json, re, sys, os
from lupa.lua54 import LuaRuntime
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cbs_mini import render
# python3 -I render_status.py 카드.charx 출력폴더
# 필요: pip install lupa playwright, node + (이 폴더에서) npm install @adobe/css-tools@4.4.4 postcss-selector-parser@7.1.1
# 상태창 HTML 은 카드의 Lua 로 만들고, CSS 는 RisuAI 와 같은 라이브러리로 x-risu- 접두사·.chattext 범위를 입혀서 그린다.
import subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
from charx_io import load_any  # noqa: E402
d = load_any(sys.argv[1])
m = d['mod']['module']; risu = d['card']['data']['extensions']['risuai']
FONTS = os.path.join(HERE, '..', 'design', 'fonts')  # design/README 의 글꼴 (git 에는 없음)
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(open(os.path.join(HERE, 'test_lua.py'), encoding='utf-8').read().split("MOCK = r'''", 1)[1].split("'''", 1)[0])
lua.execute(m['trigger'][0]['effect'][0]['code'])
G = lua.globals()
def disp(text, idx, en=False):
    lua.execute('TOGGLES = {}')
    if en: G.TOGGLES['toggle_kc_language'] = '1'
    return G._listeners.editDisplay('id', text, lua.table_from({'index': idx}))

def risu_classes(html):   # DOMPurify hook: class="a b" -> class="x-risu-a x-risu-b"
    return re.sub(r'class="([^"]*)"', lambda mm: 'class="' + ' '.join('x-risu-' + c for c in mm[1].split()) + '"', html)

def risu_css(css):        # decodeStyleRule: .a -> .x-risu-a, then ".chattext " prefix
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css = re.sub(r'@import[^;]+;', '', css)
    def rule(mm):
        sels = ','.join('.chattext ' + re.sub(r'\.([A-Za-z][\w-]*)', r'.x-risu-\1', s.strip()) for s in mm[1].split(','))
        return sels + '{' + mm[2] + '}'
    return re.sub(r'([^{}@]+)\{([^{}]*)\}', rule, css)

bg = risu['backgroundHTML']
css = subprocess.run(['node', os.path.join(HERE, 'risu_css.cjs')], input=bg.split('<style>', 1)[1].rsplit('</style>', 1)[0],
                     capture_output=True, text=True, check=True, cwd=HERE).stdout  # RisuAI 실제 CSS 변환 결과
panel = render(m['regex'][0]['out'], {}, {}, {'perma': 'fm_karenya'}).replace('{{user}}', '유저')
KO = '[IY: 429. 7.15 (D-68) | 15:00 | 기사단 연무장 | 시간 정지 || 헤드비히 | …보고만 계실 셈인가. 예전처럼 다른 자를 보러 오신 거라면, 차라리 그렇다고 말씀하시지. || 루스란 | 또 재미있는 구경거리를 찾았군. 이번엔 무슨 꿍꿍이지?]'
EN = "[IY: 429. 7.15 (D-68) | 15:00 | Knights' Training Ground | Time Stop || Hedwig | So Your Majesty means only to watch. If you came for someone else again, I would rather you just said so. || Ruslan | Found another amusing spectacle, have we?]"
GREET = '[IY: 429. 6.13 (D-100) | 17:00 | 황제의 집무실 | 미공개 || 셀레니아 | 폐하의 안색이 심상치 않다. 황의를 불러드려야 하나.]'
ALONE = '[IY: 429. 9.21 (D-0) | 23:40 | 황제의 침소 | 시간 정지]'
PROSE = '<p>헤드비히의 시선이 연무장 너머, 황제가 선 자리로 천천히 옮겨 갔다. 아무도 그 눈빛의 의미를 묻지 않았다.</p>'
cards = {
    'greeting': risu_classes(panel) + '<p>…셀레니아였다. 잠시 침묵하던 유저의 입술이 천천히 열렸다.</p>' + risu_classes(disp(GREET, -1)),
    'ko': PROSE + risu_classes(disp(KO, 4)),
    'en': '<p>Hedwig\'s gaze drifted across the training ground.</p>' + risu_classes(disp(EN, 4, True)),
    'alone_free': risu_classes(disp(ALONE, 4)) + '<p>(자유 시작)</p>' + risu_classes(disp('[IY: ? | ? | ? | ?]', -1)),
}
BASE = f"""@font-face{{font-family:'Gowun Batang';src:url({FONTS}/GowunBatang-Regular.ttf);font-weight:400}}
@font-face{{font-family:'Gowun Batang';src:url({FONTS}/GowunBatang-Bold.ttf);font-weight:700}}
@font-face{{font-family:'Noto Sans KR';src:url({FONTS}/NotoSansKR.ttf);font-weight:100 900}}
:root{{--risu-font-family:Arial,sans-serif;--FontColorStandard:#d6d3cf}}
* {{font-family:var(--risu-font-family)}}
html,body{{margin:0;background:#1e1d22}} body{{padding:14px 10px 18px}}
.chattext{{display:block;color:#d6d3cf;font-size:15px;line-height:1.75;max-width:65ch}}
.chattext p{{color:var(--FontColorStandard);margin:1.25em 0}}
.prose :where(ol){{list-style-type:decimal;margin-top:1.25em;margin-bottom:1.25em;padding-inline-start:1.625em}}
.prose :where(ol > li){{padding-inline-start:.375em;margin:.5em 0}}
.prose :where(b,strong){{color:#fff;font-weight:600}}"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    pg = b.new_page(device_scale_factor=2)
    for name, html in cards.items():
        f = os.path.abspath(f'{OUT}/{name}.html')
        open(f, 'w', encoding='utf-8').write(f'<!doctype html><meta charset="utf-8"><style>{BASE}</style><style>{css}</style><div class="chattext prose">{html}</div>')
        for w, tag in ((680, 'pc'), (375, 'm')):
            pg.set_viewport_size({'width': w, 'height': 300})
            pg.goto('file://' + f); pg.wait_for_timeout(400)
            h = pg.evaluate('Math.ceil(document.body.getBoundingClientRect().bottom)')
            pg.screenshot(path=f'{OUT}/{name}_{tag}.png', clip={'x': 0, 'y': 0, 'width': w, 'height': h}, full_page=True)
            print(name, tag, h)
    b.close()
