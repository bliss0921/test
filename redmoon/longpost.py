# 아카라이브용 세로 긴 이미지: 건물 → 초이스 → 인물소개(W4) → 누구를 → 봇 소개(별지 서식)
# python3 gen.py && python3 render.py out/draft_W4.html out/draft_W4.png   (인물소개 먼저)
# python3 longpost.py
# python3 render.py out/form.html out/form.png out/redmoon_full.html out/redmoon_full.png
import os

C = dict(seohu="#d0607f", rebel="#8a6fcf", juyoon="#5a88c2")

# 섹션: (왼쪽 큰 칸, [(항목, 내용html), ...])
SECTIONS = [
    ("봇 정보", [
        ("구성", "메인 NPC 3명, 서브 NPC n명 있는 호빠봇임."),
        ("성향", "거의 쿰봇임. 쿰질만 오지게 해서 캐해 테스트는 많이 안 함.<br>야스는 맛있었음."),
        ("기능", "별거 없음. 상태창과 일기, NPC 쪼개놓은 토글, 사이드바 은어사전 있음."),
    ]),
    ("권장 설정", [
        ("출력", "디스크립션에 한국어 섞여 있어서 <b>한출 권장</b>하는데 영출도 꽤 괜찮음. "
                 "오푸스는 나도 한출하다 너무 비싸서 영출했음. 장기 넘어가면 대사에 한국어 섞이는 찐빠는 좀 있음. "
                 "잼은 걍 한출하셈."),
        ("번역", "누더기프롬 재작성-웹소설작가 하니 대사 느낌 괜찮았음."),
        ("로어북", "은어나 지침은 <b>항상 활성화</b> 권장, NPC 리스트도 <b>상시 활성화</b> 권장."),
        ("테스트", "오육솔(천해) · 오오오푸스(attg, 천해) · 잼삼칠(누렁이)"),
    ]),
    ("플레이<br>가이드", [
        ("재밌었던<br>플레이", '<ul>'
         '<li>서후 전여친 <span class="sub">(얘 성격 잘 나옴)</span></li>'
         '<li>서후 동생 짝사랑하는데 꿩 대신 닭으로 서후 지명하기 <span class="sub">(둘이 닮았음)</span></li>'
         '<li>레블 누나 친구 <span class="sub">(누나 응급의학과 던트임)</span></li>'
         '<li>주윤이랑 원나잇한 사이 <span class="sub">(얘 가끔 게이바 감)</span></li></ul>'),
        ("난 그냥<br>쿰질<br>존나 할 거다", '<dl>'
         f'<dt style="--c:{C["seohu"]}">서후</dt><dd>돈 많은 페소로 돈 뿌리면 한 번에 2차 감.</dd>'
         f'<dt style="--c:{C["rebel"]}">레블</dt><dd>섹파 스타트하거나, 예쁘고 몸매 좋은 애로 꼬시면 재밌겠다고 2차 감.</dd>'
         f'<dt style="--c:{C["juyoon"]}">주윤</dt><dd>호빠 말고 게이바 스타트하는 게 빠름.'
         '<span class="note">※ 게이플만 해서 헤테로로 어떻게 나올진 잘 모르겠음.</span></dd>'
         '<dt style="--c:#3a3340">공용</dt><dd>모두의 공용 암캐가 되고 싶다면 호빠 선수들 스트레스 해소용 성처리 당번이 되어봅시다. '
         '돈 받고 일한다 하면 오푸스 검열도 안 하고 페티시 개잘 말아줌.</dd></dl>'),
    ]),
    ("참고 사항", [
        ("은어", "은어가 실제로 맞는지, 실제 호빠가 이렇게 돌아가는진 나도 모름. 짚한테 조사시켜서 작성함."),
        ("메인캐<br>간략버전", "누구 한 명 잡고 공략하는데, 캐랑 다른 애들 티키타카하는 거 보고 싶을 때용임."
                          '<span class="ex">ex. 서후가 페소방 들어갔다 나오면 레블이 “거기 좋음? 쓰리섬 고?” 대사 치고 '
                          '서후가 “꺼져 씨발.” 하는 이런 반응 보는 거임.</span>'
                          "성격이랑 간략한 스펙 정도만 들어간 거라 이 상태로 섹각이나 순애각 잡는 건 비추."),
        ("본명", "애들 본명 로어북에 적혀 있음. 지침상 일할 때는 본명 비밀인데 잼민이 오지게 못 지킴. "
                 "그거 잡겠다고 토큰 낭비하기 싫어서 난 걍 흐린 눈 함. <b>서후 본명 개싫어함.</b>"),
    ]),
]

