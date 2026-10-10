# 아카라이브 붙여넣기용 봇 소개 HTML (아카라이브 HTML 가이드 v6.7.1 규칙 준수)
# python3 guide.py  ->  out/guide.html (붙여넣기용 본문), out/guide_preview*.html (미리보기용)
import os
import re

SANS = "'Pretendard','Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif"
SERIF = "'Noto Serif KR','Noto Serif CJK KR','Nanum Myeongjo','AppleMyungjo','Batang',serif"

INK = "#2f2934"      # 제목
TEXT = "#4a4350"     # 본문
LINE = "#ebe6ef"     # 구분선
BAND = "linear-gradient(90deg,#f5dce4,#e9e2f6,#dde7f3)"       # 바닥빛 (인물소개 W4)
BAR = "linear-gradient(90deg,#e58aa5,#a58ee0,#7fa6d8)"


def d(style, inner):
    return f'<div style="{style}">{inner}</div>'


def s(style, inner):
    return f'<span style="{style}">{inner}</span>'


def deco(style):
    # 빈 장식 요소는 편집기가 지우므로 &nbsp;를 넣는다
    return f'<div style="{style};font-size:0;line-height:0;">&nbsp;</div>'


def section(title, items):
    head = d(f"margin-top:44px;padding-bottom:13px;border-bottom:1px solid {LINE};line-height:1.3;"
             f"font-family:{SERIF};font-size:22px;font-weight:900;color:{INK};letter-spacing:1px;", title)
    return head + d(f"padding-top:{SEC_GAP}px;", "".join(items))


SEC_GAP = 0   # 제목 밑줄 아래 여백 (위 여백과 눈으로 같아 보이게 맞춘 값)


def li(text):
    # "- " 줄글 (내어쓰기 없음)
    return d("margin-top:10px;font-size:15px;line-height:1.85;", "- " + text)


def b(text):
    return f'<strong style="color:{INK};">{text}</strong>'


# 사진 칸: 붙여넣기용은 자리 표시 글자만 두고, 편집기에서 그 글자를 지우고 사진을 넣는다
# 아카에 올린 사진 주소 (편집기에서 받은 그대로) / 미리보기용 로컬 파일
ARCA = "//ac.arca.live/20261010sac/"
IMG = {
    "toggle": (ARCA + "5a8b417e7bd5250a31a603ed4ac42b83eebc892ac07522cfcd276f327578eee2.png?expires=1791614527&key=wXMxgHH36EakmoV1i8VSSQ",
               "../img/ui_toggle.png"),
    "slang": (ARCA + "1fb06ddc1ea9aa3f6cff4fc7b49b1ee14696847e4fba4cea20a64f4e48772acf.png?expires=1791614507&key=fLox_IsQ-dF2omT-AoySzA",
              "../img/ui_slang.png"),
    "card": (ARCA + "d4917dde027488050bc76626992b863c94de898f70b0e8ca2e9c6ec13d034eb1.png?expires=1791614770&key=9OoEUcuAJLUJRe9TDwhwBA",
             "../img/card_redmoon.webp"),
}


def img(key, local):
    return f'<img src="{IMG[key][1 if local else 0]}" class="fr-fic fr-dii" style="width:100%;">'


def shots(local):
    cells = "".join(d("display:inline-block;width:320px;max-width:100%;margin:6px;vertical-align:top;", img(k, local))
                    for k in ("toggle", "slang"))
    return d("margin-top:18px;text-align:center;", cells)


def finale(local):
    # 명함 이미지: 링크는 편집기에서 사진에 직접 건다
    return d("margin-top:56px;text-align:center;",
             d(f"font-size:21px;font-weight:900;letter-spacing:1px;color:{INK};", "아래 눌러서 호빠 놀러가기")
             + d("display:inline-block;width:360px;max-width:100%;margin-top:16px;", img("card", local)))


