# RisuAI 플러그인 (API v3.0) 레퍼런스

플러그인은 앱 전체에 적용되는 JavaScript 확장이다. **샌드박스 iframe** 안에서 실행되며 전역 `Risuai`
객체로 API에 접근한다. 이 문서는 실무에 필요한 API·타입을 자체 수록한다.
(소스가 있는 환경에서의 원본: `src/ts/plugins/apiV3/` — 전체 타입 `risuai.d.ts`, 공식 가이드 리포 루트
`plugins.md`, v2→v3 마이그레이션 `migrationGuide.md`)

## 1. 기본 구조

```javascript
//@name my_plugin              ← 필수. 고유 내부 이름 (배포 후 변경 금지)
//@api 3.0                     ← 필수. 신규 플러그인은 3.0
//@version 1.0.0               ← 업데이트 체크용 (파일 상단에 위치)
//@display-name My Plugin      ← 표시 이름 (자유 변경 가능)
//@arg api_key string API 키 설명    ← 유저 설정 인자 (string | int)
//@link https://example.com/docs Documentation
//@update-url https://raw.githubusercontent.com/user/repo/main/plugin.js

(async () => {
  try {
    const char = await Risuai.getCharacter();
    console.log('로드됨:', char?.name);
  } catch (e) {
    console.log(`Error: ${e.message}`);
  }
})();
```

가져오기: 플러그인 설정 → Import Plugin (개발 시 "Import plugin with hot reload" 권장).
TypeScript 템플릿: 플러그인 설정 → `</>` 메뉴 → Download plugin template.

## 2. 핵심 규칙

1. **모든 `Risuai.*` API는 async다.** 항상 `await` 하라. (가장 흔한 버그 원인)
2. **두 개의 DOM 컨텍스트**: 자신의 iframe `document`(제약 없음, 커스텀 UI용)와
   `await Risuai.getRootDocument()`로 얻는 메인 앱 DOM(SafeDocument/SafeElement 래퍼, 보안 제약).
3. 메인 DOM 조작 제약: HTML은 DOMPurify로 새니타이즈, 속성은 `x-` 접두사만 직접 설정 가능,
   이벤트는 마우스/포인터/스크롤(무제한) + 키보드(랜덤 지연)만 허용, `addEventListener`는 제거용 ID를 반환.
   `createElement`는 화이트리스트 태그만 (그 외는 div가 됨), 링크는 `createAnchorElement(href)` (http/https만).
4. 일부 API는 유저 동의가 필요. 권한은 7종:
   `'db'`(getDatabase/setDatabase), `'mainDom'`(getRootDocument), `'replacer'`(addRisuReplacer,
   registerBodyIntercepter, addRisuChatListener), `'fetchLogs'`(getFetchLogs), `'provider'`(addProvider),
   `'sendChat'`(sendChat), `'inlay'`(readInlay).
   해당 API 첫 호출 시 자동으로 동의 프롬프트가 뜨며(`db`/`replacer`/`inlay`는 주기적 재확인),
   `requestPluginPermission(권한)`으로 미리 요청할 수도 있다. 거부되면 null 반환 또는 무동작.
5. 정리: `await Risuai.onUnload(fn)`으로 해제 콜백 등록. UI 등록 함수는 id를 반환하므로
   `unregisterUIPart(id)`로 제거. 언로드/리로드 시 MutationObserver·플러그인 채널 리스너·
   채팅 리스너·메인 문서 이벤트 리스너는 자동으로 정리된다.

## 3. API 요약

### 데이터 접근
| API | 설명 |
|---|---|
| `getCharacter()` / `setCharacter(c)` | 현재 캐릭터 읽기/쓰기 (`getChar`/`setChar`는 구명칭) |
| `getCharacterFromIndex(i)` / `setCharacterToIndex(i, c)` | 인덱스로 접근 |
| `getChatFromIndex(ci, chi)` / `setChatToIndex(ci, chi, chat)` | 채팅 접근 |
| `getCurrentCharacterIndex()` / `getCurrentChatIndex()` | 현재 선택 인덱스 |
| `getCurrentLorebookEntries()` | 현재 로어북 항목 |
| `getDatabase(includeOnly?)` / `setDatabase(db)` / `setDatabaseLite(db)` | DB 서브셋 접근. 허용 키: characters, modules, enabledModules, personas, plugins, pluginCustomStorage, temperature, maxContext, maxResponse, theme, customCSS, guiHTML, characterOrder, selectedPersona 등 |

### 저장소
| API | 특성 |
|---|---|
| `Risuai.pluginStorage` (get/set/removeItem, keys, length, clear) | **세이브 파일 종속 + 기기 간 동기화**. 문자열. 권장 기본값 |
| `Risuai.safeLocalStorage` | 기기 종속, 플러그인 간 공유. 문자열 |
| `await Risuai.getLocalPluginStorage()` | 기기 종속, JSON 직렬화 가능한 임의 값 저장 |
| `getArgument(key)` / `setArgument(key, v)` | `//@arg` 유저 설정값 |

