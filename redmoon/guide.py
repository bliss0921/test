# 아카라이브 붙여넣기용 봇 소개 HTML (아카라이브 HTML 가이드 v6.7.1 규칙 준수)
# python3 guide.py  ->  out/guide.html (붙여넣기용 본문), out/guide_preview*.html (미리보기용)
import os
import re

SANS = "'Pretendard','Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif"
SERIF = "'Noto Serif KR','Noto Serif CJK KR','Nanum Myeongjo','AppleMyungjo','Batang',serif"

INK = "#2f2934"      # 제목
TEXT = "#4a4350"     # 본문
META = "#776e7e"     # 보조
LINE = "#ebe6ef"     # 구분선
# 인물 색 (인물소개 이미지와 같은 계열): 글자색 / 연한 면
PINK, PINK_T = "#c4567a", "#fbeef2"
LAV, LAV_T = "#7a5fc6", "#f3effb"
BLUE, BLUE_T = "#4a78b5", "#edf2f9"
GRAY, GRAY_T = "#5e5666", "#f4f2f6"
BAND = "linear-gradient(90deg,#f5dce4,#e9e2f6,#dde7f3)"       # 바닥빛 (인물소개 W4)
BAR = "linear-gradient(90deg,#e58aa5,#a58ee0,#7fa6d8)"


def d(style, inner):
    return f'<div style="{style}">{inner}</div>'


def s(style, inner):
    return f'<span style="{style}">{inner}</span>'


def deco(style):
    # 빈 장식 요소는 편집기가 지우므로 &nbsp;를 넣는다
    return f'<div style="{style};font-size:0;line-height:0;">&nbsp;</div>'


def chip(text, tint="#f4f1f7"):
    return s(f"display:inline-block;margin:3px 3px;padding:5px 12px;border-radius:999px;"
             f"background:linear-gradient(90deg,{tint},{tint});border:1px solid {LINE};"
             f"font-size:13px;font-weight:700;", text)


def section(title, body):
    moon = s("display:inline-block;width:12px;height:12px;border-radius:50%;vertical-align:middle;margin-right:10px;"
             "background:radial-gradient(circle at 35% 35%,#ffffff,#eab9c9 55%,#bfb0ea);font-size:0;line-height:0;", "&nbsp;")
    head = d("margin:44px 0 0;", moon + s(f"font-family:{SERIF};font-size:22px;font-weight:900;color:{INK};"
                                          f"vertical-align:middle;letter-spacing:1px;", title))
    rule = deco("height:1px;margin:12px 0 4px;background:linear-gradient(90deg,#d8cde3,rgba(216,205,227,0))")
    return head + rule + body


def row(label, body, last=False):
    bd = "" if last else f"border-bottom:1px solid {LINE};"
    return d(f"padding:15px 2px;{bd}",
             d(f"font-size:13px;font-weight:800;color:{META};letter-spacing:1px;", label)
             + d("font-size:15px;line-height:1.85;margin-top:5px;", body))


def b(text):
    return f'<strong style="color:{INK};">{text}</strong>'


def note(text):
    return s(f"font-size:13px;color:{META};", text)


def card(name, color, tint, body):
    return d(f"margin-top:10px;padding:14px 16px;border-left:3px solid {color};border-radius:0 10px 10px 0;"
             f"background:linear-gradient(90deg,{tint},#ffffff);",
             d(f"font-family:{SERIF};font-size:17px;font-weight:900;color:{color};", name)
             + d("font-size:15px;line-height:1.8;margin-top:4px;", body))


def play(text, sub, color, tint):
    return d(f"margin-top:8px;padding:11px 16px;border-left:3px solid {color};border-radius:0 10px 10px 0;"
             f"background:linear-gradient(90deg,{tint},#ffffff);font-size:15px;line-height:1.7;",
             text + " " + note(sub))


def sublabel(text):
    return d(f"margin-top:22px;font-size:14px;font-weight:800;color:{INK};", text)


def line(name, color, words):
    return d("margin-top:6px;font-size:15px;line-height:1.7;",
             s(f"display:inline-block;width:42px;font-weight:800;color:{color};", name)
             + s(f"font-family:{SERIF};font-weight:700;color:{INK};", words))


