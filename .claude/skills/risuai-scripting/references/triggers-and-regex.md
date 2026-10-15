# 트리거 시스템 & 정규식 스크립트 레퍼런스

구현: `src/ts/process/triggers.ts`(트리거), `src/ts/process/scripts.ts`(정규식 스크립트).
캐릭터 설정 → Scripts 탭, 또는 모듈에서 정의한다. Lua 코드형 트리거는 [lua.md](lua.md) 참고.

## 1. 트리거 스크립트

트리거는 `{타입, 조건(conditions), 효과(effects)}`의 목록이다. 캐릭터 트리거 + 활성 모듈 트리거가 합쳐져
순서대로 실행된다.

### 트리거 타입 (정확한 실행 시점)

| 타입 | UI 라벨 | 정확한 시점 |
|---|---|---|
| `start` | "On chat Send" | **매 전송마다** `sendChat` 내부, 프롬프트 빌드 도중(채팅 메시지 수집 후, editprocess 적용 전)에 실행. 이름과 달리 "채팅 시작 시" 1회가 아니다. **전송을 취소(stop)할 수 있는 유일한 트리거 지점** |
| `input` | "On user's output" (실제 UI 라벨이 이렇게 표기됨 — 오타 아님) | 유저가 전송 버튼을 누른 직후, **새 유저 메시지가 채팅에 추가되기 전**. 이 시점의 stop/stopSending은 **무시된다** (전송 취소 불가 — 취소하려면 start 타입 사용) |
| `output` | "On character's output" | AI 응답이 채팅에 저장되고 runVar 패스가 끝난 후 |
| `manual` | "Manual trigger only" | `{{button::라벨::이름}}` 또는 `risu-trigger="이름"` 요소 클릭 시 (트리거의 comment=이름 매칭) |
| `display` | — | 메시지 표시 렌더링마다. **V2 safe 블록 + `v2Get/SetDisplayState`만 실행됨** (Lua·V1 효과 스킵). 변수 쓰기는 임시 |
| `request` | — | 모델 요청 직전. **V2 safe 블록 + `v2Get/SetRequestState*`만 실행됨** (Lua·V1 효과 스킵) |

- Lua 효과(`triggerlua`)인 트리거는 타입 필터를 무시하고 모든 시점에 로드된다 (코드의 콜백이 시점 결정).
  단 display/request 모드에서는 위 allowlist 때문에 Lua 효과 자체가 스킵되므로, 표시/요청 수정 Lua는
  `listenEdit('editDisplay')`/`listenEdit('editRequest')`로만 가능하다.
- V2 safe 블록 = 변수/문자열/배열 조작, if/loop, `v2Random`, `v2ExtractRegex`, `v2Calculate` 등 부작용 없는
  연산 블록들. 채팅 조작·LLM 호출 블록은 display/request에서 실행되지 않는다.
- `runtrigger` 효과로 다른 manual 트리거를 호출할 수 있다. 재귀 제한 10회 (LLA면 무제한).
- manual 트리거 클릭 요소에 `risu-id` 속성이 있으면 실행 중 `{{trigger_id}}`로 읽을 수 있다.

### 조건 (conditions)

모두 통과해야 효과가 실행된다. 값 필드에는 CBS를 쓸 수 있다.

| 조건 | 내용 |
|---|---|
| `var` | 채팅 변수를 연산자(`=`, `!=`, `>`, `<`, `>=`, `<=`, `null`, `true`)로 비교 |
| `value` | 임의 값(CBS 평가 후)을 비교 |
| `chatindex` | 메시지 수를 비교 |
| `exists` | 최근 N개(depth) 메시지에 텍스트 존재 여부. `strict`(단어 일치)/`loose`(대소문자 무시 포함)/`regex` |

### 효과 (effects)

세 가지 형태가 있다 (JSON 필드 구조는 [schemas.md](schemas.md) 참고):
1. **Lua 코드** (`triggerlua`) — 권장. [lua.md](lua.md) 참고. (`triggercode` 타입의 JS 코드형도
   레거시로 존재하지만 신규 사용은 권장하지 않는다)
