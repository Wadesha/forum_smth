# -*- coding: utf-8 -*-
"""统一生成器：把本地 CSV/XLS 版面快照转为多版面静态站（GitHub Pages 可直接托管）。
输出：
  index.html            -> 版面索引（根）
  boards/<slug>.html    -> 各版面主题列表（搜索/排序/分页，离线可用）
原始数据文件(*.xls / 水木社区手机版*.csv) 不入库（见 .gitignore），仅生成的 HTML 入库。
"""
import os, csv, glob, json, re

BASE = r"C:\Users\wade\OneDrive\forum_smth"
BOARDS_DIR = os.path.join(BASE, "boards")

# ---------- 版面配置 ----------
XLS_MAP = {
    "smth_Geography.xls":        ("Geography",       "地理"),
    "smth_Career_Servant.xls":   ("Career_Servant",  "职场·公务员"),
    "smth_DigiHome.xls":         ("DigiHome",        "数码之家"),
    "smth_Entrepreneur.xls":     ("Entrepreneur",    "创业"),
    "smth_Flyers.xls":           ("Flyers",          "飞行"),
    "smth_GreenAuto.xls":        ("GreenAuto",       "绿色汽车"),
    "smth_METech.xls":           ("METech",          "微电子"),
    "smth_MaiFang.xls":          ("MaiFang",         "买房"),
    "smth_MyWallet.xls":         ("MyWallet",        "钱包"),
    "smth_OurEstate1.xls":       ("OurEstate",       "我们的小区"),
    "smth_PieLove.xls":          ("PieLove",         "馅儿爱情"),
    "smth_Railway.xls":          ("Railway",         "铁路"),
    "smth_RealEstate_review.xls":("RealEstate_review","房产观察"),
}
SKIP_XLS = {"smth1.xls", "smth2.xls"}

CSV_MAP = {
    "水木社区手机版房屋出租houserent.csv":   ("HouseRent", "房屋出租"),
    "水木社区手机版旅游Travel.csv":          ("Travel",    "旅游"),
    "水木社区手机版电视秀版TVShow.csv":      ("TVShow",    "电视秀"),
    "水木社区手机版谈情说爱版.csv":          ("Love",      "谈情说爱"),
}
SKIP_CSV = {"水木社区手机版房屋出租houserent(1).csv"}

DELETED = "原帖已删除"

# ---------- 工具 ----------
def clean(s):
    return (s or "").replace("\xa0", " ").replace("\u3000", " ").strip()

def parse_da(s):
    """'2024-02-05 author' / '13:05:11 author' -> (date, author)"""
    s = clean(s)
    m = re.match(r"^(\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2}:\d{2})\s*(.*)$", s)
    if m:
        return m.group(1), clean(m.group(2))
    return "", s

def linkable(author):
    return bool(author) and author != DELETED and not author.startswith("原帖")

def parse_xls(path, board):
    import xlrd
    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_index(0)
    rows = []
    start = 0
    # 若首行像表头则跳过
    if clean(sh.cell_value(0, 0)) in ("标题", "title", "Title"):
        start = 1
    for r in range(start, sh.nrows):
        title = clean(sh.cell_value(r, 0))
        if not title:
            continue
        rep_s = clean(sh.cell_value(r, 1))
        m = re.search(r"(\d+)", rep_s)
        replies = int(m.group(1)) if m else 0
        post_date, post_author = parse_da(sh.cell_value(r, 2))
        last_date, last_author = parse_da(sh.cell_value(r, 4))
        rows.append({
            "title": title, "replies": replies,
            "url": None,
            "post_date": post_date, "post_author": post_author,
            "post_uid": post_author if linkable(post_author) else "",
            "last_date": last_date, "last_author": last_author,
            "last_uid": last_author if linkable(last_author) else "",
        })
    return rows