def build():
    hero = d(f"background:{BAND};",
             d("padding:50px 22px 38px;text-align:center;"
               "background:linear-gradient(180deg,#ffffff 0%,rgba(255,255,255,0.94) 42%,rgba(255,255,255,0) 100%);",
               d(f"font-family:{SERIF};font-size:15px;letter-spacing:3px;color:{META};", "신논현역, 레드문")
               + d(f"font-family:{SERIF};font-size:40px;line-height:1.2;font-weight:900;letter-spacing:7px;color:{INK};margin-top:10px;",
                   "RED MOON")
               + d("font-size:14px;font-weight:700;letter-spacing:2px;margin-top:6px;", "봇 이용 안내")
               + deco(f"width:120px;height:3px;margin:20px auto 16px;border-radius:3px;background:{BAR}")
               + d("", chip("호빠봇") + chip("메인 NPC 3명") + chip("서브 NPC n명"))))

    info = section("봇 정보",
        row("성향", "거의 쿰봇임. 쿰질만 오지게 해서 캐해 테스트는 많이 안 함. 야스는 맛있었음.")
        + row("기능", "별거 없음." + d("margin-top:6px;", chip("상태창") + chip("일기") + chip("NPC 쪼개놓은 토글")
                                                       + chip("사이드바 은어사전")), last=True))

    setting = section("권장 설정",
        row("출력", f"디스크립션에 한국어 섞여 있어서 {b('한출 권장')}하는데 영출도 꽤 괜찮음. "
                    "오푸스는 나도 한출하다 너무 비싸서 영출했음. 장기 넘어가면 대사에 한국어 섞이는 찐빠는 좀 있음. "
                    f"{b('잼은 걍 한출하셈.')}")
        + row("번역", "누더기프롬 재작성-웹소설작가 하니 대사 느낌 괜찮았음.")
        + row("로어북", f"은어나 지침은 {b('항상 활성화')} 권장, NPC 리스트도 {b('상시 활성화')} 권장.")
        + row("테스트", d("margin-top:2px;", chip("오육솔(천해)") + chip("오오오푸스(attg, 천해)") + chip("잼삼칠(누렁이)")),
              last=True))

    guide = section("플레이 가이드",
        sublabel("재밌었던 플레이")
        + play("서후 전여친", "(얘 성격 잘 나옴)", PINK, PINK_T)
        + play("서후 동생 짝사랑하는데 꿩 대신 닭으로 서후 지명하기", "(둘이 닮았음)", PINK, PINK_T)
        + play("레블 누나 친구", "(누나 응급의학과 던트임)", LAV, LAV_T)
        + play("주윤이랑 원나잇한 사이", "(얘 가끔 게이바 감)", BLUE, BLUE_T)
        + sublabel("난 그냥 쿰질 존나 할 거다")
        + card("서후", PINK, PINK_T, "돈 많은 페소로 돈 뿌리면 한 번에 2차 감.")
        + card("레블", LAV, LAV_T, "섹파 스타트하거나, 예쁘고 몸매 좋은 애로 꼬시면 재밌겠다고 2차 감.")
        + card("주윤", BLUE, BLUE_T, "호빠 말고 게이바 스타트하는 게 빠름."
               + d("margin-top:4px;", note("※ 게이플만 해서 헤테로로 어떻게 나올진 잘 모르겠음.")))
        + card("공용", GRAY, GRAY_T, "모두의 공용 암캐가 되고 싶다면 호빠 선수들 스트레스 해소용 성처리 당번이 되어봅시다. "
               "돈 받고 일한다 하면 오푸스 검열도 안 하고 페티시 개잘 말아줌."))

    sample = d(f"margin:10px 0;padding:13px 16px;border:1px solid {LINE};border-radius:10px;"
               "background:linear-gradient(180deg,#fbfafc,#f6f4f8);",
               d(f"font-size:13px;color:{META};", "ex. 서후가 페소방 들어갔다 나오면")
               + line("레블", LAV, "“거기 좋음? 쓰리섬 고?”")
               + line("서후", PINK, "“꺼져 씨발.”"))
    notes = section("참고 사항",
        row("은어", "은어가 실제로 맞는지, 실제 호빠가 이렇게 돌아가는진 나도 모름. 짚한테 조사시켜서 작성함.")
        + row("메인캐 간략버전", "누구 한 명 잡고 공략하는데, 캐랑 다른 애들 티키타카하는 거 보고 싶을 때용임."
              + sample + "성격이랑 간략한 스펙 정도만 들어간 거라 이 상태로 섹각이나 순애각 잡는 건 비추.")
        + row("본명", "애들 본명 로어북에 적혀 있음. 지침상 일할 때는 본명 비밀인데 잼민이 오지게 못 지킴. "
                     f"그거 잡겠다고 토큰 낭비하기 싫어서 난 걍 흐린 눈 함. {b('서후 본명 개싫어함.')}", last=True))

    floor = d(f"background:{BAND};",
              deco("height:40px;background:linear-gradient(180deg,#ffffff,rgba(255,255,255,0))"))

    html = d(f"max-width:860px;margin:0 auto;background:linear-gradient(180deg,#ffffff,#ffffff);border:1px solid {LINE};"
             f"color:{TEXT};font-family:{SANS};",
             hero + d("padding:0 24px 40px;", info + setting + guide + notes) + floor)
    return dark_guard(html)


