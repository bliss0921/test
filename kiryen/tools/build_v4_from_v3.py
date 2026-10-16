"""기록용: v3 카드를 v4로 바꾼 스크립트 (그대로 다시 돌릴 일은 없음. 앞으로는 v4 카드를 직접 고친다).

v3 카드는 git 커밋 0ae4d6c 에 있다:  git show 0ae4d6c:"kiryen/로판세계에서 살아남는법_v3.charx" > v3.charx
실행: python3 -I build_v4_from_v3.py rpack_map.bin v3.charx 트리거.lua ../design/out/frames/frame_cut.svg v4.charx
(트리거.lua = 퍼메 함수 머리말 + ../원작타임라인.lua, 카드의 Lua 칸 내용과 같음)
"""
import copy
import json
import re
import struct
import sys
import zipfile

MAP, SRC, LUA, FRAME_SVG, OUT = sys.argv[1:6]
mp = open(MAP, 'rb').read()
ENC, DEC = mp[:256], mp[256:512]


def read_risum(buf):
    assert buf[0] == 111 and buf[1] == 0
    n = struct.unpack('<I', buf[2:6])[0]
    assert buf[6 + n:] == b'\x00'
    return json.loads(bytes(DEC[b] for b in buf[6:6 + n]).decode('utf-8'))


def write_risum(obj):
    raw = json.dumps(obj, ensure_ascii=False, indent=2).encode('utf-8')
    body = bytes(ENC[b] for b in raw)
    return bytes([111, 0]) + struct.pack('<I', len(body)) + body + b'\x00'


def sub1(s, old, new):
    assert s.count(old) == 1, (old[:80], s.count(old))
    return s.replace(old, new)


src = zipfile.ZipFile(SRC)
files = {i.filename: src.read(i) for i in src.infolist()}
card = json.loads(files['card.json'])
mod = read_risum(files['module.risum'])
data = card['data']
risu = data['extensions']['risuai']
m = mod['module']

# ---------------------------------------------------------------- 1. 커스텀 토글 (사용자가 준 글 그대로)
TOGGLES = """=로판폭군=divider
=기본 설정=group
kc_language=언어=select=한국어,English
=퍼메 디데이 루아 언어 설정=caption
kc_scenario=빙의=select=카르엔야에 빙의,다른 인물에 빙의,빙의 없음
kc_fate=운명의 개입=select=켜기,끄기
==groupEnd
=인물 성별=group
kc_g_karenya=카르엔야=select=남,여
kc_g_hedwig=헤드비히=select=남,여
kc_g_piache=피아체=select=남,여
kc_g_ruslan=루스란=select=남,여
kc_g_myusa=뮤사=select=남,여
kc_g_daphneya=다프네야=select=남,여
kc_g_runian=루니안=select=남,여
==groupEnd
=인물 프로필=group
=리스트만은 npc리스트로 남음. 상세여도 키워드 활성화 방식임=caption
kc_p_karenya=카르엔야=select=상세,리스트만
kc_p_hedwig=헤드비히=select=상세,리스트만
kc_p_piache=피아체=select=상세,리스트만
kc_p_ruslan=루스란=select=상세,리스트만
kc_p_myusa=뮤사=select=상세,리스트만
kc_p_daphneya=다프네야=select=상세,리스트만
kc_p_runian=루니안=select=상세,리스트만
==groupEnd"""
risu['toggles'] = TOGGLES
risu['defaultVariables'] = 'perma=fm_karenya'

# 자주 쓰는 조건
SCEN_OTHER = ('{{any::{{equal::{{getglobalvar::toggle_kc_scenario}}::1}}'
              '::{{equal::{{getglobalvar::toggle_kc_scenario}}::2}}}}')          # 빙의 토글이 '다른 인물' 또는 '빙의 없음'
FREE_START = ('{{any::{{equal::{{getvar::perma}}::fm_free}}'
              '::{{equal::{{getglobalvar::toggle_kc_scenario}}::1}}'
              '::{{equal::{{getglobalvar::toggle_kc_scenario}}::2}}}}')         # 자유 시작이 보이는 경우
