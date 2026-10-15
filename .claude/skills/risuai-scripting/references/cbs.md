# CBS (Curly Braced Syntax) 레퍼런스

CBS는 RisuAI의 텍스트 매크로 언어다. `{{함수명::인자1::인자2}}` 형태로 쓰며, 프롬프트·첫 메시지·로어북·
작가의 노트·정규식 스크립트 출력·화면 표시 텍스트 등 텍스트가 파싱되는 거의 모든 곳에서 동작한다.
구현: `src/ts/cbs.ts`(함수 정의), `src/ts/parser/parser.svelte.ts`(파서 코어 `risuChatParser`).

## 1. 기본 문법과 파서 동작 원리

### 문법
```
{{char}}                     ← 인자 없는 함수
{{getvar::score}}            ← 인자는 :: 로 구분
{{? 1 + 2 * 3}}              ← 수식 전용 단축 문법 (결과: 7)
{{// 주석}}                  ← 주석 (출력 없음)
```

### 파서가 실제로 하는 일 (중요 인사이트)

1. **스택 기반, 안쪽 우선 평가.** `{{`를 만나면 스택에 새 버퍼를 쌓고, `}}`를 만나면 그 버퍼 내용을 평가한다.
   따라서 `{{upper::{{getvar::name}}}}`은 `getvar`가 먼저 평가된 결과가 `upper`의 인자가 된다.
   인자가 함수에 도달하는 시점엔 이미 내부 CBS가 모두 문자열로 치환되어 있다.
2. **함수명 정규화.** 함수명(첫 `::` 앞부분)은 소문자화 후 공백/`_`/`-`가 제거된다.
   → `{{Get_Var::x}}` == `{{getvar::x}}`. 별칭(alias)도 다수 존재한다.
3. **`:` 하나도 인자 구분자가 될 수 있다.** 첫 콜론 다음 문자가 `:`가 아니면 `:` 단일 문자로 분리한다.
   `{{getvar:x}}`도 동작. 단, 값에 콜론이 들어가면 깨지므로 항상 `::` 사용을 권장.
4. **모르는 함수는 그대로 남는다.** 매칭 실패한 `{{...}}`는 리터럴 텍스트로 출력된다.
5. **`<user>`, `<char>`, `<bot>`** 은 파싱 전에 `{{user}}`, `{{char}}`, `{{bot}}`으로 변환된다.
6. **재귀/호출 깊이 제한 20.** (`callStack`) 초과 시 `ERROR: Call stack limit reached` 문자열이 출력된다.
7. **파싱 컨텍스트 플래그**에 따라 일부 함수의 동작이 달라진다:
   - `displaying` (화면 표시 렌더 시 true): `{{file}}`, `{{comment}}` 등이 표시용 HTML을 출력
   - `runVar` (변수 실행 패스): `{{setvar}}`, `{{addvar}}`, `{{setdefaultvar}}`는 runVar=true일 때만 실제로 저장.
     그 외 컨텍스트에서는 치환되지 않고 리터럴 `{{setvar::...}}`로 남는다. 정확한 실행 시점은 2절 참고.
     (rmVar 플래그도 존재하지만 현재 코드에서 켜는 곳이 없다)
   - `tokenizeAccurate` (토큰 수 계산): 시간 함수 등이 고정값 반환
   - `consistantChar`: `{{char}}`→`botname`, `{{user}}`→`username` 고정 문자열

## 2. 변수 시스템

| 종류 | 읽기 | 쓰기 | 저장 위치 / 수명 |
|---|---|---|---|
| **채팅 변수** | `{{getvar::k}}` | `{{setvar::k::v}}` `{{addvar::k::n}}` `{{setdefaultvar::k::v}}` | `chat.scriptstate['$'+k]`. 채팅별 영구 저장. Lua/트리거와 공유 |
| **임시 변수** | `{{tempvar::k}}` | `{{settempvar::k::v}}` | 현재 파싱 1회 동안만 유효 |
| **전역 변수** | `{{getglobalvar::k}}` | (CBS로는 쓰기 불가) | `db.globalChatVariables`. 기본은 모든 채팅 공유. 토글은 `toggle_<이름>` 키. 단, 채팅에 로컬 오버레이(`chat.GLGlobalVariables`)가 있으면 읽기에서 그 값이 우선됨 — `#when`의 `toggle`/`tis`/`tisnot`도 동일 (interop.md 1절) |
| **기본값** | — | 캐릭터 설정의 Default Variables, 전역 설정의 템플릿 기본 변수 | 채팅 변수 미설정 시 폴백 (캐릭터 → 전역 템플릿 순) |

