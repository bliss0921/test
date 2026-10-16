import itertools
import json
import re
import sys

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cbs_mini import render  # noqa: E402
from charx_io import load_any  # noqa: E402

# python3 -I verify_card.py ../로판세계에서\ 살아남는법_v4.charx   (토글 조합별 CBS 결과·남은 옛 참조 검사)
d = load_any(sys.argv[1])
card, mod = d['card'], d['mod']
data, m = card['data'], mod['module']
risu = data['extensions']['risuai']
defaults = dict(l.split('=', 1) for l in risu['defaultVariables'].splitlines() if '=' in l)
lore = {l['comment']: l['content'] for l in m['lorebook']}
fails = []


def check(cond, label):
    if not cond:
        fails.append(label)
        print('FAIL', label)


def R(s, toggles=None, vars=None):
    return render(s, vars or {}, toggles or {}, defaults)


VALS = {'kc_language': ['null', '0', '1'], 'kc_scenario': ['null', '0', '1', '2']}
n = 0

# ---- 첫 메시지
for lang, scen, perma in itertools.product(VALS['kc_language'], VALS['kc_scenario'], ['null', 'fm_karenya', 'fm_free']):
    tg = {'kc_language': lang, 'kc_scenario': scen}
    vars = {} if perma == 'null' else {'perma': perma}
    out = R(data['first_mes'], tg, vars)
    free = perma == 'fm_free' or scen in ('1', '2')
    check(out.startswith('◆▶◆\n\n'), 'start marker first')
    check('{{' not in out.replace('{{user}}', ''), f'leftover CBS {tg} {perma}')
    if free:
        check(out.strip().endswith('[IY: ? | ? | ? | ?]') and '꿈을' not in out and 'English' not in out, f'free opening {tg} {perma}')
    elif lang == '1':
        check('English Karenya first message content' in out and "Selenia | The Emperor looks pale" in out and '꿈을' not in out, f'EN opening {tg}')
    else:
        check(out.split('\n')[2] == '꿈을 꾸고 있었다.' and out.rstrip().endswith('황의를 불러드려야 하나.]') and 'English' not in out, f'KO opening {tg} {perma}')
    n += 1

# ---- 시작 화면 (퍼메 버튼)
start = next(r for r in m['regex'] if r['comment'] == 'Start')
for lang, scen, perma in itertools.product(VALS['kc_language'], VALS['kc_scenario'], ['null', 'fm_karenya', 'fm_free']):
    tg = {'kc_language': lang, 'kc_scenario': scen}
    out = R(start['out'], tg, {} if perma == 'null' else {'perma': perma})
    karenya_btn = 'setPermaKarenya' in out
    check(karenya_btn == (scen in ('null', '0')), f'karenya button visibility {tg}')
    check('setPermaFree' in out, 'free button always')
    check(all(l.strip() for l in out.split('\n')), f'no empty line in panel {tg}')
    free = perma == 'fm_free' or scen in ('1', '2')
    on = re.findall(r'class="kc-btn ([^"]*)" risu-trigger="(\w+)"', out)
    lit = [t for c, t in on if 'kc-on-purple' in c]
    check(lit == (['setPermaFree'] if free else ['setPermaKarenya']), f'highlight {tg} {perma} {lit}')
    en = lang == '1'
    check(('FIRST MESSAGE' in out and 'Free Start' in out) if en else ('퍼메' in out and '자유 시작' in out), f'panel language {tg}')
    if karenya_btn:
        check(('possesses Karenya' in out) if en else ('카르엔야에 빙의' in out), 'karenya label language')
    n += 1

# ---- 로어북: 성별 / 프로필
PEOPLE = {'karenya': 'f', 'hedwig': 'm', 'piache': 'm', 'ruslan': 'm', 'myusa': 'm', 'daphneya': 'f', 'runian': 'm'}
CAP = {'hedwig': 'Hedwig', 'piache': 'Piache', 'ruslan': 'Ruslan', 'myusa': 'Myusa', 'daphneya': 'Daphneya', 'runian': 'Runian'}
npc = lore['NPC List']
for x, orig in PEOPLE.items():
    for g, p, scen in itertools.product(['null', '0', '1'], ['null', '0', '1'], VALS['kc_scenario']):
        tg = {f'kc_g_{x}': g, f'kc_p_{x}': p, 'kc_scenario': scen}
        female = (g == '1') or (g == 'null' and orig == 'f')
        detail = p != '1'
        if x == 'karenya':
            names = ('♂️오리지널카르엔야', '♀️오리지널카르엔야')
            other = scen in ('1', '2')
        else:
            names = (f'♂️{[k for k in lore if k.endswith(f"({CAP[x]})") and k.startswith("♂")][0][2:]}',
                     f'♀️{[k for k in lore if k.endswith(f"({CAP[x]})") and k.startswith("♀")][0][2:]}')
            other = True
        male_out, fem_out = (R(lore[k], tg).strip() for k in names)
        # 빈 프로필 자리는 켜져도 빈 문자열이므로 원본 내용이 있는 쪽만 비교
        male_src, fem_src = ('\n'.join(l for l in lore[k].split('\n') if not l.startswith('{{')).strip() for k in names)
        check(male_out == (male_src if (other and detail and not female) else ''), f'{x} male profile {tg}')
        check(fem_out == (fem_src if (other and detail and female) else ''), f'{x} female profile {tg}')
        lst = R(npc, tg)
        if x == 'karenya':
            line = [l for l in lst.split('\n') if 'Karenya Valkzephas' in l]
            check(bool(line) == (scen in ('1', '2')), f'karenya list line {tg}')
            if line:
                check(('female.' in line[0]) == female and 'male.' in line[0], f'karenya list gender {tg}')
        else:
            line = [l for l in lst.split('\n') if l.startswith(f'- {CAP[x]}')][0]
            check(re.search(r' — \d+, (fe)?male\. \d+ cm,', line) and (', female.' in line) == female, f'{x} list gender {tg}: {line[:80]}')
            check('{{' not in line, 'npc list line clean')
        n += 2

