# 데이터 구조 (스키마) 레퍼런스

캐릭터 카드·모듈의 JSON을 직접 생성/수정하거나, Lua/플러그인에서 객체를 주고받을 때 필요한 필드 명세.
`?`는 선택 필드. TypeScript 표기이지만 실제 데이터는 JSON이다.
(소스가 있는 환경에서의 원본: `src/ts/storage/database.svelte.ts`, `src/ts/process/triggers.ts`,
`src/ts/process/modules.ts`)

## Message — 채팅 메시지 1개

```typescript
interface Message {
  role: 'user' | 'char'
  data: string                    // 메시지 본문 (CBS 포함 가능)
  time?: number                   // 전송 시각 (ms 타임스탬프)
  chatId?: string                 // 메시지 고유 id
  name?: string                   // 표시 이름 (그룹/페르소나)
  saying?: string                 // 그룹챗에서 발화 캐릭터 chaId
  otherUser?: boolean
  disabled?: false | true | 'allBefore'   // 프롬프트에서 제외 (allBefore = 이 메시지 이전 전부)
  isComment?: boolean
  generationInfo?: { model?: string, generationId?: string, inputTokens?: number,
                     outputTokens?: number, maxContext?: number }
  promptInfo?: object             // 생성 당시 프리셋 정보
}
```

Lua `getChat`/`getFullChat`이 돌려주는 것, 플러그인 `getChatFromIndex().message[i]`가 이 구조다.

## Chat — 채팅방 1개

```typescript
interface Chat {
  name: string
  message: Message[]              // greeting(첫 메시지)은 포함되지 않음
  note: string                    // 작가의 노트
  localLore: loreBook[]           // 채팅 로컬 로어북 (Lua upsertLocalLoreBook 대상)
  scriptstate?: { [key: string]: string | number | boolean }  // 채팅 변수 저장소. 키는 '$'+이름,
                                  // getState/setState는 '$__'+이름
  modules?: string[]              // 이 채팅에서 활성화된 모듈 id 목록
  fmIndex?: number                // 선택된 greeting 인덱스 (-1 또는 미설정 = 기본 firstMessage)
  id?: string
  bindedPersona?: string
  suggestMessages?: string[]
  lastDate?: number
  folderId?: string
  useLocallySetGlobalVariables?: boolean   // true면 토글 조작이 전역 대신 아래 오버레이에 저장됨
  GLGlobalVariables?: { [key: string]: string }  // 전역 변수의 채팅 로컬 오버레이 (읽기 시 우선)
  // 그 외 메모리/북마크/스트리밍 관련: supaMemoryData, hypaV2Data, hypaV3Data, lastMemory,
  // bookmarks, isStreaming, activeStreamingDisplayOptimizationMode 등
}
```

## character — 캐릭터 (스크립팅 관련 필드 발췌)

전체 타입은 매우 크므로 스크립트 작업에 쓰이는 필드만 수록한다.

```typescript
interface character {
  type?: 'character'              // 그룹은 'group' (groupChat 타입, 필드 다름)
  chaId: string                   // 고유 id
  name: string
  nickname?: string               // {{char}}는 nickname ?? name
  firstMessage: string            // 기본 greeting
  alternateGreetings: string[]    // 추가 greeting ({{firstmsgindex}} = 선택 인덱스)
  firstMsgIndex: number
  desc: string                    // {{description}}
  personality: string
  scenario: string
  exampleMessage: string
  systemPrompt: string            // 캐릭터 전용 메인 프롬프트 대체
  replaceGlobalNote: string
  chats: Chat[]
  chatPage: number                // 현재 선택된 채팅 인덱스
  globalLore: loreBook[]          // 캐릭터 로어북
  customscript: customscript[]    // 정규식 스크립트
  triggerscript: triggerscript[]  // 트리거 스크립트
  lowLevelAccess?: boolean        // LLA 체크박스
  defaultVariables?: string       // 기본 변수. "키=값" 줄바꿈 구분 텍스트
  emotionImages: [name: string, assetId: string][]
  additionalAssets?: [name: string, assetId: string, ext: string][]   // {{asset::name}} 대상
  backgroundHTML?: string         // 배경 임베딩 (Lua get/setBackgroundEmbedding)
  backgroundCSS?: string
  moduleNamespace?: string        // 모듈↔캐릭터(charx) 변환 시 원본 모듈 네임스페이스 보존
  hideChatIcon?: boolean
  viewScreen: 'emotion' | 'none' | 'imggen'
  utilityBot: boolean
  bias: [string, number][]
  creatorNotes: string
  tags: string[]
  creator: string
  characterVersion: string
  // 그 외: 이미지·TTS·SD 설정 등 다수
}
```

## loreBook — 로어북 항목 1개

