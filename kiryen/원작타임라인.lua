-- ========================================
-- Rofan Lua: Perma buttons + 원작 타임라인 + 상태창
-- ========================================
-- 언어 · 빙의 · 운명의 개입 · 성별 · 프로필은 사이드바의 커스텀 토글(kc_...)에서 고른다.
-- 토글 값은 고른 선택지 번호다 (첫 번째 0, 두 번째 1, 세 번째 2). 한 번도 안 고르면 "null".
-- Perma: 퍼메 설정 (첫 메시지 버튼)
-- ========================================

-- ================================================
-- HELPERS: state + chatvar
-- ================================================
local function setBoth(triggerId, key, value)
  setState(triggerId, key, value)
  setChatVar(triggerId, key, tostring(value))
end

-- ================================================
-- PERMA BUTTONS (퍼메 설정)
-- perma = "fm_karenya" / "fm_free"  (처음 값은 캐릭터 기본 변수의 perma=fm_karenya)
-- ================================================
function setPermaKarenya(triggerId)    setBoth(triggerId, "perma", "fm_karenya") end
function setPermaFree(triggerId)      setBoth(triggerId, "perma", "fm_free") end

-- =========================================================
-- 황제의 연인 — 원작 타임라인 (100일 타이머) + 운명의 개입 + 상태창
--
-- 모델에게는 기본으로 "지금까지 진행된 일 + WINDOW일 안에 다가온 일"만 보낸다.
-- (원작 줄거리 토글이 '전부'면 앞으로의 일과 결말까지 보내고, '없음'이면 아무것도 안 보낸다.)
-- 플레이어에게는 상태창 아래 '다가올 일'로 보여 준다 (화면 전용, 모델에는 안 감).
-- 상태를 변수에 저장하지 않고 매번 채팅 기록(마지막 STATUS 날짜, TIMER 주석)에서
-- 다시 계산하므로 리롤·메시지 삭제·분기를 해도 꼬이지 않는다.
-- listenEdit만 쓰므로 low level access가 필요 없다.
--
-- 모델이 쓰는 STATUS 줄 (로어북 상태창 참고):
--   [IY: 429. 7.15 (D-68) | 15:00 | 기사단 연무장 | 시간 정지 || 헤드비히 | 속마음 || 루스란 | 속마음]
-- 화면에서는 이 줄을 상태창 카드(HTML)로 바꿔 그린다. 카드 모양은 배경 HTML의 .ks... CSS.
--
-- 운명의 개입: 유저가 사건을 막으면 모델이 <!-- TIMER: E5 blocked --> 를 남긴다.
-- 토글이 켜져 있으면 표시가 2번(강하게는 3번) 쌓여야 진짜 막힌다. 그 전까지는
-- REBOUND_DAYS일 안에 같은 결과가 다른 길로 다시 시도된다 (기한이 지나면 결국 일어난 일로 친다).
-- =========================================================

-- 이벤트 며칠 전부터 모델에게 알려 줄지
local WINDOW = 7

-- 상태창 '다가올 일'에 보여 줄 개수 (운명이 되돌리는 중인 일은 이것과 따로 맨 위에 붙는다)
local UPCOMING_COUNT = 3

-- 운명의 개입: 막힌 날(그 사건 날짜가 더 늦으면 사건 날짜)부터 며칠 안에 다시 시도되는지
local REBOUND_DAYS = 5

-- 커스텀 토글 값 (고른 선택지 번호. 안 골랐으면 "null")
local function toggle(id, key)
    local v = getGlobalVar(id, "toggle_" .. key)
    if v == nil then return "null" end
    return tostring(v)
end

-- kc_language: 0 한국어 / 1 English
local function isEnglish(id)
    return toggle(id, "kc_language") == "1"
end

-- kc_scenario: 0 카르엔야에 빙의 / 1 다른 인물에 빙의 / 2 빙의 없음
local function scenario(id)
    local s = toggle(id, "kc_scenario")
    if s == "1" or s == "2" then return s end
    return "0"
end

-- kc_fate: 0 보통(2번 막아야 막힘) / 1 강하게(3번) / 2 끄기(1번에 막힘). 안 고르면 보통
local function fateNeed(id)
    local f = toggle(id, "kc_fate")
    if f == "2" then return 1 end
    if f == "1" then return 3 end
    return 2
