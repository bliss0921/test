"""charx 읽기/쓰기.

charx = zip (card.json, module.risum, assets/, x_meta/). module.risum 은 RisuAI rpack 바이트 치환표로
인코딩된 JSON 이다. 가져오기(import) 때 module 의 lorebook/regex/trigger 가 card.json 보다 우선하므로
로어북은 card.json 의 character_book 과 module 양쪽을 같이 고친다.

  python3 -I charx_io.py unpack 카드.charx 덤프.json            # {"card": ..., "mod": ...}
  python3 -I charx_io.py pack 원본.charx 덤프.json 새카드.charx   # 원본의 assets/x_meta 는 그대로 복사

치환표 rpack_map.bin(512바이트)은 환경 변수 RPACK_MAP, 없으면 이 폴더의 rpack_map.bin:
  curl -sSLo rpack_map.bin https://raw.githubusercontent.com/kwaroran/RisuAI/main/src/ts/rpack/rpack_map.bin
"""
import json
import os
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))


def _map():
    mp = open(os.environ.get('RPACK_MAP') or os.path.join(HERE, 'rpack_map.bin'), 'rb').read()
    assert len(mp) == 512, 'rpack_map.bin 이 512바이트가 아님'
    return mp[:256], mp[256:512]


def read_risum(buf):
    _, dec = _map()
    assert buf[0] == 111 and buf[1] == 0
    n = struct.unpack('<I', buf[2:6])[0]
    assert buf[6 + n:] == b'\x00', 'module 안에 에셋이 있음 (이 도구는 지원 안 함)'
    return json.loads(bytes(dec[b] for b in buf[6:6 + n]).decode('utf-8'))


def write_risum(obj):
    enc, _ = _map()
    raw = json.dumps(obj, ensure_ascii=False, indent=2).encode('utf-8')
    return bytes([111, 0]) + struct.pack('<I', len(raw)) + bytes(enc[b] for b in raw) + b'\x00'


def load(path):
    """-> (card, mod)"""
    z = zipfile.ZipFile(path)
    return json.loads(z.read('card.json')), read_risum(z.read('module.risum'))


def save(base_path, out_path, card, mod):
    src = zipfile.ZipFile(base_path)
    files = {i.filename: src.read(i) for i in src.infolist()}
    files['card.json'] = json.dumps(card, ensure_ascii=False, indent=4).encode('utf-8')
    files['module.risum'] = write_risum(mod)
    assert read_risum(files['module.risum']) == mod
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as out:
        for info in src.infolist():
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            out.writestr(zi, files[info.filename])


def load_any(path):
    """charx 또는 unpack 한 json -> {"card": ..., "mod": ...}"""
    if path.endswith('.charx'):
        card, mod = load(path)
        return {'card': card, 'mod': mod}
    return json.load(open(path, encoding='utf-8'))


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'unpack':
        card, mod = load(sys.argv[2])
        json.dump({'card': card, 'mod': mod}, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    elif cmd == 'pack':
        d = json.load(open(sys.argv[3], encoding='utf-8'))
        save(sys.argv[2], sys.argv[4], d['card'], d['mod'])
    else:
        sys.exit(__doc__)
    print('ok')