for k in [k for k in lore if k[:1] in '♂♀']:
    check(lore[k].count('{{#when') == lore[k].count('{{/when}}'), f'balanced {k}')

# ---- 로어북: 빙의 / 원작 / 운명의 개입 / 상태창
for scen in VALS['kc_scenario']:
    tg = {'kc_scenario': scen}
    k0 = scen in ('null', '0')
    check(bool(R(lore['유저빙의=카르엔야'], tg).strip()) == k0, f'premise karenya {scen}')
    check(bool(R(lore['빙의상태 카르엔야 설정'], tg).strip()) == k0, f'possession settings {scen}')
    check(bool(R(lore['유저빙의=다른사람'], tg).strip()) == (scen == '1'), f'premise other {scen}')
    check(bool(R(lore['유저=빙의없음'], tg).strip()) == (scen == '2'), f'premise native {scen}')
    nov = R(lore['원작소설'], tg)
    check(('The Novel and This World' in nov) == (scen != '2') and ('novel' in nov.lower()) == (scen != '2'), f'novel frame {scen}')
    check('### World History' in nov and 'IY 416' in nov and 'IY 429, June 13 — The story begins.' in nov, f'history kept {scen}')
    n += 1
for f, on in (('null', True), ('0', True), ('1', False)):
    check(bool(R(lore['운명의개입(나중에채워)'], {'kc_fate': f}).strip()) == on, f'fate {f}')
for lang in VALS['kc_language']:
    st = R(lore['Status'], {'kc_language': lang})
    en = lang == '1'
    check('{{' not in st.replace('{{user}}', ''), 'status lore clean')
    check(('Hedwig | So Your Majesty' in st and '헤드비히' not in st and 'Undisclosed.' in st) if en
          else ('헤드비히 | …보고만' in st and 'Hedwig |' not in st and '미공개.' in st), f'status lore language {lang}')

# ---- 요청 정리 정규식
srm = next(r for r in m['regex'] if r['comment'] == 'Status 리퀘제거')
import subprocess
def js_sub(src):   # RisuAI는 JS 정규식(가변 길이 lookbehind 지원)이라 node로 확인
    js = 'const r=new RegExp(process.argv[1],"g");process.stdout.write(process.argv[2].replace(r,""))'
    return subprocess.run(['node', '-e', js, srm['in'], src], capture_output=True, text=True, check=True).stdout
s = 'text\n[IY: 429. 7.15 (D-68) | 15:00 | 연무장 | 시간 정지 || 헤드비히 | 속마음 || 루스란 | 속마음]'
check(js_sub(s) == 'text\n[IY: 429. 7.15 (D-68) | 15:00 | 연무장]', 'old status keeps date/time/location only')
check(js_sub('[IY: 429. 9.24 | 08:10 | 정원 | 시간 정지]') == '[IY: 429. 9.24 | 08:10 | 정원]', 'no thoughts: ability removed')
check(js_sub('[IY: 429. 9.24 | 08:10 | 정원]') == '[IY: 429. 9.24 | 08:10 | 정원]', 'already short unchanged')
for idx, keep in ((20, True), (17, True), (16, False), (0, False)):
    out = R(srm['out'], {}, {'@chat_index': str(idx), '@last': '20'})
    check(out.strip() == ('$&' if keep else ''), f'keep last messages {idx}')

# ---- 남은 옛 참조 / 토글 이름 / 버튼 함수
dump = json.dumps(d, ensure_ascii=False)
for bad in ('cv_', 'getvar::lang', 'getvar::scenario', 'getvar::difficulty', 'hgw-', 'cgp-', 'imperial-status', '▶◆▶',
            'setLang', 'setScenario', 'setDifficulty', 'onButtonClick', 'UPCOMING:'):
    check(bad not in dump, f'leftover {bad}')
defined = set(re.findall(r'^(kc_\w+)=', risu['toggles'], re.M))
used = set(re.findall(r'\b(kc_(?:language|scenario|fate|g_\w+?|p_\w+?))(?=::|\}|\W)', dump)) | set(re.findall(r'toggle_(kc_\w+)', dump))
check(used <= defined, f'undefined toggles {used - defined}')
check(defined - used == set(), f'unused toggles {defined - used}')
code = m['trigger'][0]['effect'][0]['code']
funcs = set(re.findall(r'^function (\w+)\(', code, re.M))
for t in set(re.findall(r'risu-trigger="(\w+)"', dump)):
    check(t in funcs, f'missing trigger function {t}')
check(risu['toggles'].startswith('=로판폭군=divider\n') and risu['toggles'].endswith('==groupEnd'), 'toggle text')
check(defaults == {'perma': 'fm_karenya'}, 'defaults')
for e, l in zip(data['character_book']['entries'], m['lorebook']):
    check(e['content'] == l['content'] and e['comment'] == l['comment'], f'card/module lore mismatch {l["comment"]}')
bg = risu['backgroundHTML']
check(bg.count('<style>') == 1 and bg.rstrip().endswith('</style>') and '.kc-box' in bg and '.ks-runin' in bg, 'background css')
print(f'{n} render combos checked; used toggles: {sorted(used)}')
print('FAILS:', len(fails))
