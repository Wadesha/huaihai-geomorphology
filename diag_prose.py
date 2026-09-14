# -*- coding: utf-8 -*-
"""内容诊断：点位完整度、观察描述是否够细、措辞是否机器化、是否混入实测数据。
只读，不改数据。输出 _diag_prose.txt
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_data import (CASES, AGENTS, CONFUSIONS, TIMELINE, FRAMES, HOME,
                       FIELD_ORDER, FIELD_TOOLS, FIELD_BOUND, TIMELINE_NOTE)

AG = {a['id']: a for a in AGENTS}
flags = []


def digits_only(name, s):
    d = re.findall(r'[0-9]', s)
    if d:
        flags.append(f'[digit] {name}：正文混入数字 → {s[:40]}')


for c in CASES:
    nm = c['name']
    for fld in ['slug', 'name', 'sub', 'agent', 'region', 'place', 'intro',
                'spots', 'why', 'read', 'related', 'sources']:
        if not c.get(fld):
            flags.append(f'[missing] {nm}：缺字段 {fld}')
    if c.get('agent') not in AG:
        flags.append(f'[agent] {nm}：营力分类 {c.get("agent")} 不在 AGENTS 中')
    for fld in ['place', 'intro', 'read']:
        digits_only(f'{nm}.{fld}', str(c.get(fld, '')))
    if len(c.get('intro', '')) < 90:
        flags.append(f'[thin] {nm}：导语过短（{len(c.get("intro", ""))} 字）')
    if len(c.get('read', '')) < 110:
        flags.append(f'[thin] {nm}：现场确认段过短（{len(c.get("read", ""))} 字）')

    spots = c.get('spots', [])
    if len(spots) < 4:
        flags.append(f'[spots] {nm}：点位数 {len(spots)}，少于 4')
    heads = []
    for i, s in enumerate(spots, 1):
        for k in ['at', 'go', 'see']:
            if not s.get(k, '').strip():
                flags.append(f'[spots] {nm}：第 {i} 个点位缺 {k}')
        if len(s.get('go', '')) < 45:
            flags.append(f'[thin] {nm}：第 {i} 个点位「怎么到」过短（{len(s.get("go", ""))} 字）')
        if len(s.get('see', '')) < 55:
            flags.append(f'[thin] {nm}：第 {i} 个点位「看什么」过短（{len(s.get("see", ""))} 字）')
        for k in ['go', 'see']:
            digits_only(f'{nm}.spots[{i}].{k}', s.get(k, ''))
            if s.get(k, '').count('——') >= 3:
                flags.append(f'[dash] {nm}：第 {i} 个点位 {k} 破折号 ≥3 处')
        heads.append(s['at'][:2])

    why = c.get('why', [])
    if len(why) < 4:
        flags.append(f'[why] {nm}：原理段数 {len(why)}，少于 4')
    for x in why:
        digits_only(f'{nm}.why', x)
        if len(x) < 45:
            flags.append(f'[thin] {nm}：原理某段过短 → {x[:30]}')

    gos = [s.get('go', '') for s in spots]
    for pos in (0, 1):
        cs = [g[pos] for g in gos if len(g) > pos]
        if len(cs) >= 3 and len(set(cs)) == 1:
            flags.append(f'[repeat] {nm}：{len(cs)} 个点位「怎么到」第 {pos + 1} 字相同（「{cs[0]}」）')
    sees = [s.get('see', '') for s in spots]
    for pos in (0, 1):
        cs = [g[pos] for g in sees if len(g) > pos]
        if len(cs) >= 3 and len(set(cs)) == 1:
            flags.append(f'[repeat] {nm}：{len(cs)} 个点位「看什么」第 {pos + 1} 字相同（「{cs[0]}」）')

    if len(c.get('related', [])) != 2:
        flags.append(f'[related] {nm}：相邻实例数 {len(c.get("related", []))}，应为 2')
    if len(c.get('sources', [])) < 2:
        flags.append(f'[sources] {nm}：来源不足 2 条')
    for t, u in c.get('sources', []):
        if not u.startswith('http'):
            flags.append(f'[sources] {nm}：来源链接异常 → {u[:40]}')
        if re.search(r'[0-9]', t):
            flags.append(f'[sources] {nm}：来源标题含数字 → {t[:40]}')

for name, two, tip in CONFUSIONS:
    if '/' not in name:
        flags.append(f'[confusion] 名称不含分隔符 → {name}')
    if len(two) != 2:
        flags.append(f'[confusion] {name}：对照项不是 2 条')
    if tip.strip()[-1] not in '。！？':
        flags.append(f'[confusion] {name}：判定要点未以句号收尾')
    for x in two:
        digits_only(f'confusion.{name}', x)
    digits_only(f'confusion.{name}.tip', tip)

for a in AGENTS:
    for k in ['id', 'name', 'oneline', 'ctrl', 'body', 'marks']:
        if not a.get(k):
            flags.append(f'[agent] {a.get("name", "?")}：缺字段 {k}')
    if not a['ctrl'].strip().endswith('。'):
        flags.append(f'[agent] {a["name"]}：控制变量未以句号收尾')
    if len(a.get('body', [])) < 4:
        flags.append(f'[agent] {a["name"]}：过程段数 {len(a.get("body", []))}，少于 4')
    if len(a.get('marks', '')) < 30:
        flags.append(f'[agent] {a["name"]}：现场辨认要点过短')
    for x in a.get('body', []):
        digits_only(f'agent.{a["name"]}', x)

for when, what, desc, aid in TIMELINE:
    if aid not in AG:
        flags.append(f'[timeline] {when}：营力分类 {aid} 不在 AGENTS 中')
    for k, v in (('事件', what), ('影响', desc)):
        if not v.strip():
            flags.append(f'[timeline] {when}：{k} 为空')
for t, p1, p2 in FRAMES:
    if len(p1) < 60 or len(p2) < 60:
        flags.append(f'[frame] {t}：段落过短')

for name, paras in HOME['how']:
    if len(paras) < 2:
        flags.append(f'[home] {name}：段落数 {len(paras)}，少于 2')

if len(FIELD_ORDER) < 5:
    flags.append('[field] 观察顺序条目过少')
digits_only('field.tools', FIELD_TOOLS)
digits_only('field.bound', FIELD_BOUND)
for x in TIMELINE_NOTE:
    digits_only('timeline.note', x)

out = [f'cases: {len(CASES)}  agents: {len(AGENTS)}  confusions: {len(CONFUSIONS)}  '
       f'timeline: {len(TIMELINE)}  frames: {len(FRAMES)}',
       f'flags: {len(flags)}', ''] + flags
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_diag_prose.txt'),
     'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out[:6]))
print('(full report in _diag_prose.txt)')
