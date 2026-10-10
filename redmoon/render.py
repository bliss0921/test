# python3 render.py in.html out.png [in2.html out2.png ...]  (Playwright + Chromium, 페이지 폭에 맞춰 전체 캡처)
import sys, os
from playwright.sync_api import sync_playwright
EXE = '/opt/pw-browsers/chromium' if os.path.exists('/opt/pw-browsers/chromium') else None
with sync_playwright() as p:
    b = p.chromium.launch(**({'executable_path': EXE} if EXE else {}))
    pg = b.new_page(viewport={'width': 1000, 'height': 1000}, device_scale_factor=1)
    for src, out in zip(sys.argv[1::2], sys.argv[2::2]):
        pg.goto('file://' + os.path.abspath(src)); pg.wait_for_timeout(600)
        w, h = pg.evaluate('[Math.ceil(document.body.getBoundingClientRect().width), document.documentElement.scrollHeight]')
        pg.set_viewport_size({'width': w, 'height': 1000})
        pg.screenshot(path=out, full_page=True, clip={'x': 0, 'y': 0, 'width': w, 'height': h})
        print(out, w, h)
    b.close()
