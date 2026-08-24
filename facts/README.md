# 事实层约定

- `data/inbox/<来源>/*.csv`：每周原始导出（例：douyin/ tmall/ erp/ reviews/ survey/）。不入 git。
- `scripts/snapshot.py [--freeze]`：inbox → `facts/facts.db`（表名 = <来源>__<文件名>）；`--freeze` 另存冻结快照 `facts/snapshots/S-YYYYMMDD.db` 并登记 `snapshots/manifest.md`。
- 查快照用 `python3 scripts/q.py <S-ID> "SQL"`（或 `--tables` 列表）。
- 答题只引用冻结快照，禁止直接引用 inbox 或 facts.db（会被下次导入覆盖）。
- 指标口径：`facts/koujing/` 一指标一文件；口径变更必须升版本并留变更记录。
- 源企划文档（pptx/pdf）：放 `data/raw/`（本地目录或符号链接），仅本地参考，不入 git。
