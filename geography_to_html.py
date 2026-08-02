# -*- coding: utf-8 -*-
"""解析水木社区手机版 Geography 版面列表快照 -> 自包含静态 HTML 展示页"""
import re
import html
import json

SRC = r"C:\Users\wade\OneDrive\forum_smth\geography_mobile.xml"
OUT = r"C:\Users\wade\OneDrive\forum_smth\index.html"

with open(SRC, encoding="utf-8") as f:
    content = f.read()

# 提取 <ul class="list sec"> 内所有 <li>
m = re.search(r'<ul class="list sec">(.*?)</ul>', content, re.S)
ul = m.group(1)
lis = re.findall(r'<li[^>]*>(.*?)</li>', ul, re.S)

items = []
for li in lis:
    # 标题 + 文章ID + 回复数 + 是否置顶
    tm = re.search(r'<a href="/article/Geography/(\d+)"([^>]*)>(.*?)</a>\s*\((\d+)\)', li, re.S)
    aid = tm.group(1)
    cls = tm.group(2)
    title = html.unescape(tm.group(3).strip())
    replies = int(tm.group(4))
    sticky = 'class="top"' in cls

    # 第二段：发帖 | 最后回复
    divs = re.findall(r'<div>(.*?)</div>', li, re.S)
    second = divs[1] if len(divs) > 1 else ''
    parts = second.split('|')
    post_raw = html.unescape(re.sub(r'\s+', ' ', parts[0]).strip()) if parts else ''
    last_raw = html.unescape(re.sub(r'\s+', ' ', parts[1]).strip()) if len(parts) > 1 else ''

    def extract(s):
        a = re.search(r'/user/query/([^"]+)"[^>]*>([^<]+)</a>', s)
        # 去掉作者前的时间/日期
        rest = s
        if a:
            rest = s[:a.start()].strip()
        return rest.strip(), (a.group(2).strip() if a else ''), (a.group(1) if a else '')

    post_date, post_author, post_uid = extract(post_raw)
    last_date, last_author, last_uid = extract(last_raw)

    items.append({
        "id": aid,
        "title": title,
        "replies": replies,
        "sticky": sticky,
        "post_date": post_date,
        "post_author": post_author,
        "post_uid": post_uid,
        "last_date": last_date,
        "last_author": last_author,
        "last_uid": last_uid,
    })

# 排序键：尽量用完整日期，否则用文章ID（越大越新）
def sort_key(it):
    d = it["last_date"] if re.match(r'\d{4}-\d{2}-\d{2}', it["last_date"]) else it["post_date"]
    if re.match(r'\d{4}-\d{2}-\d{2}', d or ''):
        return d
    return "2099"  # 仅时间的放到最新

data = {
    "board": "Geography / 地理",
    "page": "1/1001",
    "total": len(items),
    "items": items,
}

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>水木社区 · 地理(Geography)版 静态快照</title>
<style>
  :root{
    --bg:#0f1419; --panel:#1a2029; --panel2:#222b36; --line:#2c3744;
    --text:#e6edf3; --muted:#8b98a5; --accent:#4ea1ff; --sticky:#ffb454;
    --hot:#ff6b6b; --rowalt:#161c24;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--text);
    font-family:-apple-system,"PingFang SC","Microsoft YaHei",Segoe UI,sans-serif;
    font-size:14px;line-height:1.5}
  .wrap{max-width:960px;margin:0 auto;padding:16px}
  header{background:linear-gradient(135deg,#1b2735,#0f1419);border:1px solid var(--line);
    border-radius:12px;padding:18px 20px;margin-bottom:14px}
  h1{margin:0 0 4px;font-size:20px}
  h1 .em{color:var(--accent)}
  .sub{color:var(--muted);font-size:13px}
  .stats{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}
  .chip{background:var(--panel2);border:1px solid var(--line);border-radius:20px;
    padding:4px 12px;font-size:12px;color:var(--muted)}
  .chip b{color:var(--text)}
  .toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:14px 0}
  .toolbar input,.toolbar select{background:var(--panel);border:1px solid var(--line);
    color:var(--text);border-radius:8px;padding:8px 10px;font-size:13px;outline:none}
  .toolbar input:focus,.toolbar select:focus{border-color:var(--accent)}
  .toolbar .grow{flex:1;min-width:180px}
  label.tog{display:flex;align-items:center;gap:6px;color:var(--muted);font-size:13px;cursor:pointer}
  table{width:100%;border-collapse:collapse;background:var(--panel);
    border:1px solid var(--line);border-radius:12px;overflow:hidden}
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
  .au{color:var(--accent);text-decoration:none}
  .au:hover{text-decoration:underline}
  .date{color:var(--muted);font-size:12px;white-space:nowrap}
  footer{color:var(--muted);font-size:12px;margin-top:16px;line-height:1.7}
  footer code{background:var(--panel2);padding:1px 5px;border-radius:4px}
  .empty{text-align:center;color:var(--muted);padding:30px}
  @media(max-width:640px){
    th.col-last,td.col-last{display:none}
    .wrap{padding:10px}
  }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>🌍 水木社区 · <span class="em">地理 (Geography)</span> 版</h1>
    <div class="sub">手机版版面列表 · 静态快照（数据抓取自原站，离线展示，不依赖外部 CSS/JS）</div>
    <div class="stats" id="stats"></div>
  </header>

  <div class="toolbar">
    <input class="grow" id="q" placeholder="🔍 搜索标题 / 作者…">
    <select id="sort">
      <option value="origin">排序：原始顺序（新→旧）</option>
      <option value="rep_desc">回复数：多 → 少</option>
      <option value="rep_asc">回复数：少 → 多</option>
      <option value="last_desc">最后回复：新 → 旧</option>
    </select>
    <label class="tog"><input type="checkbox" id="onlySticky"> 仅看置顶</label>
  </div>

  <table>
    <thead>
      <tr>
        <th class="id">#</th>
        <th>标题</th>
        <th>回复</th>
        <th>发帖（时间 / 作者）</th>
        <th class="col-last">最后回复（时间 / 作者）</th>
      </tr>
    </thead>
    <tbody id="tbody"></tbody>
  </table>

  <footer>
    数据来源：水木社区手机版 <code>/board/Geography</code> 第 1/1001 页快照。<br>
    标题与作者名链接指向原站对应页面（需联网访问 <code>wap.newsmth.net</code>）；本页本身完全离线可用。<br>
    仅显示时间的行（如 <code>11:50:05</code>）为抓取时刻当日新帖，原站未回显日期。
  </footer>
