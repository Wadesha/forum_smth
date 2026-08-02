# -*- coding: utf-8 -*-
"""探查 forum_smth 工作区所有数据文件（CSV / XLS）的结构。"""
import os, csv, glob

base = r"C:\Users\wade\OneDrive\forum_smth"

print("==== CSV 文件（手机版版面列表） ====")
for f in sorted(glob.glob(os.path.join(base, "*.csv"))):
    print("\n###", os.path.basename(f))
    try:
        with open(f, encoding="utf-8-sig", errors="replace", newline="") as fh:
            rows = list(csv.reader(fh))
        print("行数(含表头):", len(rows))
        if rows:
            print("表头:", rows[0])
            for row in rows[1:3]:
                print("  样本:", row)
    except Exception as e:
        print("ERR", repr(e))

print("\n==== XLS 文件（smth_* 各版面） ====")
try:
    import xlrd
    have_xlrd = True
except Exception as e:
    have_xlrd = False
    print("xlrd 不可用:", repr(e))

for f in sorted(glob.glob(os.path.join(base, "*.xls"))):
    print("\n###", os.path.basename(f))
    if not have_xlrd:
        print("  (跳过，缺少 xlrd)")
        continue
    try:
        wb = xlrd.open_workbook(f)
        print("  sheets:", wb.sheet_names())
        for sh in wb.sheets():
            print(f"  - sheet[{sh.name}] 行={sh.nrows} 列={sh.ncols}")
            for r in range(min(4, sh.nrows)):
                vals = [sh.cell_value(r, c) for c in range(min(10, sh.ncols))]
                print("    ", vals)
    except Exception as e:
        print("  ERR", repr(e))