핵심 규칙:
- 모든 값은 **문자열**. 존재하지 않는 변수는 **문자열 `'null'`** 을 반환한다. 존재 검사는
  `{{#when::{{getvar::k}}::isnot::null}}` 패턴을 쓴다.
- `{{addvar}}`는 숫자로 변환해 더한다 (NaN 주의).
- `{{return::값}}`: 즉시 파싱을 중단하고 값을 전체 결과로 반환 (`#func`와 조합해 함수 반환값으로 사용).

### `{{setvar}}`가 실제로 실행되는 정확한 시점 (중요)

코드 전체에서 runVar=true로 파싱하는 곳은 **단 한 곳**, `sendChat`의 `runCurrentChatFunction`
(`src/ts/process/index.svelte.ts`)이다. 이 함수는 **저장된 채팅 메시지(chat.message) 전체를 파싱해서
그 결과로 메시지 원본을 덮어쓴다.** 전송 사이클마다 정확히 두 시점에 호출된다:

1. **전송 시작 직후, 프롬프트 빌드 전** — 유저 메시지(editinput 처리 후 저장된 상태)에 든 `{{setvar}}`는
   여기서 실행된다. 따라서 **같은 요청의 프롬프트에서 `{{getvar}}`가 이미 갱신된 값을 본다.**
2. **AI 응답이 채팅에 저장된 직후(editoutput 처리 후), output 트리거 실행 전** — AI가 출력한
   `{{setvar}}`는 여기서 실행된다. 따라서 **Lua `onOutput` / output 트리거는 이미 갱신된 값을 본다.**

이 패스의 부수 효과:
- **태그가 소거된다.** setvar는 빈 문자열을 반환하므로, 실행되면서 저장된 메시지에서 사라진다 (1회 실행 보장).
- **메시지 안의 다른 CBS도 이 시점에 전부 평가되어 고정(flatten)된다.** 저장된 메시지에 `{{getvar::hp}}`나
  `{{random}}`이 있었다면 이 시점의 값으로 치환된 문자열이 영구 저장된다.
- **첫 메시지(greeting)는 chat.message에 포함되지 않으므로** greeting 안의 `{{setvar}}`/`{{setdefaultvar}}`는
  이 패스로 실행되지 않는다 (표시에서는 리터럴로 남음). 초기값은 **캐릭터 Default Variables** 또는
  트리거 `onStart`에서 설정하라.
- 로어북·프롬프트 템플릿·설명 등 프롬프트 빌드 중의 파싱과 화면 표시 렌더는 runVar가 아니므로,
  거기에 적힌 `{{setvar}}`는 **실행되지 않고 리터럴 텍스트로 남는다** (프롬프트에 그대로 들어갈 수 있음).

## 3. 블록 문법

### `{{#when}}` — 조건 분기 (현행 표준. `#if`, `#if_pure`는 deprecated)

```
{{#when 조건}}...{{/when}}                          ← 공백 형태 (연산자 없이)
{{#when::조건}}참일 때{{:else}}거짓일 때{{/when}}
{{#when::A::is::B}}...{{/when}}
{{#when::keep::not::조건}}...{{/when}}              ← 연산자 조합 가능
```

조건의 참 = 정확히 `'1'` 또는 `'true'`.

| 연산자 | 의미 |
|---|---|
| `A::and::B` / `A::or::B` | 논리 AND / OR |
| `A::is::B` / `A::isnot::B` | 문자열 동등 / 부등 |
| `A::>::B`, `<`, `>=`, `<=` | 숫자 비교 (parseFloat) |
| `not::A` | 부정 |
| `var::이름` | 채팅 변수가 truthy인지 |
| `이름::vis::값` / `visnot` | 채팅 변수 == 리터럴 값 (getvar 없이 바로 비교) |
| `toggle::이름` | 전역 토글(`toggle_이름`)이 truthy인지 |
| `이름::tis::값` / `tisnot` | 토글 == 리터럴 값 |
| `keep::...` | 블록 내부 공백/개행을 트리밍하지 않음 |
| `legacy::...` | 구 #if 방식의 공백 처리 (`:else` 사용 불가) |