### 파이프라인 후킹
| API | 설명 |
|---|---|
| `addRisuScriptHandler(mode, fn)` / `removeRisuScriptHandler` | 텍스트 훅. mode: `'display'`/`'output'`/`'input'`/`'process'`. `fn(content) => string`. 정규식 스크립트와 같은 파이프라인 지점에서 실행됨 |
| `addRisuReplacer('beforeRequest', fn)` | 모델 요청 직전 메시지 배열 수정: `fn(messages, type) => messages` |
| `addRisuReplacer('afterRequest', fn)` | 응답 텍스트 수정: `fn(content, type) => string` |
| `registerBodyIntercepter(fn)` / `unregisterBodyIntercepter(id)` | LLM HTTP 요청 body 수정 (API 키 등 민감 필드는 제거된 상태로 전달, 권한 프롬프트 발생 가능, 거부 시 null) |
| `addTTSPreprocessor(fn)` | TTS 합성 직전 텍스트 수정: `fn({text, ttsMode, characterId}) => {text} | {skip:true}` |
| `addTTSPostprocessor(fn)` | TTS 오디오 수정: `fn({audio, mimeType, ...}) => {audio, mimeType} | {skip:true}` (webspeech/vits 제외) |
| `addRisuChatListener('output', fn)` / `removeRisuChatListener` | 모델 출력이 채팅에 **커밋된 후** 알림 (`replacer` 권한 재사용). 스트리밍 완료 → runVar 패스 → output 트리거 → 인레이 처리까지 끝난 뒤 `fn({char, chat, characterIndex, chatIndex, messageIndex})` 호출. char/chat은 **스냅샷**이라 수정해도 반영 안 됨 — 저장하려면 인덱스로 `setChatToIndex` 등 사용. output 트리거가 해당 메시지를 지웠으면 `messageIndex = -1`. 리스너는 순차 await되므로 오래 걸리는 작업은 await 없이 백그라운드로 |

훅은 등록 순서대로 체이닝되고, 훅에서 throw하면 그 훅만 건너뛴다.

### AI·모델
| API | 설명 |
|---|---|
| `addProvider(name, fn, options?)` | 커스텀 AI 프로바이더 등록 (`provider` 권한). `fn(args, abortSignal) => {success, content}` (content는 문자열 또는 `ReadableStream<string>`). args·options 구조는 아래 "핵심 타입" 참고 |
| `registerMCP(meta, getToolList, callTool)` / `unregisterMCP(id)` | MCP 툴 모듈 등록. identifier는 `plugin:` 접두사 필수. callTool 반환: `[{type:'text', text}]` 등 |
| `runLLMModel(options)` | 모델 직접 호출 |
| `sendChat(message)` | 유저로서 채팅 전송 (`sendChat` 권한) |
| `getFetchLogs()` | 최근 LLM 요청 로그 (fetchLogs 권한 필요) |

### UI
| API | 설명 |
|---|---|
| `showContainer('fullscreen')` / `hideContainer()` | 자신의 iframe UI 표시/숨김 |
| `registerSetting(name, onClick, icon?, iconType?)` | 설정 메뉴 항목 추가 |
| `registerButton({name, icon, iconType, location}, onClick)` | 버튼 추가. location: `'action'`/`'chat'`/`'hamburger'`. iconType: `'html'`/`'img'`/`'none'` |
| `unregisterUIPart(id)` | 등록 해제 |
| `createMutationObserver(cb)` | 메인 DOM 변경 감시 (`SafeMutationObserver`; 콜백 인자는 `unwarpSafeArray()`로 풀기). `disconnect()`로 중지, 언로드 시 자동 disconnect |
| `changeColorScheme(name)` / `setColorScheme(scheme)` / `getColorScheme()` | 색상 테마 |
| `changeTextTheme(name)` / `setCustomTextTheme(theme)` / `getTextTheme()` | 채팅 텍스트 테마 |

### 기타
| API | 설명 |
|---|---|
| `nativeFetch(url, options)` | CORS/프록시 처리된 fetch |
| `saveSecretHeader(key, prefix, value)` | 비밀 헤더 저장 (요청 시 자동 첨부) |
| `readImage(path)` / `saveAsset(data)` | 에셋 IO |
| `readInlay(id)` | 유저가 채팅에 첨부한 인레이 에셋 읽기 (`inlay` 권한). 메시지 원문의 `{{inlayed::<uuid>}}`에서 UUID 추출 → `{data: base64 data-URI, ext, name, type: 'image'\|'video'\|'audio'\|'signature', width?, height?}` 또는 null. 커스텀 프로바이더에서 멀티모달 첨부 복원에 사용 |
| `getRuntimeInfo()` | `{apiVersion, platform, saveMethod}` |
| `addPluginChannelListener(channel, cb)` / `postPluginChannelMessage(pluginName, channel, msg)` | 플러그인 간 통신 |
| `searchTranslationCache(partial)` / `getTranslationCache(key)` | 번역 캐시 조회 |
| `unwarpSafeArray(safeArr)` | SafeClassArray → 일반 배열 |
| `onUnload(fn)` / `loadPlugins()` | 수명 주기 |

