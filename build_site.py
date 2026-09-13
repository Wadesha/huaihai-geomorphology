# -*- coding: utf-8 -*-
"""淮海地貌现场手册 —— 静态站点生成器
用法：python build_site.py   输出至 ./docs（GitHub Pages 目录）
依据：杜恒俭等《地貌学及第四纪地质学》的营力体系，重构为淮海地区（苏北/皖北/鲁南/豫东）的现存实例。

版式原则：**全站不用表格、卡片、统计块、步骤条与侧栏**，所有内容以连续散文（大段文字）呈现。
数字仍逐条标注来源，冲突口径并列不合并。
"""
import os, html
from site_data import (BOOK, REGION, AGENTS, REMAP, CASES, CONFUSIONS, TIMELINE)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'docs')
AGENT_D = {a[0]: a for a in AGENTS}
REGION_ORDER = ['苏北', '皖北', '鲁南', '豫东']
E = html.escape


def css():
    return """
*{box-sizing:border-box}
:root{
  --bg:#fbfaf7; --panel:#f6f3ed; --ink:#23201c; --muted:#6b6459; --line:#e3ddd1;
  --rule:#d3cbbd; --accent:#3d6a8f;
}
html[data-theme=dark]{
  --bg:#15171a; --panel:#1e2126; --ink:#e9e6e0; --muted:#9b948a; --line:#2c3036;
  --rule:#3b4046; --accent:#7fb0d4;
}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Songti SC","Source Han Serif SC","Noto Serif CJK SC",Georgia,"PingFang SC","Microsoft YaHei",serif;
  font-size:16.5px;line-height:1.95;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none;border-bottom:1px solid var(--rule)}
a:hover{color:var(--accent);border-color:var(--accent)}
.wrap{max-width:820px;margin:0 auto;padding:0 22px}
nav{position:sticky;top:0;z-index:50;background:var(--bg);border-bottom:1px solid var(--line)}
nav .wrap{max-width:1000px;display:flex;align-items:center;gap:18px;height:52px;flex-wrap:wrap}
nav .brand{font-weight:700;font-size:15.5px;white-space:nowrap;border:0;letter-spacing:.02em}
nav .links{display:flex;gap:15px;flex-wrap:wrap;font-size:14px}
nav .links a{color:var(--muted);border:0;padding:2px 0;border-bottom:2px solid transparent}
nav .links a:hover,nav .links a.on{color:var(--ink);border-color:var(--accent)}
nav .spacer{flex:1}
.tg{background:none;border:1px solid var(--line);color:var(--muted);border-radius:6px;
  padding:3px 10px;font-size:13px;cursor:pointer;font-family:inherit}
main{padding-bottom:20px}
.hero{padding:46px 0 10px}
h1{font-size:30px;line-height:1.4;margin:0 0 .35em;letter-spacing:.01em}
h2{font-size:19.5px;line-height:1.5;margin:2.3em 0 .7em;padding-bottom:.3em;border-bottom:1px solid var(--line)}
h3{font-size:16.5px;line-height:1.6;margin:1.7em 0 .45em}
h4{font-size:15.5px;margin:1.4em 0 .4em}
p{margin:0 0 1em;text-indent:2em;text-align:justify}
p.lead,p.kicker,p.plain{text-indent:0}
p.lead{color:var(--muted);font-size:17px;line-height:1.85;margin-bottom:1.2em}
p.kicker{font-size:13px;color:var(--muted);margin-bottom:.4em}
p.plain{color:var(--muted);font-size:14px}
.small{font-size:13.5px;color:var(--muted)}
p.ref{font-size:14px;text-indent:0;color:var(--muted);line-height:1.85;word-break:break-word}
p.ref a{border-bottom-style:dotted}
footer{border-top:1px solid var(--line);margin-top:56px;padding:24px 0 44px;color:var(--muted);font-size:13.5px}
footer .wrap{max-width:820px}
footer p{text-indent:0;line-height:1.9}
"""


