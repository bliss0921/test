# 계층 간 상호작용 (CBS · Lua · 트리거 · 정규식 · 플러그인)

복잡한 스크립트를 설계할 때 가장 중요한 문서. 각 계층이 언제 실행되고 무엇을 공유하는지 정리한다.

## 1. 변수 공유 매트릭스

**채팅 변수는 단일 저장소** `chat.scriptstate['$'+key]` (채팅별, 세이브에 영구 저장):

| 접근자 | 읽기 | 쓰기 |
|---|---|---|
| CBS | `{{getvar::k}}` | `{{setvar::k::v}}` (runVar 패스에서만 실행) |
| Lua | `getChatVar(id, 'k')` | `setChatVar(id, 'k', v)` |
| Lua (구조화) | `getState(id, 'k')` → `$__k`에 JSON | `setState(id, 'k', table)` |
| 트리거 V1/V2 | var 조건, 변수 블록 | `setvar` 효과 |
| 플러그인 | `getChatFromIndex()`로 chat.scriptstate 직접 접근 | 동일 + `setChatToIndex()` |

- 값은 항상 문자열, 미설정 시 `'null'` 문자열. 폴백 순서: 캐릭터 Default Variables →
  전역 설정의 템플릿 기본 변수(`templateDefaultVariables`) → `'null'`.
- **전역 변수** `db.globalChatVariables`: CBS `{{getglobalvar::k}}`, Lua `getGlobalVar(id,'k')` — 읽기 전용.
  모듈 토글 UI가 `toggle_<이름>` 키에 쓴다 (CBS `{{#when::toggle::이름}}`으로 검사).
  - **채팅 로컬 오버레이**: 채팅별로 `chat.GLGlobalVariables`(키-값)가 있으면 읽기에서 전역 값보다
    우선된다. 토글 사이드바의 "local toggles" 체크(`chat.useLocallySetGlobalVariables`)를 켜면
    그 채팅에서의 토글 조작이 전역 대신 이 오버레이에 저장된다 — 같은 토글이 채팅마다 다른 값을
    가질 수 있으므로 "전역 = 모든 채팅 공유"를 전제로 한 스크립트는 주의.
- **표시(display/editDisplay) 컨텍스트에서의 변수 쓰기는 임시 저장소로만 가고 영구 반영되지 않는다.**
  영구 상태 변경은 input/output/start/manual 시점에만 하라.

## 2. 채팅 1턴의 전체 파이프라인

유저가 메시지를 보내고 응답이 표시되기까지, 스크립트가 개입하는 지점 순서:

```
[유저 입력]
 1. input 트리거 (Lua onInput / V1·V2 효과)   ← 주의: 새 유저 메시지가 채팅에 추가되기 "전"에 실행됨
 2. 입력 텍스트 처리: Lua listenEdit('editInput') → 플러그인 scriptHandler('input')
    → CBS 파싱 → 정규식 스크립트(editinput)
 3. 처리된 유저 메시지를 채팅에 추가 → sendChat 진입
[전송 준비]
 4. ★ runVar 패스: 저장된 메시지 전체를 runVar=true로 파싱해 원본을 덮어씀
    — 메시지 안의 {{setvar}}가 여기서 실행·소거되고, 다른 CBS도 평가되어 고정됨
[프롬프트 빌드]
 5. 로어북 활성화 판정 (키 매칭, 내용 CBS 파싱 — runVar 아님)
 6. 프롬프트 템플릿·설명 등의 CBS 파싱 (runVar 아님 — 여기의 setvar는 실행되지 않음)
    + 채팅 메시지 수집 (greeting도 이때 CBS+editprocess로 포함됨)
 7. start 트리거 (Lua onStart / V1·V2 효과) ← "On chat Send": 매 전송마다 여기서 실행.
    stop하면 전송 취소 (취소 가능한 유일한 지점)
 8. 정규식 스크립트(editprocess) — 요청에 들어갈 각 메시지에.
    char 메시지의 {{inlay}}/{{inlayed}} 태그는 제거되고 {{inlayeddata}}만 멀티모달로 첨부됨
 9. Lua listenEdit('editRequest')          ← 최종 메시지 배열 수정
10. request 트리거 (V2 RequestState 블록만)
11. 플러그인 replacer('beforeRequest') → bodyInterceptor → [HTTP 요청]
[응답 수신]
12. 플러그인 replacer('afterRequest')
13. Lua listenEdit('editOutput') + 플러그인 scriptHandler('output') + 정규식(editoutput) → 채팅에 저장
14. ★ runVar 패스 재실행 — AI 응답 속 {{setvar}}가 여기서 실행·소거됨
15. output 트리거 (Lua onOutput / V1·V2 효과) ← 14에서 갱신된 변수 값을 봄.
    sendAIprompt 효과가 있으면 이후 sendChat 전체가 재실행됨 (자동 재전송)
16. 플러그인 v3 chatListener('output') — 15까지 끝나고 인레이 처리된 커밋 상태의 스냅샷을 받음
    (읽기 전용 알림. 순차 await되므로 느린 리스너는 채팅 흐름을 지연시킴 — plugins.md)
[화면 표시 — 메시지마다, 리렌더마다 반복]
17. Lua listenEdit('editDisplay') → display 트리거 → 플러그인 scriptHandler('display')
    → CBS 파싱(displaying=true) → 정규식(editdisplay) → 마크다운 → DOMPurify 새니타이즈
```

