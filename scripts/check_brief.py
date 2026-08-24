#!/usr/bin/env python3
"""正确性闸：出稿前检查简报/策略卡/规则卡（启发式，宁可误报不放过）。

用法: python3 scripts/check_brief.py [文件|目录 ...]   # 默认扫 briefs/ 与 knowledge/rules/

简报（templates/brief.md 结构）:
  B1 「结论/证据」段含数字的行必须带 [S- 快照引用（豁免：标「线索」的行；⟨推断⟩不豁免——推断的引用义务不变）
  B2 「反方」段必须存在且有实际内容
  B3 快照字段必须已填（快照：S-8位日期）
  B5 「结论/证据」段样本量 N<200 的行必须标「线索」（机器只兜 200 下限；300 档红线靠纪律与评审）
策略卡（首行 # 策略候选）:
  B4 六个必备字段行必须存在且非占位（目标金额/前提假设/资源要价/主要风险与反方论证/验证方式/定价与价格带落位）；
     「可检验预测」「机会来源」必须非占位。前瞻数字（目标/批量/区间/时限）不要求快照引用；
     引用快照事实的数字应带 [S-（纪律要求，暂不机器查）。
规则卡（knowledge/rules/R-*.md，查 frontmatter）:
  R1 来源必须为枚举值：评审拍板 | 预测验证 | 历史萃取·待确认
  R2 id 必须与文件名一致
  R3 失效条件非空
有违规 exit 1。
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER = re.compile(r"^[\s\-*>]*(<[^>]*>|…|\.{3})?[\s：:／/]*$")
CARD_FIELDS = ["目标金额", "前提假设", "资源要价", "主要风险与反方论证", "验证方式", "定价与价格带落位"]
RULE_SOURCES = {"评审拍板", "预测验证", "历史萃取·待确认"}
N_PAT = re.compile(r"[Nn]\s*[=≈]\s*([\d][\d,\.]*)\s*(万|w|k|K)?")


def n_value(m):
    v = float(m.group(1).replace(",", ""))
    u = m.group(2) or ""
    if u in ("万", "w"):
        v *= 10000
    elif u in ("k", "K"):
        v *= 1000
    return v


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
            for m in N_PAT.finditer(ln):
                if n_value(m) < 200 and "线索" not in ln:
                    errs.append((path, i, "B5 样本量 N<200 未标「线索」: " + ln.strip()[:60]))
    if not any(not PLACEHOLDER.match(l) for l in fanfang):
        errs.append((path, 0, "B2 反方段缺失或为空"))


def check_card(path, lines, errs):
    text = "\n".join(lines)
    for name in CARD_FIELDS:
        m = re.search(r"^\d+\.\s+\*\*%s\*\*.*?[：:](.*)$" % re.escape(name), text, re.M)
        if not m:
            errs.append((path, 0, "B4 缺字段行: " + name))
        elif PLACEHOLDER.match(m.group(1)):
            errs.append((path, 0, "B4 字段未填: " + name))
    m = re.search(r"可检验预测.*?[：:](.*)$", text, re.M)
    if not m or PLACEHOLDER.match(m.group(1)):
        errs.append((path, 0, "B4 可检验预测未填"))
    line = next((l for l in lines if "机会来源" in l), None)
    if line is None:
        errs.append((path, 0, "B4 缺机会来源行"))
    else:
        val = re.split(r"状态", line.split("机会来源", 1)[1])[0]
        val = val.lstrip("：:").strip("　 ")
        if not val or PLACEHOLDER.match(val):
            errs.append((path, 0, "B4 机会来源未填"))


def check_rule(path, lines, errs):
    fm = {}
    if lines and lines[0].strip() == "---":
        for ln in lines[1:]:
            if ln.strip() == "---":
                break
            parts = re.split(r"[:：]", ln, 1)
            if len(parts) == 2:
                fm[parts[0].strip()] = parts[1].strip()
    src = fm.get("来源", "")
    if src not in RULE_SOURCES:
        errs.append((path, 0, "R1 来源非枚举值: " + (src or "(缺)")))
    if fm.get("id", "") != path.stem:
        errs.append((path, 0, "R2 id 与文件名不符: " + fm.get("id", "(缺)")))
    if not fm.get("失效条件"):
        errs.append((path, 0, "R3 失效条件为空"))


def main():
    targets = [Path(a) for a in sys.argv[1:]] or [ROOT / "briefs", ROOT / "knowledge" / "rules"]
    files = []
    for t in targets:
        files += sorted(t.rglob("*.md")) if t.is_dir() else [t]
    errs, n = [], 0
    for f in files:
        if f.name == "README.md":
            continue
        n += 1
        lines = f.read_text(encoding="utf-8").splitlines()
        if f.name.startswith("R-") and lines and lines[0].strip() == "---":
            check_rule(f, lines, errs)
        elif lines and lines[0].startswith("# 策略候选"):
            check_card(f, lines, errs)
        else:
            check_brief(f, lines, errs)
    for p, i, msg in errs:
        print("%s:%s %s" % (p, i or "-", msg))
    print("检查 %d 个文件，%d 处违规" % (n, len(errs)))
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