KARENYA_OPEN = '{{#when::kc_scenario::tisnot::1}}{{#when::kc_scenario::tisnot::2}}'  # 빙의 토글이 '카르엔야' (또는 안 고름)
KARENYA_CLOSE = '{{/when}}{{/when}}'
MALE_DEFAULT = ['hedwig', 'piache', 'ruslan', 'myusa', 'runian']             # 원작 남 (안 고르면 남)
FEMALE_DEFAULT = ['karenya', 'daphneya']                                      # 원작 여 (안 고르면 여)


def is_male(x):
    return f'kc_g_{x}::tis::0' if x in FEMALE_DEFAULT else f'kc_g_{x}::tisnot::1'


def is_female(x):
    return f'kc_g_{x}::tisnot::0' if x in FEMALE_DEFAULT else f'kc_g_{x}::tis::1'


def gender_text(x, male, female):
    return '{{#when::' + is_female(x) + '}}' + female + '{{:else}}' + male + '{{/when}}'


# ---------------------------------------------------------------- 2. 첫 메시지
fm = data['first_mes']
ko_story = fm.split('{{#when::{{getvar::perma}}::is::fm_karenya}}', 1)[1].split('\n[IY: 429. 6.13', 1)[0].strip('\n')
assert ko_story.startswith('꿈을 꾸고 있었다.') and ko_story.endswith('천천히 열렸다.'), ko_story[-40:]
KO_STATUS = '[IY: 429. 6.13 (D-100) | 17:00 | 황제의 집무실 | 미공개 || 셀레니아 | 폐하의 안색이 심상치 않다. 황의를 불러드려야 하나.]'
EN_STATUS = "[IY: 429. 6.13 (D-100) | 17:00 | The Emperor's Study | Undisclosed || Selenia | The Emperor looks pale. Should I send for the court physician?]"
data['first_mes'] = f"""◆▶◆

{{{{#when::{FREE_START}}}}}
[IY: ? | ? | ? | ?]
{{{{:else}}}}
{{{{#when::kc_language::tis::1}}}}
English Karenya first message content

{EN_STATUS}
{{{{:else}}}}
{ko_story}

{KO_STATUS}
{{{{/when}}}}
{{{{/when}}}}
"""

# ---------------------------------------------------------------- 3. 정규식
names = [r['comment'] for r in m['regex']]
assert names == ['Side Pannel', 'Status', 'Start', 'Start 리퀘제거', 'Side Pannel 리퀘제거', 'Status 리퀘제거'], names
start, start_rm, status_rm = m['regex'][2], m['regex'][3], m['regex'][5]
start['out'] = (
    '<div class="kc-box">\n'
    '<div class="kc-center-label kc-center">{{#when::kc_language::tis::1}}FIRST MESSAGE{{:else}}퍼메{{/when}}</div>\n'
    '<div class="kc-start-list">'
    + KARENYA_OPEN
    + '<button class="kc-btn {{#when::not::' + FREE_START + '}}kc-on-purple{{/when}}" risu-trigger="setPermaKarenya" type="button">'
      '{{#when::kc_language::tis::1}}{{user}} possesses Karenya{{:else}}{{user}}가 카르엔야에 빙의{{/when}}</button>'
    + KARENYA_CLOSE
    + '<button class="kc-btn {{#when::' + FREE_START + '}}kc-on-purple{{/when}}" risu-trigger="setPermaFree" type="button">'
      '{{#when::kc_language::tis::1}}Free Start{{:else}}자유 시작{{/when}}</button>'
    '</div>\n'
    '</div>')
# 요청에서 오래된 STATUS는 날짜 | 시간 | 장소만 남긴다 (능력·속마음 삭제). 최근 메시지는 그대로 둔다
status_rm['in'] = r'(?<=\[IY:[^|\]\r\n]*\|[^|\]\r\n]*\|[^|\]\r\n]*?)\s*\|[^\]\r\n]*(?=\])'
m['regex'] = [start, start_rm, status_rm]

# ---------------------------------------------------------------- 4. 트리거 (Lua)
assert len(m['trigger']) == 1 and m['trigger'][0]['effect'][0]['type'] == 'triggerlua'
m['trigger'][0]['effect'][0]['code'] = open(LUA, encoding='utf-8').read()

