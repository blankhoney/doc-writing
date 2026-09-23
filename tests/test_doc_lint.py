"""Run with PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v."""

import ast
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "runtime" / "doc-lint.py"
SOURCE = (ROOT / "docs" / "modules" / "constraints-writing.md").read_text(
    encoding="utf-8-sig"
)
MODULE = runpy.run_path(str(SCRIPT))
parse_rules = MODULE["parse_rules"]
scan_text = MODULE["scan_text"]
RULES = parse_rules(SOURCE)
FORMATS = MODULE["FORMATS"]


def scan(text, skip=()):
    return scan_text(text, RULES, skip)


def candidates(text, skip=()):
    return [record for record in scan(text, skip)[0] if record[1].startswith("候选/")]


class RuleTests(unittest.TestCase):
    def test_current_source_and_template_exclusion(self):
        terms = {term for _, term in RULES}
        self.assertTrue(
            {"众所周知", "不言而喻", "显著", "赋能", "解耦", "平台化"} <= terms
        )
        self.assertTrue(
            {"随着", "不断发展", "深入推进", "对 X 进行了 Y", "首先"}.isdisjoint(terms)
        )
        self.assertEqual(len(RULES), len(set(RULES)))

    def test_direct_statement_pattern_is_model_checked(self):
        row = '| 转折否定铺垫 | "……但……不等于……" | 直接说明可用范围、限制、条件或待验证项；真实引文与契约原文保留 |'
        self.assertIn(row, SOURCE)
        self.assertEqual(RULES, parse_rules(SOURCE.replace(row + "\n", "")))
        terms = {term for _, term in RULES}
        self.assertTrue({"但", "不等于", "……但……不等于……"}.isdisjoint(terms))
        self.assertEqual(candidates("数值 1 不等于 2。"), [])

    def test_changes_are_taken_only_from_g1(self):
        changed = SOURCE.replace('"众所周知/不言而喻"', '"新句式/新表达"')
        changed = changed.replace("显著、深入、全面", "巨大、深入、全面")
        changed = changed.replace("赋能、协同、闭环", "孵化、协同、闭环")
        changed += '\n| 其他 | "外部词" | 删除 |\n'
        new_rules = parse_rules(changed)
        terms = {term for _, term in new_rules}
        self.assertTrue({"新句式", "新表达", "巨大", "孵化"} <= terms)
        self.assertTrue({"众所周知", "显著", "赋能", "外部词"}.isdisjoint(terms))
        hits, _ = scan_text("新句式，巨大孵化。", new_rules)
        self.assertEqual({hit[2] for hit in hits}, {"新句式", "巨大", "孵化"})

    def test_literals_are_not_regexes(self):
        changed = SOURCE.replace('"众所周知/不言而喻"', '"a+b/稳定*"')
        new_rules = parse_rules(changed)
        self.assertEqual(scan_text("aaab", new_rules)[0], [])
        hits, _ = scan_text("a+b 稳定*", new_rules)
        self.assertEqual({hit[2] for hit in hits}, {"a+b", "稳定*"})

    def test_missing_duplicate_or_reversed_bounds_fail(self):
        g1 = "#### G1. 禁用模式清单"
        g3 = "#### G3. 排除性检验"
        for bad in (
            "",
            SOURCE.replace(g1, ""),
            SOURCE.replace(g3, ""),
            SOURCE + "\n" + g1,
            SOURCE + "\n" + g3,
            SOURCE.replace(g1, "#### TEMP.").replace(g3, g1).replace("#### TEMP.", g3),
        ):
            with self.subTest(source=bad[:40]), self.assertRaises(ValueError):
                parse_rules(bad)

    def test_damaged_required_tables_fail(self):
        replacements = [
            ("**禁用句式**", "**其他句式**"),
            ("| 类别 | 模式 | 处理 |", "| 类别 | 错列 | 处理 |"),
            ('"众所周知/不言而喻"', "众所周知/不言而喻"),
            ('"众所周知/不言而喻"', '"众所周知//不言而喻"'),
            ("**禁用修饰词**", "**其他修饰词**"),
            ("显著、深入、全面、充分、有力、极致、高效。", "。"),
            ("显著、深入、全面、充分、有力、极致、高效。", "显著、、深入。"),
            ("**禁用抽象大词**", "**其他大词**"),
            ("- 通用大词：赋能、协同、闭环、抓手、范式、沉淀、生态", "- 通用大词："),
        ]
        for old, new in replacements:
            with self.subTest(damage=old), self.assertRaises(ValueError):
                parse_rules(SOURCE.replace(old, new))
        start = SOURCE.index("- 通用大词：")
        end = SOURCE.index("#### G3.", start)
        with self.assertRaises(ValueError):
            parse_rules(SOURCE[:start] + SOURCE[end:])

    def test_no_literal_pattern_is_an_error(self):
        start = SOURCE.index("| 万能开场 |")
        end = SOURCE.index("**禁用修饰词**", start)
        with self.assertRaises(ValueError):
            parse_rules(
                SOURCE[:start] + '| 模板 | "对 X 进行了 Y" | 删除 |\n\n' + SOURCE[end:]
            )

    def test_python_39_syntax(self):
        ast.parse(SCRIPT.read_text(encoding="utf-8"), feature_version=(3, 9))


