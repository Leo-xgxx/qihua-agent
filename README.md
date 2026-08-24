# qihua-agent · AI 品类企划系统

把品类企划从「按章节写 PPT」改成「按决策问题产出证据链」：
AI 负责 **数据 → 证据 → 机会 → 候选策略 → 事后验证** 的整条产线，PM 只做取舍，评审会拍板。

设计全文：[docs/design.md](docs/design.md) ｜ 落地路线：[docs/roadmap.md](docs/roadmap.md) ｜ agent 铁律：[CLAUDE.md](CLAUDE.md)

## 四层结构与目录

| 层 | 目录 | 内容 |
|---|---|---|
| 事实层 | `data/` `facts/` `scripts/` | 每周 CSV 导出 → SQLite → 冻结快照（答题只引快照） |
| 知识层 | `knowledge/` | 规则卡（仅两种来源：评审拍板 / 预测被验证）+ 策略预测台账 |
| 产出层 | `questions/` `briefs/` | 固定十个决策问题 → 每季一组一页简报 |
| 交付层 | `templates/` | 简报 / 策略卡 / 规则卡 / 口径条目模板；评审稿由简报渲染 |

## 用法（当前 = 路线第一步）

1. 每周把平台导出的 CSV 放进 `data/inbox/<来源>/`（如 `douyin/` `tmall/` `erp/` `reviews/`）
2. `python3 scripts/snapshot.py --freeze` → 导入 `facts/facts.db` 并冻结快照 `facts/snapshots/S-YYYYMMDD.db`
3. 在仓库根目录起 Claude Code，按 `questions/questions.md` 答题，产出写进 `briefs/<季>/`

## 数据卫生

`data/` 整目录不入 git：内含品牌方经营数据。源企划文档（pptx/pdf）在本机 `~/others`，`data/raw` 是指向它的符号链接，仅本机参考。仓库里只放系统本身：规则、口径、模板、脚本、简报。