```typescript
interface loreBook {
  key: string                     // 활성화 키 (쉼표 구분)
  secondkey: string               // 보조 키 (selective일 때 AND 조건)
  insertorder: number             // 삽입 순서(우선순위)
  comment: string                 // 항목 이름 (Lua getLoreBooks의 검색 대상)
  content: string                 // 본문 (CBS 사용 가능)
  mode: 'multiple' | 'constant' | 'normal' | 'child' | 'folder'
  alwaysActive: boolean           // 키 매칭 없이 항상 활성
  selective: boolean              // key AND secondkey 요구
  useRegex?: boolean              // key를 정규식으로 해석
  activationPercent?: number      // 확률 활성화 (0~100)
  extentions?: { risu_case_sensitive: boolean }
  folder?: string
  id?: string
  bookVersion?: number
}
```

## customscript — 정규식 스크립트 1개

```typescript
interface customscript {
  comment: string                 // 이름
  type: 'editinput' | 'editoutput' | 'editprocess' | 'editdisplay'
  in: string                      // 찾을 정규식
  out: string                     // 치환 문자열
  ableFlag?: boolean              // true면 flag 필드 사용
  flag?: string                   // 정규식 플래그 + <메타 액션> (기본 'g')
}
```

## triggerscript — 트리거 1개

```typescript
interface triggerscript {
  comment: string                 // 이름 (manual 트리거는 {{button::라벨::이름}}과 매칭)
  type: 'start' | 'manual' | 'output' | 'input' | 'display' | 'request'
  conditions: triggerCondition[]  // 모두 통과해야 effect 실행
  effect: triggerEffect[]
  lowLevelAccess?: boolean        // 모듈 트리거용 LLA 플래그
}

// ── 조건 ──
type triggerCondition =
  | { type: 'var' | 'value', var: string, value: string,
      operator: '=' | '!=' | '>' | '<' | '>=' | '<=' | 'null' | 'true' }
  | { type: 'chatindex', value: string,
      operator: '=' | '!=' | '>' | '<' | '>=' | '<=' | 'null' | 'true' }
  | { type: 'exists', value: string, type2: 'strict' | 'loose' | 'regex', depth: number }

// ── 효과: Lua/JS 코드형 ──
{ type: 'triggerlua', code: string }        // 권장. Lua 트리거는 effect[0]에 이것 하나만 둔다
{ type: 'triggercode', code: string }       // JS 코드형 (레거시, 신규 사용 비권장)

// ── 효과: V1 (값 필드에 CBS 사용 가능) ──
{ type: 'setvar', operator: '=' | '+=' | '-=' | '*=' | '/=', var: string, value: string }
{ type: 'cutchat', start: string, end: string }
{ type: 'modifychat', index: string, value: string }
{ type: 'systemprompt', location: 'start' | 'historyend' | 'promptend', value: string }
{ type: 'impersonate', role: 'user' | 'char', value: string }
{ type: 'command', value: string }
{ type: 'stop' }
{ type: 'runtrigger', value: string }       // value = 대상 manual 트리거의 comment
{ type: 'extractRegex', value: string, regex: string, flags: string,
  result: string, inputVar: string }        // value에서 regex 매칭 → result 템플릿($1..)을 inputVar에 저장
// [LLA 필요]
{ type: 'showAlert', alertType: string, value: string, inputVar: string }
{ type: 'runLLM', value: string, inputVar: string }      // value=프롬프트, 결과를 inputVar 변수에 저장
{ type: 'runAxLLM', value: string, inputVar: string }
{ type: 'checkSimilarity', source: string, value: string, inputVar: string }
{ type: 'runImgGen', value: string, negValue: string, inputVar: string }
{ type: 'sendAIprompt' }                    // output 트리거 후 sendChat 재실행 (자동 재전송)

// ── 효과: V2 (전 블록 공통: type + indent. 대표 예시) ──
{ type: 'v2If', condition: '=' | '!=' | '>' | '<' | '>=' | '<=',
  targetType: 'var' | 'value', target: string, source: string, indent: number }
{ type: 'v2Else', indent: number }
{ type: 'v2EndIndent', endOfLoop?: boolean, indent: number }
{ type: 'v2SetVar', operator: '=' | '+=' | '-=' | '*=' | '/=' | '%=',
  var: string, valueType: 'var' | 'value', value: string, indent: number }
{ type: 'v2Loop', indent: number }
{ type: 'v2LoopNTimes', value: string, valueType: 'var' | 'value', indent: number }
{ type: 'v2BreakLoop', indent: number }
{ type: 'v2RunTrigger', target: string, indent: number }
{ type: 'v2ConsoleLog', sourceType: 'var' | 'value', source: string, indent: number }
// display/request 전용 블록은 triggers-and-regex.md 참고
```

## RisuModule — 모듈

```typescript
interface RisuModule {
  id: string
  name: string
  description: string
  namespace?: string              // {{moduleenabled::ns}} 등에서 참조
  lorebook?: loreBook[]
  regex?: customscript[]
  trigger?: triggerscript[]
  assets?: [name: string, assetId: string, ext: string][]
  lowLevelAccess?: boolean        // 모듈 트리거의 LLA (캐릭터 LLA와 별개)
  backgroundEmbedding?: string
  customModuleToggle?: string     // 토글 UI 정의. 상태는 전역 변수 toggle_<이름>
  hideIcon?: boolean
  mcp?: object                    // MCP 설정
  icon?: string
}
```
