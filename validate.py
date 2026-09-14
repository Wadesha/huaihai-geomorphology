# -*- coding: utf-8 -*-
"""站点自检：标签闭合 + 内链 + 「纯散文正文」约束 + 交互结构 + 关键内容抽查。
结果写入 _validate.txt（适配单页标签式结构：docs/ 下只有 index.html）
"""
import os, re, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, 'docs')
out = []

files = sorted(glob.glob(os.path.join(DOCS, '**', '*.html'), recursive=True))
out.append('html files: %d %s' % (len(files), [os.path.relpath(f, DOCS) for f in files]))

bad = 0
TAGS = ['div', 'main', 'nav', 'section', 'a', 'p', 'span', 'h1', 'h2', 'h3', 'h4',
        'b', 'button', 'footer', 'style', 'script', 'html', 'head', 'body']
for f in files:
    t = open(f, encoding='utf-8').read()
    for tag in TAGS:
        o = len(re.findall('<' + tag + r'(?=[\s>])', t))
        c = t.count('</' + tag + '>')
        if o != c:
            out.append('TAGMISMATCH %s %s open=%d close=%d' % (os.path.basename(f), tag, o, c))
            bad += 1
    for href in re.findall(r'href="([^"]+)"', t):
        if href.startswith(('http', 'mailto', '#')):
            continue
        p = os.path.normpath(os.path.join(os.path.dirname(f), href))
        if not os.path.isfile(p):
            out.append('DEAD %s -> %s' % (os.path.basename(f), href))
            bad += 1

out.append('link/tag problems: %d' % bad)

# ── 纯散文正文约束：正文里不得出现表格、统计块、步骤条、侧栏、筛选控件、列表
FORBIDDEN = {
    '<table': '表格', '<tbody': '表格', '<thead': '表格', '<tr>': '表格行',
    '<td': '表格单元', '<th>': '表头单元',
    '<dl': '定义列表', '<dt': '定义列表', '<dd': '定义列表',
    '<aside': '侧栏', '<select': '下拉控件', '<input': '输入控件',
    '<ul': '无序列表', '<ol': '有序列表', '<li': '列表项',
    'class="stat"': '统计块', 'class="tag"': '标签块',
    'class="grid"': '网格布局', 'class="kv"': '键值表',
    'class="steps"': '步骤条', 'class="tick"': '清单条',
    'class="tl"': '时间轴块', 'class="filters"': '筛选栏', 'class="src"': '来源列表',
}
struct = 0
for f in files:
    t = open(f, encoding='utf-8').read()
    for k, label in FORBIDDEN.items():
        n = t.count(k)
        if n:
            out.append('STRUCTURED %s: %s ×%d' % (os.path.basename(f), label, n))
            struct += n
out.append('structured-display hits (should be 0): %d' % struct)

# ── 标签式交互结构
idx = open(os.path.join(DOCS, 'index.html'), encoding='utf-8').read()
out.append('module cards: %d (should be 6)' % idx.count('data-v="'))
out.append('case cards: %d (should be 16)' % idx.count('data-c="'))
out.append('views: %d (should be 6)' % idx.count('<section class="view"'))
out.append('case bodies: %d (should be 16)' % idx.count('<div class="casebody'))

# ── 段落体量：散文是否真的成段
body = idx.split('<main>')[1].split('<footer>')[0] if '<main>' in idx else idx
ps = re.findall(r'<p(?: [^>]*)?>(.*?)</p>', body, re.S)
ps = [re.sub(r'<[^>]+>', '', x).strip() for x in ps]
ps = [x for x in ps if x]
avg = sum(len(x) for x in ps) / max(len(ps), 1)
out.append('paragraphs in main: %d  avg len: %.0f' % (len(ps), avg))
if avg < 60:
    out.append('WARN thin paragraphs')

# ── 内容抽查
for kw in ['苏北', '皖北', '鲁南', '豫东', '洪泽湖', '废黄河', '岱崮', '潘安湖',
           '辐射沙洲', '天沐湖', '芒砀山', '郯城']:
    out.append('index contains %s: %s' % (kw, kw in idx))

# hash 内链抽查：所有 #c/<slug> 的 slug 必须真实存在
slugs = set(re.findall(r'data-c="([^"]+)"', idx))
bad_h = 0
for h in re.findall(r'href="#c/([^"]+)"', idx):
    if h not in slugs:
        out.append('DEADHASH #c/%s' % h)
        bad_h += 1
out.append('bad hash links: %d' % bad_h)

open(os.path.join(ROOT, '_validate.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
