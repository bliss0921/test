---
name: risuai-scripting
description: RisuAI의 CBS(Curly Braced Syntax), Lua 트리거 스크립팅, 플러그인(API v3), 정규식 스크립트, 트리거 시스템에 대한 레퍼런스. RisuAI용 캐릭터 카드 스크립트, 봇 로직, Lua 트리거, CBS 매크로, 플러그인을 작성·수정·디버깅할 때 사용. 소스 코드가 없는 환경에서도 이 문서만으로 작업할 수 있도록 API 명세와 내부 동작 인사이트를 포함.
---

# RisuAI 스크립팅 & 확장 가이드

RisuAI는 Svelte 5 + TypeScript 기반의 AI 채팅 앱으로, 4가지 확장 계층을 제공한다.
각 계층의 상세 명세는 `references/` 하위 문서를 읽어라.

| 계층 | 용도 | 실행 위치 | 상세 문서 |
|---|---|---|---|
| **CBS** `{{...}}` | 프롬프트/메시지 안의 매크로·조건·변수 치환 | 텍스트가 파싱되는 모든 곳 (프롬프트 빌드, 화면 표시, 로어북 등) | [references/cbs.md](references/cbs.md) |
| **트리거 & 정규식 스크립트** | 캐릭터/모듈 단위의 이벤트 로직, 텍스트 변환 | 채팅 파이프라인의 정해진 시점 | [references/triggers-and-regex.md](references/triggers-and-regex.md) |
| **Lua 스크립팅** | 트리거의 코드 형태. 채팅 조작, 변수, LLM 호출 등 | wasmoon(Lua 5.4) 엔진, 트리거 시점에 실행 | [references/lua.md](references/lua.md) |
| **플러그인 (API v3)** | 앱 전체 기능 확장 (UI, 프로바이더, MCP, 요청 가로채기) | 샌드박스 iframe, 항상 로드됨 | [references/plugins.md](references/plugins.md) |

계층 간 상호작용(변수 공유, 실행 순서, 상호 호출)은 **[references/interop.md](references/interop.md)** 참고.
복잡한 스크립트를 작성할 때는 interop.md를 먼저 읽는 것을 권장한다.
캐릭터·채팅·메시지·로어북·트리거·모듈의 **JSON 필드 구조는 [references/schemas.md](references/schemas.md)**
참고 (카드 JSON 직접 편집, Lua/플러그인에서 객체를 다룰 때 필요).

## 어떤 계층을 쓸지 고르는 기준

- **프롬프트/첫 메시지/로어북 안에서 조건 분기·변수 표시** → CBS만으로 충분
- **메시지 텍스트의 패턴 치환 (표시용 HTML 변환 등)** → 정규식 스크립트
- **상태 머신, 스탯 관리, 조건부 채팅 조작, 버튼 인터랙션** → Lua 트리거 (+ CBS로 표시)
- **LLM 추가 호출, 네트워크 요청, 이미지 생성** → Lua 트리거 + 캐릭터의 low level access 활성화
- **앱 UI 변경, 커스텀 AI 프로바이더, 요청 본문 수정, 모든 캐릭터에 적용되는 기능** → 플러그인
- **캐릭터에 종속되지 않는 재사용 묶음 (로어북+정규식+트리거+에셋)** → 모듈

## 반드시 알아야 할 핵심 사실 (요약)

1. **변수는 한 저장소를 공유한다.** CBS `{{getvar::x}}`, Lua `getChatVar(triggerId, 'x')`, 트리거 V2의 변수는
   전부 현재 채팅의 `chat.scriptstate['$'+key]`를 읽고 쓴다. 값은 항상 **문자열**이고, 없으면 문자열 `'null'`이
   반환된다 (빈 문자열이 아님!). 폴백: 캐릭터 Default Variables → 전역 설정의 템플릿 기본 변수.
