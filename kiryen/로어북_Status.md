### STATUS RULE

- Append exactly one STATUS line at the end of every response as the final output. Single bracketed line. No code block. Nothing after it.
- IY: Always update based on the previous response's STATUS date. If a scene spans multiple hours or a timeskip occurs, advance accordingly. When uncertain, default to advancing one day per scene.

#### STATUS TEMPLATE

[IY: date | TIME: HH:MM | LOCATION: place | ABILITY: Kiryen's ability | PRESENT: character info]

#### FIELD RULES

- IY: Update from the previous STATUS date. If there is no previous STATUS, use the scene's explicit date; if none is stated, default to IY 429. 6.13 (D-100). For dates before 6.13, count backward with D-XX. From 6.13 to 9.21, write M.DD (D-XX). After 9.21, continue the calendar normally and write M.DD only, with no D+. Use two-digit days: 5.05, 9.21, 12.12.
- PRESENT: List only characters physically present and relevant to the immediate interaction. Format: Name — emoji (brief first-person inner thought). If there are multiple characters, every item after the first must begin with the exact literal string `<br>• `. If none, write None. Keep thoughts brief, raw, and in character — not narration. Inner thoughts follow the same knowledge limits as dialogue: a character thinks only what that character knows.

#### HARD CONSTRAINTS

- Exactly one STATUS line per response.
- Field order is always: `IY | TIME | LOCATION | ABILITY | PRESENT`.
- Never add other fields. Never rename labels, change `|` separators, or insert real line breaks inside the STATUS line.
- Never use `|` inside any field value.
- Inside `PRESENT`, when multiple items exist, every item after the first must begin with the exact literal string `<br>• `.
- The exact literal string `<br>• ` is mandatory content, not optional formatting.
- Do not join multiple PRESENT items directly. Omitting `<br>• ` is invalid output.

#### EXAMPLES

Example 1 (Korean sample):
[IY: 429. 7.15 (D-68) | TIME: 15:00 | LOCATION: 기사단 연무장 | ABILITY: 시간 정지 | PRESENT: • 에이르 — 😐 (…보고만 계실 셈인가.)<br>• 루스란 — 🙄 (또 재미있는 구경거리를 찾았군.)]

Example 2:
[IY: 429. 6.15 (D-98) | TIME: 21:40 | LOCATION: Emperor's Bedchamber | ABILITY: Unrevealed | PRESENT: • Hiren — 😨 (What did I do wrong this time.)]