2. **V1 효과** — 단순 목록형: `setvar`(=, +=, -=, *=, /=), `cutchat`, `modifychat`, `systemprompt`(위치:
   start/historyend/promptend에 프롬프트 추가), `impersonate`(user/char 메시지 추가), `command`, `stop`(전송 중단),
   `runtrigger`, `extractRegex`, [LLA] `showAlert`, `runLLM`, `runAxLLM`, `checkSimilarity`, `runImgGen`, `sendAIprompt`
3. **V2 효과** — GUI 블록 코딩 방식. indent 기반 스코프로 `v2If`/`v2Else`/`v2Loop`/`v2LoopNTimes`/`v2BreakLoop`
   등 제어 구조와 약 115종의 블록(문자열/배열/딕셔너리 변수 조작, 로어북 CRUD, 채팅 조작, 요청 상태 편집,
   `v2RunLLM`, `v2GetAlertInput`, `v2Wait`, `v2Tokenize`, `v2Calculate` 등)을 제공한다.
   - V2 변수 블록의 값 필드는 대부분 `valueType: 'var'|'value'` 선택지가 있어 변수 참조/리터럴을 구분한다.
   - `v2DeclareLocalVar`로 선언한 로컬 변수는 indent 스코프를 따르며 채팅 변수보다 우선 조회된다.
   - `v2GetDisplayState`/`v2SetDisplayState`: display 모드에서 표시 텍스트를 읽고/쓴다.
   - `v2GetRequestState*`/`v2SetRequestState*`: request 모드에서 모델로 보낼 메시지 배열을 읽고/쓴다.

#### display/request 모드 전용 블록 명세 (이 모드는 V2로만 작업 가능하므로 구조를 기재)

모든 V2 블록 공통 필드: `type`(블록명), `indent`(중첩 깊이, 0부터). `*Type: 'var'|'value'` 필드는
짝이 되는 값 필드를 변수 이름으로 해석할지 리터럴로 해석할지 결정한다.

```typescript
// display 모드 — 표시 텍스트 읽기/쓰기
{ type: 'v2GetDisplayState', outputVar: string, indent: number }   // 표시 텍스트 → 변수
{ type: 'v2SetDisplayState', value: string, valueType: 'var'|'value', indent: number }

// request 모드 — 모델로 보낼 메시지 배열 읽기/쓰기 (index는 메시지 위치)
{ type: 'v2GetRequestState',       outputVar: string, index: string, indexType: 'var'|'value', indent: number }
{ type: 'v2GetRequestStateRole',   outputVar: string, index: string, indexType: 'var'|'value', indent: number }
{ type: 'v2SetRequestState',       value: string, valueType: 'var'|'value', index: string, indexType: 'var'|'value', indent: number }
{ type: 'v2SetRequestStateRole',   value: string, valueType: 'var'|'value', index: string, indexType: 'var'|'value', indent: number }
{ type: 'v2GetRequestStateLength', outputVar: string, indent: number }
```

### 실행 의미론 (중요)

- 트리거 실행은 **캐릭터·채팅의 복사본** 위에서 이루어지고, 종료 시 결과가 반영된다.
  단 `display` 모드는 복사 없이 임시로 동작하며 변수 쓰기는 tempVars로만 간다.
- `setvar`/`getvar`는 CBS·Lua와 동일한 `chat.scriptstate` 저장소를 사용한다. 미설정 변수는 `'null'`.
- `systemprompt` 효과로 추가된 프롬프트는 start/input/output 트리거 결과로 수집되어 요청 시 삽입된다.
- `stop` / Lua `stopChat` / 콜백 `return false`: **start 트리거에서만 전송이 실제로 취소된다.**
  input 트리거의 stopSending은 호출부에서 확인하지 않아 무시된다.