- 연산자들은 **오른쪽부터** pop하며 평가된다. `{{#when::A::and::B::or::C}}`는 `A and (B or C)`처럼
  오른쪽 묶음이 먼저 계산된다. 복잡한 논리는 `{{and}}`/`{{or}}` 함수로 조건을 미리 만들어 넣는 것이 안전하다.
- `{{:else}}`는 여러 줄 블록에서는 **단독 줄**에 있어야 한다.
- **주의(부작용)**: 조건이 거짓이어도 블록 **내부의 CBS는 일단 평가된 후 버려진다**. `setvar` 같은 부작용
  함수를 `#when` 안에 넣으면 거짓 분기에서도 실행될 수 있다. 부작용을 조건부로 하려면 트리거/Lua를 쓰거나
  값 자체를 조건식으로 구성하라.

### `{{#each}}` — 배열 반복

```
{{#each {{makearray::a::b::c}} as item}}
- {{slot::item}}
{{/each}}
{{#each::keep 배열 as item}}...{{/each}}   ← 공백 유지
```
- 배열은 JSON 문자열 (`["a","b"]`). 요소가 객체면 `{{slot::item}}`은 JSON 문자열을 반환.
- 본문은 캡처 중에는 평가되지 않고(pure), `{{slot::item}}` 치환 후 스트림에 재삽입되어 **반복마다 재평가**된다.
  따라서 본문 안의 CBS 부작용은 반복 횟수만큼 실행된다.

### `{{#func}}` / `{{call}}` — 사용자 정의 함수

```
{{#func greet name}}Hello, {{arg::1}}!{{/func}}
{{call::greet::World}}          → Hello, World!
```
- `{{arg::N}}`: N번째 인자. **`{{arg::0}}`은 함수 이름 자신**이므로 실제 인자는 1부터.
- 함수 본문은 정의 시점엔 평가되지 않고 호출 시 파싱된다. `{{return}}`과 조합 가능.
- 함수 정의는 같은 파싱 패스(및 그 재귀 호출) 안에서만 유효하다.

### 기타 블록

| 블록 | 동작 |
|---|---|
| `{{#puredisplay}}...{{/puredisplay}}` | 내부를 CBS 처리 없이 그대로 표시 (`{{`가 `\{\{`로 이스케이프됨). `#pure`는 deprecated |
| `{{#escape}}...{{/escape}}` (`::keep` 가능) | 중괄호·괄호를 표시용 특수문자로 이스케이프 |
| `{{#code}}...{{/code}}` | 개행/탭 제거 + `\n`,`\uXXXX` 등 이스케이프 시퀀스 해석. 여러 줄로 작성한 로직을 한 줄 출력으로 압축할 때 사용 |

## 4. 이스케이프

CBS 구문 문자를 리터럴로 출력하려면 전용 함수를 쓴다. 이들은 사설 영역 유니코드(U+E9B8~)를 출력하고,
표시 단계에서 실제 문자로 되돌려진다 (재파싱 방지).

| 함수 | 출력 | | 함수 | 출력 |
|---|---|---|---|---|
| `{{bo}}` | `{{` | | `{{bc}}` | `}}` |
| `{{decbo}}` | `{` | | `{{decbc}}` | `}` |
| `{{(}}` (debo) | `(` | | `{{)}}` (debc) | `)` |
| `{{<}}` (deabo) | `<` | | `{{>}}` (deabc) | `>` |
| `{{:}}` (dec, displayescapedcolon) | `:` | | `{{;}}` | `;` |
| `{{br}}` | 개행 `\n` | | `{{cbr}}` / `{{cbr::N}}` | 리터럴 `\n` 문자열 (N회 반복) |

## 5. 함수 카탈로그

**소스에 등록된 전체 함수의 전수 목록이다** (내부 전용 `{{__}}` 제외). 여기에 없는 함수명은 존재하지
않으며, 매칭 실패한 `{{...}}`는 리터럴로 남는다 (1절 참고).
비교/논리 함수는 `'1'`/`'0'`을 반환한다. 배열/딕셔너리는 JSON 문자열로 주고받는다.