def parse_csv(path, board):
    rows = []
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if len(row) < 6:
                continue
            raw_da = clean(row[0])          # 发帖日期 作者|最后回复日期 作者
            title_full = clean(row[2])      # 标题(含回复数)
            art_link = clean(row[3])        # /article/Board/id
            title = clean(row[4]) or re.sub(r"\s*\(\d+\)\s*$", "", title_full)
            m = re.search(r"\((\d+)\)\s*$", title_full)
            replies = int(m.group(1)) if m else 0
            mm = re.search(r"/article/([^/]+)/(\d+)", art_link)
            b = mm.group(1) if mm else board
            parts = [p.strip() for p in raw_da.split("|")]
            post_date, post_author = parse_da(parts[0] if parts else "")
            last_date, last_author = parse_da(parts[1] if len(parts) > 1 else "")
            rows.append({
                "title": title, "replies": replies,
                "url": art_link if mm else None,
                "post_date": post_date, "post_author": post_author,
                "post_uid": post_author if linkable(post_author) else "",
                "last_date": last_date, "last_author": last_author,
                "last_uid": last_author if linkable(last_author) else "",
            })
    return rows

# ---------- HTML 模板 ----------
CSS = """
:root{--bg:#0f1419;--panel:#1a2029;--panel2:#222b36;--line:#2c3744;--text:#e6edf3;
--muted:#8b98a5;--accent:#4ea1ff;--sticky:#ffb454;--hot:#ff6b6b;--rowalt:#161c24}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font-family:-apple-system,"PingFang SC","Microsoft YaHei",Segoe UI,sans-serif;font-size:14px;line-height:1.5}
.wrap{max-width:980px;margin:0 auto;padding:16px}
header{background:linear-gradient(135deg,#1b2735,#0f1419);border:1px solid var(--line);
border-radius:12px;padding:18px 20px;margin-bottom:14px}
h1{margin:0 0 4px;font-size:20px}h1 .em{color:var(--accent)}
.sub{color:var(--muted);font-size:13px}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}
.chip{background:var(--panel2);border:1px solid var(--line);border-radius:20px;padding:4px 12px;font-size:12px;color:var(--muted)}
.chip b{color:var(--text)}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:14px 0}
.toolbar input,.toolbar select{background:var(--panel);border:1px solid var(--line);color:var(--text);
border-radius:8px;padding:8px 10px;font-size:13px;outline:none}
.toolbar input:focus,.toolbar select:focus{border-color:var(--accent)}
.toolbar .grow{flex:1;min-width:180px}
a.back{color:var(--accent);text-decoration:none;font-size:13px}
a.back:hover{text-decoration:underline}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);
border-radius:12px;overflow:hidden}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--panel2);color:var(--muted);font-weight:600;font-size:12px;position:sticky;top:0}
tbody tr:nth-child(even){background:var(--rowalt)}
tbody tr:hover{background:#1f2a36}
td.id{color:var(--muted);font-variant-numeric:tabular-nums;width:54px}
td.title{font-weight:600}
td.title a{color:var(--text);text-decoration:none}
td.title a:hover{color:var(--accent);text-decoration:underline}
.pin{color:var(--sticky);margin-right:4px}
.cnt{display:inline-block;min-width:42px;text-align:center;font-variant-numeric:tabular-nums;
background:var(--panel2);border:1px solid var(--line);border-radius:6px;padding:2px 6px;font-size:12px}
.cnt.hot{color:var(--hot);border-color:#5a2a2a;background:#2a1717}
.au{color:var(--accent);text-decoration:none}.au:hover{text-decoration:underline}
.date{color:var(--muted);font-size:12px;white-space:nowrap}
.pager{display:flex;gap:10px;align-items:center;margin:14px 0;flex-wrap:wrap}
.pager button{background:var(--panel2);border:1px solid var(--line);color:var(--text);
border-radius:8px;padding:6px 14px;font-size:13px;cursor:pointer}
.pager button:disabled{opacity:.4;cursor:not-allowed}
.pager .info{color:var(--muted);font-size:13px}
.empty{text-align:center;color:var(--muted);padding:30px}
footer{color:var(--muted);font-size:12px;margin-top:16px;line-height:1.7}
footer code{background:var(--panel2);padding:1px 5px;border-radius:4px}
@media(max-width:640px){th.col-last,td.col-last{display:none}.wrap{padding:10px}}
"""

