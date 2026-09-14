# -*- coding: utf-8 -*-
"""淮海地貌现场手册 —— 静态站点生成器
用法：python build_site.py   输出至 ./docs（GitHub Pages 目录）
数据与渲染分离：本文件只负责把 site_data.py 渲染成 docs/index.html。

版式：单页标签式（总览 / 原理 / 实例 / 判定 / 时间轴 / 来源）；
实例页按「到哪看 → 看什么 → 背后的原理 → 现场怎么确认」四段成篇，
正文为连续散文，不引实测数值、不用表格与卡片网格。
"""
import os, html
from site_data import (REGION, AGENTS, CASES, CONFUSIONS, TIMELINE,
                       AGENT_EN, FRAMES, FIELD_ORDER, FIELD_TOOLS,
                       FIELD_BOUND, TIMELINE_NOTE)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'docs')
AGENT_D = {a['id']: a for a in AGENTS}
REGION_ORDER = ['苏北', '皖北', '鲁南', '豫东']
E = html.escape

MODULES = [('cases', '实例'), ('prins', '原理'),
           ('field', '判定'), ('time', '时间轴'), ('srcs', '来源')]

# 每处实例的卡片短名（顶排卡片空间有限，只放 2—4 字）
SHORT = {
    'hongze-lake': '洪泽湖', 'feihuanghe': '废黄河', 'yancheng-tidal': '盐城滩涂',
    'panan-lake': '潘安湖', 'luoma-lake': '骆马湖', 'yuntai-mountain': '云台山',
    'qinshan-island': '秦山岛', 'liyashan': '蛎岈山', 'xinghua-duotian': '垛田',
    'huangcangyu': '皇藏峪', 'huaibei-xiangshan': '相山', 'bagongshan': '八公山',
    'jingshanxia': '荆山峡',
    'daigu': '岱崮', 'tancheng-fault': '郯城地震', 'baodugu-xionger': '熊耳山',
    'lincangcang-plain': '沂沭平原', 'weishan-lake': '南四湖',
    'yishui-cave': '地下大峡', 'guimengding': '龟蒙顶',
    'sishui-quanlin': '泉林', 'liangshan-paleolake': '水泊梁山',
    'lankao-sand': '兰考沙地', 'shangqiu-gudao': '商丘故道', 'mangdangshan': '芒砀山',
    'kaifeng-river': '开封悬河',
}

# 每处实例的一行英文短注（只作地名对照，不进中文正文逻辑）
EN = {
    'hongze-lake': 'Hongze Lake — a "hanging" lake raised by silt and dikes',
    'feihuanghe': 'The Abandoned Yellow River — a dead channel that still divides two drainage systems',
    'yancheng-tidal': 'Yancheng Coastal Wetlands and the Radial Sand Ridges',
    'panan-lake': "Pan'an Lake — a coal-subsidence basin turned wetland",
    'luoma-lake': 'Luoma Lake — a fault-basin lake',
    'yuntai-mountain': 'Yuntai Mountain — a coastal range once an island in the sea',
    'qinshan-island': 'Qinshan Island — a tombolo in the making',
    'liyashan': 'Liya Mountain — an oyster reef rising at low tide',
    'xinghua-duotian': 'Duotian of Xinghua — raised fields built out of the marsh',
    'huangcangyu': 'Huangcangyu — limestone hills north of the Huaibei plain',
    'huaibei-xiangshan': 'Xiangshan, Huaibei — a karst outlier on the plain',
    'bagongshan': 'Bagong Mountain — limestone hills at the middle Huai',
    'jingshanxia': 'Jingshan Gorge and Tushan — where the Huai squeezes between two mountains',
    'daigu': 'The Dai-Gu — tabletop mountains of Mengyin',
    'tancheng-fault': 'Tancheng and the Tan-Lu Fault — the great earthquake of the early Qing',
    'baodugu-xionger': "Baodugu and Xiong'er Mountain — a gu and its collapsed twin",
    'lincangcang-plain': 'The Lin-Tan-Cang Plain — alluvium laid down by the Yi and Shu rivers',
    'weishan-lake': 'The Nansi Lakes — a chain of shallow lakes on a subsiding line',
    'yishui-cave': 'The Underground Grand Canyon of Yishui — a karst cave river',
    'guimengding': 'Guimengding — the roof of the Mengshan range',
    'sishui-quanlin': 'Quanlin Springs — where the Si River is born',
    'liangshan-paleolake': 'Liangshan and the Paleolake — where a great lake silted away',
    'lankao-sand': 'Lankao Sand Fields — dunes left on the old floodplain',
    'shangqiu-gudao': 'The Old Channel at Shangqiu and Tianmu Lake',
    'mangdangshan': 'Mangdangshan — low karst hills on the plain',
    'kaifeng-river': 'Kaifeng — the hanging river, and cities buried under cities',
}


