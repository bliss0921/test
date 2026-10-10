# RED MOON 인물소개 시안 생성기
# python3 gen.py  ->  out/draft_A.html ... out/draft_D.html, out/draft_W1~W3.html (B 흰 배경판)
# python3 render.py out/draft_A.html out/draft_A.png ...
import math
import os

W = 1000
GAP = 16          # 카드 사이 흰 대각선 틈
Y0 = 110          # 첫 카드 윗변(높은 쪽) y
SLOPE = 100       # 대각선 높이차
BIG = 850         # 인물 쪽 카드 높이
SMALL = BIG - 2 * SLOPE
BOTTOM_PAD = 40

# 경계선: (왼쪽 y, 오른쪽 y)
L = [(Y0, Y0 + SLOPE)]
L.append((L[0][0] + BIG, L[0][1] + SMALL))      # 1번 아래 / 2번 위
L.append((L[1][0] + SMALL, L[1][1] + BIG))      # 2번 아래 / 3번 위
L.append((L[2][0] + BIG, L[2][1] + SMALL))      # 3번 아래
END = max(L[3]) + BOTTOM_PAD


def line_y(i, x, off=0):
    yl, yr = L[i]
    return yl + (yr - yl) * x / W + off


def band_top(i, x):      # i번 카드(0부터) 윗변
    return line_y(i, x, GAP / 2 if i > 0 else 0)


def band_bot(i, x):      # i번 카드 아랫변
    return line_y(i + 1, x, -GAP / 2 if i < 2 else 0)


def poly(pts):
    return "polygon(" + ",".join(f"{x:.1f}px {y:.1f}px" for x, y in pts) + ")"


def band_poly(i):
    return poly([(0, band_top(i, 0)), (W, band_top(i, W)), (W, band_bot(i, W)), (0, band_bot(i, 0))])


CHARS = [
    dict(key="seohu", img="seohu.png", side="L", name="서후", en="Seohu", age=23,
         quote="누나아, 나 봐봐요.<br>아니이, 옆에 말고 나아.",
         tags=["#내숭", "#돈만주면다함"],
         desc=["고졸 일진. 입 험함. 성격 나쁨.", "대포폰으로 공사침.", "야스할 때 손버릇 험함."],
         note="(손님한텐 안 그럼)", love=35,
         c=dict(band="#f7e4e8", soft="#fbf1f3", deep="#efc6d3", acc="#d0607f", chip="#f1d0da", chipt="#a24f6a")),
    dict(key="rebel", img="rebel.png", side="R", name="레블", en="Rebel", age=24,
         quote="누나, 내 바이크 뒤에 타면<br>울겠는데? 아니야?<br>그럼 타보든가!",
         tags=["#도파민중독", "#재미가우선"],
         desc=["휴학생. 스릴이 최고임.", "야스할 때도 스릴 추구.", "섹파 많음."],
         note=None, love=70,
         c=dict(band="#ede8f5", soft="#f5f2fa", deep="#d6cbee", acc="#8a6fcf", chip="#ddd3f0", chipt="#6a55a8")),
    dict(key="juyoon", img="juyoon.png", side="L", name="주윤", en="Juyoon", age=27,
         quote="주윤입니다.",
         tags=["#클로짓게이", "#통제광"],
         desc=["다른 호빠 사장 아빠가 시켜서<br>배울 겸 일함.", "게이인 것도 집안도 비밀.", "야스할 때도 컨트롤프릭임."],
         note="(남자 한정)", love=5,
         c=dict(band="#e2eaf3", soft="#f0f4f9", deep="#c3d5e9", acc="#5a88c2", chip="#cadbeb", chipt="#3f6a9c")),
]

PH_W = 540        # 인물 컷 폭
PH_H = round(PH_W * 1660 / 948)
POP = 95          # 위 칸으로 튀어나오는 정도(머리 꼭대기 기준 대략)
TEXT_W = 400


def photo(i, ch, fade=True, gap=True):
    if ch["side"] == "L":
        left = -20
    else:
        left = W - PH_W + 20
    hx = left + PH_W * 0.45
    top = band_top(i, hx) - POP
    bot = band_bot if gap else (lambda i, x: line_y(i + 1, x))
    pts = [(0, 0), (PH_W, 0), (PH_W, bot(i, left + PH_W) - top), (0, bot(i, left) - top)]
    m = ""
    if fade:
        d = "90deg" if ch["side"] == "L" else "270deg"
        g = f"linear-gradient({d},#000 80%,transparent 99%)"
        m = f"-webkit-mask-image:{g};mask-image:{g};"
    return (f'<div class="ph" style="left:{left}px;top:{top:.0f}px;width:{PH_W}px;height:{PH_H}px;'
            f'clip-path:{poly(pts)};{m}"><img src="../img/{ch["img"]}" style="width:{PH_W}px"></div>')