end

-- kc_plot: 0 다가올 때만 / 1 전부 (모델이 앞으로의 줄거리와 결말까지 안다) / 2 없음 (원작 사건 없이).
-- '없음'은 빙의가 '다른 인물'·'빙의 없음'일 때만. 카르엔야 빙의는 100일 파멸이 전제라 '다가올 때만'으로 동작. 안 고르면 다가올 때만
local function plotMode(id)
    local p = toggle(id, "kc_plot")
    if p == "1" then return "full" end
    if p == "2" and scenario(id) ~= "0" then return "off" end
    return "window"
end

-- day: D-숫자, date: M.DD
-- title: 화면에 보이는 한국어 이름 / title_en: 영어 설정일 때 화면 이름이자 모델에게 보내는 이름
-- ongoing: 이야기 시작 전부터 진행 중인 일 (항상 '이미 진행된 일'로 취급)
-- knows: 비밀 이벤트를 아는 인물. 없으면 공개 행사
-- needs: 이 중 하나라도 막히면 같이 막힌다 / any: 전부 막혀야 막힌다
-- side: 반역에 가담하는 세력 (D-Day 문구에 남은 세력만 나열된다)
-- after: D-Day가 지난 뒤에만 모델에게 보여 주는 이벤트 (날짜 없음, 화면 '다가올 일'에도 안 나온다)
local EVENTS = {
    { id = "E0", ongoing = true, title = "다프네야의 은밀한 준비", title_en = "Daphneya's quiet preparations", knows = "Daphneya",
      plot = "Daphneya is quietly preparing to bring Karenya down, gathering information inside and outside the palace through familiars. Outwardly Daphneya stays idle and frivolous, and nothing has surfaced yet." },
    { id = "E1", day = 82, date = "7.01", title = "하계 하지 축연", title_en = "Summer Solstice Festival",
      plot = "Summer Solstice Festival. All four of Karenya's partners gather at the palace for the banquet." },
    { id = "E2", day = 75, date = "7.08", title = "다프네야 → 루스란 접촉", title_en = "Daphneya → Ruslan", knows = "Daphneya, Ruslan", needs = {"E0"},
      plot = "Through a familiar, Daphneya delivers a note to Ruslan saying that Runian is alive." },
    { id = "E3", day = 68, date = "7.15", title = "하계 무술대회", title_en = "Summer Martial Tournament",
      plot = "Summer Martial Tournament of the Imperial Knights. Karenya attends; Hedwig competes." },
    { id = "E4", day = 55, date = "7.28", title = "루스란, 다프네야 협력 수락", title_en = "Ruslan agrees to work with Daphneya", knows = "Daphneya, Ruslan", needs = {"E2"},
      side = "Ruslan, with the surviving Mage Kingdom rebels",
      plot = "Ruslan agrees to work with Daphneya." },
    { id = "E5", day = 49, date = "8.03", title = "다프네야 → 피아체 접촉", title_en = "Daphneya → Piache", knows = "Daphneya, Piache", needs = {"E0"},
      plot = "A handwritten letter from Daphneya reaches Piache: \"I hope we can meet again.\" It is the first direct message from Daphneya in six years." },
    { id = "E6", day = 42, date = "8.10", title = "솔카 축일", title_en = "Feast of Solka",
      plot = "Feast Day of the Sun God Solka. A rite is held at the imperial shrine; Karenya, Piache, and Hedwig attend." },
    { id = "E7", day = 38, date = "8.13", title = "피아체, 다프네야에게 답장", title_en = "Piache replies to Daphneya", knows = "Daphneya, Piache", needs = {"E5"},
      side = "Piache",
      plot = "Piache sends a reply to Daphneya." },
    { id = "E8", day = 32, date = "8.20", title = "카르엔야 탄신연", title_en = "Karenya's Birthday Banquet",
      plot = "Karenya's birthday banquet. All four partners attend; nobles, knights, and members of the Order are invited. Daphneya also attends." },
    { id = "E9", day = 27, date = "8.25", title = "피아체 → 교단 밀서", title_en = "Piache's secret letter to the Order", knows = "Piache, the Order's leadership", needs = {"E7"},
      side = "the Order, which excommunicates Karenya",
      plot = "Piache sends a secret letter to the Order. Within the Order, talk of excommunicating the Emperor begins." },
    { id = "E10", day = 25, date = "8.27", title = "루스란, 헤드비히 의중 타진", title_en = "Ruslan sounds out Hedwig", knows = "Ruslan (Hedwig does not recognize it as a test)", needs = {"E4"},
      plot = "Ruslan sounds Hedwig out, using a casual conversation to test Hedwig's reaction." },
    { id = "E11", day = 20, date = "9.01", title = "추수 제례", title_en = "Harvest Rite",
      plot = "Harvest Rite, an imperial ceremony led by the Emperor in person. Piache, Hedwig, and Ruslan attend." },
    { id = "E12", day = 18, date = "9.03", title = "헤드비히 합류 결심", title_en = "Hedwig decides to join", knows = "Hedwig, Ruslan, Daphneya, House Hugem", needs = {"E10"},
      side = "Hedwig, with House Hugem's northern forces and part of the Imperial Knights",
      plot = "Hedwig decides to join. A coded letter goes to House Hugem, and preparations to move troops begin." },
    { id = "E13", day = 7, date = "9.14", title = "초커 열쇠 완성", title_en = "Choker key completed", knows = "Ruslan",
      plot = "Ruslan completes the key that can unlock the mana-suppressing choker." },
    { id = "E14", day = 0, date = "9.21", title = "반역", title_en = "Rebellion", any = {"E4", "E7", "E9", "E12"},
      plot = "A coordinated rebellion breaks out against Karenya, meant to raise Daphneya as the next Emperor. By default, Myusa hears of it, falls into extreme terror, and makes a contract with the Spirit of Fear; whether that happens depends on Myusa's state now." },
    { id = "E15", after = true, title = "원작의 결말", title_en = "If the rebellion succeeds", needs = {"E14"},
      plot = "What follows a successful rebellion if nothing else has changed: the Order excommunicated Karenya, Hedwig won over most of the Imperial Knights, killed Karenya, then died by suicide, and Daphneya was raised as the next Emperor. Ruslan arrived with the finished key only to find Hedwig and Karenya already dead. Afterward, Daphneya remarries Piache and offers Piache as a dark-magic sacrifice (announced as illness), and Piache dies. Once the Mage Kingdom regains independence, Ruslan refuses the throne and seals away the rest of life in the Mage Tower; the throne passes to Runian. Myusa is fully consumed by the spirit and disappears. This is only the default course: anything the story has already changed stands." },
}