인사이트:
- **표시 단계(17)는 저장된 원본을 바꾸지 않는다.** 원본을 바꾸려면 output 시점(13~15)에서 수정.
- `{{setvar}}`는 runVar 패스(4, 14)에서만 실행된다. 유저 메시지의 setvar는 같은 요청의 프롬프트에
  반영되고(4가 5보다 먼저), AI 출력의 setvar는 output 트리거가 보기 전에 반영된다(14가 15보다 먼저).
  상세는 [cbs.md](cbs.md) 2절.
- input 트리거(1)는 새 유저 메시지가 추가되기 전에 실행되므로, `getUserLastMessage`/`{{previoususerchat}}`는
  직전 턴의 유저 메시지를 반환한다. 이번에 입력된 텍스트는 input 트리거에서 접근할 수 없다.
  또한 이 시점의 stop은 무시된다 — 전송 취소는 start 트리거(7)에서만 가능하다.
- **리롤(응답 재생성)**: 마지막 캐릭터 메시지를 제거하고 4~15를 다시 돈다 (1~3의 input 처리는
  재실행 안 됨). 따라서 start 트리거·runVar·output 트리거의 부작용이 리롤마다 반복되고,
  프롬프트 속 비결정 CBS(`{{random}}` 등)도 다시 굴려진다.
- Lua/트리거의 변수 쓰기는 즉시 DB에 반영(write-through)되므로, 같은 사이클에서 뒤에 오는 단계
  (프롬프트 CBS, 다른 트리거)가 바로 새 값을 읽는다. 기존 값과 같은 값을 쓰면 쓰기 자체가 스킵된다
  (Lua `setChatVarChanged`/`setStateChanged`로 실제 변경 여부를 받을 수 있다).
- 같은 텍스트에 CBS가 여러 번 적용될 수 있다 (파이프라인 여러 지점에서 파싱). 이스케이프 함수들이
  PUA 문자를 쓰는 이유가 재파싱 방지다.

## 3. 상호 호출 경로

### 화면 → 스크립트 (버튼/클릭)
| HTML | 실행되는 것 |
|---|---|
| `{{button::라벨::이름}}` = `<button risu-trigger="이름">` | manual 트리거 실행. Lua면 **트리거 이름과 같은 전역 함수** 호출. `risu-id` 속성값은 `{{trigger_id}}`로 읽힘 |
| `<div risu-btn="데이터">` | Lua `onButtonClick(id, "데이터")` 호출 |
| `<div risu-ctrl="...">` | 내장 컨트롤 (bgm 등) |

### Lua → CBS
`cbs('{{getvar::hp}} / {{char}}')` — 임의 텍스트를 CBS 파서로 처리.

### CBS → 트리거
`{{button}}`으로 간접 실행만 가능. CBS 자체에서 트리거를 직접 실행하는 문법은 없다.