# ---------------------------------------------------------------- 5. 로어북
STATUS_LORE = """### STATUS RULE

- End every response with exactly one STATUS line as the final output: a single bracketed line, no code block, nothing after it.

#### FORMAT

[IY: date (D-XX) | time | location | ability || Name | inner thought || Name | inner thought]

#### FIELD RULES

- date: Advance from the previous STATUS date. If there is no previous STATUS, use the date the scene states; if none is stated, IY 429. 6.13 (D-100). If a scene spans hours or skips time, advance accordingly; when unsure, one day per scene. Write M.DD with two-digit days (5.05, 9.21, 12.12). Up to 9.21, add (D-XX), the days left until 9.21. After 9.21, write the date only.
- time: HH:MM, 24-hour.
- location: Where {{user}} is now, in a few words.
- ability: {{user}}'s special ability, as {{user}} has named it. Until it is named, write {{#when::kc_language::tis::1}}Undisclosed{{:else}}미공개{{/when}}. If {{user}} has none, write -.
- `|| Name | inner thought`: One block for each character physically present and part of the moment, other than {{user}}. Name only, with no title or emoji. The thought is that character's raw first-person inner voice in one or two short sentences: in character, not narration. A character thinks only what that character knows, the same limit as dialogue. If no one else is present, end the line after ability.
- Language: {{#when::kc_language::tis::1}}Write every value in English, with English names (Hedwig, Selenia).{{:else}}Write every value in Korean, with Korean names (헤드비히, 셀레니아).{{/when}}

#### HARD CONSTRAINTS

- Exactly one STATUS line per response, always last.
- Order: date | time | location | ability, then the character blocks.
- Put ` | ` between fields and ` || ` before each character. Never add labels, extra fields, or line breaks, and never use `|` or `]` inside a value.

#### EXAMPLES

{{#when::kc_language::tis::1}}
[IY: 429. 7.15 (D-68) | 15:00 | Knights' Training Ground | Time Stop || Hedwig | So Your Majesty means only to watch. || Ruslan | Found another amusing spectacle, have we?]
[IY: 429. 6.15 (D-98) | 21:40 | Emperor's Bedchamber | Undisclosed || Myusa | What did I do wrong this time.]
[IY: 429. 9.24 | 08:10 | Imperial Garden | Time Stop]
{{:else}}
[IY: 429. 7.15 (D-68) | 15:00 | 기사단 연무장 | 시간 정지 || 헤드비히 | …보고만 계실 셈인가. || 루스란 | 또 재미있는 구경거리를 찾았군.]
[IY: 429. 6.15 (D-98) | 21:40 | 황제의 침소 | 미공개 || 뮤사 | 이번엔 또 뭘 잘못한 거지.]
[IY: 429. 9.24 | 08:10 | 황궁 정원 | 시간 정지]
{{/when}}
"""

NATIVE_LORE = """{{#when::kc_scenario::tis::2}}

### Premise

{{user}} is a native of this world, born and raised here, with no memory of any other life and no knowledge of what is to come. {{user}}'s name, background, and position are whatever {{user}} establishes.

One hundred days from the story's start, a coordinated rebellion against Emperor Karenya is set to break out. {{user}} does not know this. It approaches through the world's own causes, and {{user}} meets it only as it surfaces.

### Naming Rule

In narration and dialogue, {{user}} is referred to by the name and position {{user}} holds in this world. Never use meta expressions such as "user" or "player" in-story.

{{/when}}
"""

KARENYA_LIST = (SCEN_OTHER, '- Karenya Valkzephas Gabitz di Sieghart (카르엔야 발크제파스 가비츠 디 지크하트) — 27, '
                + gender_text('karenya', 'male. 169 cm,', 'female. 169 cm,')
                + ' long black hair, black eyes. Emperor of the Sieghart Empire. Hedwig\'s spouse; Piache and Ruslan are consorts, Myusa a bedslave. Imperial Palace.')


def profile(x, gender_cond, body):
    """상세 프로필: 프로필 토글이 '상세'(또는 안 고름)이고 성별이 맞을 때만"""
    return f'{{{{#when::kc_p_{x}::tisnot::1}}}}\n{{{{#when::{gender_cond}}}}}\n\n{body}\n\n{{{{/when}}}}\n{{{{/when}}}}\n'


