# forum_smth

水木社区（新水木 BBS / smth）版面数据采集与静态展示项目。

## 项目内容

- **数据采集**：针对水木社区各版面（地理、房屋、旅游、职场等）的帖子列表抓取。
- **静态展示**：将抓取的版面列表（XHTML 手机版源码）解析为自包含、可离线浏览的静态 HTML。

## 目录与文件

| 文件 | 说明 |
|------|------|
| `geography_to_html.py` | 解析脚本：从手机版版面列表源码抽取主题帖（标题/回复数/发帖与最后回复时间+作者），生成静态 HTML |
| `geography_board.html` | 地理(Geography)版第 1/1001 页的静态展示页（深色主题、搜索、排序、仅看置顶，离线可用） |
| `geography_mobile.xml` | 原始抓取源码存档（水木社区手机版 Geography 版面列表页） |

## 使用

```bash
python geography_to_html.py   # 读取 geography_mobile.xml，输出 geography_board.html
```

打开 `geography_board.html` 即可离线浏览；标题/作者链接指向原站 `wap.newsmth.net`（需联网）。

## 说明

- 原始抓取的二进制数据（`.xls` / 大型 `.csv`）不纳入本仓库，仅保留源码与静态展示产物，保持仓库精简可审查。
- 如需纳入原始数据集，建议通过 Git LFS 或单独的 `data` 分支管理。
