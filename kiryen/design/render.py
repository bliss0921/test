# python3 render.py  →  out/{시안}_pc.png, out/{시안}_m.png, out/sheet_minimal.png
import os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
EXE = '/opt/pw-browsers/chromium' if os.path.exists('/opt/pw-browsers/chromium') else None
def shot(pg, src, out, width):
    pg.set_viewport_size({'width': width, 'height': 200})
    pg.goto('file://' + os.path.join(OUT, src)); pg.wait_for_timeout(500)
    h = pg.evaluate('Math.ceil(document.body.getBoundingClientRect().bottom)')
    pg.screenshot(path=os.path.join(OUT, out), clip={'x': 0, 'y': 0, 'width': width, 'height': h}, full_page=True)
    print(out, width, h)
with sync_playwright() as p:
    b = p.chromium.launch(**({'executable_path': EXE} if EXE else {}))
    pg = b.new_page(device_scale_factor=2)
    for v in ('final', 'final_one', 'final_none', 'final_en'):
        shot(pg, f'{v}.html', f'{v}_pc.png', 680)
        shot(pg, f'{v}.html', f'{v}_m.png', 375)
    pg2 = b.new_page(device_scale_factor=1)
    shot(pg2, 'sheet_final.html', 'sheet_final.png', 1244)
    b.close()
