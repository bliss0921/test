# 레드문 퍼메 선택기 (Risu 정규식 + 배경 CSS)
# python3 build_fm.py <원본 배경CSS.txt>
#   -> 20_퍼메_선택기.json, 배경_CSS.txt, preview_fm.html
# Lua(onButtonClick)와 퍼메 본문은 그대로 사용한다. 버튼 risu-btn 값과 변수명은 바꾸지 않았다.
import json
import os
import sys

TITLE = {
    "ko": "반하나와 레드문에 첫방문한 {{user}}",
    "en": "{{user}}'s first visit to Red Moon with Ban Hana",
    "free": "자유설정",
}

MENU = (
    '<div class="rm-fm" role="region" aria-label="첫 메시지 선택"><div class="rm-fm-options">'
    f'<button type="button" class="rm-fm-choice" risu-btn="rm-fm-ko">{TITLE["ko"]}</button>'
    f'<button type="button" class="rm-fm-choice rm-fm-choice-en" risu-btn="rm-fm-en">{TITLE["en"]}</button>'
    f'<button type="button" class="rm-fm-choice" risu-btn="rm-fm-free">{TITLE["free"]}</button>'
    '</div></div>'
)

SELECTED_TITLE = (
    '{{#when::{{getvar::cv_rm_fm_choice}}::is::ko}}' + TITLE["ko"] + '{{:else}}'
    '{{#when::{{getvar::cv_rm_fm_choice}}::is::en}}' + TITLE["en"] + '{{:else}}'
    + TITLE["free"] + '{{/when}}{{/when}}'
)

COMPACT = (
    '<div class="rm-fm rm-fm-compact" role="region" aria-label="선택한 첫 메시지"><div class="rm-fm-selected">'
    f'<span class="rm-fm-title">{SELECTED_TITLE}</span>'
    '<button type="button" class="rm-fm-reopen" risu-btn="rm-fm-reopen">다시 선택</button>'
    '</div></div>'
)

OUT = ('{{#when::{{lastmessageid}}::is::-1}}{{#when::{{getvar::cv_rm_fm_menu}}::is::0}}'
       + COMPACT + '{{:else}}' + MENU + '{{/when}}{{/when}}')

REGEX = {
    "type": "regex",
    "data": [
        {"comment": "20_v2_퍼메_선택기UI", "in": "⟦RM_FM⟧", "out": OUT,
         "type": "editdisplay", "ableFlag": True, "flag": "g"},
        {"comment": "20_v2_퍼메_리퀘스트마커제거", "in": "⟦RM_FM⟧", "out": "",
         "type": "editprocess", "ableFlag": True, "flag": "g"},
    ],
}

