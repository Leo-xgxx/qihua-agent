#!/usr/bin/env python3
"""inbox CSV -> facts.db -> 冻结快照。

用法:
  python3 scripts/snapshot.py            # 仅导入 data/inbox/<来源>/*.csv 到 facts/facts.db
  python3 scripts/snapshot.py --freeze   # 导入后另存冻结快照并登记 manifest

约定: 表名 = <来源>__<文件名>; 每次全量重建该表; 所有列存 TEXT(计算在查询侧按口径做)。
"""
import csv, re, shutil, sqlite3, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "data" / "inbox"
DB = ROOT / "facts" / "facts.db"
SNAP = ROOT / "facts" / "snapshots"


def norm(s):
    s = re.sub(r"[^\w一-鿿]+", "_", s.strip())
    return s.strip("_") or "col"


def main():
    freeze = "--freeze" in sys.argv
    files = sorted(INBOX.glob("*/*.csv"))
    if not files:
        sys.exit("data/inbox/ 下没有 CSV（期望 data/inbox/<来源>/xxx.csv）")
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    imported, warns = [], []
    for f in files:
        table = norm(f.parent.name) + "__" + norm(f.stem)
        with open(f, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.reader(fh))
        if len(rows) < 2:
            print("跳过（无数据行）:", f)
            continue
        cols, seen = [], {}
        for c in rows[0]:
            c = norm(c)
            n = seen.get(c, 0)
            seen[c] = n + 1
            cols.append(c if n == 0 else c + "_" + str(n))
        prev = [r[1] for r in con.execute('PRAGMA table_info("%s")' % table)]
        if prev and prev != cols:
            w = "⚠ 列集变更 %s: 旧%s -> 新%s（平台导出格式可能已变，核对后再答题）" % (table, prev, cols)
            print(w)
            warns.append(w)
        con.execute('DROP TABLE IF EXISTS "%s"' % table)
        con.execute('CREATE TABLE "%s" (%s)' % (table, ", ".join('"%s" TEXT' % c for c in cols)))
        ph = ", ".join(["?"] * len(cols))
        data = [(r + [None] * len(cols))[: len(cols)] for r in rows[1:]]
        con.executemany('INSERT INTO "%s" VALUES (%s)' % (table, ph), data)
        imported.append((table, len(data), str(f.relative_to(ROOT))))
    con.commit()
    con.close()
    for t, n, src in imported:
        print("%s: %d 行 <- %s" % (t, n, src))
    if freeze and imported:
        SNAP.mkdir(parents=True, exist_ok=True)
        base = "S-" + datetime.date.today().strftime("%Y%m%d")
        dest, k = SNAP / (base + ".db"), 2
        while dest.exists():
            dest, k = SNAP / ("%s-%d.db" % (base, k)), k + 1
        shutil.copy2(DB, dest)
        with open(SNAP / "manifest.md", "a", encoding="utf-8") as m:
            m.write("\n## %s（%s）\n" % (dest.stem, datetime.date.today()))
            for t, n, src in imported:
                m.write("- %s: %d 行 <- %s\n" % (t, n, src))
            for w in warns:
                m.write("- %s\n" % w)
        print("冻结快照:", dest.relative_to(ROOT), "（简报引用 ID:", dest.stem + "）")


if __name__ == "__main__":
    main()
