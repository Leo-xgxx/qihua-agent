#!/usr/bin/env python3
"""查快照（本机无 sqlite3 CLI，统一用本脚本，只读打开）。

用法:
  python3 scripts/q.py <S-ID|db路径> "SQL" [更多SQL...]
  python3 scripts/q.py <S-ID|db路径> --tables      # 列出所有表
输出 TSV（首行列名）。
"""
import sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def resolve(arg):
    p = Path(arg)
    if p.exists():
        return p
    name = arg if arg.endswith(".db") else arg + ".db"
    p = ROOT / "facts" / "snapshots" / name
    if p.exists():
        return p
    sys.exit("找不到库: %s（期望 facts/snapshots/ 下的快照 ID 或 db 路径）" % arg)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    db = resolve(sys.argv[1])
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    for sql in sys.argv[2:]:
        if sql == "--tables":
            sql = "select name from sqlite_master where type='table' order by name"
        cur = con.execute(sql)
        if cur.description:
            print("\t".join(c[0] for c in cur.description))
            for row in cur:
                print("\t".join("" if v is None else str(v) for v in row))


if __name__ == "__main__":
    main()
