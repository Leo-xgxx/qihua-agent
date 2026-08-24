# data/inbox/ — 每周导出 CSV 的进件目录

用法：
1. 按数据来源建子目录（首次自己 mkdir）：`douyin/`、`tmall/`、`erp/`、`reviews/` …
2. 把后台导出的 CSV 原样丢进对应子目录（UTF-8、首行列名；xlsx 先另存为 CSV）
3. 跑 `python3 scripts/snapshot.py --freeze`

命名即表名：`inbox/erp/sku周报.csv` → 表 `erp__sku周报`。
文件名每周保持一致（同名重跑=整表重建，不会越堆越多）。