def transform(comment, c):
    if comment == 'Status':
        return STATUS_LORE
    if comment in ('유저빙의=카르엔야', '빙의상태 카르엔야 설정'):
        c = sub1(c, '{{#when::{{getvar::scenario}}::is::karenya}}', KARENYA_OPEN)
        i = c.rindex('{{/when}}')
        return c[:i] + KARENYA_CLOSE + c[i + len('{{/when}}'):]
    if comment == '유저빙의=다른사람':
        return sub1(c, '{{#when::{{getvar::scenario}}::is::other}}', '{{#when::kc_scenario::tis::1}}')
    if comment == '원작소설':
        head, hist = c.split('### World History', 1)
        assert head.startswith('### The Novel and This World')
        hist = sub1(hist, " ({{user}}'s count: D-100 until the novel's ruin.)",
                    "{{#when::kc_scenario::tisnot::2}} ({{user}}'s count: D-100 until the novel's ruin.){{/when}}")
        return '{{#when::kc_scenario::tisnot::2}}\n' + head.strip('\n') + '\n{{/when}}\n\n### World History' + hist
    if comment in ('♂️오리지널카르엔야', '♀️오리지널카르엔야'):
        female = comment.startswith('♀')
        old = '{{#when::{{getvar::cv_KarenyaF}}::is::' + ('1' if female else '0') + '}}'
        body = c.split(old, 1)[1].rsplit('{{/when}}', 2)[0].strip('\n')
        return f'{{{{#when::{SCEN_OTHER}}}}}\n' + profile('karenya', is_female('karenya') if female else is_male('karenya'), body) + '{{/when}}\n'
    if comment == 'NPC List':
        for x, age, h in (('hedwig', 29, 193), ('piache', 25, 181), ('ruslan', 26, 185), ('myusa', 22, 178), ('runian', 19, 182)):
            c = sub1(c, f' — {age}, male. {h} cm,', f' — {age}, ' + gender_text(x, f'male. {h} cm,', f'female. {h} cm,'))
        c = sub1(c, '{{#when::{{getvar::cv_DaphneyaF}}::is::0}}male. 184 cm,{{/when}} {{#when::{{getvar::cv_DaphneyaF}}::is::1}}female. 168 cm,{{/when}}',
                 gender_text('daphneya', 'male. 184 cm,', 'female. 168 cm,'))
        c = sub1(c, 'Former Crown Prince of the Mage Kingdom', 'Former Crown Heir of the Mage Kingdom')
        c = sub1(c, 'Former prince of the Mage Kingdom.', "Of the Mage Kingdom's royal family.")
        cond, line = KARENYA_LIST
        return sub1(c, '### NPC List\n\n', f'### NPC List\n\n{{{{#when::{cond}}}}}{line}{{{{/when}}}}\n')
    g = re.fullmatch(r'([♂♀])\ufe0f?(\S+)\((\w+)\)', comment)
    if g and g[3].lower() in MALE_DEFAULT + FEMALE_DEFAULT:
        x, female = g[3].lower(), g[1] == '♀'
        cond = is_female(x) if female else is_male(x)
        if c.strip() == '':
            return profile(x, cond, '')
        old = '{{#when::{{getvar::cv_' + g[3] + 'F}}::is::1}}'
        assert female and c.startswith(old), comment
        body = c[len(old):].rsplit('{{/when}}', 1)[0].strip('\n')
        return profile(x, cond, body)
    if comment == '운명의개입(나중에채워)':
        return sub1(c, '{{#when::keep::{{getvar::difficulty}}::is::on}}', '{{#when::keep::kc_fate::tisnot::1}}')
    return c


changed = []
for lore in m['lorebook']:
    new = transform(lore['comment'], lore['content'])
    if new != lore['content']:
        changed.append(lore['comment'])
    lore['content'] = new
entries = data['character_book']['entries']
assert [e['comment'] for e in entries] == [l['comment'] for l in m['lorebook']]
for e, lore in zip(entries, m['lorebook']):
    e['content'] = lore['content']

# 빙의 없음 전제 (빙의 폴더, '유저빙의=다른사람' 바로 뒤)
at = [l['comment'] for l in m['lorebook']].index('유저빙의=다른사람') + 1
native = copy.deepcopy(m['lorebook'][at - 1])
native.update(comment='유저=빙의없음', content=NATIVE_LORE, insertorder=3)
m['lorebook'].insert(at, native)
native_e = copy.deepcopy(entries[at - 1])
native_e.update(comment='유저=빙의없음', name='유저=빙의없음', content=NATIVE_LORE, insertion_order=3)
entries.insert(at, native_e)
changed.append('유저=빙의없음 (new)')