class ScanTests(unittest.TestCase):
    def test_candidates_and_normal_prose(self):
        self.assertEqual(
            {hit[2] for hit in candidates("众所周知，显著赋能。")},
            {"众所周知", "显著", "赋能"},
        )
        self.assertEqual(
            scan("接口每天处理 100 条请求。选择缓存方案，因为数据库耗时 30 ms。"),
            ([], 0),
        )
        self.assertEqual(len(candidates("显著降低 30%，赋能指代此处定义的操作。")), 2)

    def test_repeated_literal_occurrences_and_quotes(self):
        self.assertEqual(len(candidates("显著、显著。")), 2)
        self.assertEqual(
            [hit[0] for hit in candidates("> 显著。\n“显著”不是自动豁免。")], [1, 2]
        )

    def test_metadata_bom_and_physical_lines(self):
        text = "﻿---\r\ntitle: 显著API\r\n---\r\n显著。\r\n"
        self.assertEqual(candidates(text), [(4, "候选/修饰词", "显著")])
        self.assertEqual(candidates('+++\nx = "显著"\n+++\n显著。')[0][0], 4)
        self.assertEqual(candidates("---\ntitle: 显著\n...\n显著。")[0][0], 4)
        self.assertEqual(candidates("正文。\n---\n显著。\n---")[0][0], 3)

    def test_backtick_and_tilde_fence_lengths(self):
        for fence in ("````", "~~~~"):
            text = f"{fence}\n显著。\n{fence[:3]}\n显著。\n{fence[0] * 5}\n显著。"
            with self.subTest(fence=fence):
                self.assertEqual(candidates(text), [(6, "候选/修饰词", "显著")])
                self.assertEqual(len(scan(text)[0]), 1)
        text = "```python\n显著。\n~~~\n显著。\n```\n显著。"
        self.assertEqual(candidates(text)[0][0], 6)

    def test_blockquote_code_is_excluded_but_not_quote_prose(self):
        text = (
            "> ```\n> 显著。\n> ```\n> 显著。\n> > ~~~\n> > 显著。\n> > ~~~\n> > 显著。"
        )
        self.assertEqual([hit[0] for hit in candidates(text)], [4, 8])

    def test_inline_code_and_urls(self):
        text = "`显著API(中文):` ``显著 ` API中文``\nhttps://example.test/显著\n<https://example.test/赋能>\nmailto:显著@example.test"
        self.assertEqual(scan(text), ([], 0))
        self.assertEqual(candidates("`code`显著。"), [(1, "候选/修饰词", "显著")])

    def test_link_labels_survive_destination_masking(self):
        text = '[显著](https://example.test/赋能)赋能。\n[显著](../显著.md "赋能")\n![显著](图片/赋能.png)\n[显著](https://example.test/a_(赋能))'
        self.assertEqual(
            [hit[2] for hit in candidates(text)],
            ["显著", "赋能", "显著", "显著", "显著"],
        )
        self.assertEqual(
            len(candidates("[显著][赋能]\n[赋能]: https://example.test/显著")), 1
        )

    def test_unclosed_regions_warn_instead_of_claiming_success(self):
        for text in ("```\n显著。", "~~~\n显著。", "---\n显著。", "+++\n显著。"):
            with self.subTest(text=text):
                records, _ = scan(text)
                self.assertEqual(candidates(text), [])
                self.assertTrue(any("未闭合" in hit for _, _, hit in records))
        records, _ = scan("`显著。")
        self.assertEqual(len(candidates("`显著。")), 1)
        self.assertTrue(any(category == "范围" for _, category, _ in records))

    def test_complex_exclusion_limits_warn(self):
        for text in ("[显著](a(b(c)))", "https://example.test/a(显著)", "<!-- 未闭合"):
            with self.subTest(text=text):
                self.assertTrue(
                    any(category == "范围" for _, category, _ in scan(text)[0])
                )
        self.assertEqual(scan("")[0][0][1], "范围")

    def test_format_categories_and_skips(self):
        examples = {
            "punctuation": "**说明**: 正文。",
            "spacing": "中文API接口",
            "parentheses": "方案(需要审批)",
        }
        for name, text in examples.items():
            with self.subTest(name=name):
                hits = candidates(text)
                self.assertTrue(hits)
                self.assertEqual(
                    {category for _, category, _ in hits}, {"候选/" + name}
                )
                self.assertEqual(candidates(text, (name, name)), [])
        self.assertEqual(candidates("说明：中文 API 接口（需要审批）。"), [])
        self.assertEqual(candidates("API (English only)."), [])
        self.assertEqual(
            candidates("显著API:方案(中文)", FORMATS), [(1, "候选/修饰词", "显著")]
        )
        self.assertEqual([hit[2] for hit in candidates("中A文")], ["中A", "A文"])

    def test_reported_context_is_original_text(self):
        text = "方案(说明 `code` 可省略)"
        self.assertEqual(candidates(text)[0][2], "(说明 `code` 可省略)")