### 트리거 → 트리거
V1 `runtrigger` 효과 / V2 `v2RunTrigger` 블록으로 manual 트리거 호출 (재귀 10회 제한).

### 플러그인 → 전부
플러그인은 DB에 직접 접근하므로 캐릭터의 트리거/정규식/변수를 모두 읽고 쓸 수 있고,
`addRisuScriptHandler`로 정규식 스크립트와 같은 파이프라인에 참여한다.

## 4. 모듈 시스템

모듈(`RisuModule`)은 캐릭터에 종속되지 않는 재사용 묶음: **로어북 + 정규식 스크립트 + 트리거 +
에셋(+ 배경 임베딩, MCP 설정)**. `namespace`로 식별된다.

- 전역 활성화 또는 채팅별 활성화 가능. 활성 모듈의 로어북/정규식/트리거는 캐릭터 것과 **합쳐져** 실행된다.
- CBS: `{{moduleenabled::ns}}`, `{{moduleassetlist::ns}}`. 모듈 에셋은 `{{asset::이름}}`으로 캐릭터
  에셋과 동일하게 접근된다 (이름 충돌 주의).
- 모듈 트리거는 자체 `lowLevelAccess` 플래그를 가진다 (캐릭터 LLA와 별개).
- `customModuleToggle`: 모듈이 제공하는 토글 UI. 토글 상태는 전역 변수 `toggle_<이름>`으로 저장되어
  CBS `{{#when::toggle::이름}}` / `tis`/`tisnot` 연산자로 읽는다. 채팅에 "local toggles"가 켜져 있으면
  해당 채팅의 토글 상태는 `chat.GLGlobalVariables`에 채팅 로컬로 저장·조회된다 (1절 참고).
- "Apply module" 버튼은 모듈을 캐릭터에 **복사(병합)**하는 것이지 활성화가 아니다.

## 5. 권한 모델 요약

| 계층 | 게이트 |
|---|---|
| CBS | 제한 없음 (표시 HTML은 DOMPurify로 새니타이즈) |
| Lua/트리거 일반 API | 항상 허용 (editDisplay 제외) |
| Lua/트리거 LLA API (LLM, 네트워크, 이미지 생성, 유사도, 로어북 로드) | 캐릭터 "low level access" 체크 필요. 캐릭터 가져오기 시 경고 표시. **listenEdit 계열에서는 캐릭터·모듈 트리거 모두 LLA가 강제 해제됨** |
| Lua `request()` | LLA여도 HTTPS GET·120자·분당 5회 제한 |
| 플러그인 | 설치 자체가 신뢰 행위. db/mainDom/replacer/fetchLogs는 별도 동의 프롬프트 |

## 6. 설계 레시피

**"AI 응답에서 상태를 추출해 다음 프롬프트에 반영하고 화면에 게이지 표시"**
1. AI에게 로어북/시스템 프롬프트로 `<hp>숫자</hp>` 태그 출력 지시
2. Lua `onOutput`: 마지막 메시지에서 태그 파싱 → `setChatVar` → `setChat`으로 태그 제거
3. 프롬프트 반영: 로어북(alwaysActive)에 `현재 HP: {{getvar::hp}}` 또는 `listenEdit('editRequest')`
4. 화면 표시: 첫 메시지나 배경 임베딩에 CBS+HTML로 게이지 렌더 (`{{getvar::hp}}`)

**"유저 선택지 버튼"**
1. 표시 텍스트/정규식 editdisplay로 `{{button::선택1::choice1}}` 삽입
2. Lua에 `function choice1(id)` 정의 → `addChat(id, 'user', '...')` 후 필요 시 자동 전송은 불가하므로
   변수 설정 + `reloadDisplay(id)`로 이어가기 (자동 전송이 필요하면 트리거 V1 `sendAIprompt`(LLA) 사용)

**"메시지 표시만 바꾸고 원본 유지"** → 정규식 editdisplay 또는 Lua `listenEdit('editDisplay')`.
**"보내는 프롬프트에서만 제거"** → 정규식 editprocess 또는 `listenEdit('editRequest')`.