## 4. 핵심 타입 (risuai.d.ts에서 발췌)

```typescript
// 파이프라인 훅·프로바이더가 주고받는 메시지 형식
interface OpenAIChat {
  role: 'system' | 'user' | 'assistant' | 'function'
  content: string
  name?: string
}

// addRisuScriptHandler의 mode / addRisuReplacer의 name
type ScriptMode = 'display' | 'output' | 'input' | 'process'
type ReplacerType = 'beforeRequest' | 'afterRequest'

// addProvider의 fn이 받는 인자 (temperature 등 페널티류는 0~100 스케일)
interface ProviderArguments {
  prompt_chat: OpenAIChat[]
  temperature: number
  max_tokens: number
  frequency_penalty: number
  min_p: number
  presence_penalty: number
  repetition_penalty: number
  top_k: number
  top_p: number
  mode: string          // 생성 모드 (일반 채팅 외 번역·감정 등 보조 요청 구분)
}
interface ProviderResponse { success: boolean; content: string | ReadableStream<string> }
interface ProviderOptions {
  tokenizer?: string    // 예: 'gpt-4'
  tokenizerFunc?: (content: string) => number[] | Promise<number[]>
}

// getDatabase(includeOnly?) / setDatabase가 다루는 서브셋의 허용 키
interface DatabaseSubset {
  characters?: any[]              // 캐릭터·그룹 배열 (구조는 schemas.md 참고)
  modules?: RisuModule[]
  enabledModules?: string[]
  moduleIntergration?: string
  personas?: Persona[]
  plugins?: RisuPlugin[]
  pluginCustomStorage?: { [key: string]: any }
  temperature?: number            // 0~100
  maxContext?: number
  maxResponse?: number
  frequencyPenalty?: number       // 0~100
  PresensePenalty?: number        // 0~100
  theme?: string
  textTheme?: string
  lineHeight?: number
  customCSS?: string
  guiHTML?: string
  colorSchemeName?: string
  // 그 외: askRemoval, seperateModels(memory/emotion/translate/otherAx) 등
}

interface Persona {
  personaPrompt: string
  name: string
  icon: string
  largePortrait?: boolean
  id?: string
  note?: string
}

// addRisuChatListener('output', fn)의 fn이 받는 인자
interface ChatOutputListenerArg {
  char: any               // 현재 캐릭터 스냅샷
  chat: any               // 커밋된 채팅 스냅샷
  characterIndex: number  // setCharacterToIndex용
  chatIndex: number       // setChatToIndex용
  messageIndex: number    // 생성된 메시지의 chat.message 인덱스, 제거됐으면 -1
}

// readInlay(id)의 반환 타입
interface InlayAssetForPlugin {
  data: string            // base64 data-URI ("data:image/png;base64,...")
  ext: string             // 확장자 (점 없이, 예: "png")
  name: string            // 원본 파일명
  type: 'image' | 'video' | 'audio' | 'signature'
  height?: number
  width?: number
}
```

캐릭터/채팅/메시지/로어북/모듈의 상세 구조는 [schemas.md](schemas.md) 참고 — 플러그인이
`getCharacter()`/`getChatFromIndex()`로 받는 객체가 그 구조다.

## 5. 버전 정책

| 버전 | 상태 |
|---|---|
| 1.0 | 지원 종료 |
| 2.0 | 설치 차단 (import 시 에러) |
| 2.1 | **신규 설치 차단** (import 시 "no longer supported" 에러). 기설치된 2.1 플러그인만 계속 로드됨 (전역 함수 기반, 비-샌드박스) |
| 3.0 | **신규 플러그인 표준이자 설치 가능한 유일한 버전.** iframe 샌드박스 + async API |

v2 플러그인의 스크립트 핸들러(`risuScriptHandler` 등)는 내부적으로 `pluginV2` 레지스트리로 채팅
파이프라인에 연결된다 — 새 코드는 v3의 `addRisuScriptHandler`를 쓰면 같은 지점에 연결된다.

## 6. 흔한 함정

- `await` 누락 → undefined/Promise 반환. 모든 Risuai API에 await.
- 메인 DOM에 `setAttribute('onclick', ...)` 등은 에러 — `x-` 접두사 속성과 `addEventListener`만.
- `setInnerHTML`의 `<script>`는 제거된다 (의도된 동작).
- iframe DOM과 메인 DOM은 서로 접근 불가 — 각자 컨텍스트에서 조작.
- DB 수정 후 `setDatabase()`/`setDatabaseLite()` 호출을 잊으면 저장 안 됨.
- `pluginStorage`(동기화됨) vs `safeLocalStorage`(기기 전용) 용도 구분.