class SuppressionTests(unittest.TestCase):
    directive = "<!-- doc-lint: ignore-next-line 引用原文 -->"

    def test_only_next_physical_line_and_application_record(self):
        records, count = scan(self.directive + "\r\n显著API\r\n显著。\r\n")
        self.assertEqual(count, 2)
        self.assertEqual(
            [row for row in records if row[1].startswith("候选/")],
            [(3, "候选/修饰词", "显著")],
        )
        application = [row for row in records if row[1] == "抑制应用"]
        self.assertEqual(application[0][0], 2)
        self.assertIn("引用原文", application[0][2])
        self.assertIn("抑制 2", application[0][2])

    def test_blank_line_consumes_suppression(self):
        records, count = scan(self.directive + "\n\n显著。")
        self.assertEqual(count, 0)
        self.assertEqual(candidates(self.directive + "\n\n显著。")[0][0], 3)
        self.assertTrue(any(row[0] == 2 and row[1] == "抑制应用" for row in records))

    def test_reason_is_required_and_other_commands_are_inert(self):
        for bad in (
            "<!-- doc-lint: ignore-next-line -->",
            "<!-- doc-lint: ignore-next-line   -->",
            "<!-- doc-lint: ignore-file 原因 -->",
            "<!-- doc-lint: ignore-next-line原因 -->",
        ):
            with self.subTest(directive=bad):
                records, count = scan(bad + "\n显著。")
                self.assertEqual(count, 0)
                self.assertEqual(len(candidates(bad + "\n显著。")), 1)
                self.assertTrue(any(category == "范围" for _, category, _ in records))

    def test_directives_in_code_or_metadata_are_inert(self):
        texts = [
            f"`{self.directive}`\n显著。",
            f"``{self.directive}``\n显著。",
            f"```\n{self.directive}\n```\n显著。",
            f"~~~\n{self.directive}\n~~~\n显著。",
            f"---\n{self.directive}\n---\n显著。",
            f"`跨行\n{self.directive}\n`\n显著。",
        ]
        for text in texts:
            with self.subTest(text=text):
                records, count = scan(text)
                self.assertEqual(count, 0)
                self.assertEqual(len(candidates(text)), 1)
                self.assertFalse(
                    any(category == "抑制应用" for _, category, _ in records)
                )

    def test_escaped_backslashes_before_inline_code(self):
        for length in (2, 4):
            text = "\\" * length + f"`{self.directive}`\n显著。"
            with self.subTest(backslashes=length):
                records, count = scan(text)
                self.assertEqual(count, 0)
                self.assertEqual(candidates(text), [(2, "候选/修饰词", "显著")])
                self.assertFalse(
                    any(category == "抑制应用" for _, category, _ in records)
                )

    def test_container_fences_are_conservative_and_inert(self):
        for opening, closing in (
            ("- ~~~~", "  ~~~~"),
            ("1. ```", "   ```"),
            ("    ```", "    ```"),
        ):
            text = f"{opening}\n  {self.directive}\n  显著。\n{closing}\n显著。"
            with self.subTest(opening=opening):
                records, count = scan(text)
                self.assertEqual(count, 0)
                self.assertEqual(candidates(text), [(5, "候选/修饰词", "显著")])
                self.assertTrue(any(category == "范围" for _, category, _ in records))
                self.assertFalse(
                    any(category == "抑制应用" for _, category, _ in records)
                )

    def test_eof_is_not_an_extra_line_or_cross_file_state(self):
        for ending in ("", "\n", "\r\n"):
            records, _ = scan(self.directive + ending)
            self.assertTrue(any("没有下一物理行" in row[2] for row in records))
            self.assertFalse(any(row[1] == "抑制应用" for row in records))
            self.assertEqual(len(candidates("显著。")), 1)

    def test_no_drift_past_code_and_no_suppression_of_scope_warnings(self):
        text = self.directive + "\n```\n显著。\n```\n显著。"
        self.assertEqual(candidates(text)[0][0], 5)
        records, count = scan(self.directive + "\n`显著。")
        self.assertEqual(count, 1)
        self.assertTrue(any(category == "范围" for _, category, _ in records))

    def test_inline_comment_reason_is_not_scanned(self):
        text = "说明。<!-- doc-lint: ignore-next-line 显著一词是引用 -->\n显著。"
        records, count = scan(text)
        self.assertEqual(count, 1)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "抑制应用")


