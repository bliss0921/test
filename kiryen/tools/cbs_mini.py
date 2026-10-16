"""Small CBS renderer following RisuAI parser.svelte.ts rules for the parts this card uses.

Supported: {{#when::...}} (is/isnot/tis/tisnot/not/and/or/keep), {{:else}}, getvar, getglobalvar,
equal, any, all, and, not, greater_equal, chat_index, lastmessageid, {{? expr}}. Unknown tags stay literal.
vars: chat variables (missing -> defaults -> 'null'); toggles: {'kc_language': '1', ...} (missing -> 'null').
"""
import re

T = ('1', 'true')


def call(dat, ctx):
    if dat.startswith('? '):
        expr = dat[2:].strip()
        assert re.fullmatch(r'[\d\s+\-*/().]+', expr), expr
        return str(int(eval(expr)))
    parts = dat.split('::') if '::' in dat else dat.split(':')
    name = re.sub(r'[\s_\-]', '', parts[0].lower())
    a = parts[1:]
    if name == 'getvar': return ctx['vars'].get(a[0], 'null')
    if name == 'getglobalvar':
        k = a[0]
        return ctx['toggles'].get(k[len('toggle_'):], 'null') if k.startswith('toggle_') else 'null'
    if name == 'equal': return '1' if a[0] == a[1] else '0'
    if name == 'not': return '0' if a[0] == '1' else '1'
    if name == 'and': return '1' if a[0] == '1' and a[1] == '1' else '0'
    if name in ('any', 'all'):
        f = any if name == 'any' else all
        return '1' if f(x == '1' for x in a) else '0'
    if name == 'greaterequal': return '1' if float(a[0]) >= float(a[1]) else '0'
    if name == 'chatindex': return ctx['vars']['@chat_index']
    if name == 'lastmessageid': return ctx['vars']['@last']
    return None


def block_start(dat, ctx):
    if not dat.startswith('#when'):
        raise ValueError('unsupported block ' + dat)
    if dat.startswith('#when '):
        return ('newif' if dat.split(' ', 2)[1] in T else 'newif-falsy'), None
    st = dat.split('::')[1:]
    if len(st) == 1:
        return ('newif' if st[0] in T else 'newif-falsy'), None
    mode = None
    tog = ctx['toggles']
    while len(st) > 1:
        c, op = st.pop(), st.pop()
        if op == 'not': st.append('0' if c in T else '1')
        elif op == 'keep': mode = 'keep'; st.append(c)
        elif op == 'and': c2 = st.pop(); st.append('1' if c in T and c2 in T else '0')
        elif op == 'or': c2 = st.pop(); st.append('1' if c in T or c2 in T else '0')
        elif op == 'is': c2 = st.pop(); st.append('1' if c == c2 else '0')
        elif op == 'isnot': c2 = st.pop(); st.append('1' if c != c2 else '0')
        elif op == 'tis': st.append('1' if tog.get(st.pop(), 'null') == c else '0')
        elif op == 'tisnot': st.append('1' if tog.get(st.pop(), 'null') != c else '0')
        else: st.append('1' if c in T else '0')
    return ('newif' if st[0] in T else 'newif-falsy'), mode


def block_end(body, kind, mode):
    lines = body.split('\n')
    if len(lines) == 1:
        i = body.find('{{:else}}')
        if i != -1:
            return body[:i] if kind == 'newif' else body[i + 9:]
        return body if kind == 'newif' else ''
    el = next((n for n, l in enumerate(lines) if l.strip() == '{{:else}}'), -1)
    if el != -1 and kind == 'newif':
        lines = lines[:el]
    if el != -1 and kind == 'newif-falsy':
        lines = lines[el + 1:]
    if el == -1 and kind == 'newif-falsy':
        return ''
    if mode != 'keep':
        while lines and lines[0].strip() == '': lines.pop(0)
        while lines and lines[-1].strip() == '': lines.pop()
    return '\n'.join(lines)


def render(s, vars=None, toggles=None, defaults=None):
    ctx = {'vars': {**(defaults or {}), **(vars or {})}, 'toggles': toggles or {}}
    bufs, kinds, blocks = [''], ['root'], []
    i = 0
    while i < len(s):
        if s.startswith('{{', i):
            bufs.append(''); kinds.append('tag'); i += 2; continue
        if s.startswith('}}', i) and kinds[-1] == 'tag':
            dat = bufs.pop(); kinds.pop(); i += 2
            if dat.startswith('#'):
                blocks.append(block_start(dat, ctx)); bufs.append(''); kinds.append('body')
            elif dat.startswith(':'):
                bufs[-1] += '{{' + dat + '}}'
            elif dat.startswith('/') and not dat.startswith('//'):
                assert kinds[-1] == 'body', 'stray close'
                body = bufs.pop(); kinds.pop()
                kind, mode = blocks.pop()
                bufs[-1] += block_end(body, kind, mode)
            else:
                r = call(dat, ctx)
                bufs[-1] += ('{{' + dat + '}}') if r is None else r
            continue
        bufs[-1] += s[i]; i += 1
    assert len(bufs) == 1, 'unclosed block/tag'
    return bufs[0]
