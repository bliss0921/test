# RisuAI Lua 스크립팅 레퍼런스

Lua 스크립트는 캐릭터/모듈의 **트리거 스크립트**를 코드로 작성하는 방식이다.
wasmoon(Lua 5.4, WASM) 엔진에서 실행된다. 구현: `src/ts/process/scriptings.ts`.

## 1. 작성 위치와 실행 모델

- 캐릭터 설정 → Scripts → Trigger Script에서 트리거 타입을 Lua로 선택해 코드를 작성한다.
  (내부적으로는 `triggerscript.effect[0] = { type: 'triggerlua', code }`)
- **Lua 트리거는 트리거의 타입(start/input/output...)과 무관하게 모든 트리거 시점에 로드**되고,
  어떤 이벤트에 반응할지는 코드에 정의한 콜백 함수가 결정한다.
- 모듈에도 동일하게 트리거 스크립트를 넣을 수 있다 (`getModuleTriggers()`로 합쳐짐).

### 엔진 수명 주기 (핵심 인사이트)

- **엔진은 실행 모드별로 별도 인스턴스**다. `onInput`이 도는 엔진과 `onOutput`이 도는 엔진, `editDisplay`용
  엔진은 서로 다르다. **manual 트리거는 트리거 이름이 곧 모드 키이므로 이름마다 별도 엔진**이다.
  **Lua 전역 변수는 모드 간 공유되지 않는다.** 모드 간 상태 공유는 반드시
  `setState`/`setChatVar`(채팅 변수)로 하라.
- 같은 모드의 엔진은 코드가 바뀌지 않는 한 재사용된다 → Lua 전역 변수는 같은 모드의 연속 호출 사이엔
  유지되지만, 코드 수정/앱 재시작 시 초기화된다. 영구 상태는 채팅 변수에 저장하라.
- 코드가 바뀌면 엔진을 새로 만들고 스크립트 전체를 다시 실행한 뒤 콜백을 호출한다.
  (전역 스코프의 코드는 초기화 용도로만 사용)
- 동일 엔진에 대한 호출은 mutex로 직렬화된다.

### 콜백 (전역 함수로 정의)

```lua
-- 유저가 전송 버튼을 누른 직후 — 단, 새 유저 메시지가 채팅에 "추가되기 전"에 실행됨.
-- 따라서 getUserLastMessage는 직전 턴의 유저 메시지를 반환하고, 이번 입력 텍스트에는 접근 불가.
-- 여기서 return false / stopChat은 무시된다 (전송 취소 불가).
function onInput(triggerId) ... end

-- AI 응답이 채팅에 저장되고 runVar 패스(응답 속 {{setvar}} 실행)까지 끝난 후
function onOutput(triggerId) ... end

-- 이름과 달리 "채팅 시작"이 아니라 **매 전송마다** 프롬프트 빌드 도중에 실행됨 (UI 라벨: "On chat Send").
-- 전송을 취소(return false / stopChat)할 수 있는 유일한 콜백.
function onStart(triggerId) ... end

-- {{button::라벨::이름}} 또는 risu-trigger="이름" 클릭 시:
-- manual 트리거의 경우 트리거 "이름"과 같은 이름의 전역 함수가 호출된다
function attack(triggerId) ... end

-- HTML 요소의 risu-btn="데이터" 클릭 시
function onButtonClick(triggerId, data) ... end

-- 편집 리스너 (등록형): type은 'editRequest'|'editInput'|'editOutput'|'editDisplay'
listenEdit('editRequest', function(triggerId, value, meta)
    -- value를 수정해 반환
    return value
end)
```

- **`false` 반환(또는 `stopChat`)으로 전송을 중단할 수 있는 것은 `onStart`뿐이다.**
  `onInput`의 stopSending은 호출부에서 확인하지 않는다.
  stop 판정은 반환값이 **정확히 `false`**일 때만 발동한다 — nil은 무시되므로
  `return setStateChanged(...)`처럼 nil을 반환할 수 있는 호출로 끝나도 전송이 끊기지 않는다.
- `listenEdit` 콜백의 `value`:
  - `editRequest`: 모델에 보낼 메시지 배열 `[{role='user'|'char'|'system', data=...}, ...]` 형태의 테이블
  - `editInput`/`editOutput`/`editDisplay`: 문자열 (해당 메시지 텍스트)
  - `meta`: `editInput`/`editOutput`/`editDisplay`에서는 `{index = 메시지 인덱스}`, **`editRequest`에서는 빈 테이블**
  - 반환값이 다음 리스너의 입력이 된다 (체이닝).