### 캐릭터·페르소나·프롬프트 데이터
| 함수 | 설명 |
|---|---|
| `{{char}}` (`bot`) | 캐릭터 닉네임 또는 이름 |
| `{{user}}` | 유저 이름 |
| `{{personality}}`, `{{description}}`, `{{scenario}}`, `{{exampledialogue}}` | 캐릭터 각 필드 (CBS 재파싱됨, 그룹이면 빈 문자열) |
| `{{persona}}` | 유저 페르소나 프롬프트 |
| `{{mainprompt}}`, `{{jb}}`, `{{globalnote}}` (`ujb`) | 메인 프롬프트 / 제일브레이크 / 글로벌 노트 |
| `{{authornote}}` | 현재 채팅의 작가의 노트 |
| `{{lorebook}}` | 활성 로어북 전체 (JSON 배열) |
| `{{emotionlist}}`, `{{assetlist}}`, `{{chardisplayasset}}` | 감정 이미지/추가 에셋 이름 배열 |

### 채팅 이력
| 함수 | 설명 |
|---|---|
| `{{history}}` (`messages`) | 전체 이력 JSON 배열 (첫 메시지 포함). `{{history::role}}`은 `role: 내용` 문자열 배열 |
| `{{userhistory}}` / `{{charhistory}}` | 역할별 메시지 배열 |
| `{{previouscharchat}}` (`lastcharmessage`) / `{{previoususerchat}}` | 직전 캐릭터/유저 메시지 |
| `{{lastmessage}}` / `{{lastmessageid}}` | 마지막 메시지 내용 / 인덱스 |
| `{{previouschatlog::N}}` | N번 인덱스 메시지 내용 |
| `{{chatindex}}` | 현재 메시지 인덱스 (-1 = 컨텍스트 없음) |
| `{{firstmsgindex}}` | 선택된 인사말 인덱스 (-1 = 기본) |
| `{{role}}` | 현재 메시지 역할 (`user`/`char`/`system`) |
| `{{isfirstmsg}}` | 첫 메시지 컨텍스트면 `'1'` |

### 시간
| 함수 | 설명 |
|---|---|
| `{{time}}`, `{{date}}` | 현재 시각/날짜. `{{date::YYYY-MM-DD HH:mm::타임스탬프ms}}` 포맷 지정 가능 (Moment 서브셋: YYYY MM DD HH hh mm ss ddd A X x 등) |
| `{{isotime}}`, `{{isodate}}` | UTC 기준 |
| `{{unixtime}}` | 유닉스 초 |
| `{{messagetime}}`, `{{messagedate}}` | 현재 메시지의 전송 시각/날짜 |
| `{{messageidleduration}}` | 최근 두 유저 메시지 사이 간격 (H:MM:SS) |
| `{{idleduration}}` | 마지막 메시지 이후 경과 시간 |
| `{{messageunixtimearray}}` | 모든 메시지 타임스탬프(ms) 배열 |

### 수학·논리·비교
| 함수 | 설명 |
|---|---|
| `{{? 수식}}` | 수식 평가. `+ - * / % ^ () < > <= >= == != && \|\|` 지원 |
| `{{calc::수식}}` | 위와 동일한 계산기 |
| `{{equal::a::b}}`, `{{notequal}}`, `{{greater}}`, `{{less}}`, `{{greaterequal}}`, `{{lessequal}}` | 비교 |
| `{{and::a::b}}`, `{{or::a::b}}`, `{{not::a}}`, `{{all::...}}`, `{{any::...}}` | 논리 |
| `{{round}}`, `{{floor}}`, `{{ceil}}`, `{{abs}}`, `{{pow::a::b}}`, `{{remaind::a::b}}` | 산술 |
| `{{min}}`, `{{max}}`, `{{sum}}`, `{{average}}` | 집계 (배열 1개 또는 다중 인자) |
| `{{fixnum::수::자릿수}}` | 소수점 고정 |
| `{{tonumber::문자열}}` | 숫자·점만 추출 |

### 난수
| 함수 | 설명 |
|---|---|
| `{{random}}` / `{{random::a::b::c}}` / `{{random::a,b,c}}` | 0~1 난수 / 무작위 선택. **재렌더마다 값이 바뀜** |
| `{{pick::...}}` | random과 같지만 메시지 인덱스+채팅ID 시드 고정 → **재렌더에도 일관된 값** |
| `{{roll::2d6}}` / `{{roll::20}}` | 주사위 (매번 다름) |
| `{{rollp::...}}` | 시드 고정 주사위 |
| `{{dice::2d6}}` | roll과 동일 표기 |
| `{{randint::min::max}}` | 정수 난수 |
| `{{hash::문자열}}` | 입력 기반 결정적 7자리 수 |