</div>

<script>
const DATA = __DATA__;

function fmtDate(s){ return s || '—'; }
function authorLink(uid, name){
  if(!uid) return name || '—';
  return '<a class="au" href="https://wap.newsmth.net/user/query/'+encodeURIComponent(uid)+'" target="_blank" rel="noopener">'+name+'</a>';
}
function articleLink(id, title){
  return '<a href="https://wap.newsmth.net/article/Geography/'+id+'" target="_blank" rel="noopener">'+title+'</a>';
}

function render(){
  const q = document.getElementById('q').value.trim().toLowerCase();
  const sort = document.getElementById('sort').value;
  const onlySticky = document.getElementById('onlySticky').checked;

  let rows = DATA.items.filter(it=>{
    if(onlySticky && !it.sticky) return false;
    if(q){
      const hay = (it.title+' '+it.post_author+' '+it.last_author).toLowerCase();
      if(!hay.includes(q)) return false;
    }
    return true;
  });

  if(sort==='rep_desc') rows.sort((a,b)=>b.replies-a.replies);
  else if(sort==='rep_asc') rows.sort((a,b)=>a.replies-b.replies);
  else if(sort==='last_desc') rows.sort((a,b)=> (b.last_date||'').localeCompare(a.post_date||''));

  const tb = document.getElementById('tbody');
  if(!rows.length){ tb.innerHTML='<tr><td colspan="5" class="empty">没有匹配的结果</td></tr>'; }
  else {
    tb.innerHTML = rows.map((it,i)=>{
      const hot = it.replies>=50 ? ' hot':'';
      const pin = it.sticky ? '<span class="pin">📌</span>':'';
      return '<tr>'
        + '<td class="id">'+(i+1)+'</td>'
        + '<td class="title">'+pin+articleLink(it.id, it.title)+'</td>'
        + '<td><span class="cnt'+hot+'">'+it.replies+'</span></td>'
        + '<td><div class="date">'+fmtDate(it.post_date)+'</div><div>'+authorLink(it.post_uid, it.post_author)+'</div></td>'
        + '<td class="col-last"><div class="date">'+fmtDate(it.last_date)+'</div><div>'+authorLink(it.last_uid, it.last_author)+'</div></td>'
        + '</tr>';
    }).join('');
  }
  document.getElementById('stats').innerHTML =
    '<span class="chip">版面 <b>'+DATA.board+'</b></span>'
    + '<span class="chip">页码 <b>'+DATA.page+'</b></span>'
    + '<span class="chip">本页主题 <b>'+DATA.total+'</b> 条</span>'
    + '<span class="chip">置顶 <b>'+DATA.items.filter(x=>x.sticky).length+'</b> 条</span>'
    + '<span class="chip">最高回复 <b>'+Math.max(...DATA.items.map(x=>x.replies))+'</b></span>';
}

document.getElementById('q').addEventListener('input', render);
document.getElementById('sort').addEventListener('change', render);
document.getElementById('onlySticky').addEventListener('change', render);
render();
</script>
</body>
</html>
"""

html_out = HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False))
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html_out)

print("解析条目:", len(items))
print("置顶:", sum(1 for i in items if i["sticky"]))
print("最高回复:", max(i["replies"] for i in items))
print("输出:", OUT, "（GitHub Pages 根路径直接可访问）")