- `editDisplay`는 화면 표시마다 실행된다. 이 모드에서는 **변수 쓰기가 임시 저장소로만 가고 영구 반영되지
  않으며**, 대부분의 조작 API(권한 필요 API)가 무시된다. 표시 변환 전용으로 써라.

### triggerId (접근 키)

모든 콜백의 첫 인자 `triggerId`는 해당 실행에 부여된 접근 키다. **거의 모든 API의 첫 인자로 그대로
전달해야 한다.** 키의 권한 등급:

| 등급 | 부여 조건 | 허용 API |
|---|---|---|
| editDisplay | editDisplay 실행 | 읽기 API + `setChatVar` |
| safe | 그 외 모든 실행 | 아래 표의 "일반" API 전부 |
| lowLevel (LLA) | 캐릭터의 "low level access" 체크 + safe | `request`, `LLM`, `axLLM`, `simpleLLM`, `similarity`, `generateImage`, `loadLoreBooks` |

주의: **`listenEdit` 계열(editRequest/editInput/editOutput/editDisplay)은 항상 LLA 없이 실행된다**
(캐릭터 트리거·모듈 트리거 모두 강제로 lowLevelAccess=false). LLA API는 onInput/onOutput/onStart/버튼/manual
트리거에서만 쓸 수 있다.

### 비동기 모델

wasmoon은 JS Promise를 Lua로 노출한다. 저수준 API 중 async인 것은 `:await()`가 필요하며, `:await()`는
**coroutine 안에서만** 동작한다. 래퍼가 준비되어 있다:

- `async(function(...) ... end)` — 코루틴 기반 async 함수 생성기 (전역 제공). Promise를 반환하는
  함수를 만들어 준다.
- **await가 필요한 콜백은 `onOutput = async(function(triggerId) ... end)` 형태로 할당한다.**
  호출부(JS)가 콜백의 반환값을 await하므로 이 형태가 그대로 동작한다. await가 필요 없으면
  일반 `function onOutput(triggerId) ... end` 정의로 충분하다.
- **`listenEdit` 콜백은 예외**: 디스패처 자체가 `async(...)`로 감싸여 코루틴 안에서 실행되므로,
  콜백 내부에서 `async` 래핑 없이 `sleep`·`getTokens` 등 async API와 `:await()`를 바로 쓸 수 있다.
- `LLM`, `axLLM`, `loadLoreBooks`, `getCharacterImage`, `getPersonaImage`는 이미 내부에서 `:await()`
  처리된 동기풍 래퍼다 — **단, 이들을 호출하는 콜백은 위처럼 `async(...)`로 할당해야 한다.**
- `json` 모듈 내장: `json.encode(table)`, `json.decode(str)`.

```lua
onOutput = async(function(triggerId)
    local res = LLM(triggerId, {
        { role = 'user', content = '한 문장으로 요약: ' .. getUserLastMessage(triggerId) }
    })
    if res.success then
        setChatVar(triggerId, 'summary', res.result)
    end
end)
```

## 2. API 레퍼런스

표기: `[LLA]` = low level access 필요, `[async]` = Promise 반환(`:await()` 필요 또는 async 컨텍스트).
인덱스는 0부터이며 음수 인덱스는 뒤에서부터 접근한다 (JS `.at()` 의미론).

### 변수·상태
| 함수 | 설명 |
|---|---|
| `getChatVar(id, key)` → string | 채팅 변수 읽기 (CBS `{{getvar}}`와 동일 저장소, 없으면 `'null'`) |
| `setChatVar(id, key, value)` | 채팅 변수 쓰기. **즉시 DB에 반영(write-through)**되므로 같은 사이클의 이후 CBS 파싱·트리거가 바로 새 값을 본다 (editDisplay에서도 허용되지만 표시 모드에선 임시). 기존 값과 같으면 쓰기가 스킵된다 |
| `setChatVarChanged(id, key, value)` → boolean\|nil | setChatVar와 동일하되 값이 **실제로 바뀌었으면 `true`**, 무변경이면 nil 반환 |
| `getGlobalVar(id, key)` → string | 전역 변수 읽기 (읽기 전용). 현재 채팅에 로컬 오버레이(`GLGlobalVariables`)가 있으면 그 값이 우선됨 — [interop.md](interop.md) 1절 |
| `getState(id, name)` / `setState(id, name, value)` | JSON 직렬화 래퍼. 테이블 등 구조화 값을 `__name` 채팅 변수에 저장/복원. **Lua 간 상태 저장은 이걸 권장** |
| `setStateChanged(id, name, value)` → boolean\|nil | setState와 동일하되 값이 바뀌었으면 `true`, 무변경이면 nil 반환 |

