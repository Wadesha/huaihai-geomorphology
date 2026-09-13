# -*- coding: utf-8 -*-
"""站点自检：标签闭合 + 内链 + 「纯散文版式」约束 + 关键内容抽查。
结果写入 _validate.txt
"""
import os, re, glob, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, 'docs')
out = []

files = sorted(glob.glob(os.path.join(DOCS, '**', '*.html'), recursive=True))
out.append('html files: %d' % len(files))

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
    for href in re.findall(r'href="([^"#]+)"', t):
        if href.startswith('http') or href.startswith('mailto'):
            continue
        p = os.path.normpath(os.path.join(os.path.dirname(f), href))
        if not os.path.isfile(p):
            out.append('DEAD %s -> %s' % (os.path.basename(f), href))
            bad += 1

out.append('link/tag problems: %d' % bad)

# ── 纯散文版式约束：不得出现表格、卡片、统计块、步骤条、标签块、侧栏、筛选控件
FORBIDDEN = {
    '<table': '表格',
    '<tbody': '表格',
    '<thead': '表格',
    '<tr>': '表格行',
    '<td': '表格单元',
    '<th>': '表头单元',
    '<dl': '定义列表',
    '<dt': '定义列表',
    '<dd': '定义列表',
    '<aside': '侧栏',
    '<select': '下拉控件',
    '<input': '输入控件',
    '<ul': '无序列表',
    '<ol': '有序列表',
    '<li': '列表项',
    'class="card"': '卡片',
    'class="stat"': '统计块',
    'class="tag"': '标签块',
    'class="case"': '卡片',
    'class="grid"': '网格布局',
    'class="kv"': '键值表',
    'class="steps"': '步骤条',
    'class="tick"': '清单条',
    'class="tl"': '时间轴块',
    'class="filters"': '筛选栏',
    'class="src"': '来源列表',
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

# ── 段落体量：散文是否真的成段
tot_p = 0
short = []
for f in files:
    t = open(f, encoding='utf-8').read()
    ps = re.findall(r'<p(?: [^>]*)?>(.*?)</p>', t, re.S)
    ps = [re.sub(r'<[^>]+>', '', x).strip() for x in ps]
    ps = [x for x in ps if x]
    tot_p += len(ps)
    if ps:
        avg = sum(len(x) for x in ps) / len(ps)
        if avg < 60:
            short.append('%s avg=%.0f' % (os.path.basename(f), avg))
out.append('paragraphs total: %d' % tot_p)
out.append('files with thin paragraphs: %s' % (', '.join(short) if short else 'none'))

# ── 内容抽查
idx = open(os.path.join(DOCS, 'index.html'), encoding='utf-8').read()
for kw in ['苏北', '皖北', '鲁南', '豫东', '洪泽湖', '废黄河', '岱崮', '潘安湖', '辐射沙洲', '天沐湖']:
    out.append('index contains %s: %s' % (kw, kw in idx))

for slug in ['hongze-lake', 'feihuanghe', 'tancheng-fault', 'daigu', 'panan-lake', 'yancheng-tidal']:
    p = os.path.join(DOCS, 'cases', slug + '.html')
    t = open(p, encoding='utf-8').read()
    ps = re.findall(r'<p(?: [^>]*)?>(.*?)</p>', t, re.S)
    plain = re.sub(r'<[^>]+>', '', t)
    out.append('%s: h1=%d p=%d src_links=%d chars=%d'
               % (slug, len(re.findall(r'<h1', t)), len(ps), t.count('target="_blank"'), len(plain)))

open(os.path.join(ROOT, '_validate.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