BOARD_JS = """
const DATA = __DATA__;
const PS = 200;
let view = DATA.items.slice();
let page = 1;
function esc(s){return (s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function au(uid,name){if(!uid)return esc(name);return '<a class="au" href="https://m.mysmth.net/user/query/'+encodeURIComponent(uid)+'" target="_blank" rel="noopener">'+esc(name)+'</a>';}
function tl(url,title){if(!url)return esc(title);return '<a href="'+url+'" target="_blank" rel="noopener">'+esc(title)+'</a>';}
function apply(){const q=document.getElementById('q').value.trim().toLowerCase();
const sort=document.getElementById('sort').value;let arr=DATA.items;
if(q)arr=arr.filter(it=>(it.title+' '+it.post_author+' '+it.last_author).toLowerCase().includes(q));
if(sort==='rep_desc')arr=arr.slice().sort((a,b)=>b.replies-a.replies);
else if(sort==='rep_asc')arr=arr.slice().sort((a,b)=>a.replies-b.replies);
else if(sort==='last_desc')arr=arr.slice().sort((a,b)=>(b.last_date||'').localeCompare(a.post_date||''));
view=arr;page=1;render();}
function render(){const total=view.length;const pages=Math.max(1,Math.ceil(total/PS));
if(page>pages)page=pages;const start=(page-1)*PS,end=Math.min(start+PS,total);const tb=document.getElementById('tbody');
if(!total){tb.innerHTML='<tr><td colspan="5" class="empty">无匹配结果</td></tr>';}
else{tb.innerHTML=view.slice(start,end).map((it,i)=>{const hot=it.replies>=50?' hot':'';
return '<tr><td class="id">'+(start+i+1)+'</td><td class="title">'+tl(it.url,it.title)+'</td>'
+'<td><span class="cnt'+hot+'">'+it.replies+'</span></td>'
+'<td><div class="date">'+(it.post_date||'—')+'</div><div>'+au(it.post_uid,it.post_author)+'</div></td>'
+'<td class="col-last"><div class="date">'+(it.last_date||'—')+'</div><div>'+au(it.last_uid,it.last_author)+'</div></td></tr>';
}).join('');}
document.getElementById('pginfo').textContent='第 '+page+' / '+pages+' 页 · 共 '+total+' 条';
document.getElementById('prev').disabled=page<=1;document.getElementById('next').disabled=page>=pages;}
document.getElementById('q').addEventListener('input',apply);
document.getElementById('sort').addEventListener('change',apply);
document.getElementById('prev').addEventListener('click',()=>{if(page>1){page--;render();}});
document.getElementById('next').addEventListener('click',()=>{page++;render();});
render();
"""

def board_page(board, label, live_url, note, rows):
    data = {"board": board, "label": label, "total": len(rows), "items": rows}
    js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>__LABEL__ · 水木社区版面快照</title>
<style>__CSS__</style></head><body><div class="wrap">
<header><h1>📋 <span class="em">__LABEL__</span> <span style="font-size:13px;color:var(--muted)">(__BOARD__)</span></h1>
<div class="sub">水木社区版面静态快照 · 离线可用</div>
<div class="stats"><span class="chip">版面 <b>__BOARD__</b></span>
<span class="chip">主题 <b>__TOTAL__</b> 条</span>
<span class="chip">最高回复 <b>__MAXREP__</b></span></div></header>
<div class="toolbar"><a class="back" href="../index.html">← 返回版面索引</a>
<input class="grow" id="q" placeholder="🔍 搜索标题 / 作者…">
<select id="sort"><option value="rep_desc">排序：回复数 多→少</option>
<option value="rep_asc">回复数 少→多</option><option value="last_desc">最后回复 新→旧</option>
<option value="origin">原始顺序</option></select>
<a class="back" href="__LIVE__" target="_blank" rel="noopener">原站版面 ↗</a></div>
<table><thead><tr><th class="id">#</th><th>标题</th><th>回复</th>
<th>发帖（时间 / 作者）</th><th class="col-last">最后回复（时间 / 作者）</th></tr></thead>
<tbody id="tbody"></tbody></table>
<div class="pager"><button id="prev">← 上一页</button><span class="info" id="pginfo"></span>
<button id="next">下一页 →</button></div>
<footer>__NOTE__<br>仅显示时间的行（如 <code>13:05:11</code>）为原快照中未回显日期的当日新帖。</footer>
</div><script>__JS__</script></body></html>
""".replace("__LABEL__", label).replace("__BOARD__", board).replace("__TOTAL__", str(len(rows))
).replace("__MAXREP__", str(max((r["replies"] for r in rows), default=0))
).replace("__LIVE__", live_url).replace("__NOTE__", note
).replace("__CSS__", CSS).replace("__JS__", BOARD_JS).replace("__DATA__", js)

def index_page(boards_meta):
    cards = []
    for b in boards_meta:
        cards.append('<a class="card" href="boards/%s.html">'
                     '<div class="cn">%s</div><div class="en">%s</div>'
                     '<div class="cnt2">%s 条主题</div></a>' % (
                         b["slug"], b["label"], b["board"], b["total"]))
    cards_html = "\n".join(cards)
    nboards = len(boards_meta)
    ntotal = sum(b["total"] for b in boards_meta)
    return """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>forum_smth · 水木社区版面快照站</title>