def short(c):
    return SHORT.get(c['slug'], c['name'][:3])


def css():
    return """
*{box-sizing:border-box}
:root{
  --bg:#fbfaf7; --panel:#f6f3ed; --ink:#23201c; --muted:#6b6459; --line:#e3ddd1;
  --rule:#d3cbbd; --accent:#3d6a8f; --accent-soft:#e7eef4;
}
html[data-theme=dark]{
  --bg:#15171a; --panel:#1e2126; --ink:#e9e6e0; --muted:#9b948a; --line:#2c3036;
  --rule:#3b4046; --accent:#7fb0d4; --accent-soft:#24303a;
}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Songti SC","Source Han Serif SC","Noto Serif CJK SC",Georgia,"PingFang SC","Microsoft YaHei",serif;
  font-size:15px;line-height:1.62;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none;border-bottom:1px solid var(--rule)}
a:hover{color:var(--accent);border-color:var(--accent)}
.wrap{max-width:900px;margin:0 auto;padding:0 18px}
nav{position:sticky;top:0;z-index:50;background:var(--bg);border-bottom:1px solid var(--line);
  padding-bottom:5px}
.topbar{max-width:1000px;margin:0 auto;display:flex;align-items:center;gap:14px;height:38px;padding:0 18px;flex-wrap:wrap}
.topbar .brand{font-weight:700;font-size:14.5px;white-space:nowrap;border:0;letter-spacing:.02em}
.topbar .spacer{flex:1}
.tg{background:none;border:1px solid var(--line);color:var(--muted);border-radius:5px;
  padding:2px 8px;font-size:12px;cursor:pointer;font-family:inherit}
.cards{max-width:1000px;margin:0 auto;padding:1px 18px 0;display:flex;gap:5px;flex-wrap:wrap}
.cards button{font-family:inherit;font-size:13px;line-height:1.3;color:var(--muted);
  background:var(--panel);border:1px solid var(--line);border-radius:7px;
  padding:3px 10px;cursor:pointer;transition:all .12s ease}
.cards button:hover{color:var(--accent);border-color:var(--accent)}
.cards button.on{color:var(--accent);border-color:var(--accent);background:var(--accent-soft);font-weight:700}
.cards.sub{padding-top:5px}
.cards.sub button{font-size:12.5px;padding:2px 8px;border-radius:6px}
.view{display:none}
.view.on{display:block}
.casebody{display:none}
.casebody.on{display:block}
main{padding-bottom:10px}
.hero{padding:16px 0 4px}
h1{font-size:23px;line-height:1.3;margin:0 0 .3em;letter-spacing:.01em}
h2{font-size:17.5px;line-height:1.35;margin:1.15em 0 .5em;padding-bottom:.25em;border-bottom:1px solid var(--line)}
h3{font-size:15.5px;line-height:1.4;margin:1em 0 .3em}
h4{font-size:14.5px;margin:.8em 0 .25em}
.en{font-size:.72em;color:var(--muted);font-weight:400;font-family:Georgia,"Times New Roman",serif;margin-left:.45em;letter-spacing:.01em;white-space:nowrap}
p{margin:0 0 .55em;text-indent:2em;text-align:justify}
p.lead,p.kicker,p.plain{text-indent:0}
p.lead{color:var(--muted);font-size:15px;line-height:1.6;margin-bottom:.7em}
p.kicker{font-size:12.5px;color:var(--muted);margin-bottom:.25em}
p.en{font-size:13px;color:var(--muted);font-style:italic;font-family:Georgia,"Times New Roman",serif;text-indent:0;margin:-0.1em 0 .6em;line-height:1.45}
p.plain{color:var(--muted);font-size:13.5px}
p.ref{font-size:13px;text-indent:0;color:var(--muted);line-height:1.5;word-break:break-word}
p.ref a{border-bottom-style:dotted}
.en-tag{font-size:12px;color:var(--muted);font-style:italic;font-family:Georgia,"Times New Roman",serif;white-space:nowrap}
@media(max-width:760px){.en-tag{display:none}}
footer{border-top:1px solid var(--line);margin-top:24px;padding:14px 0 26px;color:var(--muted);font-size:12.5px}
footer .wrap{max-width:900px}
footer p{text-indent:0;line-height:1.6}
"""


