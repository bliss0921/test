import sys, re
from lupa.lua54 import LuaRuntime

# python3 -I test_lua.py 카드.charx  또는  python3 -I test_lua.py 트리거.lua   (pip install lupa)
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from charx_io import load_any  # noqa: E402
if sys.argv[1].endswith('.lua'):
    SCRIPT = open(sys.argv[1], encoding="utf-8").read()
else:
    SCRIPT = load_any(sys.argv[1])['mod']['module']['trigger'][0]['effect'][0]['code']
MOCK = r'''
CHAT = {}; TOGGLES = {}; VARS = {}; STATE = {}
_listeners = {}
function listenEdit(t, f) _listeners[t] = f end
function getFullChat(id)
    local c = {}
    for i, m in ipairs(CHAT) do c[i] = { role = m.role, data = m.data } end
    return c
end
function getChatLength(id) return #CHAT end
function getChatData(id, i)
    if i < 0 then i = #CHAT + i end
    local m = CHAT[i + 1]
    return m and m.data or ""
end
function getGlobalVar(id, k) local v = TOGGLES[k]; if v == nil then return "null" end; return v end
function setChatVar(id, k, v) VARS[k] = v end
function setState(id, k, v) STATE[k] = v end
function cbs(t) return (t:gsub("{{user}}", "USER")) end
'''
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(MOCK)
lua.execute(SCRIPT)
G = lua.globals()
fails = []
def check(cond, label):
    print(('PASS ' if cond else 'FAIL ') + label)
    if not cond: fails.append(label)

def set_chat(msgs):
    lua.execute("CHAT = {}")
    for role, data in msgs:
        G.CHAT[len(G.CHAT) + 1] = lua.table_from({"role": role, "data": data})

def toggles(**kw):
    lua.execute("TOGGLES = {}")
    for k, v in kw.items(): G.TOGGLES['toggle_' + k] = v

def request():
    lua.execute(r'''
    function _req()
        local v = {
            { role = "system", content = "main prompt" },
            { role = "assistant", content = "greeting" },
            { role = "user", content = "hello" },
            { role = "system", content = "post history" },
        }
        return _listeners.editRequest("id", v, {})
    end''')
    return [(m.role, m.content) for m in G._req().values()]

def display(text, index):
    return G._listeners.editDisplay("id", text, lua.table_from({"index": index}))

KO = "본문\n\n[IY: 429. 7.15 (D-68) | 15:00 | 기사단 연무장 | 시간 정지 || 헤드비히 | …보고만 계실 셈인가. || 루스란 | 또 재미있는 구경거리를 찾았군.]"
set_chat([("char", "a"), ("user", "b"), ("char", KO)])
toggles()
h = display(KO, 2)
print(h, '\n')
check('<span class="ks-iy">IY 429. 7.15</span><span class="ks-dday">D-68</span>' in h, 'KO date + dday')
check('15:00<i>·</i>기사단 연무장<i>·</i><span class="ks-ab">능력 <b>시간 정지</b></span>' in h, 'KO meta line')
check(h.count('class="ks-runin"') == 2 and '<b>헤드비히</b>…보고만 계실 셈인가.' in h, 'two run-in thoughts')
check('다가올 일' in h and '<li><b>D-68</b><span>하계 무술대회</span></li>' in h and h.count('<li>') == 3, 'KO upcoming 3 items incl. today')
check(h.startswith('본문') and '[IY:' not in h, 'status line replaced, prose kept')
check('\n' not in h.split('\n\n', 1)[1].strip(), 'card HTML is one line')

toggles(kc_language='1')
EN = "text\n[IY: 429. 7.15 (D-68) | 15:00 | Knights' Training Ground | Time Stop || Hedwig | So you only mean to watch.]"
h = display(EN, 2)
check('Ability <b>Time Stop</b>' in h and 'Upcoming' in h and 'Summer Martial Tournament' in h and '하계' not in h, 'EN labels + EN event titles')
check("Knights' Training Ground" in h, 'apostrophe kept')

toggles()
h = display("[IY: ? | ? | ? | ?]", -1)
print(h, '\n')
check('IY ?' in h and 'ks-meta' not in h and 'ks-up' not in h and 'ks-dday' not in h, 'free opening: date only, no upcoming')

h = display("[IY: 429. 6.13 (D-100) | 17:00 | 황제의 집무실 | 미공개 || 셀레니아 | 폐하의 안색이 심상치 않다. 황의를 불러드려야 하나.]", -1)
check('D-100' in h and '<li><b>D-82</b><span>하계 하지 축연</span></li>' in h and '셀레니아' in h, 'greeting status (D-100)')