프롬프트에 들어가는 난수는 재생성 시 값이 흔들리므로 `pick`/`rollp`(시드 고정)를 권장.

### 문자열
`{{startswith}}`, `{{endswith}}`, `{{contains}}`, `{{replace::원문::찾기::바꾸기}}`(전체 치환),
`{{split::문자열::구분자}}`, `{{join::배열::구분자}}`, `{{spread::배열}}`(`::`로 join → 다른 함수 인자로 펼치기),
`{{trim}}`, `{{length}}`, `{{lower}}`, `{{upper}}`, `{{capitalize}}`, `{{reverse}}`,
`{{unicodeencode::A}}`, `{{unicodedecode::65}}`, `{{u::41}}`(hex→문자, 별칭 `ue`), `{{fromhex}}`, `{{tohex}}`

### 배열·딕셔너리 (JSON 문자열 기반)
`{{makearray::a::b}}` (`array`, `a`), `{{makedict::k=v::k2=v2}}` (`dict`, `d`, `object`, `o`),
`{{arraylength}}`, `{{arrayelement::배열::i}}`, `{{arraypush}}`, `{{arraypop}}`, `{{arrayshift}}`,
`{{arraysplice::배열::시작::삭제수::삽입값}}`, `{{arrayassert::배열::i::값}}`, `{{filter::배열::all|nonempty|unique}}`,
`{{range::[5]}}`→`[0..4]` / `{{range::[2,8,2]}}`, `{{dictelement::딕셔너리::키}}`, `{{objectassert}}`,
`{{element::JSON::키1::키2...}}`(중첩 접근, 실패 시 `'null'`)

주의: `makeArray`는 요소 내 `::`를 이스케이프해 저장한다. 배열을 인자로 펼칠 땐 `{{spread}}` 사용.

### 미디어·에셋 (표시 전용 — 별도 패스에서 처리됨)
| 함수 | 설명 |
|---|---|
| `{{asset::이름}}` | 추가 에셋을 타입에 맞는 요소로 표시 |
| `{{image::이름}}` / `{{img::이름}}` | 스타일 있는/없는 이미지 |
| `{{video::이름}}` / `{{video-img::이름}}` | 비디오 (controls / 이미지처럼 muted loop) |
| `{{audio::이름}}` / `{{bgm::이름}}` | 오디오 / 숨김 BGM |
| `{{bg::이름}}` | 배경 이미지 (배경 임베딩용) |
| `{{emotion::이름}}` | 감정 이미지 |
| `{{path::이름}}` (`raw`) | 에셋의 실제 경로 문자열 (CSS url() 등에 사용) |
| `{{inlay::id}}` / `{{inlayed::id}}` / `{{inlayeddata::id}}` | 인레이(채팅에 삽입된 미디어). `inlayeddata`만 모델 요청에도 포함됨 |
| `{{source::char}}` / `{{source::user}}` | 캐릭터/유저 아이콘 URL |

에셋 이름이 정확히 일치하지 않으면 Levenshtein 거리 기반 근사 매칭이 시도된다 (설정 `assetMaxDifference` 이내).

### UI·인터랙션
| 함수 | 설명 |
|---|---|
| `{{button::라벨::트리거이름}}` | 클릭 시 해당 이름의 manual 트리거를 실행하는 버튼 HTML |
| `{{trigger_id}}` | 클릭된 요소의 `risu-id` 속성값 (manual 트리거 안에서) |
| `{{comment::텍스트}}` | 표시 전용 주석 박스 (`{{//}}`와 달리 화면에 보임) |
| `{{tex::E=mc^2}}` (`latex`) | KaTeX 수식 |
| `{{ruby::漢字::かんじ}}` | 후리가나 |
| `{{codeblock::lang::코드}}` | 코드 블록 (하이라이팅) |
| `{{risu::크기}}` | RisuAI 로고 |