2. **CBS의 참(truthy)은 정확히 `'1'` 또는 `'true'` 문자열뿐이다.** 비교 함수들은 `'1'`/`'0'`을 반환한다.
3. **Lua 엔진은 트리거 모드별로 분리**된다. `onInput`이 실행되는 엔진과 `onOutput`이 실행되는 엔진은 서로 다른
   인스턴스이므로, Lua 전역 변수로 모드 간 상태 공유가 안 된다. 상태 공유는 반드시 chat 변수(`setState`/`setChatVar`)로.
4. **Lua API 함수의 첫 인자는 항상 `triggerId`**(콜백이 받은 접근 키)다. 이 키로 권한(safe/lowLevel)이 검증된다.
5. **CBS는 안쪽 `{{}}`부터 평가**되며, falsy한 `{{#when}}` 블록 내부도 일단 평가된 뒤 버려진다
   (부작용 있는 CBS를 조건 블록 안에 넣을 때 주의).
6. 플러그인 API v3는 **모든 메서드가 async**이며 `Risuai` 전역 객체를 통해 접근한다.
   2.x는 신규 설치가 차단됐다 (기설치된 2.1 플러그인만 계속 로드됨).
7. 처리 파이프라인 순서(한 메시지 기준): Lua edit 트리거 → display 트리거 → 플러그인 v2 핸들러 → CBS 파싱 →
   정규식 스크립트 → (표시 시) 마크다운/새니타이즈. 상세는 interop.md.
8. **`{{setvar}}`는 채팅 메시지 안에 있을 때만, 전송 시작 직후와 응답 저장 직후 두 시점(runVar 패스)에
   실행되며 실행되면서 태그가 소거된다.** greeting·로어북·표시 렌더에서는 실행되지 않는다 (cbs.md 2절).
9. 트리거 `start`(Lua `onStart`)는 이름과 달리 **매 전송마다** 실행되며, 전송을 취소할 수 있는 유일한
   지점이다. `input`(`onInput`)은 새 유저 메시지가 추가되기 **전에** 실행되고 취소가 불가능하다.

## 디버깅 방법

- **Lua**: `log(값)`이 브라우저 개발자 도구 콘솔에 출력된다 (테이블도 JSON 디코드되어 표시).
  콜백에서 난 에러는 **콘솔에만 `console.error`로 찍히고 파이프라인은 계속 진행**되므로,
  "조용히 아무 일도 안 일어나면" 콘솔부터 확인하라. 엔진이 코드를 (재)로드할 때
  `Running Lua code:` 로그가 찍히므로 코드가 로드됐는지도 콘솔로 확인 가능.
  UI로 확인하려면 `alertNormal(id, msg)` 사용.
- **CBS**: 함수명이 틀리면 에러 없이 `{{...}}`가 리터럴로 그대로 남는다 — 출력에 중괄호가 보이면
  오타·미지원 함수 신호다. 변수 상태는 표시 텍스트에 `{{getvar::이름}}`을 임시로 넣어 확인.
- **트리거 V2**: `v2ConsoleLog` 블록으로 변수/값을 콘솔에 출력.
- **플러그인**: 샌드박스 iframe도 같은 브라우저 devtools 콘솔에 출력된다. `console.log` 사용.
  요청/응답 확인은 `getFetchLogs()`(fetchLogs 권한). 개발 중에는 "Import plugin with hot reload"로
  가져오면 파일 저장 시 자동 재로드된다.

## 소스 코드 위치 (소스가 있는 환경에서 검증할 때)

- CBS 함수 정의: `src/ts/cbs.ts` / 파서 코어: `src/ts/parser/parser.svelte.ts`
- 변수 저장: `src/ts/parser/chatVar.svelte.ts`
- 데이터 타입 정의(schemas.md의 원본): `src/ts/storage/database.svelte.ts`, `src/ts/process/modules.ts`
- Lua 엔진·API: `src/ts/process/scriptings.ts`
- 트리거 실행: `src/ts/process/triggers.ts` / 정규식 스크립트: `src/ts/process/scripts.ts`
- 플러그인 v3: `src/ts/plugins/apiV3/` (타입 정의 `risuai.d.ts`), 가이드 `plugins.md`(리포 루트)