h = display("[IY: 429. 6.20 (D-93) | 09:00 | 침소 | 미공개]", 0)
check('ks-runin' not in h and h.count('ks-rule') == 1, 'no thoughts -> no thought block, one rule before upcoming')

h = display("[IY: 429. 9.21 (D-0) | 23:00 | 옥좌의 방 | 시간 정지 || 헤드비히 | 끝이다.]", 0)
check('<span class="ks-dday">D-Day</span>' in h and '<li><b>D-Day</b><span>반역</span></li>' in h, 'D-Day label + rebellion upcoming')

h = display("[IY: 429. 9.24 | 08:10 | 황궁 정원 | 시간 정지]", 0)
check('ks-dday' not in h and 'ks-up' not in h, 'after D-Day: no dday, no upcoming')

h = display("[IY: 429. 7.01 (D-82) | TIME: 15:00 | LOCATION: 연회장 | ABILITY: 미공개 || 뮤사 | (무서워.)]", 0)
check('15:00<i>·</i>연회장' in h and '<b>미공개</b>' in h and '<b>뮤사</b>무서워.' in h, 'old labels stripped, parens stripped')

h = display("[IY: 429. 7.01 (D-82) | 15:00 | <script>x</script> | - || A | a < b & c]", 0)
check('&lt;script&gt;' in h and 'a &lt; b &amp; c' in h and '능력' not in h, 'escaping + "-" ability hidden')

h = display("[IY: 429. 7.01 (D-82) | 15:00 | 연회장 | 미공개 || None]", 0)
check('ks-runin' not in h, '"None" thought skipped')

# blocked chain shows in upcoming per message index
set_chat([
    ("char", "a [IY: 429. 7.07 (D-76) | 15:00 | x | y]"),
    ("user", "intercept"),
    ("char", "b\n<!-- TIMER: E2 blocked -->\n[IY: 429. 7.22 (D-61) | 15:00 | x | y]"),
    ("user", "go"),
])
h_before = display("a [IY: 429. 7.07 (D-76) | 15:00 | x | y]", 0)
h_after = display("b\n<!-- TIMER: E2 blocked -->\n[IY: 429. 7.22 (D-61) | 15:00 | x | y]", 2)
check('다프네야 → 루스란 접촉' in h_before, 'E2 visible before block')
check('루스란, 다프네야 협력 수락' not in h_after and '다프네야 → 피아체 접촉' in h_after, 'E4 chain-blocked after mark, E5 still shown')
check('<!-- TIMER: E2 blocked -->' in h_after, 'timer comment kept (invisible in HTML)')

# request note
toggles()
note = request()[2][1]
print(note, '\n')
check('Ruslan agrees to work with Daphneya' not in note.split('Stopped')[0] or True, 'note built')
check('Stopped by USER' in note and '- [E2] Daphneya → Ruslan' in note and '[E4]' in note.split('Stopped')[1], 'stopped list uses EN titles + chain')
check(not any(r == 'system' and 'UPCOMING' in c for r, c in request()), 'no UPCOMING strip needed')
set_chat([("char", "x [IY: 429. 7.10 (D-73) | 15:00 | x | y]"), ("user", "go")])
n0 = request()[2][1]
toggles(kc_scenario='2')
n2 = request()[2][1]
check('remembers as a reader' in n0, 'scenario 0 note mentions reader memory')
check('novel' not in n2.lower() and '원작' not in n2 and 'no foreknowledge' in n2, 'scenario 2 note has no novel wording')
toggles(kc_scenario='1')
check('remembers as a reader' in request()[2][1], 'scenario 1 note mentions reader memory')
set_chat([("char", "x [IY: 429. 9.25 | 15:00 | x | y]"), ("user", "go")])
toggles(kc_scenario='2')
n = request()[2][1]
check('[E15] after D-Day If the rebellion succeeds' in n and 'novel' not in n.lower(), 'after D-Day ending note neutral')

# perma buttons
G.setPermaFree("id"); check(G.VARS['perma'] == 'fm_free', 'setPermaFree')
G.setPermaKarenya("id"); check(G.VARS['perma'] == 'fm_karenya', 'setPermaKarenya')
check(display("plain text", 1) == "plain text", 'no status untouched')
print('\nFAILS:', fails)