def js_toggle():
    return """
(function(){var t=localStorage.getItem('hhgmtheme');if(t)document.documentElement.setAttribute('data-theme',t);
else if(matchMedia('(prefers-color-scheme:dark)').matches)document.documentElement.setAttribute('data-theme','dark');})();
function toggleTheme(){var c=document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark';
document.documentElement.setAttribute('data-theme',c);localStorage.setItem('hhgmtheme',c);}
"""


def page(title, body, active='', root=''):
    nav_items = [('index.html', '总览', 'index'), ('principles.html', '原理', 'principles'),
                 ('cases/index.html', '实例', 'cases'), ('field.html', '野外判定', 'field'),
                 ('timeline.html', '时间轴', 'timeline'), ('sources.html', '来源', 'sources')]
    links = ''.join(
        f'<a href="{root}{u}" class="{"on" if a==active else ""}">{n}</a>' for u, n, a in nav_items)
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="基于《{E(BOOK['title'])}》（{E(BOOK['author'])}）重构的淮海地貌现场手册：{len(AGENTS)} 类营力原理 + {len(CASES)} 个淮海现存实例 + 野外判定对照。">
<style>{css()}</style></head><body>
<script>{js_toggle()}</script>
<nav><div class="wrap">
<a class="brand" href="{root}index.html">淮海地貌现场手册</a>
<div class="links">{links}</div><div class="spacer"></div>
<button class="tg" onclick="toggleTheme()">明 / 暗</button>
</div></nav>
<main class="wrap">{body}</main>
<footer><div class="wrap">
<p>底本：{E(BOOK['author'])}《{E(BOOK['title'])}》，{BOOK['pages']} 页、{BOOK['chapters']} 章、{BOOK['toc_entries']} 条目录条目；文字层由 {E(BOOK['ocr'])}，扫描件原图未做任何重压缩或替换。</p>
<p>地域范围：{E(REGION['name'])}（{E(REGION['scope'])}）。本站为读书笔记性质的二次整理，非教材替代品。实例数据来自公开来源并逐条标注出处；同一指标的多个口径一律并列呈现、不作换算；凡查不到来源的数字一概不写。</p>
</div></footer>
</body></html>"""


def case_links(cs, sep='、'):
    return sep.join(f'<a href="cases/{c["slug"]}.html">{E(c["name"])}</a>' for c in cs)


def case_links_local(cs, sep='、'):
    return sep.join(f'<a href="{c["slug"]}.html">{E(c["name"])}</a>' for c in cs)


# ─────────────────────────────────────────── 总览

def build_index():
    nsrc = sum(len(c['sources']) for c in CASES)
    rcount = {r: sum(1 for c in CASES if c['region'] == r) for r in REGION_ORDER}

    regions = ''
    for r in REGION_ORDER:
        cs = [c for c in CASES if c['region'] == r]
        items = '；'.join(
            f'<a href="cases/{c["slug"]}.html">{E(c["name"])}</a>，{E(c["sub"])}' for c in cs)
        regions += f'<p>{E(r)}共 {len(cs)} 处：{items}。</p>'

    remap = '；'.join(f'{E(a)}，对应<a href="{u}">{E(b)}</a>' for a, b, u in REMAP)

    agents = ''
    for a in AGENTS:
        rel = [c for c in CASES if c['agent'] == a[0]]
        tail = (f'淮海境内归入这一类的实例有{case_links(rel)}。'
                if rel else '这一类在淮海境内没有选入的实例，把它保留在原理层，是为了在读邻区或更远地方时不缺参照。')
        agents += f'<h3>{E(a[1])}</h3>\n<p>{E(a[2])}。{E(a[4])}{tail}</p>\n'

    body = f'''
<section class="hero">
<h1>把一本教材，落成 {len(CASES)} 个能去的淮海地点</h1>
<p class="lead">《{E(BOOK['title'])}》是按学科体系写成的：先讲地貌学与第四纪地质学的基本问题，再分别讨论各种内外营力，最后落到中国第四纪与研究方法的综述。这套结构适合上课，却不适合「我要去看」，所以本站把它重构到淮海这一片地上——黄河、淮河、沂沭泗三条水系在这里交汇改写，黄泛平原、鲁中南低山丘陵、苏北滨海平原三种大地貌在这里接合。</p>
<p>全书 {BOOK['pages']} 页、{BOOK['chapters']} 章，从中归纳出 {len(AGENTS)} 类营力系统，落到淮海境内 {len(CASES)} 处现存而可到达的地点，覆盖苏北、皖北、鲁南、豫东四片；另配 {len(CONFUSIONS)} 组最容易被认错的地貌对照与 {len(TIMELINE)} 个时间锚点。所有实测数字出自 {nsrc} 条公开来源，逐条标注出处；同一指标的多个口径并列呈现，不换算、不取单值；查不到来源的数字一概不写。</p>
</section>

<h2 id="how">重构逻辑：从章节顺序改到地方顺序</h2>
<p>第一层是原理。原书分论各章被归纳为 {len(AGENTS)} 类营力系统（其中「方山与崮」「人为地貌」两项原书未单列，由本站依据实例补充）。每一类只回答四件事：控制变量是什么、作用过程怎么推进、留下什么产物、野外凭什么认出来。</p>
<p>第二层是实例。{len(CASES)} 处淮海境内现存、可到达的地点，覆盖{'、'.join(REGION_ORDER)}。每一处都给出坐标与可达性、现场观察要点、成因机制链、实测数字与它们说明的问题，以及存争议处的双方口径。</p>
<p>第三层是判定。把淮海最容易认错的 {len(CONFUSIONS)} 组地貌与堆积物摊开对照——悬河故道还是一般河谷、构造湖还是夺淮湖、崮还是丹霞，各自凭什么定案。再往上，一条时间轴把这些地点放回 {len(TIMELINE)} 个锚点，看出它们不是同时形成的。</p>

<h2>地域格局：{E(REGION['name'])}</h2>
<p>{E(REGION['note'])}</p>
{regions}

<h2>原书章节与本站模块的对应</h2>
<p>{remap}。这份对应关系是「读原书」与「去现场」之间的桥：原书的章节顺序不便携带，换成地方顺序之后，每一类营力都能落到几处具体的地名上。</p>

<h2>{len(AGENTS)} 类营力与它们的实例</h2>
{agents}
<p class="plain">说明：营力分类是为方便查阅而作的归纳，同一处地貌常是几种营力接力或叠加的结果，分类不构成对成因的排他判断。</p>
'''
    return page('淮海地貌现场手册 · 总览', body, 'index')


# ─────────────────────────────────────────── 原理

def build_principles():
    frames = [
        ('内力与外力',
         '内力（构造运动、火山活动）制造高差与格局，是「舞台」；外力（风化、流水、岩溶、风、海浪）削平高差，是「演员」。淮海是典型的外力主导区：鲁中南的构造隆起提供了碎屑与高差，黄河、淮河、沂沭泗再把碎屑一遍遍铺成平原。'),
        ('成因、形态与年代',
         '看一处地貌，要回答三个问题：什么营力造成的（成因）、现在长什么样（形态）、什么时候造成的（年代）。三者缺一，解释就不完整。淮海尤其如此——同样叫「湖」，洪泽湖是淤塞成的，骆马湖是构造成的，潘安湖是人为塌陷成的，形态相近而来历全不相同。'),
        ('规模等级与地域分带',
         '地貌是有等级的：大地貌如黄泛平原、鲁中南低山丘陵，中地貌如故道、冲积扇、湖盆，小地貌如沙丘、溶洞、裂谷。同一营力在不同气候与岩性条件下表现完全不同——同为石灰岩，皖北削成残丘，鲁南却成崮。'),
        ('时间是隐藏变量',
         '速率乘以时间等于结果。盐城滩涂是每年约两万亩地成陆，废黄河是七百年淤高四到六米，潘安湖塌陷是几十年的事。动手解释之前先算量级，很多看似「不可能」的现象，其实只是「时间不够」。'),
    ]
    fr = ''.join(f'<h3>{E(t)}</h3>\n<p>{E(d)}</p>\n' for t, d in frames)

    blocks = ''
    for aid, name, chap, color, ctrl in AGENTS:
        rel = [c for c in CASES if c['agent'] == aid]
        tail = (f'淮海境内这一类的实例是{case_links(rel)}。'
                if rel else '这一类在淮海境内没有选入的实例，把它保留在原理层，是为了在读邻区或更远地方时不缺参照。')
        blocks += f'<h3 id="{aid}">{E(name)}</h3>\n<p>{E(chap)}。{E(ctrl)}{tail}</p>\n'

    body = f'''
<section class="hero">
<h1>原理：营力、过程与产物</h1>
<p class="lead">原书第一、二、三章回答的是「地貌是什么」：地貌形态是内外地质营力相互作用的结果。内力给出骨架与高差，外力按各自的规律去削、去搬、去堆。本页把原书分论各章归纳为 {len(AGENTS)} 类营力系统，其中「方山与崮」「人为地貌」两项为教材未单列、由本站依据实例补充。每一类只回答四件事：控制变量、作用过程、留下的产物、野外怎么认。</p>
</section>

<h2>读地貌的四条底层框架</h2>
{fr}

<h2>{len(AGENTS)} 类营力系统</h2>
{blocks}

<h2>怎么用这套框架读一处淮海地方</h2>
<p>先定营力：眼前的形态，多半是几种营力接力或叠加的结果，比如废黄河故道等于黄河流水淤积加上人工筑堤，盐城滩涂等于古长江、古黄河供沙加上海洋动力。再找控制变量：把「为什么会这样」翻译成「哪个变量变了」——洪泽湖与骆马湖的差别，追到最后是湖盆究竟由淤塞而来还是由构造而来。然后问年代：形态相似不等于同时形成，同一条郯庐断裂带上，抬升、陷落与发震发生在完全不同的时间尺度上。最后做排除：列出所有能造成相似形态的成因，逐条排除，构造湖还是夺淮湖、采空塌陷还是构造沉降，靠的都是这一步。</p>
<p>本站所有「原理」表述以原书的章节体系为骨架，实例数据全部来自各页标注的公开来源，凡无来源的数字一律不写。原理与实例之间不是一一对应关系：一类营力可以解释多处地点，一处地点也常常需要几类营力合起来解释。</p>
'''
    return page('原理 · 营力与过程', body, 'principles')


# ─────────────────────────────────────────── 实例页

# 现场观察段的开篇导语：按营力分别措辞，避免 16 个实例页用同一句话开头
OBS_LEAD = {
    'fluvial': '河流留下的痕迹，先看地面高低，再看土质的粗细与分选，然后找人工改造的部分。',
    'lacustrine': '湖泊现场，重点看「水与岸」的关系：水面比岸外高还是低，岸线是自然的还是人工的。',
    'coastal': '海岸现场，看潮汐留下的分带，以及岸线正在向哪个方向推进。',
    'aeolian': '风沙现场，先看颗粒粗细，再看植被与防护工程，最后判断沙的来路。',
    'karst': '岩溶现场，看岩性、溶蚀痕迹，以及残丘与周围平原之间的高差。',
    'slope': '重力地貌现场，看陡崖、裂隙与堆积体，重点在它们的接触关系与规模。',
    'tectonic': '构造现场，找直线状的地形痕迹，以及地层被错开的位置。',
    'mesa': '方山现场，看「顶平、身陡、麓缓」这套三段式是否齐备，再看岩层产状。',
    'anthropogenic': '人为地貌现场，看地形与工程、矿井位置的对应关系，再看治理留下的痕迹。',
}


def coord_clause(coord):
    """coord 字段有时是经纬度、有时是尺度数据，按内容决定怎么起句，避免出现「坐标总面积…」。"""
    txt = E(coord)
    if '°' in coord:
        sep = '' if coord.rstrip().endswith(('。', '；')) else '。'
        return f'坐标{txt}{sep}'
    if coord.rstrip().endswith(('。', '；')):
        return txt
    return f'{txt}。'


def build_case(c):
    a = AGENT_D[c['agent']]
    name = E(c['name'])

    obs = E(OBS_LEAD.get(c['agent'], '到了现场，以下几处值得逐一对照。')) + ''.join(E(x) for x in c['observe'])
    mech = ''.join(E(x) for x in c['mech'])
    mean = ''.join(f'{E(k)}，{E(v)}。' for k, v in c['meaning'])
    facts = ''.join(f'{E(k)}，{E(v)}——{E(n)}。' for k, v, n in c['facts'])
    srcs = '；'.join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>'
                    for t, u in c['sources'])
    rel = '、'.join(f'<a href="{s}.html">{E(next(x["name"] for x in CASES if x["slug"] == s))}</a>'
                    for s in c['related'])
    nsrc = len(c['sources'])
    nfact = len(c['facts'])

    sec = []
    sec.append(f'<p class="kicker"><a href="../index.html">总览</a> · <a href="index.html">实例</a> · {E(c["region"])} · {E(a[1])}</p>')
    sec.append(f'<h1>{name}</h1>')
    sec.append(f'<p class="lead">{E(c["sub"])}</p>')
    sec.append(f'<p>{name}地处{E(c["place"])}。{coord_clause(c["coord"])}在淮海四片里属{E(c["region"])}，在书中的营力体系里归入{E(a[1])}一类，对应{E(a[2])}。它的现状是：{E(c["status"])}。到现场去，{E(c["access"])}</p>')
    sec.append(f'<p>{E(c["summary"])}</p>')

    sec.append('<h2>现场能看到什么</h2>')
    sec.append(f'<p>{obs}</p>')

    sec.append('<h2>背后的原理</h2>')
    sec.append(f'<p>{mech}</p>')

    if c['meaning']:
        sec.append('<h2>这些数字在说什么</h2>')
        sec.append(f'<p>{mean}</p>')

    if c['facts']:
        sec.append('<h2>实测数据</h2>')
        sec.append(f'<p>{facts}</p>')

    if c['dispute']:
        sec.append('<h2>争议与口径</h2>')
        sec.append(f'<p>{E(c["dispute"])}</p>')

    sec.append('<h2>来源</h2>')
    sec.append(f'<p class="ref">本页数据出自 {nsrc} 条公开来源：{srcs}。</p>')
    sec.append(f'<p class="ref">相邻的实例还有{rel}，可以接在一起看；同一类营力下的其他地点见<a href="index.html">实例索引</a>。</p>')
    sec.append(f'<p class="plain">以上观察点与数字均取自公开来源，未做现场复核；实地情况会随季节、水位与工程进展变化，出发前请再核对一次。本页共 {nfact} 组实测数据，全部标注来源。</p>')

    return page(f"{c['name']} · 实例", '\n'.join(sec), 'cases', root='../')


def build_cases_index():
    parts = []
    for r in REGION_ORDER:
        cs = [c for c in CASES if c['region'] == r]
        body = '；'.join(
            f'<a href="{c["slug"]}.html">{E(c["name"])}</a>，{E(c["sub"])}（{E(c["place"])}）' for c in cs)
        parts.append(f'<p>{E(r)}共 {len(cs)} 处：{body}。</p>')

    byagent = ''
    for a in AGENTS:
        cs = [c for c in CASES if c['agent'] == a[0]]
        if not cs:
            continue
        byagent += f'<h3>{E(a[1])}</h3>\n<p>{E(a[2])}。这一类在淮海境内有 {len(cs)} 处可看：'
        byagent += '；'.join(f'<a href="{c["slug"]}.html">{E(c["name"])}</a>，{E(c["sub"])}' for c in cs)
        byagent += '。</p>\n'

    nsrc = sum(len(c['sources']) for c in CASES)
    body = f'''
<section class="hero">
<h1>淮海现存实例索引</h1>
<p class="lead">{len(CASES)} 处淮海境内现存、可到达的地点，覆盖{'、'.join(REGION_ORDER)}。每一处都给出坐标与可达性、现场观察清单、成因机制链、实测数字、争议口径与来源，共 {nsrc} 条公开来源支撑。索引按两种顺序排列：先按地理分区，再按营力类别——想看「一片地方有什么」的按分区读，想追「一类营力在淮海长什么样」的按类别读。</p>
</section>

<h2>按地理分区</h2>
{''.join(parts)}

<h2>按营力类别</h2>
{byagent}

<p class="plain">分区依据是淮海经济区的核心范围（苏北、皖北、鲁南、豫东）。个别地点处在两省交界或地貌过渡带上，归属取其主要部分，不表示界线截然分明。</p>
'''
    return page('淮海实例索引', body, 'cases', root='../')


# ─────────────────────────────────────────── 野外判定

def build_field():
    conf = ''
    for name, two, tip in CONFUSIONS:
        pair = [x.strip() for x in name.split('/')]
        a1 = pair[0] if pair else name
        a2 = pair[1] if len(pair) > 1 else '另一种成因'
        lead2 = '再说另外两种' if len(pair) > 2 else f'再说{a2}'
        conf += (f'<h3>{E(name)}</h3>\n'
                 f'<p>先说{E(a1)}。{E(two[0])}。{lead2}。{E(two[1])}。{E(tip)}</p>\n')

    order = [
        ('远看形态', '先看整体轮廓、规模，以及它与周边地形的关系，定下等级：这是大地貌还是小地貌。'),
        ('近看物质', '看粒度、分选、磨圆、层理与胶结程度。堆积物的「手感」往往比形态更可靠。'),
        ('找接触关系', '与下伏、上覆地层是整合还是不整合，是谁切割谁。这是几乎免费的定年信息。'),
        ('量方向', '砾石长轴定向、斜层理倾向、擦痕方向、断裂走向，方向里藏着古水流与古应力。'),
        ('记空间组合', '孤立的形态多半多解，成组出现才有诊断意义——陡崖、平顶加缓麓三者齐备，才谈得上方山组合。'),
        ('最后问年代', '能测年就测年，不能测年就用相对年代，比如阶地级序、风化程度、覆盖关系。'),
    ]
    od = ''.join(f'<b>{E(t)}</b>，{E(d)}' for t, d in order)

    tools = (
        '罗盘加测距，解决产状、方向与厚度的问题，本站实例里用来量崮的岩层产状（小于 10° 是成崮的前提）与断裂走向；'
        '卷尺与标尺，解决粒度、层厚与位移量，用来量裂谷的宽深、故堤的高差与沙丘的高度；'
        'GPS 或手机定位，解决点位与高程的记录，比如皇藏洞、麦坡遗址这类需要写清坐标的剖面；'
        '遥感影像加地形图，解决区域格局与变化速率，盐城滩涂的成陆、南四湖面积的淤缩、采空塌陷的范围都靠它；'
        '定点重复拍照，解决变化速率，云台山危岩、塌陷地治理、故道湿地的变化都属这一类；'
        '年代学与史料，解决定年与对比，1668 年郯城地震的史料、1855 年铜瓦厢改道、历代治河档案都在这个位置上。'
    )

    body = f'''
<section class="hero">
<h1>野外判定：怎么认，怎么防认错</h1>
<p class="lead">原书第十七章讲的是研究方法。这里把它压缩成可以直接带到现场的东西：{len(CONFUSIONS)} 组淮海地区高发的易混淆对照，加一份通用的观察顺序。核心原则只有一句——形态相似的成因未必相同，孤立的证据不足以定案。</p>
</section>

<h2>{len(CONFUSIONS)} 组最容易认错的地貌与堆积物</h2>
{conf}

<h2>通用观察顺序</h2>
<p>{od}</p>
<p>这六步的顺序不是随意的：先形态、后物质，是因为形态容易被第一印象带偏；把年代放在最后，是因为前面五步收集到的信息本身就是定年的材料。反过来做，最常见的后果是先入为主——看到高出地面的河床就断定是悬河故道，看到水洼就断定是构造湖。</p>

<h2>测量与记录的最小工具集</h2>
<p>{tools}</p>

<h2>这套方法的边界</h2>
<p>方法页的价值不在于记住这些条目，而在于养成一个习惯：看到形态，先想它还能怎么形成。这才是从「认得」走到「判得准」的分界线。同时也要承认，判定需要相应条件——没有测年手段时，很多结论只能停在相对先后；没有区域资料时，孤立一点的观察很容易被局部现象误导。本站的实例页都标出了数据来源，凡有争议的都并列双方口径，正是出于这个理由。</p>
'''
    return page('野外判定', body, 'field')


# ─────────────────────────────────────────── 时间轴

def build_timeline():
    # 每个锚点后接一句短评：按营力分组、组内按出现次序轮换措辞，避免同一句式反复出现
    PH = {
        'mesa': ['崮与方山的物质基础，就此埋下'],
        'karst': ['这一次抬升，决定了后来残丘能站多高'],
        'fluvial': ['水系从这里开始被改写',
                    '又一次改道，把平原重新铺了一遍',
                    '同一条故道，就此换了去向'],
        'lacustrine': ['湖盆的命运在这一步定型',
                       '湖面被人工抬高，并固定下来',
                       '湖水的出路，从此改由人来定',
                       '湖被水坝切成两级，水位改由闸门调度'],
        'tectonic': ['构造带的一次活动，同时改了山体与湖盆'],
        'coastal': ['入海口再挪一次位置',
                    '这片海岸从「资源」变成了「遗产」'],
        'anthropogenic': ['人为营力正式介入地表形态'],
    }
    seen = {}
    items = ''
    for when, what, desc, aid in TIMELINE:
        v = PH.get(aid)
        if not v:
            phrase = '淮海的形态在这一步发生变化'
        else:
            i = seen.get(aid, 0)
            phrase = v[i] if i < len(v) else v[-1]
            seen[aid] = i + 1
        items += f'<p><b>{E(when)}</b>，{E(what)}——{E(desc)}。{E(phrase)}。</p>\n'

    body = f'''
<section class="hero">
<h1>时间轴：淮海的地貌是怎么被一步步改写的</h1>
<p class="lead">淮海今天的模样，是几件事叠加出来的结果：燕山期的构造抬升给出了山与残丘，黄河的南徙与北归改写了水系，郯庐断裂带的地震重塑了山体，近现代的人类又用采矿与治水直接改动了地表。下面这条时间轴把原书第四纪部分与本站实例串起来，{len(TIMELINE)} 个锚点，每一个都能在实地找到落点。</p>
</section>

<h2>{len(TIMELINE)} 个时间锚点</h2>
{items}

<h2>年代口径的处理</h2>
<p>年代的口径常有差异，读起来要留意它究竟指什么。岱崮「开始形成」就有 6700 万年前与 177 万年前两种说法，前者指构造背景形成的时间，后者指崮形被削出来的时间，说的其实不是同一件事；郯城地震的震源深度也有 15、23、36 公里等不同的反演结果，这是震源参数反演本身的正常分歧。凡遇此类情形，本站一律并列呈现而不取单值，也不代为换算。</p>
<p>另需说明，时间轴上的次序只表示先后关系，不表示等间隔。构造运动以百万年计，水系改道以百年计，工程活动以十年计，把它们放在同一条线上，尺度差距是被压缩过的。</p>
'''
    return page('时间轴', body, 'timeline')


# ─────────────────────────────────────────── 来源

def build_sources():
    blocks = ''
    for c in CASES:
        srcs = '；'.join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>' for t, u in c['sources'])
        blocks += (f'<h3><a href="cases/{c["slug"]}.html">{E(c["name"])}</a>　{E(c["region"])}　{E(c["place"])}</h3>\n'
                   f'<p class="ref">{len(c["sources"])} 条：{srcs}。</p>\n')

    nsrc = sum(len(c['sources']) for c in CASES)
    body = f'''
<section class="hero">
<h1>来源清单</h1>
<p class="lead">本站所有实测数字都出自下列公开来源，共 {nsrc} 条，按实例排列。采集方式是以原书的营力体系为线索逐类联网检索，优先采用期刊论文、政府部门、景区官方与主流媒体的实测数据；同一指标出现多个数值时并列呈现，不做加权也不做换算。</p>
</section>

<h2>按实例分列</h2>
{blocks}

<h2>底本</h2>
<p>底本是{E(BOOK['author'])}《{E(BOOK['title'])}》，{BOOK['pages']} 页、{BOOK['chapters']} 章、{BOOK['toc_entries']} 条目录条目。文字层由 {E(BOOK['ocr'])}，扫描件原图未做任何重压缩、缩小或替换。地域范围是{E(REGION['name'])}——{E(REGION['scope'])}。</p>
<p>需要说明的是，本书参考文献页在原扫描件中即已截断，书内第 374 页仅存一页，这是原件缺页，并非处理过程引入。本站的实例数据不依赖该参考文献，全部另行采集公开来源。凡无来源可依的数字一律不写入；同一指标多值并列、不作换算；学术争议只列双方论据、不作裁决。</p>
<p>最后一点提醒：这些来源多为机构发布或媒体报道，其中的数字经二次转述，与原始论文口径可能有出入；本站只保证「在此处如此陈述」，不代人判断其权威程度。需要引用于正式场合时，请回到原始文献核对。</p>
'''
    return page('来源清单', body, 'sources')


def main():
    # 注意：不要用 shutil.rmtree（本机沙箱会把它改写成回收站操作并失败）。
    # 改为「就地覆盖 + 只清掉本次不再产出的多余文件」。
    os.makedirs(os.path.join(OUT, 'cases'), exist_ok=True)

    pages = {
        'index.html': build_index(),
        'principles.html': build_principles(),
        'field.html': build_field(),
        'timeline.html': build_timeline(),
        'sources.html': build_sources(),
        'cases/index.html': build_cases_index(),
    }
    for c in CASES:
        pages[f"cases/{c['slug']}.html"] = build_case(c)

    # 清理旧产物中不在本次清单内的文件（逐个删除，失败不影响构建）
    stale = []
    for dp, dn, fn in os.walk(OUT):
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), OUT).replace('\\', '/')
            if rel not in pages and rel != '.nojekyll':
                stale.append(os.path.join(dp, f))
    for p in stale:
        try:
            os.remove(p)
        except OSError:
            pass

    for rel, s in pages.items():
        with open(os.path.join(OUT, rel), 'w', encoding='utf-8') as fh:
            fh.write(s)
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    if stale:
        print('removed stale:', len(stale))
    print('pages:', 6 + len(CASES), 'cases:', len(CASES),
          'sources:', sum(len(c['sources']) for c in CASES))


if __name__ == '__main__':
    main()