FORM_CSS = """
.paper-wrap{background:#ebe9ee;padding:56px 40px 40px}
.sheet{background:#fff;padding:40px 46px 34px;box-shadow:0 3px 18px #0000001f;color:#222;
 font-family:'Noto Sans CJK KR','Noto Sans KR',sans-serif}
.law{font-size:17px;color:#333;letter-spacing:-.2px}
.law b{font-weight:700}
.law small{color:#777;font-size:15px;margin-left:6px}
.sheet h1{text-align:center;font-size:44px;font-weight:900;letter-spacing:.32em;margin:30px 0 6px;padding-left:.32em}
.sheet .h1sub{text-align:center;font-size:18px;color:#666;letter-spacing:.12em}
.notice{font-size:16px;color:#444;margin:26px 0 8px}
table.form{width:100%;border-collapse:collapse;border-top:3px solid #222;border-bottom:3px solid #222;font-size:21px;line-height:1.62}
.form td,.form th{border:1px solid #9a9a9a;vertical-align:middle;word-break:keep-all}
.form tr>*:first-child{border-left:0} .form tr>*:last-child{border-right:0}
.form th{background:#f2f1f3;font-weight:700;color:#333;text-align:center;padding:14px 8px}
.form th.sec{font-size:21px;background:#e8e6ea;line-height:1.4}
.form th.item{font-size:19px;line-height:1.4}
.form td{padding:14px 20px;color:#2c2830}
.form td b{font-weight:700;color:#000}
.form tr.meta th{font-size:16px;padding:9px 8px;background:#f2f1f3}
.form tr.meta td{font-size:17px;padding:9px 16px;color:#555}
.form ul{list-style:none} .form li{padding-left:18px;position:relative}
.form li::before{content:'·';position:absolute;left:2px;font-weight:900}
.form .sub,.form .note{color:#8a8290;font-size:18px}
.form .note{display:block;margin-top:2px}
.form .ex{display:block;margin:8px 0;padding:10px 14px;background:#f6f5f7;border-left:3px solid #c9c4ce;font-size:19px;color:#555}
.form dl{display:grid;grid-template-columns:auto 1fr;column-gap:14px;row-gap:12px;align-items:baseline}
.form dt{font-weight:700;color:var(--c);white-space:nowrap}
.form dt::before{content:'';display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--c);margin-right:7px;vertical-align:2px}
.sign{margin-top:34px;font-size:20px;color:#222;position:relative}
.sign .t{text-align:center}
.sign .date{text-align:right;margin-top:22px;letter-spacing:.05em}
.sign .who{text-align:right;margin-top:34px;position:relative}
.sign .who .blank{display:inline-block;width:180px;border-bottom:1px solid #444;margin:0 10px;vertical-align:-4px}
.sign .who small{color:#777;font-size:16px}
.seal{position:absolute;right:-18px;top:50%;margin-top:-38px;background:#ffffffb0;width:76px;height:76px;border-radius:50%;border:3.5px solid #c8323c;
 color:#c8323c;display:flex;flex-direction:column;align-items:center;justify-content:center;transform:rotate(-12deg);opacity:.86;
 font-family:'Gowun Batang',serif;font-weight:700;font-size:18px;line-height:1;letter-spacing:-1px;box-shadow:inset 0 0 0 3px #fff,inset 0 0 0 4.5px #c8323c}
.to{margin-top:36px;font-size:24px;font-weight:700;letter-spacing:.05em}
.paper-foot{text-align:right;font-size:14px;color:#888;margin-top:10px;font-family:'Noto Sans CJK KR',sans-serif}
"""


def form_html():
    rows = ['<tr class="meta"><th>접수번호</th><td>RM-0001</td><th>처리기간</th><td>초이스 즉시</td></tr>']
    for sec, items in SECTIONS:
        for k, (item, body) in enumerate(items):
            head = f'<th class="sec" rowspan="{len(items)}">{sec}</th>' if k == 0 else ""
            rows.append(f'<tr>{head}<th class="item">{item}</th><td colspan="2">{body}</td></tr>')
    # meta 줄은 4칸, 나머지는 sec+item+td(colspan2)=4칸
    return f'''<div class="paper-wrap"><div class="sheet">
<div class="law">■ 레드문 운영 규정 <b>[별지 제1호서식]</b><small>&lt;개정 2026. 10.&gt;</small></div>
<h1>봇 이용 안내서</h1>
<div class="h1sub">RED MOON · 신논현역, 레드문</div>
<div class="notice">※ 아래 사항을 확인하신 후 초이스하시기 바랍니다.</div>
<table class="form"><colgroup><col style="width:96px"><col style="width:132px"><col style="width:150px"><col></colgroup>
{"".join(rows)}</table>
<div class="sign"><div class="t">위와 같이 안내합니다.</div>
<div class="date">2026년 &nbsp;&nbsp;&nbsp;&nbsp;월 &nbsp;&nbsp;&nbsp;&nbsp;일</div>
<div class="who">제작자<span class="blank"></span><small>(서명 또는 인)</small><div class="seal">레드문</div></div></div>
<div class="to">레드문 손님 귀하</div>
</div><div class="paper-foot">210mm×297mm[백상지 80g/㎡]</div></div>'''


def page(body, extra_css=""):
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
@font-face{{font-family:'Gowun Batang';src:url('../fonts/GowunBatang-Bold.ttf');font-weight:700}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{width:1000px}} body{{width:1000px;background:#fff}}
.panel{{display:block;width:1000px;height:auto}}
{FORM_CSS}{extra_css}</style></head><body>{body}</body></html>'''


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = lambda n: os.path.join(here, "out", n)
    open(out("form.html"), "w", encoding="utf-8").write(page(form_html()))
    panels = "".join(f'<img class="panel" src="{p}">' for p in [
        "../img/scene_street.webp", "../img/panel_choice.webp", "draft_W4.png", "../img/panel_who.webp"])
    open(out("redmoon_full.html"), "w", encoding="utf-8").write(page(panels + form_html()))
    print("ok")
