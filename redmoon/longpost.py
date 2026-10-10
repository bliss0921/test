# 아카라이브용 세로 긴 이미지: 건물 → 초이스 → 인물소개(W4) → 누구를 고르시겠습니까
# python3 gen.py && python3 render.py out/draft_W4.html out/draft_W4.png   (인물소개 먼저)
# python3 longpost.py && python3 render.py out/redmoon_full.html out/redmoon_full.png
import os

PANELS = ["../img/scene_street.webp", "../img/panel_choice.webp", "draft_W4.png", "../img/panel_who.webp"]

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    imgs = "".join(f'<img src="{p}" style="display:block;width:1000px;height:auto">' for p in PANELS)
    html = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>*{margin:0;padding:0}'
            f'body{{width:1000px;background:#000}}</style></head><body>{imgs}</body></html>')
    open(os.path.join(here, "out", "redmoon_full.html"), "w", encoding="utf-8").write(html)
    print("ok")