def js():
    return """
(function(){var t=localStorage.getItem('hhgmtheme');if(t)document.documentElement.setAttribute('data-theme',t);
else if(matchMedia('(prefers-color-scheme:dark)').matches)document.documentElement.setAttribute('data-theme','dark');})();
function toggleTheme(){var c=document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark';
document.documentElement.setAttribute('data-theme',c);localStorage.setItem('hhgmtheme',c);}
var CASES=%s;
function route(){
  var h=decodeURIComponent(location.hash.replace(/^#\\/?/,''));
  var view='cases',caso=null;
  if(h.slice(0,2)==='c/'){view='cases';caso=h.slice(2);}
  else if(h){view=h;}
  if(!document.getElementById('v-'+view)) view='cases';
  if(view==='cases'&&(caso===null||CASES.indexOf(caso)<0)) caso=CASES[0];
  var vs=document.querySelectorAll('.view');
  for(var i=0;i<vs.length;i++) vs[i].classList.remove('on');
  document.getElementById('v-'+view).classList.add('on');
  var bs=document.querySelectorAll('.cards[data-k=mod] button');
  for(var j=0;j<bs.length;j++) bs[j].classList.toggle('on',bs[j].getAttribute('data-v')===view);
  var cs=document.querySelectorAll('.cards[data-k=case] button');
  for(var k=0;k<cs.length;k++) cs[k].classList.toggle('on',cs[k].getAttribute('data-c')===caso);
  document.getElementById('casebar').style.display=(view==='cases')?'flex':'none';
  var cts=document.querySelectorAll('.casebody');
  for(var m=0;m<cts.length;m++) cts[m].classList.remove('on');
  if(view==='cases'){
    var el=document.getElementById('case-'+caso);
    if(el) el.classList.add('on');
  }
  window.scrollTo(0,0);
}
window.addEventListener('hashchange',route);
route();
""" % json_dumps([c['slug'] for c in CASES])


def json_dumps(arr):
    return '[' + ','.join('"%s"' % a for a in arr) + ']'