`getState`/`setState`는 내부적으로 `__` 접두사가 붙으므로 CBS에서 읽으려면 `{{getvar::__name}}`(JSON 문자열).

### 채팅 조작
| 함수 | 설명 |
|---|---|
| `getChat(id, index)` → `{role, data, time}` | 메시지 읽기 (role: `'user'`/`'char'`) |
| `getChatData(id, index)` → string | 메시지 본문만 읽기 (없으면 빈 문자열). 테이블 변환 없는 경량 API |
| `getChatRole(id, index)` → string | 메시지 역할만 읽기 (없으면 빈 문자열) |
| `getRecentChats(id, count)` → table | 최근 count개 메시지를 `{role, data, time}` 배열로. `getFullChat` 전체 복사 없이 가볍게 읽는 용도 |
| `setChat(id, index, value)` | 메시지 내용 교체 |
| `setChatRole(id, index, role)` | 역할 변경 |
| `addChat(id, role, value)` | 끝에 추가 |
| `insertChat(id, index, role, value)` | 삽입 |
| `removeChat(id, index)` | 삭제 |
| `cutChat(id, start, end)` | slice(start, end)로 잘라냄 |
| `getChatLength(id)` → number | 메시지 수 |
| `getFullChat(id)` → table | 전체 메시지 배열. JSON 배열을 `json.decode`한 **Lua 테이블이므로 1부터 인덱싱**(`ipairs` 사용). 요소는 `{role, data, time?, ...}` |
| `setFullChat(id, table)` | 전체 교체 (같은 형식의 테이블) |
| `getCharacterLastMessage(id)` / `getUserLastMessage(id)` → string | 마지막 캐릭터/유저 메시지 (onInput 시점엔 새 입력이 아직 없으므로 직전 턴 기준) |
| `stopChat(id)` | 전송 중단 (return false와 동일 — **onStart에서만 실제로 취소됨**) |

트리거 실행 중 조작은 채팅의 복사본에 적용된 뒤 실행 종료 시 반영된다.

### 캐릭터·페르소나
| 함수 | 설명 |
|---|---|
| `getName(id)` / `setName(id, name)` | 캐릭터 이름 |
| `getDescription(id)` / `setDescription(id, desc)` | 설명 (그룹이면 에러) |
| `getCharacterFirstMessage(id)` / `setCharacterFirstMessage(id, msg)` | 첫 메시지 |
| `getBackgroundEmbedding(id)` / `setBackgroundEmbedding(id, html)` | 배경 임베딩 HTML |
| `getPersonaName(id)` / `getPersonaDescription(id)` | 유저 페르소나 (읽기 전용) |
| `getAuthorsNote(id)` | 작가의 노트 (읽기 전용) |
| `getCharacterImage(id)` / `getPersonaImage(id)` → string | 아이콘을 인레이로 만들어 `{{inlayed::id}}` 태그 반환. async 래퍼이므로 async 컨텍스트 필요 |

### 로어북
| 함수 | 설명 |
|---|---|
| `getLoreBooks(id, name)` → table | comment(이름)가 일치하는 로어북 항목들 (chat/글로벌/모듈 전체 검색, content는 CBS 파싱됨) |
| `upsertLocalLoreBook(id, name, content, options)` | 채팅 로컬 로어북 생성/교체. options: `{alwaysActive, insertOrder, key, secondKey, regex}` |
| `loadLoreBooks(id)` [LLA] → table | 현재 활성화 판정된 로어북을 프롬프트 형태(`{data, role}` 배열)로 로드 (async 래퍼). 내부 JS 함수엔 토큰 예약분 `reserve` 인자가 있으나 Lua 래퍼는 전달하지 않는다 |

### UI·알림
| 함수 | 설명 |
|---|---|
| `alertNormal(id, msg)` / `alertError(id, msg)` | 알림 표시 |
| `alertInput(id, msg)` [async] → string | 입력 프롬프트 |
| `alertSelect(id, {옵션들})` [async] → string | 선택 프롬프트 |
| `alertConfirm(id, msg)` [async] → boolean | 확인 대화상자 |
| `reloadDisplay(id)` | 전체 GUI 리렌더 |
| `reloadChat(id, index)` | 특정 메시지만 리렌더 |

### 유틸
| 함수 | 설명 |
|---|---|
| `cbs(text)` → string | 텍스트를 CBS 파서로 처리 (id 불필요) |
| `log(value)` | 콘솔 로그 (json 인코딩되어 출력) |
| `getTokens(id, text)` [async] → number | 토큰 수 계산 |
| `sleep(id, ms)` [async] | 대기 |
| `hash(id, text)` [async] → string | SHA-256 hex |

