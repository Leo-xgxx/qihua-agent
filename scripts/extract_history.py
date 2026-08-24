#!/usr/bin/env python3
"""从历史企划 pptx 抽取结构化表格 → data/inbox/history/*.csv（每行带来源文档+幻灯片号）。

覆盖：
1. 分价格带品牌份额（26春 s9、26秋冬 s7）
2. 老品复盘卡：产品档案表 + 六维复盘表（26春 s29-42、26秋冬 s35-38、27夏 s22-23）
图片型页（27夏 s6、26秋冬 s10-11 流入流出等）无法抽取，按溯源规则不硬编。
《26休闲裤夏季企划案.pdf》为 PDF，本机无解析库，待补。
源文档目录默认 data/raw（→ ~/others 符号链接）。
"""
import csv, re, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "inbox" / "history"

BAND_TARGETS = [
    ("26春休闲裤企划.pptx", 9, "26春企划"),
    ("26秋冬休闲裤企划案.pptx", 7, "26秋冬企划"),
]
REVIEW_TARGETS = [
    ("26春休闲裤企划.pptx", range(29, 43), "26春企划"),
    ("26秋冬休闲裤企划案.pptx", range(35, 39), "26秋冬企划"),
    ("！27夏品类企划案-休闲裤.pptx", range(22, 24), "27夏企划"),
]


def slide_tables(path, idx):
    z = zipfile.ZipFile(path)
    s = z.read("ppt/slides/slide%d.xml" % idx).decode("utf8", "ignore")
    for tm in re.finditer(r"<a:tbl>.*?</a:tbl>", s, re.S):
        rows = []
        for rm in re.finditer(r"<a:tr[ >].*?</a:tr>", tm.group(0), re.S):
            cells = []
            for cm in re.finditer(r"<a:tc[ >].*?</a:tc>", rm.group(0), re.S):
                t = re.sub(r"</a:p>", "\n", cm.group(0))
                t = re.sub(r"<[^>]+>", "", t).replace(" ", " ")
                cells.append(t)
            rows.append(cells)
        yield rows


def clean(c):
    return "；".join(p.strip() for p in c.split("\n") if p.strip())


def extract_bands(w):
    n = 0
    for fname, idx, season in BAND_TARGETS:
        for rows in slide_tables(RAW / fname, idx):
            if not rows or len(rows[0]) < 3:
                continue
            m = re.search(r"\d+-\d+", clean(rows[0][0]))
            seg = m.group(0) if m else clean(rows[0][0])
            for r in rows[1:]:
                c0 = clean(r[0]) if r else ""
                if len(r) < 3 or not c0 or set(c0) <= set("."):
                    continue
                w.writerow([season, seg, c0, clean(r[1]), clean(r[2]), fname, idx])
                n += 1
    return n


def extract_reviews(w1, w2):
    n1 = n2 = 0
    for fname, ids, season in REVIEW_TARGETS:
        for i in ids:
            pname = ""
            got = False
            for t in slide_tables(RAW / fname, i):
                if not t:
                    continue
                head = clean(t[0][0]) if t[0] else ""
                if "产品名称" in head:  # 档案表（键值对）
                    got = True
                    pname = clean(t[0][1]) if len(t[0]) > 1 else ""
                    for r in t:
                        k = clean(r[0]) if r else ""
                        if k and len(r) > 1:
                            w1.writerow([season, pname, k, clean(r[1]), fname, i])
                            n1 += 1
                elif "维度" in head:  # 六维复盘表
                    got = True
                    for r in t[1:]:
                        row = [clean(c) for c in (list(r) + ["", "", ""])[:3]]
                        if not any(row):
                            continue
                        w2.writerow([season, pname, row[0], row[1], row[2], fname, i])
                        n2 += 1
            if not got:
                print("跳过（无可识别复盘表）: %s s%d" % (fname, i))
    return n1, n2


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    f1 = OUT / "大盘分价格带品牌份额.csv"
    with open(f1, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["企划季", "价格段", "品牌", "销售额原文", "销额占比", "来源文档", "幻灯片号"])
        n = extract_bands(w)
    print("%s: %d 行" % (f1.name, n))
    f2 = OUT / "老品复盘卡_产品档案.csv"
    f3 = OUT / "老品复盘卡_维度复盘.csv"
    with open(f2, "w", newline="", encoding="utf-8") as h2, open(f3, "w", newline="", encoding="utf-8") as h3:
        w1, w2 = csv.writer(h2), csv.writer(h3)
        w1.writerow(["企划季", "产品名称", "字段", "内容", "来源文档", "幻灯片号"])
        w2.writerow(["企划季", "产品名称", "维度", "畅销不畅销理由", "改善或升级点", "来源文档", "幻灯片号"])
        n1, n2 = extract_reviews(w1, w2)
    print("%s: %d 行 / %s: %d 行" % (f2.name, n1, f3.name, n2))


if __name__ == "__main__":
    main()