직접 HTML도 쓸 수 있다: 표시 텍스트는 DOMPurify로 새니타이즈되며, class는 `x-risu-` 접두사가 붙고
`<style>`은 `.chattext` 스코프로 재작성된다. 커스텀 속성 `risu-trigger`, `risu-btn`, `risu-id`,
`risu-ctrl`은 허용된다 (`risu-btn="데이터"`는 Lua `onButtonClick`으로 전달).

### 출력 조작·특수
| 함수 | 설명 |
|---|---|
| `{{bkspc}}` | 지금까지 출력된 텍스트에서 마지막 단어 제거 |
| `{{erase}}` | 마지막 문장 제거 |
| `{{blank}}` (`none`) | 빈 문자열 |
| `{{hiddenkey::값}}` | 로어북 활성화 키로는 작동하지만 프롬프트엔 포함 안 됨 |
| `{{position::이름}}` | 프롬프트 템플릿의 `@@position` 데코레이터 삽입 지점 정의 |
| `{{slot}}` / `{{slot::이름}}` | 컨텍스트 의존 슬롯 (#each, 프롬프트 템플릿 등) |
| `{{declare::이름}}` | 파서 동작 변경용 선언 플래그 |
| `{{iserror::문자열}}` | `error:`로 시작하면 `'1'` |
| `{{metadata::키}}` | 시스템 정보: `version`, `major`, `lang`, `browserlang`, `mobile`, `local`, `node`, `risutype`(web/local/node), `maxcontext`, `modelname`, `modelshortname`, `modelinternalid`, `modelformat`, `modelprovider`, `modeltokenizer` |
| `{{model}}` / `{{axmodel}}` | 현재 모델 / 보조 모델 ID |
| `{{maxcontext}}` | 최대 컨텍스트 |
| `{{jbtoggled}}` | 제일브레이크 토글 상태 |
| `{{prefillsupported}}` | 모델이 prefill 지원(claude 계열)이면 `'1'` |
| `{{moduleenabled::네임스페이스}}` | 모듈 활성 여부 |
| `{{moduleassetlist::네임스페이스}}` | 모듈 에셋 목록 |
| `{{file::이름::base64}}` | 표시 시 파일 박스, 프롬프트에선 base64 디코드 내용 |
| `{{xor::s}}` / `{{xordecrypt::s}}` / `{{crypt::s::시프트}}` | 간단한 난독화 |
| `{{screenwidth}}` / `{{screenheight}}` | 뷰포트 크기 |

참고: Lua 쪽에서 CBS를 실행하려면 Lua API `cbs(text)`를 사용한다 (CBS에서 Lua를 직접 호출하는 문법은 없음).

## 6. 실전 패턴

```
설정과 기본값:
{{setdefaultvar::hp::100}}                          ← 최초 1회만 설정

상태 표시 (첫 메시지/표시 텍스트에서):
HP: {{getvar::hp}} / 100

조건 표시:
{{#when::{{getvar::hp}}::<=::0}}💀 사망{{:else}}생존{{/when}}

변수 존재 검사:
{{#when::{{getvar::quest}}::isnot::null}}퀘스트: {{getvar::quest}}{{/when}}

인터랙티브 버튼 (manual 트리거 'attack'과 연동):
{{button::공격::attack}}

일관된 랜덤 (재렌더에도 동일):
오늘의 날씨: {{pick::맑음::비::흐림}}
```

## 7. 흔한 함정

- `getvar` 미설정 시 `'null'` 문자열 — `{{#when::{{getvar::x}}}}`는 x가 `'1'`일 때만 참.
- `setvar`는 채팅 메시지 안에 있을 때만, 전송 사이클의 정해진 두 시점에 실행된다 (2절 참고).
  표시 텍스트·greeting·로어북에 넣어도 실행되지 않고 리터럴로 남는다. "표시할 때마다 증가" 같은 동작은
  불가능하며, 상태 변경은 트리거/Lua에서 하는 것이 확실하다.
- `#when` 안의 부작용 CBS는 거짓 분기에서도 평가된다 (위 3절).
- 인자 안에 `::`가 들어가는 값(URL 등)은 그대로 쓰면 인자가 쪼개진다 — `{{:}}`(displayescapedcolon)로 escape.
- `{{random}}`은 표시 재렌더마다 바뀐다. 저장돼야 하는 값이면 트리거에서 굴려 변수에 저장하라.
- 배열은 JSON 문자열이므로 `{{arrayelement}}` 등에 넘길 때 따옴표 구조가 유지되어야 한다.