-- 9월 21일(D-0)이 1년 중 몇 번째 날인지
local MONTH_START = {0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334}
local RUIN_YEAR, RUIN_DAY = 429, 243 + 21

-- STATUS의 IY 날짜 → D-0까지 남은 날 수 (지나면 음수). 날짜가 없으면 nil
local function daysLeft(text)
    local y, m, d = text:match("%[IY:%s*(%d+)%.%s*(%d+)%.(%d+)")
    if y and MONTH_START[tonumber(m)] then
        return (RUIN_YEAR - tonumber(y)) * 365 + RUIN_DAY - (MONTH_START[tonumber(m)] + tonumber(d))
    end
    local dd = text:match("%[IY:[^|%]]-D%-(%d+)")
    return dd and tonumber(dd) or nil
end

local function currentDays(history)
    for i = #history, 1, -1 do
        if history[i].role == "char" then
            local left = daysLeft(tostring(history[i].data or ""))
            if left then return left end
        end
    end
    return 100
end

local MARK = "<!%-%-%s*TIMER:%s*(E%d+)%s+blocked%s*%-%->"
local cache = { key = nil, marks = {} }

-- 채팅 전체의 TIMER 주석: 몇 번째 메시지인지 + 그 메시지의 D-남은 날.
-- 보내기 직전(history를 넘길 때)에는 항상 새로 센다. 화면 렌더 때는 채팅 전체를 매번 읽지 않도록
-- 캐시를 쓴다 (중간 메시지를 고친 것은 다음 전송이나 새 메시지 때 화면에 반영된다).
local function timerMarks(id, history)
    local key = getChatLength(id) .. "\0" .. getChatData(id, 0) .. "\0" .. getChatData(id, -1)
    if history or cache.key ~= key then
        local marks, lastLeft = {}, nil
        for i, msg in ipairs(history or getFullChat(id) or {}) do
            local data = tostring(msg.data or "")
            lastLeft = daysLeft(data) or lastLeft
            for eid in data:gmatch(MARK) do
                marks[#marks + 1] = { index = i, id = eid, left = lastLeft }
            end
        end
        cache = { key = key, marks = marks }
    end
    return cache.marks
end

-- lastIndex번째 메시지까지의 상태
--   st.blocked[id]  : 진짜 막힘 (표시가 need번 이상, 또는 선행 조건이 막혀 연쇄로)
--   st.count[id]    : 막힘 표시 개수
--   st.markLeft[id] : 마지막 막힘 표시가 있던 메시지의 D-남은 날
local function timelineState(id, lastIndex, history, need)
    local count, markLeft = {}, {}
    for _, m in ipairs(timerMarks(id, history)) do
        if m.index <= lastIndex then
            count[m.id] = (count[m.id] or 0) + 1
            markLeft[m.id] = m.left
        end
    end
    local blocked = {}
    for _, e in ipairs(EVENTS) do
        local b = (count[e.id] or 0) >= need
        for _, n in ipairs(e.needs or {}) do
            if blocked[n] then b = true end
        end
        if e.any then
            local alive = false
            for _, other in ipairs(e.any) do
                if not blocked[other] then alive = true end
            end
            if not alive then b = true end
        end
        blocked[e.id] = b
    end
    return { blocked = blocked, count = count, markLeft = markLeft, need = need }
end

local function isPast(e, left)
    if e.after then return left < 0 end
    return e.ongoing or e.day > left
end

-- 운명이 다시 시도하는 기한 (D-숫자). 막힌 날과 원래 날짜 중 늦은 쪽에서 REBOUND_DAYS일 뒤
local function reboundBy(e, st)
    local due = st.markLeft[e.id] or e.day or 0
    if e.day and e.day < due then due = e.day end
    return due - REBOUND_DAYS
end

-- 한 번 이상 막혔지만 아직 진짜 막히지 않았고, 다시 시도하는 기한 안이면 "운명이 되돌리는 중"
local function rebounding(e, left, st)
    return (st.count[e.id] or 0) > 0 and not st.blocked[e.id] and left >= reboundBy(e, st)
end

-- D-숫자 → "M.DD" (IY 429 안에서만, 밖이면 nil)
local function dateOf(left)
    local doy = RUIN_DAY - left
    if doy < 1 or doy > 365 then return nil end
    for m = 12, 1, -1 do
        if doy > MONTH_START[m] then return m .. "." .. string.format("%02d", doy - MONTH_START[m]) end
    end
end

local function describe(e, st)
    local when = e.ongoing and "ongoing" or e.after and "after D-Day" or ("D-" .. e.day .. " (" .. e.date .. ")")
    local text = "- [" .. e.id .. "] " .. when .. " " .. e.title_en .. ": " .. e.plot
    if e.any then
        local sides = {}
        for _, other in ipairs(EVENTS) do
            if other.side and not st.blocked[other.id] then sides[#sides + 1] = other.side end
        end
        text = text .. " Factions still in: " .. table.concat(sides, "; ") .. ". Factions that dropped out take no part."
    end
    if e.knows then text = text .. " Secret, known only to: " .. e.knows .. "." end
    return text
end

local function describeRebound(e, st)
    local by = reboundBy(e, st)
    local date = dateOf(by)
    return "- [" .. e.id .. "] " .. e.title_en .. ": thwarted by {{user}} " .. st.count[e.id] .. " of the " .. st.need
        .. " times it takes to stop it for good. By " .. (date and (date .. " ") or "") .. "(D-" .. by .. ") the same outcome is attempted again through a new route."
        .. " What it aims at: " .. e.plot .. (e.knows and (" Secret, known only to: " .. e.knows .. ".") or "")
end

-- scen: 빙의 토글. "2"(빙의 없음)면 {{user}}가 원작을 모르므로 '독자의 기억' 문구를 뺀다
-- full: 원작 줄거리 '전부'
local function worldNote(left, st, scen, full)
    local past, stopped, fated, soon = {}, {}, {}, {}
    for _, e in ipairs(EVENTS) do
        if st.blocked[e.id] then
            stopped[#stopped + 1] = "- [" .. e.id .. "] " .. e.title_en
        elseif rebounding(e, left, st) then
            fated[#fated + 1] = describeRebound(e, st)
        elseif isPast(e, left) or (st.count[e.id] or 0) > 0 then
            local text = describe(e, st)
            if (st.count[e.id] or 0) > 0 then
                text = text .. " {{user}} interfered, but it came about anyway by another route."
            end
            past[#past + 1] = text
        elseif full or (e.day and left - e.day <= WINDOW) then
            soon[#soon + 1] = describe(e, st)
        end
    end

    local course = scen == "2" and "the course events take while their causes stand"
        or "the novel's course, which {{user}} remembers as a reader"
    local soonTitle = "Approaching within " .. WINDOW .. " days (" .. course .. "):"
    if full then
        soonTitle = "Still ahead, to the end (" .. course .. "; each comes only if its causes still stand):"
    end

    local lines = {
        "[World State: hidden note for the narrator. Never quote or reveal it.]",
        "Today: " .. (left >= 0 and ("D-" .. left) or "after D-Day") .. " (from the latest STATUS).",
    }
    local function section(title, items)
        if #items == 0 then return end
        lines[#lines + 1] = ""
        lines[#lines + 1] = title
        for _, item in ipairs(items) do lines[#lines + 1] = item end
    end
    section("Already set in motion (true unless the chat history shows otherwise):", past)
    section("Stopped by {{user}}'s actions (these threads no longer advance; nothing that depends on them can happen):", stopped)
    section("Fate pushes back (the world bends toward its set course; see Fate's Pull):", fated)
    section(soonTitle, soon)
    lines[#lines + 1] = ""
    lines[#lines + 1] = "Rules:"
    lines[#lines + 1] = "- An approaching event unfolds on its date only if its causes still stand in this story. {{user}}'s earlier actions may delay or change it."
    lines[#lines + 1] = "- Secret events happen off-screen and leave no visible trace unless {{user}} is present or deliberately investigates."
    lines[#lines + 1] = "- Each character acts only on what that character personally knows. \"Known only to\" is strict, and no one foresees the future."
    if full then
        lines[#lines + 1] = "- You know the whole course. Let it shape tension and quiet foreshadowing, but never reveal it and never bring an event before its date."
    else
        lines[#lines + 1] = "- Do not foreshadow events that are not listed here."
    end
    if #fated > 0 then
        lines[#lines + 1] = "- An event under \"Fate pushes back\" is attempted again by its deadline through a new, plausible route, never the one {{user}} closed. If {{user}} thwarts that attempt too, mark it again."
    end
    lines[#lines + 1] = "- If {{user}}'s actions have made a listed event or ongoing scheme impossible, write <!-- TIMER: ID blocked --> on its own line right before the STATUS line, once, in the response where it happens. Never write it otherwise."
    return table.concat(lines, "\n")
end

-- 화면 '다가올 일': { {"D-82", "하계 하지 축연"}, ... }. 운명이 되돌리는 중인 일은 맨 위에 "곧"으로
local function upcoming(left, st, en)
    local items = {}
    for _, e in ipairs(EVENTS) do
        if rebounding(e, left, st) and not e.after then
            items[#items + 1] = { en and "Soon" or "곧", (en and e.title_en or e.title) .. (en and " (another way)" or " (다른 길로)") }
        end
    end
    local n = 0
    for _, e in ipairs(EVENTS) do
        if n < UPCOMING_COUNT and e.day and not isPast(e, left) and not st.blocked[e.id] and (st.count[e.id] or 0) == 0 then
            items[#items + 1] = { e.day == 0 and "D-Day" or ("D-" .. e.day), en and e.title_en or e.title }
            n = n + 1
        end
    end
    return items
end

-- ---------------------------------------------------------
-- 상태창 카드
-- ---------------------------------------------------------
local function trim(s)
    return (s:gsub("^%s+", ""):gsub("%s+$", ""))
end

local function esc(s)
    return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

-- 모델이 옛 형식처럼 라벨을 붙여 쓴 경우 (TIME: 15:00) 라벨만 떼어 낸다
local LABELS = { TIME = true, LOCATION = true, ABILITY = true }
local EMPTY = { [""] = true, ["?"] = true, ["-"] = true, none = true, ["없음"] = true }

local function field(s)
    s = trim(s or "")
    local label, rest = s:match("^(%u+):%s*(.*)$")
    if label and LABELS[label] then s = rest end
    return s
end

-- status: "[IY: ... ]" 한 줄 / st: 이 메시지까지의 타임라인 상태 (원작 사건 없음이면 nil: D-day·다가올 일 없음)
local function statusCard(status, st, en)
    local inner = status:match("^%[IY:(.*)%]$") or ""
    local head, rest = inner:match("^(.-)||(.*)$")
    if not head then head, rest = inner, "" end

    local f = {}
    for part in (head .. "|"):gmatch("(.-)|") do f[#f + 1] = field(part) end

    local date = trim((f[1] or ""):gsub("%(.-%)", ""))
    if date == "" then date = "?" end
    local left = st and daysLeft(status)
    local dday = ""
    if left and left > 0 then dday = "D-" .. left elseif left == 0 then dday = "D-Day" end

    local html = { '<div class="ks"><div class="ks-date"><span class="ks-iy">IY ', esc(date), '</span>' }
    if dday ~= "" then html[#html + 1] = '<span class="ks-dday">' .. dday .. '</span>' end
    html[#html + 1] = '</div>'

    local meta = {}
    for i = 2, 3 do
        if f[i] and not EMPTY[f[i]:lower()] then meta[#meta + 1] = esc(f[i]) end
    end
    if f[4] and not EMPTY[f[4]:lower()] then
        meta[#meta + 1] = '<span class="ks-ab">' .. (en and "Ability" or "능력") .. ' <b>' .. esc(f[4]) .. '</b></span>'
    end
    if #meta > 0 then
        html[#html + 1] = '<div class="ks-meta">' .. table.concat(meta, '<i>·</i>') .. '</div>'
    end

    -- 속마음: "|| 이름 | 속마음" 마다 한 문단, 이름은 문단 맨 앞에 굵게
    local thoughts = {}
    for seg in (rest .. "||"):gmatch("(.-)||") do
        seg = trim(seg)
        local name, text = seg:match("^(.-)%s*|%s*(.*)$")
        if not name then name, text = "", seg end
        text = trim(text:match("^%((.*)%)$") or text)
        if not EMPTY[text:lower()] then
            thoughts[#thoughts + 1] = '<p class="ks-runin">' .. (name ~= "" and ('<b>' .. esc(name) .. '</b>') or "") .. esc(text) .. '</p>'
        end
    end
    if #thoughts > 0 then
        html[#html + 1] = '<div class="ks-rule"></div>' .. table.concat(thoughts)
    end

    -- 다가올 일: 날짜를 알 때만
    if left then
        local items = upcoming(left, st, en)
        if #items > 0 then
            html[#html + 1] = '<div class="ks-rule"></div><div class="ks-up-label">' .. (en and "Upcoming" or "다가올 일") .. '</div><ol class="ks-up">'
            for _, it in ipairs(items) do
                html[#html + 1] = '<li><b>' .. it[1] .. '</b><span>' .. esc(it[2]) .. '</span></li>'
            end
            html[#html + 1] = '</ol>'
        end
    end
    html[#html + 1] = '</div>'
    return table.concat(html)
end

-- 요청 직전: World State를 마지막 유저 메시지 앞에 끼워 넣는다
listenEdit("editRequest", function(id, value, meta)
    local history = getFullChat(id) or {}
    local left = currentDays(history)
    local mode = plotMode(id)
    if mode == "off" then return value end
    local st = timelineState(id, #history, history, fateNeed(id))

    local at = #value + 1
    for i = #value, 1, -1 do
        if value[i].role == "user" then at = i; break end
    end
    table.insert(value, at, { role = "system", content = cbs(worldNote(left, st, scenario(id), mode == "full")) })
    return value
end)

-- 화면 표시: STATUS 줄을 상태창 카드로 바꿔 그린다 (저장된 원문은 그대로)
listenEdit("editDisplay", function(id, value, meta)
    if type(value) ~= "string" or not value:find("[IY:", 1, true) then return value end
    local index = meta and tonumber(meta.index)
    local st = plotMode(id) ~= "off" and timelineState(id, index and index + 1 or 0, nil, fateNeed(id)) or nil
    local en = isEnglish(id)
    return (value:gsub("%[IY:[^%]\n]*%]", function(status)
        return "\n\n" .. statusCard(status, st, en) .. "\n\n"
    end))
end)
