# data/ — 业务数据区（内容不入 git，只有本 README 和目录骨架可见）

- `inbox/`：每周原始导出 CSV 的进件目录（见 inbox/README.md）
- `raw/`：源企划文档（pptx/pdf）。在运行机上是指向存放处的符号链接或普通目录，自备：
  `ln -s <历史企划案目录> data/raw`（或直接把文件拷进来）

clone 后本目录几乎是空的——这是刻意的：数据只活在运行机本地，git 里只有系统。
