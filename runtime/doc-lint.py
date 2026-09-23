#!/usr/bin/env python3
"""Read-only, Python >= 3.9 candidate scanner; not a full Markdown parser.

Only G1's literal alternatives and word lists are read from the writing-rules
module (docs/modules/constraints-writing.md).
Templates are not converted to regexes, and semantic exceptions are not judged.
Metadata must start on physical line 1. Fences use the same character and a
closing run at least as long as the opener. Backtick spans may cross lines;
paragraph boundaries, indented code, HTML and deeply nested links are not parsed.
UTF-8 (including BOM) and CRLF are accepted. Malformed exclusions produce scope
warnings, not a claim that the remaining document passed. Inputs are never edited.
"""

import argparse
import re
import sys
from pathlib import Path

RULES_PATH = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "modules"
    / "constraints-writing.md"
)
FORMATS = ("punctuation", "spacing", "parentheses")
HAN = r"[㐀-䶿一-鿿豈-﫿]"
FORMAT_PATTERNS = {
    "punctuation": re.compile(HAN + r"+(?:\*\*|__)?[ \t]*[,:;.!?]"),
    "spacing": re.compile(r"(?=(" + HAN + r"[A-Za-z0-9]|[A-Za-z0-9]" + HAN + r"))"),
    "parentheses": re.compile(r"\([^()\n]*" + HAN + r"[^()\n]*\)"),
}
URL = re.compile(
    r"(?:[A-Za-z][A-Za-z0-9+.-]*://|mailto:)[^\s<>\"'`\[\]{}，。；：！？、（）()]+"
)
SCOPE = (
    "仅检查 G1 字面候选和所选格式；复杂模板不展开，不判断语义例外。"
    "有限排除首行元数据、围栏、反引号代码、URL 和常见链接目标；"
    "不做完整 Markdown 解析：缩进代码、HTML、深层嵌套链接不解析，"
    "裸 URL 须与正文分隔，跨段代码边界可能多排除。"
)


def parse_rules(text):
    """Return (category, literal) pairs from the unique G1..G3 source, or fail."""
    bounds = [
        list(re.finditer(r"^####[ \t]+" + name + r"\.[^\n]*$", text, re.MULTILINE))
        for name in ("G1", "G3")
    ]
    if (
        any(len(matches) != 1 for matches in bounds)
        or bounds[0][0].start() >= bounds[1][0].start()
    ):
        raise ValueError("词源必须有唯一且有序的 G1、G3 标题")
    block = text[bounds[0][0].end() : bounds[1][0].start()]
    anchors = []
    for heading in ("禁用句式", "禁用修饰词", "禁用抽象大词"):
        matches = list(
            re.finditer(r"^\*\*" + heading + r"\*\*[^\n]*$", block, re.MULTILINE)
        )
        if len(matches) != 1:
            raise ValueError("词源缺失或重复：" + heading)
        anchors.append(matches[0])
    if [a.start() for a in anchors] != sorted(a.start() for a in anchors):
        raise ValueError("G1 词表章节顺序损坏")
    rules = []
    rows = [
        line.strip()
        for line in block[anchors[0].end() : anchors[1].start()].splitlines()
        if line.strip()
    ]
    cells = [row.strip("|").split("|") for row in rows]
    cells = [[cell.strip() for cell in row] for row in cells]
    if (
        len(cells) < 3
        or cells[0] != ["类别", "模式", "处理"]
        or len(cells[1]) != 3
        or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells[1])
        or any(not row.startswith("|") or not row.endswith("|") for row in rows)
    ):
        raise ValueError("禁用句式表缺失或表头损坏")
    for row in cells[2:]:
        if len(row) != 3 or not all(row):
            raise ValueError("禁用句式表存在损坏行")
        match = re.fullmatch(r'(?:"([^"\n]+)"|“([^”\n]+)”)(?:（[^）]*）)?', row[1])
        if not match:
            raise ValueError("句式模式须为引号内字面文本：" + row[1])
        pattern = match[1] or match[2]
        # Skip the whole template row: slash alternatives may share a placeholder.
        if re.search(
            r"…|\.{2,}|(?<![A-Za-z])[XY](?![A-Za-z])|[<>{}\[\]（）()]", pattern
        ):
            continue
        terms = [part.strip() for part in pattern.split("/")]
        if not all(terms):
            raise ValueError("句式字面片段为空")
        rules.extend(("候选/句式·" + row[0], term) for term in terms)
    if not rules:
        raise ValueError("禁用句式表没有可扫描的字面片段")

    def add_words(category, payload):
        payload = re.sub(r"（[^）]*）[。.]?$", "", payload.strip()).rstrip("。.")
        terms = [part.strip() for part in payload.split("、")]
        if not terms or any(not re.fullmatch(r"[\w-]+", term) for term in terms):
            raise ValueError(category + "词列表为空或格式损坏")
        rules.extend(("候选/" + category, term) for term in terms)

    modifier = re.fullmatch(
        r"\*\*禁用修饰词\*\*(?:（[^）]*）)?[：:]\s*(.+)", anchors[1][0].strip()
    )
    if not modifier or block[anchors[1].end() : anchors[2].start()].strip():
        raise ValueError("禁用修饰词列表缺失或格式损坏")
    add_words("修饰词", modifier[1])
    bullets = [
        line.strip() for line in block[anchors[2].end() :].splitlines() if line.strip()
    ]
    if not bullets:
        raise ValueError("禁用抽象大词列表缺失")
    for line in bullets:
        bullet = re.fullmatch(r"- ([^：:]+)[：:]\s*(.+)", line)
        if not bullet:
            raise ValueError("抽象大词列表格式损坏：" + line)
        add_words("抽象大词·" + bullet[1], bullet[2])
    return list(dict.fromkeys(rules))