def dark_guard(html):
    # 가이드 7-7-1: 인라인 color가 있는 요소에 background-color:rgba(0,0,0,0.004)를 덧붙인다
    def fix(m):
        st = m.group(1)
        if re.search(r"(?<![-\w])color:", st) and "background-color" not in st:
            st = st.rstrip(";") + ";background-color:rgba(0,0,0,0.004);"
        return f'style="{st}"'
    return re.sub(r'style="([^"]*)"', fix, html)


BLOCKED_PROPS = r"(?<![-\w])(display:\s*(flex|grid|inline-grid)|grid-template|position|z-index|overflow|(?<![-\w])gap|transform|animation|transition|opacity|filter|clip-path|mask|cursor|pointer-events|user-select|writing-mode|content:|outline|url\()"
BLOCKED_TAGS = r"<(style|script|link|code|button|form|input|small|big|mark|svg|dl|dt|dd|q|cite|abbr|var)\b"


def lint(html):
    errs = []
    for st in re.findall(r'style="([^"]*)"', html):
        m = re.search(BLOCKED_PROPS, st)
        if m:
            errs.append(f"blocked css: {m.group(0)} in {st[:60]}")
        if re.search(r"(?<![-\w])color:", st) and "background-color" not in st:
            errs.append(f"no dark guard: {st[:60]}")
        if re.search(r"background-color:\s*#", st):
            errs.append(f"solid light bg: {st[:60]}")
    for m in re.finditer(BLOCKED_TAGS, html):
        errs.append(f"blocked tag: {m.group(0)}")
    for bad in ["<!--", "{", "}", " class=", "::"]:
        if bad in html:
            errs.append(f"found {bad!r}")
    if re.search(r"<(div|span)[^>]*></\1>", html):
        errs.append("empty div/span")
    opens = len(re.findall(r"<div\b", html)); closes = html.count("</div>")
    if opens != closes:
        errs.append(f"div balance {opens}/{closes}")
    opens = len(re.findall(r"<span\b", html)); closes = html.count("</span>")
    if opens != closes:
        errs.append(f"span balance {opens}/{closes}")
    return errs


# 미리보기: 아카 다크 테마 스크립트(가이드 EV-ARCA-DARK-004 설명)를 흉내 낸다
DARK_JS = """
function rgb(s){var m=s.match(/[\\d.]+/g)||[0,0,0,0];return{r:+m[0],g:+m[1],b:+m[2],a:m.length>3?+m[3]:1}}
function L(c){return [c.r,c.g,c.b].map(function(v){v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)})
 .reduce(function(s,v,i){return s+v*[0.2126,0.7152,0.0722][i]},0)}
function cr(a,b){var x=L(a),y=L(b);return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05)}
var page={r:34,g:34,b:34},n=0;
document.querySelectorAll('.article-content *').forEach(function(el){
 var cs=getComputedStyle(el),bg=rgb(cs.backgroundColor),cand=bg.a===0;
 if(!cand&&cr(bg,page)>6){cand=true;el.style.backgroundColor='initial'}
 if(cand&&cr(rgb(cs.color),page)<3&&el.style.color){el.style.removeProperty('color');n++}
});
document.title='stripped '+n;
"""


def preview(frag, dark=False, width=1000):
    bg, fg = ("#222", "#ccc") if dark else ("#fff", "#333")
    js = f"<script>{DARK_JS}</script>" if dark else ""
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"></head>'
            f'<body style="margin:0;width:{width}px;background:{bg};color:{fg}">'
            f'<div class="article-content" style="padding:20px 0">{frag}</div>{js}</body></html>')


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = lambda n: os.path.join(here, "out", n)
    frag = build()
    errs = lint(frag)
    print("lint:", "OK" if not errs else "\n  " + "\n  ".join(errs))
    open(out("guide.html"), "w", encoding="utf-8").write(frag)
    open(out("guide_preview.html"), "w", encoding="utf-8").write(preview(frag))
    open(out("guide_preview_dark.html"), "w", encoding="utf-8").write(preview(frag, dark=True))
    open(out("guide_preview_mobile.html"), "w", encoding="utf-8").write(preview(frag, width=360))
