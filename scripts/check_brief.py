#!/usr/bin/env python3
"""正确性闸：出稿前检查简报/策略卡（启发式，宁可误报不放过）。

用法: python3 scripts/check_brief.py [文件|目录 ...]    # 默认扫 briefs/

简报（templates/brief.md 结构）:
  B1 「结论/证据」段里含数字的行必须带 [S- 快照引用（豁免：标注「线索」的行）
  B2 「反方」段必须存在且有实际内容
  B3 快照字段必须已填（出现 S-________ 或缺「快照：S-8位日期」即未填）
策略卡（首行 # 策略候选）:
  B4 五个编号字段与「可检验预测」必须非占位
引用纪律在简报侧把关；策略卡的前瞻数字（小批量件数等）不要求快照引用。
有违规 exit 1。
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER = re.compile(r"^[\s\-*>]*(<[^>]*>|…|\.{3})?[\s：:／/]*$")


def check_brief(path, lines, errs):
    text = "\n".join(lines)
    if "S-________" in text or not re.search(r"快照：\s*S-\d{8}", text):
        errs.append((path, 0, "B3 快照字段未填"))
    sec, fanfang = "", []
    for i, ln in enumerate(lines, 1):
        if ln.startswith("## "):
            sec = ln[3:].strip()
            continue
        if sec.startswith("反方"):
            fanfang.append(ln)
        if sec.startswith(("结论", "证据")):
            if re.search(r"\d", ln) and "[S-" not in ln and "线索" not in ln and not PLACEHOLDER.match(ln):
                errs.append((path, i, "B1 含数字无快照引用: " + ln.strip()[:60]))
    if not any(not PLACEHOLDER.match(l) for l in fanfang):
        errs.append((path, 0, "B2 反方段缺失或为空"))


def check_card(path, lines, errs):
    text = "\n".join(lines)
    for m in re.finditer(r"^\d\.\s+\*\*(.+?)\*\*.*?[：:](.*)$", text, re.M):
        if PLACEHOLDER.match(m.group(2)):
            errs.append((path, 0, "B4 字段未填: " + m.group(1)))
    m = re.search(r"可检验预测.*?[：:](.*)$", text, re.M)
    if not m or PLACEHOLDER.match(m.group(1)):
        errs.append((path, 0, "B4 可检验预测未填"))


def main():
    targets = [Path(a) for a in sys.argv[1:]] or [ROOT / "briefs"]
    files = []
    for t in targets:
        files += sorted(t.rglob("*.md")) if t.is_dir() else [t]
    errs, n = [], 0
    for f in files:
        if f.name == "README.md":
            continue
        n += 1
        lines = f.read_text(encoding="utf-8").splitlines()
        if lines and lines[0].startswith("# 策略候选"):
            check_card(f, lines, errs)
        else:
            check_brief(f, lines, errs)
    for p, i, msg in errs:
        print("%s:%s %s" % (p, i or "-", msg))
    print("检查 %d 个文件，%d 处违规" % (n, len(errs)))
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
