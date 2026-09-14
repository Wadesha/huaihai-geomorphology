# -*- coding: utf-8 -*-
"""淮海地貌现场手册 —— 静态站点生成器
用法：python build_site.py   输出至 ./docs（GitHub Pages 目录）
数据与渲染分离：本文件只负责把 site_data.py 渲染成 docs/index.html。

版式：单页标签式。顶排短名卡片切换模块，实例模块内有第二排地点短名卡片；
正文仍是连续散文，数字逐条标注来源，冲突口径并列不合并。
"""
import os, html
from site_data import (REGION, AGENTS, CASES, CONFUSIONS, TIMELINE)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'docs')
AGENT_D = {a[0]: a for a in AGENTS}
REGION_ORDER = ['苏北', '皖北', '鲁南', '豫东']
E = html.escape

MODULES = [('cases', '实例'), ('prins', '原理'),
           ('field', '判定'), ('time', '时间轴'), ('srcs', '来源')]

# 每处实例的卡片短名（顶排卡片空间有限，只放 2—4 字）
SHORT = {
    'hongze-lake': '洪泽湖', 'feihuanghe': '废黄河', 'yancheng-tidal': '盐城滩涂',
    'panan-lake': '潘安湖', 'luoma-lake': '骆马湖', 'yuntai-mountain': '云台山',
    'huangcangyu': '皇藏峪', 'huaibei-xiangshan': '相山', 'daigu': '岱崮',
    'tancheng-fault': '郯城地震', 'baodugu-xionger': '熊耳山',
    'lincangcang-plain': '沂沭平原', 'weishan-lake': '南四湖',
    'lankao-sand': '兰考沙地', 'shangqiu-gudao': '商丘故道', 'mangdangshan': '芒砀山',
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
.wrap{max-width:960px;margin:0 auto;padding:0 18px}
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
main{padding-bottom:10px}
.hero{padding:16px 0 4px}
h1{font-size:23px;line-height:1.3;margin:0 0 .3em;letter-spacing:.01em}
h2{font-size:17.5px;line-height:1.35;margin:1.15em 0 .5em;padding-bottom:.25em;border-bottom:1px solid var(--line)}
h3{font-size:15.5px;line-height:1.4;margin:.95em 0 .3em}
h4{font-size:14.5px;margin:.8em 0 .25em}
p{margin:0 0 .55em;text-indent:2em;text-align:justify}
p.lead,p.kicker,p.plain{text-indent:0}
p.lead{color:var(--muted);font-size:15px;line-height:1.6;margin-bottom:.7em}
p.kicker{font-size:12.5px;color:var(--muted);margin-bottom:.25em}
p.plain{color:var(--muted);font-size:13.5px}
.small{font-size:13px;color:var(--muted)}
p.ref{font-size:13px;text-indent:0;color:var(--muted);line-height:1.5;word-break:break-word}
p.ref a{border-bottom-style:dotted}
footer{border-top:1px solid var(--line);margin-top:24px;padding:14px 0 26px;color:var(--muted);font-size:12.5px}
footer .wrap{max-width:960px}
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
  var view='cases',caso=CASES[0];
  if(h.slice(0,2)==='c/'){caso=h.slice(2);}
  else if(h) view=h, caso=null;
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
<meta name="description" content="淮海地貌现场手册：{len(AGENTS)} 类营力原理 + {len(CASES)} 个淮海现存实例 + 野外判定对照。">
<style>{css()}</style></head><body>
<nav>
<div class="topbar"><span class="brand">淮海地貌现场手册</span><span class="spacer"></span>
<button class="tg" onclick="toggleTheme()">明 / 暗</button></div>
<div class="cards" data-k="mod">{mod_cards}</div>
<div class="cards sub" data-k="case" id="casebar" style="display:none">{case_cards}</div>
</nav>
<main>{body}</main>
<footer><div class="wrap">
<p>数字均出自标注的公开来源，多口径并列不换算；实地情况以现场为准。</p>
</div></footer>
<script>{js()}</script>
</body></html>"""


def case_links(cs, sep='、'):
    return sep.join(f'<a href="#c/{c["slug"]}">{E(c["name"])}</a>' for c in cs)


def place_brief(c):
    """place 字段常自带（…）补充说明；索引行里只留主地名，避免双重括号。"""
    return c['place'].split('（')[0].strip() or c['place']


# ─────────────────────────────────────────── 原理

def body_prins():
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

    return f'''
<section class="hero wrap">
<h1>原理：营力、过程与产物</h1>
<p class="lead">地貌形态是内外地质营力相互作用的结果：内力给出骨架与高差，外力按各自的规律去削、去搬、去堆。本页把 {len(AGENTS)} 类营力各讲一节，每节只回答四件事：控制变量、作用过程、留下的产物、野外怎么认。其中「方山与崮」「人为地貌」两类是本站依据淮海实例补充的——它们恰是淮海最值得看的东西。</p>
</section>

<div class="wrap">
<h2>读地貌的四条底层框架</h2>
{fr}

<h2>{len(AGENTS)} 类营力系统</h2>
{blocks}

<h2>怎么用这套框架读一处淮海地方</h2>
<p>先定营力：眼前的形态，多半是几种营力接力或叠加的结果，比如废黄河故道等于黄河流水淤积加上人工筑堤，盐城滩涂等于古长江、古黄河供沙加上海洋动力。再找控制变量：把「为什么会这样」翻译成「哪个变量变了」——洪泽湖与骆马湖的差别，追到最后是湖盆究竟由淤塞而来还是由构造而来。然后问年代：形态相似不等于同时形成，同一条郯庐断裂带上，抬升、陷落与发震发生在完全不同的时间尺度上。最后做排除：列出所有能造成相似形态的成因，逐条排除，构造湖还是夺淮湖、采空塌陷还是构造沉降，靠的都是这一步。</p>
<p>本页的原理表述是通用的地貌学结论；实例数据全部来自各处标注的公开来源，凡无来源的数字一律不写。原理与实例之间不是一一对应关系：一类营力可以解释多处地点，一处地点也常常需要几类营力合起来解释。</p>
</div>
'''


# ─────────────────────────────────────────── 实例

# 现场观察段的开篇导语：按营力分别措辞，避免 16 个实例用同一句话开头
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


def case_inner(c):
    a = AGENT_D[c['agent']]
    name = E(c['name'])

    obs = E(OBS_LEAD.get(c['agent'], '到了现场，以下几处值得逐一对照。')) + ''.join(E(x) for x in c['observe'])
    mech = f'{E(a[4])}落到这一处，机制是这样的：' + ''.join(E(x) for x in c['mech'])
    mean = ''.join(f'{E(k)}，{E(v)}。' for k, v in c['meaning'])
    facts = ''.join(f'{E(k)}，{E(v)}——{E(n)}。' for k, v, n in c['facts'])
    srcs = '；'.join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>'
                    for t, u in c['sources'])
    rel = '、'.join(f'<a href="#c/{s}">{E(short(next(x for x in CASES if x["slug"] == s)))}</a>'
                    for s in c['related'])
    nsrc = len(c['sources'])
    nfact = len(c['facts'])

    sec = []
    sec.append(f'<p class="kicker">{E(c["region"])} · {E(a[1])} · {name}</p>')
    sec.append(f'<h1>{name}</h1>')
    sec.append(f'<p class="lead">{E(c["sub"])}</p>')
    sec.append(f'<p>{name}地处{E(c["place"])}。{coord_clause(c["coord"])}在淮海四片里属{E(c["region"])}，塑造它的营力是{E(a[1])}。它的现状是：{E(c["status"])}。到现场去，{E(c["access"])}</p>')
    sec.append(f'<p>{E(c["summary"])}</p>')

    sec.append('<h2>到哪看，看什么</h2>')
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
    sec.append(f'<p class="ref">相邻的实例还有{rel}，点顶排短名卡片即可切过去看。</p>')
    sec.append(f'<p class="plain">以上观察点与数字均取自公开来源，未做现场复核；实地情况会随季节、水位与工程进展变化，出发前请再核对一次。本页共 {nfact} 组实测数据，全部标注来源。</p>')

    return '\n'.join(sec)


def body_cases():
    cases = ''.join(
        f'<div class="casebody wrap" id="case-{c["slug"]}">{case_inner(c)}</div>'
        for c in CASES)
    return cases


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

    return f'''
<section class="hero wrap">
<h1>野外判定：怎么认，怎么防认错</h1>
<p class="lead">这是一份可以直接带到现场的判定手册：{len(CONFUSIONS)} 组淮海地区高发的易混淆对照，加一份通用的观察顺序。核心原则只有一句——形态相似的成因未必相同，孤立的证据不足以定案。</p>
</section>

<div class="wrap">
<h2>{len(CONFUSIONS)} 组最容易认错的地貌与堆积物</h2>
{conf}

<h2>通用观察顺序</h2>
<p>{od}</p>
<p>这六步的顺序不是随意的：先形态、后物质，是因为形态容易被第一印象带偏；把年代放在最后，是因为前面五步收集到的信息本身就是定年的材料。反过来做，最常见的后果是先入为主——看到高出地面的河床就断定是悬河故道，看到水洼就断定是构造湖。</p>

<h2>测量与记录的最小工具集</h2>
<p>{tools}</p>

<h2>这套方法的边界</h2>
<p>方法页的价值不在于记住这些条目，而在于养成一个习惯：看到形态，先想它还能怎么形成。这才是从「认得」走到「判得准」的分界线。同时也要承认，判定需要相应条件——没有测年手段时，很多结论只能停在相对先后；没有区域资料时，孤立一点的观察很容易被局部现象误导。本站的实例都标出了数据来源，凡有争议的都并列双方口径，正是出于这个理由。</p>
</div>
'''


# ─────────────────────────────────────────── 时间轴

def body_time():
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

    return f'''
<section class="hero wrap">
<h1>时间轴：淮海的地貌是怎么被一步步改写的</h1>
<p class="lead">淮海今天的模样，是几件事叠加出来的结果：燕山期的构造抬升给出了山与残丘，黄河的南徙与北归改写了水系，郯庐断裂带的地震重塑了山体，近现代的人类又用采矿与治水直接改动了地表。下面这条时间轴把这 {len(TIMELINE)} 个锚点串起来，每一个都能在实地找到落点。</p>
</section>

<div class="wrap">
<h2>{len(TIMELINE)} 个时间锚点</h2>
{items}

<h2>年代口径的处理</h2>
<p>年代的口径常有差异，读起来要留意它究竟指什么。岱崮「开始形成」就有 6700 万年前与 177 万年前两种说法，前者指构造背景形成的时间，后者指崮形被削出来的时间，说的其实不是同一件事；郯城地震的震源深度也有 15、23、36 公里等不同的反演结果，这是震源参数反演本身的正常分歧。凡遇此类情形，本站一律并列呈现而不取单值，也不代为换算。</p>
<p>另需说明，时间轴上的次序只表示先后关系，不表示等间隔。构造运动以百万年计，水系改道以百年计，工程活动以十年计，把它们放在同一条线上，尺度差距是被压缩过的。</p>
</div>
'''


# ─────────────────────────────────────────── 来源

def body_srcs():
    blocks = ''
    for c in CASES:
        srcs = '；'.join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>' for t, u in c['sources'])
        blocks += (f'<h3><a href="#c/{c["slug"]}">{E(c["name"])}</a>　{E(c["region"])}　{E(c["place"])}</h3>\n'
                   f'<p class="ref">{len(c["sources"])} 条：{srcs}。</p>\n')

    nsrc = sum(len(c['sources']) for c in CASES)
    return f'''
<section class="hero wrap">
<h1>来源清单</h1>
<p class="lead">本站所有实测数字都出自下列公开来源，共 {nsrc} 条，按实例排列。采集方式是按营力类别逐类联网检索，优先采用期刊论文、政府部门、景区官方与主流媒体的实测数据；同一指标出现多个数值时并列呈现，不做加权也不做换算。</p>
</section>

<div class="wrap">
<h2>按实例分列</h2>
{blocks}

<h2>使用边界</h2>
<p>本站的营力框架是通用地貌学的归纳，实例与数据全部来自上列公开来源；同一指标的多个口径并列呈现，不作换算，也不代人取舍。学术争议只列双方论据与出处，本站不作裁决。</p>
<p>最后一点提醒：这些来源多为机构发布或媒体报道，其中的数字经二次转述，与原始论文口径可能有出入；本站只保证「在此处如此陈述」，不代人判断其权威程度。需要引用于正式场合时，请回到原始文献核对。</p>
</div>
'''


def main():
    # 注意：不要用 shutil.rmtree（本机沙箱会把它改写成回收站操作并失败）。
    # 改为「就地覆盖 + 只清掉本次不再产出的多余文件」。
    body = ''.join(
        f'<section class="view" id="v-{k}">{b}</section>'
        for k, b in [('cases', body_cases()), ('prins', body_prins()),
                     ('field', body_field()), ('time', body_time()),
                     ('srcs', body_srcs())])
    pages = {'index.html': shell(body)}

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
    print('pages: 1 (single-page tabs)  cases:', len(CASES),
          'sources:', sum(len(c['sources']) for c in CASES))


if __name__ == '__main__':
    main()
