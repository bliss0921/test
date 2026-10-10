#!/bin/sh
# 시안에 쓴 웹폰트(고운바탕, Cormorant Garamond)를 fonts/ 에 받는다. 없으면 Noto 폰트로 대체돼서 렌더링됨.
cd "$(dirname "$0")" && mkdir -p fonts && cd fonts
B=https://raw.githubusercontent.com/google/fonts/main/ofl
curl -fsSLO $B/gowunbatang/GowunBatang-Regular.ttf
curl -fsSLO $B/gowunbatang/GowunBatang-Bold.ttf
curl -fsSL -o CormorantGaramond.ttf "$B/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf"
curl -fsSL -o CormorantGaramond-Italic.ttf "$B/cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf"
