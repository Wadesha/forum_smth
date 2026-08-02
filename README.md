# forum_smth

水木社区（新水木 BBS / smth）版面数据采集与静态展示项目。

## 项目内容

- **数据采集**：针对水木社区各版面（地理、房屋、旅游、职场等）的帖子列表抓取。
- **静态展示**：将抓取的版面列表（XHTML 手机版源码）解析为自包含、可离线浏览的静态 HTML。

## 目录与文件

| 文件 | 说明 |
|------|------|
| `build_site.py` | 统一生成器：解析本地 CSV/XLS 各版面快照 → 生成 `index.html`（版面索引）+ `boards/<slug>.html`（每版面主题列表，含搜索/排序/分页） |
| `inspect_data.py` | 探查脚本：打印所有 CSV/XLS 的字段、行数、结构，用于确认解析方式 |
| `geography_to_html.py` | 早期单版面脚本（地理版手机版 XML → 单页），已被 `build_site.py` 取代，保留作参考 |
| `geography_mobile.xml` | 原始抓取源码存档（水木社区手机版 Geography 版面列表页，单页快照） |
| `index.html` | 版面索引（首页），列出全部 17 个版面与主题数 |
| `boards/*.html` | 各版面主题列表静态页（深色主题、搜索、排序、分页，离线可用） |

## 使用

```bash
python build_site.py   # 读取本地 CSV/XLS，生成 index.html + boards/*.html
```

打开 `index.html` 即可离线浏览；各版面页标题/作者链接指向原站 `m.mysmth.net`（需联网）。

## 在线访问（GitHub Pages）

本仓库已启用 GitHub Pages，静态快照站在线地址：

- 首页（版面索引）：https://wadesha.github.io/forum_smth/
- 数据源为本地抓取的各版面 CSV/XLS 快照，由 `build_site.py` 解析生成 `index.html` + `boards/*.html`。
- 共 17 个版面、约 27 万条主题（单页几 MB，加载稍慢属正常）。

## 说明

- 原始抓取的二进制数据（`.xls` / 大型 `.csv`）不纳入本仓库，仅保留源码与静态展示产物，保持仓库精简可审查。
- 如需纳入原始数据集，建议通过 Git LFS 或单独的 `data` 分支管理。