- `sendAIprompt` 효과(LLA): output 트리거까지 끝난 뒤 **sendChat 전체가 다시 실행**된다 (자동 재전송 —
  start 트리거·runVar 패스·프롬프트 빌드가 전부 다시 돈다. 무한 재전송 루프 주의).
- **리롤(reroll)의 동작**: 마지막 캐릭터 메시지(들)를 pop한 뒤 sendChat을 다시 호출한다.
  → input 트리거·editinput은 재실행되지 **않고**, start 트리거·runVar 패스·프롬프트 빌드·output 트리거는
  다시 실행된다. (스와이프로 캐시된 리롤을 넘기는 것은 파이프라인 없이 메시지 데이터만 교체)
- LLA 필요 효과는 캐릭터의 "low level access" 체크박스(가져오기 시 경고 표시됨)가 켜져야 동작한다.

## 2. 정규식 스크립트 (customscript)

메시지 텍스트에 정규식 치환을 적용한다. 캐릭터 스크립트 + 프리셋 정규식(`presetRegex`) + 모듈 정규식이
순서대로 실행된다.

### 필드

| 필드 | 의미 |
|---|---|
| type | 적용 시점: `editinput`(전송되는 유저 입력) / `editoutput`(수신된 AI 출력) / `editprocess`(요청 직전 프롬프트 각 메시지) / `editdisplay`(화면 표시 전용) |
| in | 찾을 정규식 (JS 정규식 문법) |
| out | 치환 문자열. `$1` 등 캡처 그룹, `$&` 전체 매치, `$n`은 개행으로 치환됨. CBS 사용 가능 (치환 후 파싱됨) |
| flag | 정규식 플래그 (`ableFlag` 활성 시). 기본 `g`. 허용: `dgimsuvy` |

### 플래그 메타 액션 `<...>`

flag 문자열 안에 `<액션1, 액션2, order N>` 형태로 부가 동작을 지정할 수 있다:

| 액션 | 동작 |
|---|---|
| `order N` | 실행 우선순위 (클수록 먼저) |
| `cbs` | in(정규식 패턴)을 먼저 CBS 파싱 |
| `move_top` / `move_bottom` | 매치를 제거하고 out을 텍스트 맨 위/아래로 이동 |
| `inject` | 매치를 원본 메시지에 저장하고 표시에서 제거 |
| `repeat_back` | 매치가 없으면 같은 역할의 직전 메시지에서 매치를 가져와 덧붙임 (`end`/`start`/`end_nl`/`start_nl` 인자) |
| `no_end_nl` | out이 `>`로 끝날 때 자동 개행 추가를 막음 |

out이 `@@emo 이름`으로 시작하면 매치 시 해당 감정 이미지를 표시한다. (`@@inject`, `@@move_top`,
`@@move_bottom`, `@@repeat_back` 접두사는 위 메타 액션의 구식 표기)

### 처리 순서 (한 텍스트 기준, processScriptFull)

```
Lua listenEdit(editInput/editOutput/editDisplay) 
→ (editdisplay일 때) display 트리거 
→ 플러그인 v2 스크립트 핸들러 
→ CBS 파싱 (risuChatParser)
→ 정규식 스크립트 (order 순)
→ (설정 시) 다이나믹 에셋 매칭 (임베딩 유사도로 {{asset::...}} 이름 교정)
```

결과는 해시 기반으로 캐시된다 (동일 입력 반복 처리 방지) — 비결정적 CBS(random 등)가 정규식 out에 있으면
캐시로 인해 같은 값이 재사용될 수 있다.

## 3. 어느 도구를 쓸까

- 텍스트 모양 변환(태그→HTML, 검열, 말투 교정): **정규식 스크립트**
- 상태·조건·분기·채팅 구조 조작: **Lua 트리거** (V2 블록은 GUI 사용자용; 코드로 작성한다면 Lua가 항상 우선)
- 프롬프트에 동적 텍스트 삽입: 로어북 + CBS, 또는 트리거 `systemprompt` / Lua `listenEdit('editRequest')`