def shell(body):
    mod_cards = ''
    for k, n in MODULES:
        cls = ' class="on"' if k == 'cases' else ''
        dest = 'c/' if k == 'cases' else k
        mod_cards += (f'<button data-v="{k}"{cls} '
                      f'onclick="location.hash=\'{dest}\'">{E(n)}</button>')
    case_cards = ''.join(
        f'<button data-c="{c["slug"]}" onclick="location.hash=\'c/{c["slug"]}\'">{E(short(c))}</button>'
        for c in CASES)
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>淮海地貌现场手册</title>
<meta name="description" content="淮海地貌现场手册：{len(AGENTS)} 类营力的原理，{len(CASES)} 处淮海现存地点的到哪看、看什么与判定方法。">
<style>{css()}</style></head><body>
<nav>
<div class="topbar"><span class="brand">淮海地貌现场手册</span><span class="en-tag">A field guide to the landforms of the Huaihai region</span><span class="spacer"></span>
<button class="tg" onclick="toggleTheme()">明 / 暗</button></div>
<div class="cards" data-k="mod">{mod_cards}</div>
<div class="cards sub" data-k="case" id="casebar" style="display:none">{case_cards}</div>
</nav>
<main>{body}</main>
<footer><div class="wrap">
<p>本手册写的是位置、现象、过程与判据；实地情况会随季节、水位与工程进展变化，出发前请再确认一次当下的通行与开放情况。</p>
</div></footer>
<script>{js()}</script>
</body></html>"""


def case_links(cs, sep='、'):
    return sep.join(f'<a href="#c/{c["slug"]}">{E(c["name"])}</a>' for c in cs)


# ─────────────────────────────────────────── 原理

def body_prins():
    fr = ''
    for t, p1, p2 in FRAMES:
        fr += f'<h3>{E(t)}</h3>\n<p>{E(p1)}</p>\n<p>{E(p2)}</p>\n'

    blocks = ''
    for a in AGENTS:
        rel = [c for c in CASES if c['agent'] == a['id']]
        tail = (f'在淮海，这一类的实例是{case_links(rel)}。把它们放在一起看，能比较出同一个机制在不同条件下的差别。'
                if rel else '这一类在淮海境内没有选入的实例，保留在原理层，是为了读邻区或更远的地方时不缺参照。')
        body = ''.join(f'<p>{E(x)}</p>\n' for x in a['body'])
        blocks += (f'<h3 id="{a["id"]}">{E(a["name"])} <span class="en">{E(AGENT_EN.get(a["id"], ""))}</span></h3>\n'
                   f'<p class="lead">{E(a["oneline"])}。{E(a["ctrl"])}</p>\n'
                   f'{body}'
                   f'<p>{tail}</p>\n'
                   f'<p>现场怎么认：{E(a["marks"])}</p>\n')

    return f'''
<section class="hero wrap">
<h1>原理：营力是怎么做出形态的</h1>
<p class="lead">地貌形态是内外地质营力相互作用的结果：内力给出骨架与高差，外力按各自的规律去削、去搬、去堆。这一页把 {len(AGENTS)} 类营力各讲一节，每节回答三件事——过程是怎么走的、控制变量是什么、到了现场靠什么辨认。看见形态只是第一步，能说出它是被什么过程做出来的，才算读懂。</p>
</section>

<div class="wrap">
<h2>读地貌的四条底层框架</h2>
{fr}

<h2>{len(AGENTS)} 类营力系统</h2>
{blocks}

<h2>怎么用这套框架读一处地方</h2>
<p>先定营力。眼前的形态多半是几种营力接力或叠加的结果：废黄河故道等于黄河流水淤积加上人工筑堤，盐城滩涂等于古长江、古黄河供沙加上海洋动力，潘安湖等于采煤塌陷加上治理复垦。先认出参与者，再谈过程。</p>
<p>再找控制变量。把「为什么会这样」翻译成「哪个变量变了」——洪泽湖与骆马湖的差别，追到最后是湖盆究竟由淤塞而来还是由构造而来；同为灰岩，皖北被削成孤丘、鲁南被削成崮，差别在岩层产状与抬升幅度。变量定了，解释就有了方向。</p>
<p>然后问时间。形态相似不等于同时形成：同一条郯庐断裂带上，抬升、陷落与发震发生在完全不同的时间尺度上；一片滩涂的推进与一道故堤的淤高，也不是同一个速率量级的事。量级对了，结论才不会离谱。</p>
<p>最后做排除。列出所有能造成相似形态的成因，逐条排除：构造湖还是夺淮湖，采空塌陷还是构造沉降，海蚀残留还是人工削坡。到这一步，剩下的就是可以带到现场去检验的假设。</p>
<p>本页的原理表述是通用的地貌学结论；实例部分的观察点与判断依据逐条写在各自页面里，方便到现场对照。原理与实例之间不是一一对应关系：一类营力可以解释多处地点，一处地点也常常需要几类营力合起来解释。</p>
</div>
'''


# ─────────────────────────────────────────── 实例

def case_inner(c):
    a = AGENT_D[c['agent']]
    name = E(c['name'])

    spots = ''
    for s in c['spots']:
        spots += (f'<h3>{E(s["at"])}</h3>\n'
                  f'<p>{E(s["go"])}</p>\n'
                  f'<p>{E(s["see"])}</p>\n')

    why = f'<p>{E(a["oneline"])}。落到这一处，过程是这样一步步走下来的：</p>\n'
    why += ''.join(f'<p>{E(x)}</p>\n' for x in c['why'])
    why += (f'<p>把这一段过程和眼前的形态对着看，就能明白为什么它长成这样：'
            f'物质与条件决定了它能变成什么，过程决定了它现在是什么样子，时间决定了它走到哪一步。</p>\n')

    srcs = '；'.join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>'
                    for t, u in c['sources'])
    rel = '、'.join(f'<a href="#c/{s}">{E(short(next(x for x in CASES if x["slug"] == s)))}</a>'
                    for s in c['related'])

    sec = []
    sec.append(f'<p class="kicker">{E(c["region"])} · {E(a["name"])} <span class="en">{E(AGENT_EN.get(c["agent"], ""))}</span> · {E(name)}</p>')
    sec.append(f'<h1>{name}</h1>')
    en = EN.get(c['slug'])
    if en:
        sec.append(f'<p class="en">{E(en)}</p>')
    sec.append(f'<p class="lead">{E(c["sub"])}</p>')
    sec.append(f'<p>{name}在{E(c["place"])}。塑造它的营力是{E(a["name"])}——{E(a["oneline"])}。'
               f'{E(c["intro"])}</p>')

    sec.append('<h2>到哪看，看什么</h2>')
    sec.append('<p class="plain">下面按点位排开。每一处先写怎么到、在哪儿站定、什么时间或条件去最合适，接着写真到了那里该看什么、拿什么当凭据。点位之间的顺序就是一条顺路的走法。</p>')
    sec.append(spots)

    sec.append('<h2>背后的原理</h2>')
    sec.append(why)

    sec.append('<h2>现场怎么确认</h2>')
    sec.append(f'<p>{E(c["read"])}</p>')

    sec.append('<h2>来源</h2>')
    sec.append(f'<p class="ref">这一页的观察点与判断依据对照了下列公开资料：{srcs}。</p>')
    sec.append(f'<p class="ref">相邻的实例还有{rel}，点顶排短名卡片即可切过去看。</p>')
    sec.append('<p class="plain">以上点位与判断依据是据公开资料整理的现场观察笔记，未做逐点实测；季节、水位与工程进度都会改变同一处景观的面貌，出发前请再核对一次当日的通行与开放情况。</p>')

    return '\n'.join(sec)


def body_cases():
    return ''.join(
        f'<div class="casebody wrap" id="case-{c["slug"]}">{case_inner(c)}</div>'
        for c in CASES)


# ─────────────────────────────────────────── 野外判定

def body_field():
    conf = ''
    for name, two, tip in CONFUSIONS:
        pair = [x.strip() for x in name.split('/')]
        a1 = pair[0] if pair else name
        a2 = pair[1] if len(pair) > 1 else '另一种成因'
        lead2 = '再说另外两种' if len(pair) > 2 else f'再说{a2}'
        conf += (f'<h3>{E(name)}</h3>\n'
                 f'<p>先说{E(a1)}。{E(two[0])}。{lead2}。{E(two[1])}。{E(tip)}</p>\n')

    od = ''.join(f'<p><b>{E(t)}</b>，{E(d)}</p>' for t, d in FIELD_ORDER)

    return f'''
<section class="hero wrap">
<h1>野外判定：怎么认，怎么防认错</h1>
<p class="lead">这是一份可以直接带到现场的判定手册：{len(CONFUSIONS)} 组淮海高发的易混淆对照，加一套通用的观察顺序。核心原则只有一句——形态相似的成因未必相同，孤立的证据不足以定案。</p>
</section>

<div class="wrap">
<h2>{len(CONFUSIONS)} 组最容易认错的地貌与堆积物</h2>
{conf}

<h2>通用观察顺序</h2>
{od}
<p>这六步的顺序不是随意的。先形态、后物质，是因为形态容易被第一印象带偏；把年代放在最后，是因为前面五步收集到的信息本身就是定年的材料。反过来做，最常见的后果是先入为主——看到高出地面的河床就断定是悬河故道，看到水洼就断定是构造湖。</p>

<h2>测量与记录的最小工具集</h2>
<p>{E(FIELD_TOOLS)}</p>

<h2>这套方法的边界</h2>
<p>{E(FIELD_BOUND)}</p>
</div>
'''


# ─────────────────────────────────────────── 时间轴

def body_time():
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
        'coastal': ['入海口的位置，再挪一次',
                    '这片海岸从资源变成了遗产'],
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

    note = ''.join(f'<p>{E(x)}</p>\n' for x in TIMELINE_NOTE)

    return f'''
<section class="hero wrap">
<h1>时间轴：淮海的地貌是怎么被一步步改写的</h1>
<p class="lead">淮海今天的模样是几件事叠出来的：古老岩层就位与构造抬升给出山与残丘，黄河的南徙与北归改写水系，断裂带的强震重塑山体，近现代的人又用采矿与治水直接改动地表。下面这 {len(TIMELINE)} 个锚点串起这条线，每一个都能在实地找到落点。</p>
</section>

<div class="wrap">
<h2>{len(TIMELINE)} 个时间锚点</h2>
{items}

<h2>怎么读这条时间轴</h2>
{note}
</div>
'''


# ─────────────────────────────────────────── 来源

def body_srcs():
    blocks = ''
    for c in CASES:
        srcs = '；'.join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>' for t, u in c['sources'])
        blocks += (f'<h3><a href="#c/{c["slug"]}">{E(c["name"])}</a>　{E(c["region"])}　{E(c["place"])}</h3>\n'
                   f'<p class="ref">{srcs}。</p>\n')

    nsrc = sum(len(c['sources']) for c in CASES)
    return f'''
<section class="hero wrap">
<h1>来源清单</h1>
<p class="lead">本手册各页的位置、现象与判断依据对照了下列公开资料，共 {nsrc} 条，按实例排列。采集方式是按营力类别逐类检索，优先采用政府部门、景区官方、专业机构与主流媒体的公开材料。</p>
</section>

<div class="wrap">
<h2>按实例分列</h2>
{blocks}

<h2>使用边界</h2>
<p>手册里的营力框架是通用地貌学的归纳，观察点与判断依据来自上列公开资料与野外常识，不替代你自己的现场核对。同一处地点在不同季节、不同水位与不同工程进度下，可见的现象会不一样；点位之间的通行条件也会变化。</p>
<p>另需说明，这些来源多为机构发布或媒体报道，内容经二次转述；本手册只保证「在此处如此表述」，不代人判断其权威程度。需要引用于正式场合时，请回到原始文献核对。</p>
<p>最后一句提醒：写这份手册的目的是让你到了现场知道往哪儿站、往哪儿看、看到的东西意味着什么。凡是与现场不符的地方，以现场为准。</p>
</div>
'''


def main():
    # 注意：不要用 shutil.rmtree（本机沙箱会把它改写成回收站操作并失败）。
    # 改为「就地覆盖 + 只清掉本次不再产出的多余文件」。
    body = ''.join(
        f'<section class="view" id="v-{k}">{b}</section>'
        for k, b in [('prins', body_prins()), ('cases', body_cases()),
                     ('field', body_field()), ('time', body_time()), ('srcs', body_srcs())])
    pages = {'index.html': shell(body)}

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
    print('pages: 1 (single-page tabs)  cases:', len(CASES),
          'sources:', sum(len(c['sources']) for c in CASES))


if __name__ == '__main__':
    main()