<style>__CSS__
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-top:14px}
.card{display:block;background:var(--panel);border:1px solid var(--line);border-radius:12px;
padding:14px 16px;text-decoration:none;color:var(--text);transition:.15s}
.card:hover{border-color:var(--accent);transform:translateY(-2px)}
.card .cn{font-weight:700;font-size:15px}.card .en{color:var(--muted);font-size:12px;margin-top:2px}
.card .cnt2{color:var(--accent);font-size:12px;margin-top:8px}
</style></head><body><div class="wrap">
<header><h1>🌐 <span class="em">forum_smth</span> · 水木社区版面快照站</h1>
<div class="sub">对水木社区多个版面的静态快照，由本地数据生成，可离线 / 在线浏览。标题或作者链接指向原站（需联网）。</div>
<div class="stats"><span class="chip">版面 <b>__NBOARDS__</b> 个</span>
<span class="chip">主题合计 <b>__NTOTAL__</b> 条</span></div></header>
<div class="grid">__CARDS__</div>
<footer>数据来源：本地抓取的各版面列表（CSV / XLS），为某一时刻快照，原站可能已有更新。<br>
本项目仅作数据展示与归档用途。</footer></div></body></html>
""".replace("__CSS__", CSS).replace("__NBOARDS__", str(nboards)
).replace("__NTOTAL__", f"{ntotal:,}").replace("__CARDS__", cards_html)

# ---------- 主流程 ----------
def main():
    os.makedirs(BOARDS_DIR, exist_ok=True)
    boards_meta = []

    # XLS
    for fn, (board, label) in XLS_MAP.items():
        p = os.path.join(BASE, fn)
        if not os.path.exists(p):
            print("跳过(不存在):", fn); continue
        rows = parse_xls(p, board)
        slug = board.lower()
        live = f"https://m.mysmth.net/board/{board}"
        note = "数据来自本地版面快照（XLS）：作者链接至用户页；标题无文章 ID，故不链具体帖。原站可能已有更新。"
        html = board_page(board, label, live, note, rows)
        with open(os.path.join(BOARDS_DIR, slug + ".html"), "w", encoding="utf-8") as f:
            f.write(html)
        boards_meta.append({"slug": slug, "board": board, "label": label, "total": len(rows)})
        print(f"[XLS] {label}({board}): {len(rows)} 条 -> boards/{slug}.html")

    # CSV
    for fn, (board, label) in CSV_MAP.items():
        p = os.path.join(BASE, fn)
        if not os.path.exists(p):
            print("跳过(不存在):", fn); continue
        rows = parse_csv(p, board)
        slug = board.lower()
        live = f"https://m.mysmth.net/board/{board}"
        note = "数据来自手机版版面列表快照（CSV）：标题链接至原帖，作者链接至用户页。"
        html = board_page(board, label, live, note, rows)
        with open(os.path.join(BOARDS_DIR, slug + ".html"), "w", encoding="utf-8") as f:
            f.write(html)
        boards_meta.append({"slug": slug, "board": board, "label": label, "total": len(rows)})
        print(f"[CSV] {label}({board}): {len(rows)} 条 -> boards/{slug}.html")

    # 索引
    boards_meta.sort(key=lambda b: -b["total"])
    idx = index_page(boards_meta)
    with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
        f.write(idx)
    print(f"\n索引页 -> index.html（{len(boards_meta)} 个版面，合计 "
          f"{sum(b['total'] for b in boards_meta):,} 条）")

if __name__ == "__main__":
    main()
