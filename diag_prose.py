# -*- coding: utf-8 -*-
"""散文衔接诊断：找出「标题词在解释里重复」「破折号叠用」「括号相邻」等影响阅读的地方。
只读，不改数据。输出 _diag_prose.txt
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_data import CASES, AGENTS, CONFUSIONS, REMAP

AG = {a[0]: a for a in AGENTS}
flags = []

for c in CASES:
    for k, v in c.get('meaning', []):
        k2, v2 = k.strip(), v.strip()
        if k2 and k2 in v2:
            flags.append(f"[meaning] {c['name']}：标题词「{k2}」在解释里重复 → {v2[:34]}")
        if v2.count('——') >= 2:
            flags.append(f"[meaning] {c['name']}：解释里破折号 ≥2 处 → {v2[:34]}")
    for k, v, n in c.get('facts', []):
        k2, v2, n2 = k.strip(), v.strip(), n.strip()
        if k2 and k2 in v2:
            flags.append(f"[facts] {c['name']}：标题词「{k2}」在数值里重复 → {v2[:34]}")
        if k2 and k2 in n2:
            flags.append(f"[facts] {c['name']}：标题词「{k2}」在注里重复 → {n2[:34]}")
        if '——' in n2:
            flags.append(f"[facts] {c['name']}：注里已含破折号，前面再加会叠用 → {n2[:34]}")
        if v2.endswith('）') and n2.startswith('（'):
            flags.append(f"[facts] {c['name']}：括号相邻 → {v2[-16:]} + {n2[:16]}")
        lead = (k2 + '，' + v2)
        if '（' in v2 and lead.count('（') - v2.count('）') > 0:
            flags.append(f"[facts] {c['name']}：括号不配对 → {lead[:40]}")
    # 观察清单首词重复（“看…看…看…”）
    obs = c.get('observe', [])
    heads = [re.match(r'^(.{1,6}?)[：，]', x) for x in obs]
    heads = [h.group(1) for h in heads if h]
    if len(heads) >= 3 and len(set(h[0] for h in heads)) == 1:
        flags.append(f"[observe] {c['name']}：{len(heads)} 条观察均以「{heads[0][0]}」起句")
    # 必备字段
    for fld in ['observe', 'mech', 'meaning', 'facts', 'dispute', 'sources', 'access', 'coord', 'status']:
        if not c.get(fld):
            flags.append(f"[missing] {c['name']}：缺字段 {fld}")

for name, two, tip in CONFUSIONS:
    if '/' not in name:
        flags.append(f"[confusion] 名称不含分隔符 → {name}")
    if len(two) != 2:
        flags.append(f"[confusion] {name}：对照项不是 2 条")
    if tip.strip()[-1] not in '。！？':
        flags.append(f"[confusion] {name}：判定要点未以句号收尾")
    if tip.strip() in [x.strip() for x in two]:
        flags.append(f"[confusion] {name}：判定要点与对照项重复")

for a in AGENTS:
    if not a[4].strip().endswith('。'):
        flags.append(f"[agent] {a[1]}：控制变量未以句号收尾 → {a[4][-14:]}")
    if len(a) != 5:
        flags.append(f"[agent] {a[1]}：字段数为 {len(a)}，应为 5")

for x in REMAP:
    if len(x) != 3:
        flags.append(f"[remap] {x[0]}：字段数 {len(x)}")

out = [f'cases: {len(CASES)}  agents: {len(AGENTS)}  confusions: {len(CONFUSIONS)}  remap: {len(REMAP)}',
       f'flags: {len(flags)}', ''] + flags
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_diag_prose.txt'),
     'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
