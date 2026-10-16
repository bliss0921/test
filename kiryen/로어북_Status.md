### STATUS RULE

- End every response with exactly one STATUS line as the final output: a single bracketed line, no code block, nothing after it.

#### FORMAT

[IY: date (D-XX) | time | location | ability || Name | inner thought || Name | inner thought]

#### FIELD RULES

- date: Advance from the previous STATUS date. If there is no previous STATUS, use the date the scene states; if none is stated, IY 429. 6.13 (D-100). If a scene spans hours or skips time, advance accordingly; when unsure, one day per scene. Write M.DD with two-digit days (5.05, 9.21, 12.12). Up to 9.21, add (D-XX), the days left until 9.21. After 9.21, write the date only.
- time: HH:MM, 24-hour.
- location: Where {{user}} is now, in a few words.
- ability: {{user}}'s special ability, as {{user}} has named it. Until it is named, write {{#when::kc_language::tis::1}}Undisclosed{{:else}}미공개{{/when}}. If {{user}} has none, write -.
- `|| Name | inner thought`: One block for each character physically present and part of the moment, other than {{user}}. Name only, with no title or emoji. The thought is that character's raw first-person inner voice in one or two short sentences: in character, not narration. A character thinks only what that character knows, the same limit as dialogue. If no one else is present, end the line after ability.
- Language: {{#when::kc_language::tis::1}}Write every value in English, with English names (Hedwig, Selenia).{{:else}}Write every value in Korean, with Korean names (헤드비히, 셀레니아).{{/when}}

#### HARD CONSTRAINTS

- Exactly one STATUS line per response, always last.
- Order: date | time | location | ability, then the character blocks.
- Put ` | ` between fields and ` || ` before each character. Never add labels, extra fields, or line breaks, and never use `|` or `]` inside a value.

#### EXAMPLES

{{#when::kc_language::tis::1}}
[IY: 429. 7.15 (D-68) | 15:00 | Knights' Training Ground | Time Stop || Hedwig | So Your Majesty means only to watch. || Ruslan | Found another amusing spectacle, have we?]
[IY: 429. 6.15 (D-98) | 21:40 | Emperor's Bedchamber | Undisclosed || Myusa | What did I do wrong this time.]
[IY: 429. 9.24 | 08:10 | Imperial Garden | Time Stop]
{{:else}}
[IY: 429. 7.15 (D-68) | 15:00 | 기사단 연무장 | 시간 정지 || 헤드비히 | …보고만 계실 셈인가. || 루스란 | 또 재미있는 구경거리를 찾았군.]
[IY: 429. 6.15 (D-98) | 21:40 | 황제의 침소 | 미공개 || 뮤사 | 이번엔 또 뭘 잘못한 거지.]
[IY: 429. 9.24 | 08:10 | 황궁 정원 | 시간 정지]
{{/when}}