def text_box(i, ch, inner, dy=0, width=TEXT_W):
    if ch["side"] == "L":
        x = W - 50 - width
    else:
        x = 50
    cx = x + width / 2
    mid = (band_top(i, cx) + band_bot(i, cx)) / 2
    # 높이를 몰라도 세로 가운데 맞춤: top=mid, translateY(-50%)
    return (f'<div class="info c{i}" style="left:{x}px;top:{mid + dy:.0f}px;width:{width}px">{inner}</div>')


FONTFACE = """
@font-face{font-family:'Gowun Batang';src:url('../fonts/GowunBatang-Regular.ttf');font-weight:400}
@font-face{font-family:'Gowun Batang';src:url('../fonts/GowunBatang-Bold.ttf');font-weight:700}
@font-face{font-family:'Gowun Dodum';src:url('../fonts/GowunDodum-Regular.ttf');font-weight:400}
@font-face{font-family:'Cormorant';src:url('../fonts/CormorantGaramond.ttf');font-weight:300 700}
@font-face{font-family:'Cormorant';src:url('../fonts/CormorantGaramond-Italic.ttf');font-weight:300 700;font-style:italic}
"""

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html{width:1000px;overflow:hidden}
body{width:1000px;height:%(END)dpx;position:relative;overflow:hidden;background:#fff;color:#3a3340;
 font-family:'Noto Sans CJK KR','Noto Sans KR',sans-serif;-webkit-font-smoothing:antialiased}