class CLITests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="doc lint test ")
        self.addCleanup(self.directory.cleanup)
        self.cwd = Path(self.directory.name)

    def run_cli(self, *args, script=SCRIPT):
        return subprocess.run(
            [sys.executable, str(script), *map(str, args)],
            cwd=self.cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def input(self, name, data):
        path = self.cwd / name
        path.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)
        return path

    def test_foreign_cwd_spaces_crlf_read_only_and_warning_exit_zero(self):
        data = "﻿---\r\ntitle: 显著\r\n---\r\n显著API\r\n`显著`\r\n".encode()
        path = self.input("带 空格.md", data)
        result = self.run_cli(path.name)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"{path.name}:4:warning/候选/修饰词:显著", result.stdout)
        self.assertIn("显示候选 2", result.stdout)
        self.assertIn("候选≠违规；0命中≠全文通过", result.stdout)
        self.assertEqual(path.read_bytes(), data)

    def test_repeated_skip_options_and_invalid_choice(self):
        path = self.input("options.md", "说明:中文API(中文)")
        args = [str(path)]
        for option in (*FORMATS, "spacing"):
            args.extend(("--skip-format", option))
        result = self.run_cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("显示候选 0", result.stdout)
        self.assertIn("0命中≠全文通过", result.stdout)
        self.assertEqual(self.run_cli(path, "--skip-format", "unknown").returncode, 2)

    def test_multiple_files_do_not_share_suppression(self):
        first = self.input("first.md", SuppressionTests.directive + "\n")
        second = self.input("second.md", "显著。")
        result = self.run_cli(first, second)
        self.assertEqual(result.returncode, 0)
        self.assertIn(f"{second}:1:warning/候选/修饰词:显著", result.stdout)
        self.assertIn("完成 2/2", result.stdout)

    def test_missing_input_and_no_arguments_exit_two(self):
        self.assertEqual(self.run_cli().returncode, 2)
        result = self.run_cli("missing.md")
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing.md:0:error:", result.stderr)
        self.assertIn("完成 0/1", result.stdout)
        self.assertEqual(self.run_cli(self.cwd).returncode, 2)

    def test_invalid_utf8_does_not_skip_other_files(self):
        bad = self.input("bad.md", b"\xff\xfe")
        good = self.input("good.md", "显著。")
        result = self.run_cli(bad, good)
        self.assertEqual(result.returncode, 2)
        self.assertIn(f"{bad}:0:error:", result.stderr)
        self.assertIn(f"{good}:1:warning/候选/修饰词:显著", result.stdout)
        self.assertIn("完成 1/2", result.stdout)
        self.assertEqual(bad.read_bytes(), b"\xff\xfe")

    def test_missing_or_damaged_word_source_exit_two(self):
        package = self.cwd / "package"
        (package / "runtime").mkdir(parents=True)
        script = package / "runtime" / "doc-lint.py"
        script.write_bytes(SCRIPT.read_bytes())
        target = self.input("input.md", "显著。")
        for source in (None, "# 损坏词源\n", b"\xff"):
            if source is not None:
                (package / "docs" / "modules").mkdir(parents=True, exist_ok=True)
                (package / "docs" / "modules" / "constraints-writing.md").write_bytes(
                    source.encode("utf-8") if isinstance(source, str) else source
                )
            with self.subTest(source=source):
                result = self.run_cli(target, script=script)
                self.assertEqual(result.returncode, 2)
                self.assertIn("error:词源不可用", result.stderr)
                self.assertNotIn("显示候选 0", result.stdout)

    def test_missing_word_source_does_not_fall_back_to_spec(self):
        # 旧路径即使放着可用副本也必须失败：脚本只认单一词源，不回退到 design-spec.md。
        package = self.cwd / "package"
        (package / "runtime").mkdir(parents=True)
        script = package / "runtime" / "doc-lint.py"
        script.write_bytes(SCRIPT.read_bytes())
        (package / "docs").mkdir(parents=True, exist_ok=True)
        (package / "docs" / "design-spec.md").write_bytes(
            (ROOT / "docs" / "modules" / "constraints-writing.md").read_bytes()
        )
        target = self.input("input.md", "显著。")
        result = self.run_cli(target, script=script)
        self.assertEqual(result.returncode, 2)
        self.assertIn("error:词源不可用", result.stderr)
        self.assertNotIn("显示候选", result.stdout)

    def test_unclosed_fence_still_warns_with_zero_candidates(self):
        target = self.input("unclosed.md", "```\n显著。")
        result = self.run_cli(target)
        self.assertEqual(result.returncode, 0)
        self.assertIn("围栏未闭合", result.stdout)
        self.assertIn("显示候选 0", result.stdout)
        self.assertIn("0命中≠全文通过", result.stdout)


if __name__ == "__main__":
    unittest.main()