def blank(text):
    """Mask rather than delete, preserving physical lines and match offsets."""
    return re.sub(r"[^\n]", " ", text)


def mask_markdown(lines):
    masked, notices = list(lines), []
    metadata = (
        lines[0].strip() if lines and lines[0].strip() in ("---", "+++") else None
    )
    fence = None
    for index, line in enumerate(lines):
        if metadata:
            masked[index] = blank(line)
            if index and line.strip() in (
                ("---", "...") if metadata == "---" else ("+++",)
            ):
                metadata = None
            continue
        # Quote prose is scanned. Container fences get a conservative fallback.
        body = re.sub(r"^(?:[ \t]*>[ \t]?)+", "", line)
        opening_body = (
            re.sub(r"^[ \t]*(?:[-+*]|\d+[.)])[ \t]+", "", body) if not fence else body
        )
        opening = re.match(r"^[ \t]*(`{3,}|~{3,})(.*)$", opening_body)
        if fence:
            masked[index] = blank(line)
            indent = r"[ \t]*" if fence[3] else r" {0,3}"
            if re.fullmatch(
                indent + re.escape(fence[0]) + "{" + str(fence[1]) + r",}[ \t]*", body
            ):
                fence = None
        elif opening and not (opening[1][0] == "`" and "`" in opening[2]):
            relaxed = opening_body != body or not re.match(r"^ {0,3}[`~]", body)
            if relaxed:
                notices.append(
                    (
                        index + 1,
                        "范围",
                        "列表或深缩进围栏按定界符保守排除，不解析容器边界",
                    )
                )
            fence = (opening[1][0], len(opening[1]), index + 1, relaxed)
            masked[index] = blank(line)
    if metadata:
        notices.append((1, "范围", "元数据未闭合；其后内容按元数据排除，可能漏扫正文"))
    if fence:
        notices.append(
            (fence[2], "范围", "围栏未闭合；其后内容按代码排除，可能漏扫正文")
        )

    joined = "\n".join(masked)

    def code(match):
        if "\n" in match[0]:
            notices.append(
                (
                    joined.count("\n", 0, match.start()) + 1,
                    "范围",
                    "跨行反引号按匹配定界符排除；未判断段落边界，可能多排除",
                )
            )
        return blank(match[0])

    joined = re.sub(r"(?<![\\`])(?:\\\\)*(`+)(?!`)[\s\S]*?(?<!`)\1(?!`)", code, joined)
    masked = joined.split("\n") if lines else []
    for index, line in enumerate(masked):
        if "`" in line:
            notices.append(
                (index + 1, "范围", "未配对或转义反引号未作代码排除，按正文扫描")
            )
        # Keep link labels/alt text. Destinations support at most one nested pair.
        line = re.sub(
            r"(?<=\])\((?:[^()\n]|\([^()\n]*\))*\)", lambda m: blank(m[0]), line
        )
        if re.search(r"(?<=\])\(", line):
            notices.append(
                (index + 1, "范围", "复杂或未闭合链接目标未完整排除，剩余内容仍扫描")
            )
        line = re.sub(r"(?<=\])\[[^\]\n]*\]", lambda m: blank(m[0]), line)
        if re.match(r"^(?: {0,3}>[ \t]?)* {0,3}\[[^\]]+\]:[ \t]*\S", line):
            line = blank(line)
        if any(
            m.end() < len(line) and line[m.end()] == "(" for m in URL.finditer(line)
        ):
            notices.append(
                (index + 1, "范围", "裸 URL 内半角括号未完整排除，括号内容仍扫描")
            )
        masked[index] = URL.sub(lambda m: blank(m[0]), line)
    return masked, notices