### LLA (low level access) 전용
| 함수 | 설명 |
|---|---|
| `LLM(id, prompt, useMultimodal?, options?)` → `{success, result}` | 메인 모델 호출. prompt = `{{role='user'|'system'|'assistant'/'char'/'bot', content='...'}, ...}`. options에 `{streaming=true}` 가능. useMultimodal=true면 content 내 `{{inlay::...}}` 태그를 이미지로 첨부 |
| `axLLM(id, prompt, ...)` | 보조(auxiliary) 모델로 동일 동작 |
| `simpleLLM(id, prompt문자열)` [async] → `{success, result}` | 단일 유저 메시지 헬퍼 |
| `similarity(id, source, {문장들})` [async] → table | 임베딩 유사도 정렬 결과 |
| `request(id, url)` [async] → JSON 문자열 | HTTPS GET 전용. **URL 최대 120자, 분당 5회**, risuai.net 계열 차단. 결과는 `json.decode(...)` 후 `{status, data}` |
| `generateImage(id, prompt, negativePrompt?)` [async] → string | 이미지 생성 후 `{{inlay::id}}` 반환 |

## 3. 실전 예제

### 스탯 시스템 + 버튼
```lua
-- 첫 로드 시 초기화
function onStart(triggerId)
    if getChatVar(triggerId, 'hp') == 'null' then
        setChatVar(triggerId, 'hp', '100')
    end
end

-- {{button::공격::attack}} 클릭 시 (manual 트리거 이름 = 함수 이름)
function attack(triggerId)
    local hp = tonumber(getChatVar(triggerId, 'hp')) or 0
    local dmg = math.random(5, 15)
    setChatVar(triggerId, 'hp', tostring(hp - dmg))
    addChat(triggerId, 'char', '공격! ' .. dmg .. ' 피해를 입혔다.')
    reloadDisplay(triggerId)
end
```

### 출력 후처리 (AI 응답에서 태그 추출 → 변수 저장)
```lua
function onOutput(triggerId)
    local msg = getCharacterLastMessage(triggerId)
    local mood = msg:match('<mood>(.-)</mood>')
    if mood then
        setChatVar(triggerId, 'mood', mood)
        -- 태그를 화면에서 제거
        local idx = getChatLength(triggerId) - 1
        setChat(triggerId, idx, (msg:gsub('<mood>.-</mood>', '')))
    end
end
```

### 요청 직전 프롬프트 수정
```lua
listenEdit('editRequest', function(triggerId, messages, meta)
    table.insert(messages, 1, {
        role = 'system',
        data = '현재 HP: ' .. getChatVar(triggerId, 'hp')
    })
    return messages
end)
```

## 4. 흔한 함정

- **triggerId 누락**: 권한 검증에 쓰이므로 빼먹으면 API가 조용히 아무것도 안 한다 (에러도 없음).
- **모드 간 Lua 전역 공유 불가**: onInput에서 만든 전역 테이블은 onOutput에서 안 보인다. `setState` 사용.
- **onStart는 매 전송마다 실행된다** ("채팅 시작 시 1회"가 아님). 1회성 초기화는
  `if getChatVar(id, 'init') == 'null'` 가드를 넣어라.
- **onInput에서는 전송 취소 불가 + 이번 입력 텍스트 접근 불가** (메시지 추가 전에 실행됨).
  입력 텍스트를 다루려면 `listenEdit('editInput')`, 취소하려면 `onStart`를 써라.
- **그룹 채팅에서는 캐릭터의 트리거 스크립트가 실행되지 않는다** (모듈 트리거만 실행됨).
- **listenEdit에서 LLA API 사용 불가**: `LLM()` 등은 nil을 반환한다. LLA가 필요하면 onOutput 등에서 처리.
- **editDisplay에서의 setChatVar는 영구 저장되지 않는다** (표시용 임시 변수로만 반영).
- `:await()`를 코루틴 밖에서 호출하면 에러. LLM 등 async 래퍼를 쓰는 함수는 `async(function...)`로 감싸라.
- 콜백에서 에러가 나면 콘솔에만 찍히고 파이프라인은 계속 진행된다 — 디버깅 시 브라우저 콘솔 확인.
- Lua 문자열 패턴은 정규식이 아니다 (`%d`, `.-` 등 Lua 패턴 문법).
- Python(pyodide) 엔진도 코드상 존재하지만 현재 UI에서 선택 불가 — Lua만 사용하라.