# ---------------------------------------------------------------- 6. 배경 HTML (CSS)
bg = risu['backgroundHTML']
cut = bg.index('/* ========================================\n   Imperial Status Card')
svg = open(FRAME_SVG, encoding='utf-8').read().strip()
frame_uri = 'data:image/svg+xml,' + svg.replace('"', "'").replace('#', '%23').replace('<', '%3C').replace('>', '%3E')
assert ';' not in frame_uri and '}' not in frame_uri
STATUS_CSS = """/* ========================================
   상태창 — 모서리 컷 테두리 · 아이보리/와인
   트리거(Lua)가 STATUS 줄을 아래 클래스로 그린다
   ======================================== */
.ks{--ks-ink:#3b2c27;--ks-sub:#6b584d;--ks-wine:#6e1f30;--ks-gold:#94702f;--ks-rule:#e2d5bf;--ks-edge:#d6c3a0;
  display:block;position:relative;box-sizing:border-box;max-width:640px;margin:20px 0 8px !important;padding:0 6px !important;
  border:30px solid transparent;border-image:url("FRAME") 40 fill / 30px stretch;filter:drop-shadow(0 6px 14px rgba(0,0,0,.35));
  color:var(--ks-ink) !important;font-family:'Noto Sans KR',sans-serif !important;font-size:14px !important;line-height:1.6 !important;
  text-align:left !important;white-space:normal !important;word-break:keep-all;overflow-wrap:anywhere}
.ks *{box-sizing:border-box;font-family:inherit !important;color:inherit;text-shadow:none !important}
.ks-date{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.ks-iy{font-family:'Gowun Batang',serif !important;font-weight:700;font-size:20px;line-height:1.3;color:var(--ks-wine) !important;font-variant-numeric:lining-nums}
.ks-dday{font-size:14px;font-weight:700;color:var(--ks-wine) !important}
.ks-meta{margin-top:3px;font-size:14px;line-height:1.6;color:var(--ks-sub) !important}
.ks-meta i{font-style:normal;margin:0 6px;color:var(--ks-edge) !important}
.ks-meta b{font-weight:500;color:var(--ks-wine) !important}
.ks-ab{white-space:nowrap}
.ks-rule{height:1px;background:var(--ks-rule);margin:13px 0}
.ks-runin{margin:0 !important;padding:0 !important;font-family:'Gowun Batang',serif !important;font-size:15.5px !important;line-height:1.75 !important;color:var(--ks-ink) !important}
.ks-runin + .ks-runin{margin-top:8px !important}
.ks-runin b{font-family:'Noto Sans KR',sans-serif !important;font-size:14px;font-weight:700;color:var(--ks-wine) !important;margin-right:9px}
.ks-up-label{font-size:13px;font-weight:700;color:var(--ks-sub) !important;margin-bottom:4px}
.ks-up{list-style:none !important;margin:0 !important;padding:0 !important}
.ks-up li{display:flex;gap:14px;margin:0 !important;padding:0 !important;font-size:14px;line-height:1.75}
.ks-up li::marker{content:none}
.ks-up b{flex:0 0 58px;font-weight:700;color:var(--ks-gold) !important;font-variant-numeric:tabular-nums}
.ks-up span{flex:1;min-width:0}
@media (max-width:480px){
  .ks{border-width:24px;border-image-width:24px;padding:0 2px !important}
  .ks-iy{font-size:19px}
  .ks-up b{flex-basis:56px}
}
""".replace('FRAME', frame_uri)
FONTS = "@import url('https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Noto+Sans+KR:wght@400;500;700&display=swap');\n"
assert bg.startswith('<style>\n')
risu['backgroundHTML'] = '<style>\n' + FONTS + bg[len('<style>\n'):cut] + STATUS_CSS + '</style>\n'

# ---------------------------------------------------------------- write
files['card.json'] = json.dumps(card, ensure_ascii=False, indent=4).encode('utf-8')
files['module.risum'] = write_risum(mod)
assert read_risum(files['module.risum']) == mod
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as out:
    for info in src.infolist():
        zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        zi.compress_type = info.compress_type
        out.writestr(zi, files[info.filename])
json.dump({'card': card, 'mod': mod}, open(OUT + '.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('lorebooks changed:', changed)
print('regex:', [r['comment'] for r in m['regex']])
print('wrote', OUT)