def scan_text(text, rules, skip_format=()):
    """Return (line/category/text records, suppressed candidate count)."""
    text = text.removeprefix("﻿").replace("\r\n", "\n")
    lines = text.split("\n") if text else []
    if lines and lines[-1] == "" and text.endswith("\n"):
        lines.pop()  # A terminal newline does not create another physical line.
    masked, records = mask_markdown(lines)
    pending, suppressed = None, 0
    if not text.strip():
        records.append((1, "范围", "空输入，没有可扫描正文"))
    for index, (raw, visible) in enumerate(zip(lines, masked)):
        number, reasons = index + 1, []
        for comment in re.finditer(r"<!--.*?-->", visible):
            original = raw[comment.start() : comment.end()]
            if "doc-lint:" in original:
                directive = re.fullmatch(
                    r"<!--[ \t]*doc-lint: ignore-next-line[ \t]+(.+?)[ \t]*-->",
                    original,
                )
                if directive and directive[1].strip():
                    reasons.append(directive[1].strip())
                else:
                    records.append(
                        (
                            number,
                            "范围",
                            "无效抑制注释：仅支持 ignore-next-line 且必须有原因",
                        )
                    )
        visible = re.sub(r"<!--.*?-->", lambda m: blank(m[0]), visible)
        if "<!--" in visible:
            records.append((number, "范围", "跨行或未闭合 HTML 注释不解析，按正文扫描"))
        candidates = []
        for category, term in rules:
            candidates.extend(
                (number, category, match[0])
                for match in re.finditer(re.escape(term), visible)
            )
        for name, pattern in FORMAT_PATTERNS.items():
            if name not in skip_format:
                for match in pattern.finditer(visible):
                    start, end = match.span(1) if name == "spacing" else match.span()
                    candidates.append((number, "候选/" + name, raw[start:end]))
        if pending:
            suppressed += len(candidates)
            records.append(
                (
                    number,
                    "抑制应用",
                    f"来自第 {pending[0]} 行；原因：{pending[1]}；抑制 {len(candidates)} 个候选",
                )
            )
        else:
            records.extend(candidates)
        pending = (number, "；".join(reasons)) if reasons else None
    if pending:
        records.append(
            (pending[0], "范围", "抑制未应用：没有下一物理行；原因：" + pending[1])
        )
    return sorted(records, key=lambda record: record[0]), suppressed


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="只读扫描文档候选；候选≠违规，0命中≠全文通过。", epilog=SCOPE
    )
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="+",
        help="UTF-8 文件（支持 BOM、CRLF 和含空格路径）",
    )
    parser.add_argument(
        "--skip-format",
        action="append",
        choices=FORMATS,
        default=[],
        help="跳过一个格式候选类别；可重复；默认全部检查，均只 warning",
    )
    args = parser.parse_args(argv)
    try:
        rules = parse_rules(RULES_PATH.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"{RULES_PATH}:0:error:词源不可用：{exc}", file=sys.stderr)
        return 2
    print(f"{RULES_PATH}:0:warning/范围:{SCOPE}")
    completed = errors = candidates = suppressed = 0
    scope_warnings = 1
    for filename in args.files:
        try:
            path = Path(filename)
            if not path.is_file():
                raise OSError("输入不存在或不是普通文件")
            records, count = scan_text(
                path.read_text(encoding="utf-8-sig"), rules, args.skip_format
            )
        except (OSError, UnicodeError) as exc:
            print(f"{filename}:0:error:{exc}", file=sys.stderr)
            errors += 1
            continue
        completed += 1
        suppressed += count
        for number, category, hit in records:
            print(f"{filename}:{number}:warning/{category}:{hit}")
            candidates += category.startswith("候选/")
            scope_warnings += category == "范围"
    print(
        f"统计：完成 {completed}/{len(args.files)} 个文件；显示候选 {candidates}；抑制 {suppressed}；"
        f"范围提醒 {scope_warnings}；错误 {errors}。候选≠违规；0命中≠全文通过。"
    )
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
