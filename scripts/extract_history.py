#!/usr/bin/env python3
"""从历史企划 pptx 抽取结构化表格 → data/inbox/history/*.csv（每行带来源文档+幻灯片号）。

目前覆盖：分价格带品牌份额（26春 s9 五张表、26秋冬 s7 三张表）。
27夏 s6 / 26秋冬 s10-11 为图片型，无法抽取（按溯源规则记录，不硬编）。
源文档目录默认 data/raw（→ ~/others 符号链接）。
"""
import csv, re, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "inbox" / "history"

TARGETS = [  # (文件, 幻灯片号, 企划季标签)
    ("26春休闲裤企划.pptx", 9, "26春企划"),
    ("26秋冬休闲裤企划案.pptx", 7, "26秋冬企划"),
]


def slide_tables(path, idx):
    z = zipfile.ZipFile(path)
    s = z.read("ppt/slides/slide%d.xml" % idx).decode("utf8", "ignore")
    for tm in re.finditer(r"<a:tbl>.*?</a:tbl>", s, re.S):
        rows = []
        for rm in re.finditer(r"<a:tr[ >].*?</a:tr>", tm.group(0), re.S):
            cells = []
            for cm in re.finditer(r"<a:tc[ >].*?</a:tc>", rm.group(0), re.S):
                t = re.sub(r"</a:p>", " ", cm.group(0))
                t = re.sub(r"<[^>]+>", "", t)
                cells.append(t.replace(" ", " ").strip())
            rows.append(cells)
        yield rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "大盘分价格带品牌份额.csv"
    n = 0
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["企划季", "价格段", "品牌", "销售额原文", "销额占比", "来源文档", "幻灯片号"])
        for fname, idx, season in TARGETS:
            src = RAW / fname
            for rows in slide_tables(src, idx):
                if not rows or len(rows[0]) < 3:
                    continue
                seg = re.sub(r"[价格位段元\-—]*$", "", rows[0][0]).strip() or rows[0][0]
                seg = re.search(r"\d+-\d+", rows[0][0])
                seg = seg.group(0) if seg else rows[0][0]
                for r in rows[1:]:
                    if len(r) < 3 or not r[0] or set(r[0]) <= set("."):
                        continue  # 跳过空行/省略号填充行
                    w.writerow([season, seg, r[0], r[1], r[2], fname, idx])
                    n += 1
    print("%s: %d 行" % (out.relative_to(ROOT), n))


if __name__ == "__main__":
    main()
