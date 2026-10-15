-- =========================================================
-- 황제의 연인 — 원작 타임라인 (100일 타이머)
--
-- 모델에게는 "지금까지 진행된 일 + WINDOW일 안에 다가온 일"만 보낸다.
-- 플레이어에게는 STATUS 줄의 UPCOMING으로 보여 준다 (화면 전용, 모델에는 안 감).
-- 상태를 변수에 저장하지 않고 매번 채팅 기록(마지막 STATUS 날짜, TIMER 주석)에서
-- 다시 계산하므로 리롤·메시지 삭제·분기를 해도 꼬이지 않는다.
-- listenEdit만 쓰므로 low level access가 필요 없다.
-- =========================================================

-- 이벤트 며칠 전부터 모델에게 알려 줄지
local WINDOW = 7

-- 화면의 UPCOMING에 보여 줄 개수
local UPCOMING_COUNT = 3

-- day: D-숫자, date: M.DD
-- ongoing: 이야기 시작 전부터 진행 중인 일 (항상 '이미 진행된 일'로 취급)
-- knows: 비밀 이벤트를 아는 인물. 없으면 공개 행사
-- needs: 이 중 하나라도 막히면 같이 막힌다 / any: 전부 막혀야 막힌다
-- side: 반역에 가담하는 세력 (D-Day 문구에 남은 세력만 나열된다)
-- after: D-Day가 지난 뒤에만 모델에게 보여 주는 이벤트 (날짜 없음, 화면 UPCOMING에도 안 나온다)
local EVENTS = {
    { id = "E0", ongoing = true, title = "다프네야의 은밀한 준비", knows = "Daphneya",
      plot = "Daphneya is quietly preparing to bring Karenya down, gathering information inside and outside the palace through familiars. Outwardly Daphneya stays idle and frivolous, and nothing has surfaced yet." },
    { id = "E1", day = 82, date = "7.01", title = "하계 하지 축연",
      plot = "Summer Solstice Festival. All four of Karenya's partners gather at the palace for the banquet." },
    { id = "E2", day = 75, date = "7.08", title = "다프네야 → 루스란 접촉", knows = "Daphneya, Ruslan", needs = {"E0"},
      plot = "Through a familiar, Daphneya delivers a note to Ruslan saying that Runian is alive." },
    { id = "E3", day = 68, date = "7.15", title = "하계 무술대회",
      plot = "Summer Martial Tournament of the Imperial Knights. Karenya attends; Hedwig competes." },
    { id = "E4", day = 55, date = "7.28", title = "루스란, 다프네야 협력 수락", knows = "Daphneya, Ruslan", needs = {"E2"},
      side = "Ruslan, with the surviving Mage Kingdom rebels",
      plot = "Ruslan agrees to work with Daphneya." },
    { id = "E5", day = 49, date = "8.03", title = "다프네야 → 피아체 접촉", knows = "Daphneya, Piache", needs = {"E0"},
      plot = "A handwritten letter from Daphneya reaches Piache: \"I hope we can meet again.\" It is the first direct message from Daphneya in seven years." },
    { id = "E6", day = 42, date = "8.10", title = "솔카 축일",
      plot = "Feast Day of the Sun God Solka. A rite is held at the imperial shrine; Karenya, Piache, and Hedwig attend." },
    { id = "E7", day = 38, date = "8.13", title = "피아체, 다프네야에게 답장", knows = "Daphneya, Piache", needs = {"E5"},
      side = "Piache",
      plot = "Piache sends a reply to Daphneya." },
    { id = "E8", day = 32, date = "8.20", title = "카르엔야 탄신연",
      plot = "Karenya's birthday banquet. All four partners attend; nobles, knights, and members of the Order are invited. Daphneya also attends." },
    { id = "E9", day = 27, date = "8.25", title = "피아체 → 교단 밀서", knows = "Piache, the Order's leadership", needs = {"E7"},
      side = "the Order, which excommunicates Karenya",
      plot = "Piache sends a secret letter to the Order. Within the Order, talk of excommunicating the Emperor begins." },
    { id = "E10", day = 25, date = "8.27", title = "루스란, 헤드비히 의중 타진", knows = "Ruslan (Hedwig does not recognize it as a test)", needs = {"E4"},
      plot = "Ruslan sounds Hedwig out, using a casual conversation to test Hedwig's reaction." },
    { id = "E11", day = 20, date = "9.01", title = "추수 제례",
      plot = "Harvest Rite, an imperial ceremony led by the Emperor in person. Piache, Hedwig, and Ruslan attend." },
    { id = "E12", day = 18, date = "9.03", title = "헤드비히 합류 결심", knows = "Hedwig, Ruslan, Daphneya, House Hugem", needs = {"E10"},
      side = "Hedwig, with House Hugem's northern forces and part of the Imperial Knights",
      plot = "Hedwig decides to join. A coded letter goes to House Hugem, and preparations to move troops begin." },
    { id = "E13", day = 7, date = "9.14", title = "초커 열쇠 완성", knows = "Ruslan",
      plot = "Ruslan completes the key that can unlock the mana-suppressing choker." },
    { id = "E14", day = 0, date = "9.21", title = "반역", any = {"E4", "E7", "E9", "E12"},
      plot = "A coordinated rebellion breaks out against Karenya, meant to raise Daphneya as the next Emperor. In the novel, Myusa heard of it, fell into extreme terror, and made a contract with the Spirit of Fear; whether that happens depends on Myusa's state now." },
    { id = "E15", after = true, title = "원작의 결말", needs = {"E14"},
      plot = "The novel's course once the rebellion succeeds: the Order excommunicated Karenya, Hedwig won over most of the Imperial Knights, killed Karenya, then died by suicide, and Daphneya was raised as the next Emperor. Ruslan arrived with the finished key only to find Hedwig and Karenya already dead. Afterward, Daphneya remarries Piache and offers Piache as a dark-magic sacrifice (announced as illness), and Piache dies. Once the Mage Kingdom regains independence, Ruslan refuses the throne and seals away the rest of life in the Mage Tower; the throne passes to Runian. Myusa is fully consumed by the spirit and disappears. This is only the default course: anything the story has already changed stands." },
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

-- 채팅 전체의 TIMER 주석 위치. 화면 렌더마다 채팅 전체를 다시 읽지 않도록 캐시한다.
local function timerMarks(id, history)
    local key = getChatLength(id) .. "\0" .. getChatData(id, 0) .. "\0" .. getChatData(id, -1)
    if cache.key ~= key then
        local marks = {}
        for i, msg in ipairs(history or getFullChat(id) or {}) do
            for eid in tostring(msg.data or ""):gmatch(MARK) do
                marks[#marks + 1] = { index = i, id = eid }
            end
        end
        cache = { key = key, marks = marks }
    end
    return cache.marks
end

-- lastIndex번째 메시지까지의 TIMER 주석 + 선행 조건이 막혀 연쇄로 막힌 이벤트
local function blockedUpTo(id, lastIndex, history)
    local marked = {}
    for _, m in ipairs(timerMarks(id, history)) do
        if m.index <= lastIndex then marked[m.id] = true end
    end
    local blocked = {}
    for _, e in ipairs(EVENTS) do
        local b = marked[e.id] == true
        for _, need in ipairs(e.needs or {}) do
            if blocked[need] then b = true end
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
    return blocked
end

local function isPast(e, left)
    if e.after then return left < 0 end
    return e.ongoing or e.day > left
end

local function describe(e, blocked)
    local when = e.ongoing and "ongoing" or e.after and "after D-Day" or ("D-" .. e.day .. " (" .. e.date .. ")")
    local text = "- [" .. e.id .. "] " .. when .. " " .. e.title .. ": " .. e.plot
    if e.any then
        local sides = {}
        for _, other in ipairs(EVENTS) do
            if other.side and not blocked[other.id] then sides[#sides + 1] = other.side end
        end
        text = text .. " Factions still in: " .. table.concat(sides, "; ") .. ". Factions that dropped out take no part."
    end
    if e.knows then text = text .. " Secret, known only to: " .. e.knows .. "." end
    return text
end

local function worldNote(left, blocked)
    local past, stopped, soon = {}, {}, {}
    for _, e in ipairs(EVENTS) do
        if blocked[e.id] then
            stopped[#stopped + 1] = "- [" .. e.id .. "] " .. e.title
        elseif isPast(e, left) then
            past[#past + 1] = describe(e, blocked)
        elseif e.day and left - e.day <= WINDOW then
            soon[#soon + 1] = describe(e, blocked)
        end
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
    section("Approaching within " .. WINDOW .. " days (the novel's course, which {{user}} remembers as a reader):", soon)
    lines[#lines + 1] = ""
    lines[#lines + 1] = "Rules:"
    lines[#lines + 1] = "- An approaching event unfolds on its date only if its causes still stand in this story. {{user}}'s earlier actions may delay or change it."
    lines[#lines + 1] = "- Secret events happen off-screen and leave no visible trace unless {{user}} is present or deliberately investigates."
    lines[#lines + 1] = "- Each character acts only on what that character personally knows. \"Known only to\" is strict, and no one foresees the future."
    lines[#lines + 1] = "- Do not foreshadow novel events that are not listed here."
    lines[#lines + 1] = "- If {{user}}'s actions have made a listed event or ongoing scheme impossible, write <!-- TIMER: ID blocked --> on its own line right before the STATUS line. Never write it otherwise."
    return table.concat(lines, "\n")
end

local function upcoming(left, blocked)
    local items = {}
    for _, e in ipairs(EVENTS) do
        if #items < UPCOMING_COUNT and e.day and not isPast(e, left) and not blocked[e.id] then
            items[#items + 1] = "D-" .. e.day .. " " .. e.title
        end
    end
    if #items == 0 then return "None" end
    return "• " .. table.concat(items, "<br>• ")
end

-- 요청 직전: World State를 마지막 유저 메시지 앞에 끼워 넣고, 기록 속 UPCOMING은 지운다
listenEdit("editRequest", function(id, value, meta)
    local history = getFullChat(id) or {}
    local left = currentDays(history)
    local blocked = blockedUpTo(id, #history, history)

    -- 첫 메시지 등 이전 STATUS에 남은 UPCOMING은 모델에게 보내지 않는다
    for _, msg in ipairs(value) do
        if type(msg.content) == "string" then
            msg.content = msg.content:gsub("%s*|%s*UPCOMING:[^%]]*", "")
        end
    end

    local at = #value + 1
    for i = #value, 1, -1 do
        if value[i].role == "user" then at = i; break end
    end
    table.insert(value, at, { role = "system", content = cbs(worldNote(left, blocked)) })
    return value
end)

-- 화면 표시: UPCOMING이 없는 STATUS에 그 메시지 날짜 기준 UPCOMING을 붙인다 (저장 원본은 그대로)
listenEdit("editDisplay", function(id, value, meta)
    if type(value) ~= "string" or not value:find("[IY:", 1, true) then return value end
    local index = meta and tonumber(meta.index)
    local blocked = blockedUpTo(id, index and index + 1 or 0)
    return (value:gsub("(%[IY:[^%]]*)%]", function(status)
        if status:find("UPCOMING:", 1, true) then return nil end
        return status .. " | UPCOMING: " .. upcoming(daysLeft(status) or 100, blocked) .. "]"
    end))
end)