def build(local=False):
    hero = d(f"background:{BAND};",
             d("padding:50px 22px 38px;text-align:center;"
               "background:linear-gradient(180deg,#ffffff 0%,rgba(255,255,255,0.94) 42%,rgba(255,255,255,0) 100%);",
               d(f"font-family:{SERIF};font-size:40px;line-height:1.2;font-weight:900;letter-spacing:7px;color:{INK};",
                 "RED MOON")
               + d("font-size:14px;font-weight:700;letter-spacing:2px;margin-top:8px;", "신논현역 소재 호스트바")
               + deco(f"width:120px;height:3px;margin:20px auto 0;border-radius:3px;background:{BAR}")))

    info = section("봇 정보", [
        li("메인 NPC 3명, 서브 NPC 11명 있는 호빠봇임."),
        li("거의 쿰봇임. 쿰질만 오지게 해서 캐해 테스트는 많이 안 함. 야스는 맛있었음."),
        li("퍼메는 유저가 친구 반하나랑 처음으로 레드문에 방문하는 1개만 있음. "
           "영어/한국어 각각 있는데 영어는 일부러 한국 느낌 유지하려고 hyung, oppa 이런 식으로 썼음."),
        li("기능은 별거 없음. 상태창과 일기, NPC 쪼개놓은 토글, 사이드바 은어사전 있음. 알아서 토글로 토큰 조절할 것."),
        li("/일기, /diary, /Diary 뒤에 인물 이름 입력하면 (ex. /일기 서후 오늘 일) 인물의 일기를 볼 수 있음. "
           "뒤에 주제를 붙여도 되고 안 붙여도 됨. 근데 무조건 문장 시작에 적어야 함."),
        shots(local),
    ])

    test = section("테스트 환경", [
        li(f"디스크립션에 한글 섞여 있어서 {b('한출 권장')}하는데 영출도 꽤 괜찮음. "
           "오푸스는 나도 한출하다 너무 비싸서 영출했음. 장기 넘어가면 대사에 한국어 섞이는 찐빠는 좀 있음. "
           "잼은 걍 한출하셈."),
        li("번역은 누더기프롬 재작성-웹소설작가 하니 대사 느낌 괜찮았음."),
        li(f"테스트는 {b('오육솔(천해), 오오오푸스(attg, 천해), 잼삼칠(누렁이)')}"),
    ])

    play = section("플레이 가이드", [
        li(f"{b('재밌었던 플레이:')} 서후 전여친(얘 성격 잘 나옴), 서후 동생 짝사랑하는데 꿩 대신 닭으로 서후 지명하기(둘이 닮았음), "
           "레블 누나 친구(누나 응급의학과 던트임), 주윤이랑 원나잇한 사이(얘 가끔 게이바 감)"),
        li(f"{b('난 그냥 쿰질 존나 할 거다:')} 돈 많은 페소로 돈 뿌리면 서후는 한 번에 2차 감. "
           "레블은 섹파 스타트하거나 예쁘고 몸매 좋은 애로 꼬시면 재밌겠다고 2차 감. "
           "주윤이는 호빠 말고 게이바 스타트하는 게 빠름. "
           "모두의 공용 암캐가 되고 싶다면 호빠 선수들 스트레스 해소용 성처리 당번이 되어봅시다. "
           "돈 받고 일한다 하면 오푸스 검열도 안 하고 페티시 개잘 말아줌."),
        li("주윤이랑은 게이플만 해서 헤테로로 어떻게 나올진 잘 모르겠음."),
    ])

    notes = section("일러두기", [
        li(f"은어나 지침은 {b('항상 활성화')} 권장, NPC 리스트도 {b('상시 활성화')} 권장."),
        li("은어가 실제로 맞는지, 실제 호빠가 이렇게 돌아가는진 나도 모름. 짚한테 조사시켜서 작성함."),
        li(f"메인캐 {b('간략버전')}은 누구 한 명 잡고 공략하는데 캐랑 다른 애들 티키타카하는 거 보고 싶을 때용임. "
           "(ex. 서후가 페소방 들어갔다 나오면 레블이 “거기 좋음? 쓰리섬 고?” 대사 치고 서후가 “꺼져 씨발.” 하는 이런 반응 보는 거임) "
           "성격이랑 간략한 스펙 정도만 들어간 거라 이 상태로 섹각이나 순애각 잡는 건 비추."),
        li(f"애들 본명 로어북에 적혀 있음. 지침상 일할 때는 본명 비밀인데 {b('잼민이 오지게 못 지킴.')} "
           "그거 잡겠다고 토큰 낭비하기 싫어서 난 걍 흐린 눈 함. 서후 본명 개싫어함."),
    ])

    floor = d(f"background:{BAND};",
              deco("height:40px;background:linear-gradient(180deg,#ffffff,rgba(255,255,255,0))"))

    html = d(f"max-width:860px;margin:0 auto;background:linear-gradient(180deg,#ffffff,#ffffff);border:1px solid {LINE};"
             f"color:{TEXT};font-family:{SANS};",
             hero + d("padding:0 26px 48px;", info + test + play + notes + finale(local)) + floor)
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
    plain = html.replace(' class="fr-fic fr-dii"', "")
    for bad in ["<!--", "{", "}", " class=", "::"]:
        if bad in plain:
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
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<style>.article-content img{max-width:100%;height:auto}.fr-dii{display:inline-block;vertical-align:bottom}</style></head>'
            f'<body style="margin:0;width:{width}px;background:{bg};color:{fg}">'
            f'<div class="article-content" style="padding:20px 0">{frag}</div>{js}</body></html>')


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = lambda n: os.path.join(here, "out", n)
    frag = build()
    shown = build(local=True)
    errs = lint(frag)
    print("lint:", "OK" if not errs else "\n  " + "\n  ".join(errs))
    open(out("guide.html"), "w", encoding="utf-8").write(frag)
    open(out("guide_preview.html"), "w", encoding="utf-8").write(preview(shown))
    open(out("guide_preview_dark.html"), "w", encoding="utf-8").write(preview(shown, dark=True))
    open(out("guide_preview_mobile.html"), "w", encoding="utf-8").write(preview(shown, width=360))