# 명함(검정·금색)처럼: 검은 판, 가는 금색 테두리 두 줄, 가운데 정렬 명조 제목만.
# 금색은 상태창 타이머 색(#c8a56a)과 같은 계열.
FM_CSS = """/* REDMOON_FIRST_MESSAGE_V2 — 선택기 전용 */
.rm-fm, .rm-fm * { box-sizing: border-box; }
.rm-fm {
  width: 100%;
  max-width: 520px;
  min-width: 0;
  margin: 14px auto 26px;
  padding: 12px 18px;
  border: 1px solid rgba(200,165,106,.55);
  border-radius: 2px;
  background: #0d0c0e !important;
  box-shadow: inset 0 0 0 5px #0d0c0e, inset 0 0 0 6px rgba(200,165,106,.24);
  color: #ece4d7 !important;
  font-family: "Noto Serif KR", "Noto Serif CJK KR", "Nanum Myeongjo", "AppleMyungjo", "Batang", serif;
  text-align: center;
  line-height: 1.6;
}
.rm-fm * { text-shadow: none !important; }
.rm-fm .rm-fm-choice {
  all: unset;
  box-sizing: border-box;
  display: block !important;
  width: 100% !important;
  margin: 0 !important;
  padding: 22px 8px !important;
  border: 0 !important;
  border-top: 1px solid rgba(200,165,106,.18) !important;
  border-radius: 0 !important;
  background: transparent !important;
  color: #ece4d7 !important;
  -webkit-text-fill-color: #ece4d7 !important;
  font-family: inherit !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  line-height: 1.55 !important;
  letter-spacing: .3px !important;
  text-align: center !important;
  white-space: normal !important;
  word-break: keep-all;
  overflow-wrap: anywhere;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: color .2s ease, background-color .2s ease;
}
.rm-fm .rm-fm-choice:first-child { border-top: 0 !important; }
.rm-fm .rm-fm-choice:hover {
  background: rgba(200,165,106,.06) !important;
  color: #dcbc7c !important;
  -webkit-text-fill-color: #dcbc7c !important;
}
.rm-fm .rm-fm-choice:focus-visible,
.rm-fm .rm-fm-reopen:focus-visible {
  outline: 1px solid #c8a56a !important;
  outline-offset: -4px;
}
.rm-fm-compact { padding: 14px 18px; }
.rm-fm .rm-fm-selected {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  min-width: 0;
}
.rm-fm .rm-fm-title {
  flex: 1 1 auto;
  min-width: 0;
  color: #ece4d7 !important;
  -webkit-text-fill-color: #ece4d7 !important;
  font-size: 14px !important;
  font-weight: 600;
  line-height: 1.5 !important;
  text-align: left;
  word-break: keep-all;
  overflow-wrap: anywhere;
}
.rm-fm .rm-fm-reopen {
  all: unset;
  box-sizing: border-box;
  flex: 0 0 auto;
  padding: 6px 12px !important;
  border: 1px solid rgba(200,165,106,.5) !important;
  border-radius: 2px !important;
  background: transparent !important;
  color: #dcbc7c !important;
  -webkit-text-fill-color: #dcbc7c !important;
  font-family: inherit !important;
  font-size: 12px !important;
  line-height: 1.4 !important;
  letter-spacing: 1px !important;
  white-space: nowrap;
  cursor: pointer;
  transition: background-color .2s ease;
}
.rm-fm .rm-fm-reopen:hover { background: rgba(200,165,106,.1) !important; }
@media (max-width: 480px) {
  .rm-fm { padding: 10px 12px; }
  .rm-fm .rm-fm-choice { padding: 19px 4px !important; font-size: 15px !important; }
  .rm-fm-compact { padding: 12px 14px; }
}
@media (prefers-reduced-motion: reduce) {
  .rm-fm .rm-fm-choice, .rm-fm .rm-fm-reopen { transition: none; }
}
"""


def preview(state_html):
    return state_html.replace("{{user}}", "Kang Chan")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    src = open(sys.argv[1], encoding="utf-8").read()
    head = src[:src.index("/* REDMOON_FIRST_MESSAGE_V1")]
    css = head + FM_CSS + "\n</style>\n"
    open(os.path.join(here, "배경_CSS.txt"), "w", encoding="utf-8").write(css)
    with open(os.path.join(here, "20_퍼메_선택기.json"), "w", encoding="utf-8") as f:
        json.dump(REGEX, f, ensure_ascii=False, indent=2)

    compact = {k: COMPACT.replace(SELECTED_TITLE, TITLE[k]) for k in TITLE}
    body = (f'<div class="lbl">선택 전</div>{preview(MENU)}'
            f'<div class="lbl">선택 후 (한국어)</div>{preview(compact["ko"])}'
            f'<div class="lbl">선택 후 (영문)</div>{preview(compact["en"])}')
    page = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            + css.replace("</style>", ".lbl{color:#777;font:12px sans-serif;margin:24px auto 0;max-width:520px}</style>")
            + '</head><body style="margin:0;padding:20px 16px 30px;background:#1c1d21">' + body + '</body></html>')
    open(os.path.join(here, "preview_fm.html"), "w", encoding="utf-8").write(page)
    print("ok", len(OUT))