.band{position:absolute;left:0;top:0;width:1000px;height:%(END)dpx;z-index:1;overflow:hidden}
.ph{position:absolute;z-index:3}
.ph img{display:block;height:auto}
.info{position:absolute;z-index:4;transform:translateY(-50%%)}
.name{font-size:92px;font-weight:900;line-height:1;letter-spacing:-3px;display:flex;align-items:baseline;color:#3a3340}
.name small{font-size:32px;font-weight:400;letter-spacing:0;margin-left:10px;color:#7a7180}
.en{font-size:17px;font-weight:700;letter-spacing:.42em;color:var(--acc);display:flex;align-items:center;gap:12px;margin-bottom:12px}
.en::before{content:'';width:34px;height:2px;background:var(--acc);opacity:.7}
.quote{position:relative;margin-top:22px;padding-top:50px;font-family:'Gowun Batang',serif;font-weight:700;
 font-size:31px;line-height:1.55;letter-spacing:-.5px;color:#3a3340;word-break:keep-all}
.quote::before{content:'\\201C';position:absolute;left:-6px;top:-40px;font-family:'Cormorant',serif;font-weight:700;
 font-size:170px;line-height:1;color:var(--acc);opacity:.6}
.quote .qc{font-family:'Cormorant',serif;font-weight:700;font-size:104px;line-height:0;color:var(--acc);opacity:.6;
 vertical-align:-48px;margin-left:6px}
.rule{height:1px;background:#3a334022;margin:26px 0 22px}
.tags{display:flex;gap:10px;flex-wrap:wrap}
.tags span{font-size:20px;font-weight:700;padding:6px 15px;border-radius:7px;background:var(--chip);color:var(--chipt)}
.desc{margin-top:20px;font-size:21px;line-height:1.72;color:#5b5361;word-break:keep-all}
.desc .note{color:#9a92a0;font-size:19px}
"""


def vars_css():
    out = []
    for i, ch in enumerate(CHARS):
        c = ch["c"]
        out.append(f".c{i}{{--band:{c['band']};--soft:{c['soft']};--deep:{c['deep']};--acc:{c['acc']};"
                   f"--chip:{c['chip']};--chipt:{c['chipt']}}}")
    return "\n".join(out)


def desc_html(ch):
    d = "".join(f"<p>{x}</p>" for x in ch["desc"])
    if ch["note"]:
        d += f'<p class="note">{ch["note"]}</p>'
    return f'<div class="desc">{d}</div>'


def tags_html(ch):
    return '<div class="tags">' + "".join(f"<span>{t}</span>" for t in ch["tags"]) + "</div>"


def quote_html(ch):
    return f'<div class="quote">{ch["quote"]}<span class="qc">”</span></div>'


def name_html(ch):
    return f'<div class="name">{ch["name"]}<small>({ch["age"]})</small></div>'


def page(css, body):
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>{FONTFACE}'
            f'{BASE_CSS % {"END": END}}{vars_css()}{css}</style></head><body>{body}</body></html>')


# ───────────────────────── A. 파스텔 카드 (레퍼런스형)
def draft_A():
    body = []
    for i, ch in enumerate(CHARS):
        body.append(f'<div class="band c{i}" style="clip-path:{band_poly(i)};background:var(--band)"></div>')
    for i, ch in enumerate(CHARS):
        body.append(photo(i, ch))
        inner = (f'<div class="en">{ch["en"].upper()}</div>{name_html(ch)}{quote_html(ch)}'
                 f'<div class="rule"></div>{tags_html(ch)}{desc_html(ch)}')
        body.append(text_box(i, ch, inner, dy=-20))
    return page("", "".join(body))


# ───────────────────────── B. 달(Moon) + 영문 이름
B_TYPE_CSS = """
.enb{font-family:'Cormorant',serif;font-style:italic;font-weight:500;font-size:64px;line-height:1;color:var(--acc);
 letter-spacing:1px;margin-bottom:-6px;opacity:.9}
.name{font-family:'Gowun Batang',serif;font-weight:700;letter-spacing:-2px;font-size:96px}
.name small{font-family:'Noto Sans CJK KR',sans-serif}
"""


def moon_divs(i, ch, r=300):
    # 인물 머리 뒤에 달
    cx = 245 if ch["side"] == "L" else W - 245
    cy = band_top(i, cx) + 330
    return (f'<div class="moon" style="left:{cx - r}px;top:{cy - r:.0f}px;width:{2 * r}px;height:{2 * r}px"></div>'
            f'<div class="ring" style="left:{cx - r - 22}px;top:{cy - r - 22:.0f}px;width:{2 * r + 44}px;height:{2 * r + 44}px"></div>')


def draft_B():
    css = """
.band{background:linear-gradient(160deg,var(--band) 0%,var(--soft) 48%,var(--band) 100%)}
.moon{position:absolute;border-radius:50%;
 background:radial-gradient(circle at 50% 38%,#ffffffcc 0%,#ffffff00 46%),linear-gradient(180deg,var(--deep) 0%,var(--band) 92%)}
.ring{position:absolute;border-radius:50%;border:1.5px solid var(--acc);opacity:.28}
""" + B_TYPE_CSS
    body = []
    for i, ch in enumerate(CHARS):
        body.append(f'<div class="band c{i}" style="clip-path:{band_poly(i)}">{moon_divs(i, ch)}</div>')
    for i, ch in enumerate(CHARS):
        body.append(photo(i, ch))
        inner = (f'<div class="enb">{ch["en"]}</div>{name_html(ch)}{quote_html(ch)}'
                 f'<div class="rule"></div>{tags_html(ch)}{desc_html(ch)}')
        body.append(text_box(i, ch, inner, dy=-20))
    return page(css, "".join(body))


# ───────────────────────── B 흰 배경 버전
# W1 완전 하양 / W2 달만 / W3 달 + 바닥빛 / W4 바닥빛만 / W5 바닥빛만(진하게)
def card_poly(i):
    return poly([(0, line_y(i, 0)), (W, line_y(i, W)), (W, line_y(i + 1, W)), (0, line_y(i + 1, 0))])


def floor_glow(i, h=280, cls="floor"):
    # 카드 아랫변을 따라 위로 옅어지는 띠
    yl, yr = L[i + 1]
    ang = math.degrees(math.atan2(yr - yl, W))
    cy = (yl + yr) / 2
    return (f'<div class="{cls}" style="left:-100px;top:{cy - h:.0f}px;width:{W + 200}px;height:{h}px;'
            f'transform-origin:50% 100%;transform:rotate({ang:.2f}deg)"></div>')


def draft_W(kind):
    css = """
.band{background:transparent}
.moon{position:absolute;border-radius:50%;
 background:radial-gradient(circle at 50% 38%,#ffffffb3 0%,#ffffff00 46%),linear-gradient(180deg,var(--deep) 0%,var(--band) 92%)}
.ring{position:absolute;border-radius:50%;border:1.5px solid var(--acc);opacity:.3}
.floor{position:absolute;background:linear-gradient(0deg,var(--band) 0%,#ffffff00 100%)}
.floor2{position:absolute;background:linear-gradient(0deg,var(--band) 0%,var(--band) 20%,#ffffff00 100%)}
svg.lines{position:absolute;left:0;top:0;z-index:2}
svg.lines line{stroke:#e2dce7;stroke-width:2}
""" + B_TYPE_CSS
    body = []
    for i, ch in enumerate(CHARS):
        inner = ""
        if kind in ("moon", "floor"):
            inner += moon_divs(i, ch)
        if kind in ("floor", "flooronly"):
            inner += floor_glow(i)
        if kind == "floorstrong":
            inner += floor_glow(i, h=440, cls="floor2")
        if inner:
            body.append(f'<div class="band c{i}" style="clip-path:{card_poly(i)}">{inner}</div>')
    ls = "".join(f'<line x1="0" y1="{yl}" x2="{W}" y2="{yr}"/>' for yl, yr in L)
    body.append(f'<svg class="lines" width="{W}" height="{END}" viewBox="0 0 {W} {END}">{ls}</svg>')
    for i, ch in enumerate(CHARS):
        body.append(photo(i, ch, gap=False))
        inner = (f'<div class="enb">{ch["en"]}</div>{name_html(ch)}{quote_html(ch)}'
                 f'<div class="rule"></div>{tags_html(ch)}{desc_html(ch)}')
        body.append(text_box(i, ch, inner, dy=-20))
    return page(css, "".join(body))


# ───────────────────────── C. 대사창 (미연시 텍스트박스)
def draft_C():
    css = """
.vn{position:relative;margin-top:34px;background:#ffffffe6;border:2px solid var(--deep);border-radius:20px;
 padding:34px 30px 26px;box-shadow:0 6px 0 var(--deep)}
.vn .tab{position:absolute;top:-21px;left:22px;background:var(--acc);color:#fff;font-size:20px;font-weight:700;
 padding:6px 22px;border-radius:999px;letter-spacing:.05em}
.vn .quote{margin-top:0;padding-top:0;font-size:29px}
.vn .quote::before{display:none}
.vn .qo,.vn .qc2{font-family:'Gowun Batang',serif;color:var(--acc);font-size:1.15em}
.vn .next{position:absolute;right:20px;bottom:12px;width:0;height:0;border-left:9px solid transparent;
 border-right:9px solid transparent;border-top:12px solid var(--acc);opacity:.75}
.vn .quote .qc{display:none}
.tags{margin-top:28px}
"""
    body = []
    for i, ch in enumerate(CHARS):
        body.append(f'<div class="band c{i}" style="clip-path:{band_poly(i)};background:var(--band)"></div>')
    for i, ch in enumerate(CHARS):
        body.append(photo(i, ch))
        q = f'<div class="quote"><span class="qo">“</span>{ch["quote"]}<span class="qc2">”</span></div>'
        inner = (f'<div class="en">{ch["en"].upper()}</div>{name_html(ch)}'
                 f'<div class="vn"><div class="tab">{ch["name"]}</div>{q}<div class="next"></div></div>'
                 f'{tags_html(ch)}{desc_html(ch)}')
        body.append(text_box(i, ch, inner, dy=-10, width=430))
    return page(css, "".join(body))


# ───────────────────────── D. 호감도 게이지
HEART = ('<svg viewBox="0 0 24 22" width="22" height="20"><path d="M12 21s-8.5-5.3-10.6-10.2C-.2 6.9 2.2 2 6.6 2'
         'c2.4 0 4.2 1.3 5.4 3.1C13.2 3.3 15 2 17.4 2c4.4 0 6.8 4.9 5.2 8.8C20.5 15.7 12 21 12 21z" fill="currentColor"/></svg>')


def draft_D():
    css = """
.love{display:flex;align-items:center;gap:12px;margin-top:24px;color:var(--acc)}
.love .lbl{font-size:19px;font-weight:700;letter-spacing:.08em;color:var(--chipt);white-space:nowrap}
.love .bar{flex:1;height:16px;border-radius:999px;background:#ffffffb3;border:1.5px solid var(--deep);overflow:hidden}
.love .bar i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,var(--deep),var(--acc))}
.love .val{font-weight:900;font-size:24px;line-height:1;color:var(--acc);min-width:62px;text-align:right}
.love .val small{font-size:16px;font-weight:700}
"""
    body = []
    for i, ch in enumerate(CHARS):
        body.append(f'<div class="band c{i}" style="clip-path:{band_poly(i)};background:var(--band)"></div>')
    for i, ch in enumerate(CHARS):
        body.append(photo(i, ch))
        love = (f'<div class="love">{HEART}<span class="lbl">호감도</span><div class="bar"><i style="width:{ch["love"]}%">'
                f'</i></div><span class="val">{ch["love"]}<small>%</small></span></div>')
        inner = (f'<div class="en">{ch["en"].upper()}</div>{name_html(ch)}{quote_html(ch)}'
                 f'{love}<div class="rule"></div>{tags_html(ch)}{desc_html(ch)}')
        body.append(text_box(i, ch, inner, dy=-20))
    return page(css, "".join(body))


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for k, f in [("A", draft_A), ("B", draft_B), ("C", draft_C), ("D", draft_D),
                 ("W1", lambda: draft_W("plain")), ("W2", lambda: draft_W("moon")), ("W3", lambda: draft_W("floor")),
                 ("W4", lambda: draft_W("flooronly")), ("W5", lambda: draft_W("floorstrong"))]:
        with open(os.path.join(here, "out", f"draft_{k}.html"), "w", encoding="utf-8") as fp:
            fp.write(f())
    print("END", END, "lines", L)
