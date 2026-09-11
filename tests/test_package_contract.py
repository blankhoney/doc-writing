"""Static package checks; these do not prove model behavior or skill discovery."""

from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
TYPES = {
    "prd", "tech-design", "api-doc", "changelog", "test-report", "deploy-runbook",
    "adr", "tutorial", "how-to", "reference", "explanation",
}


def outside_fences(text):
    """Ignore fenced examples when checking prose links, not Markdown semantics."""
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            run = marker[1]
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield re.sub(r"(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)", "", line)


class PackageTests(unittest.TestCase):
    def test_manual_entry_fields_and_size(self):
        data = (ROOT / "SKILL.md").read_bytes()
        self.assertTrue(data.startswith(b"---\n"))
        text = data.decode("utf-8")
        front = text.split("---", 2)[1]
        fields = dict(re.findall(r"^([a-z-]+):[ \t]*(.*)$", front, re.M))
        self.assertEqual(fields["name"], "doc-writing")
        self.assertEqual(fields["disable-model-invocation"], "true")
        self.assertEqual(fields["user-invocable"], "true")
        self.assertIn("description", fields)
        self.assertNotIn("hooks", fields)
        self.assertNotIn("allowed-tools", fields)
        self.assertLess(len(text.splitlines()), 500)
        self.assertEqual(text.count("$ARGUMENTS"), 1)
        self.assertIn("需要批准", text)
        self.assertIn("安全检查无法分析命令", text)
        self.assertIn("不得通过改变引号", text)

    def test_entry_resources_are_real_and_portable(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        resources = set(re.findall(r"\$\{CLAUDE_SKILL_DIR\}/([a-zA-Z0-9_./-]+\.(?:md|py))", text))
        self.assertTrue({"docs/design-spec.md", "templates/_index.md", "runtime/write-assist.md",
                         "runtime/verify-checks.md", "runtime/doc-lint.py", "examples/SOURCES.md"} <= resources)
        for resource in resources:
            with self.subTest(resource=resource):
                self.assertTrue((ROOT / resource).is_file())
        for path in [ROOT / "SKILL.md", *sorted((ROOT / "runtime").glob("*.md"))]:
            body = path.read_text(encoding="utf-8")
            self.assertNotIn("/Users/", body)
            self.assertNotIn("/home/", body)

    def test_template_index_and_metadata(self):
        index = (ROOT / "templates" / "_index.md").read_text(encoding="utf-8")
        links = set(re.findall(r"\]\(([a-z-]+)\.md\)", index))
        self.assertEqual(links, TYPES)
        for name in TYPES:
            with self.subTest(template=name):
                text = (ROOT / "templates" / (name + ".md")).read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"))
                self.assertIn("type: " + name + "\n", text.split("---", 2)[1])
                self.assertIn("default_variant:", text.split("---", 2)[1])
                self.assertIn("## 变体选择", text)
                self.assertIn("## 类型验证标准", text)
                self.assertIn("**示例使用范围**", text)
                self.assertNotIn("示例来源待核验", text)
                self.assertNotIn("未核验草稿", text)
                self.assertIn("../examples/SOURCES.md", text)

    def test_constraint_and_verification_entry_points(self):
        spec = (ROOT / "docs" / "design-spec.md").read_text(encoding="utf-8")
        for name in ("C1", "C2", "C3", "C4", "C5", "C6", "G1", "G2", "G3", "D1"):
            self.assertRegex(spec, r"(?m)^#### " + name + r"\. ")
        self.assertIn("### 3.5 收尾检查清单", spec)
        verify = (ROOT / "runtime" / "verify-checks.md").read_text(encoding="utf-8")
        for number in range(1, 12):
            self.assertRegex(verify, r"#" + str(number) + r"(?!\d)")
        for name in ("V1", "V2", "V3", "V4", "V5"):
            self.assertIn(name, verify)
        self.assertIn("../docs/design-spec.md", verify)
        self.assertIn("../templates/_index.md", verify)

    def test_local_markdown_links_resolve_inside_package(self):
        paths = [ROOT / "README.md", ROOT / "CONTRIBUTING.md"]
        for directory in ("runtime", "templates", "docs", "examples"):
            paths.extend((ROOT / directory).rglob("*.md"))
        for path in paths:
            for line in outside_fences(path.read_text(encoding="utf-8")):
                for link in re.findall(r"\]\(([^\s)]+)\)", line):
                    parts = urlsplit(link)
                    if parts.scheme or parts.netloc or not parts.path:
                        continue
                    target = (path.parent / unquote(parts.path)).resolve()
                    with self.subTest(file=str(path.relative_to(ROOT)), link=link):
                        self.assertTrue(target.is_relative_to(ROOT), "link escapes skill package")
                        self.assertTrue(target.exists(), "missing local link target")

    def test_active_execution_docs_have_no_stale_script_contract(self):
        paths = [ROOT / "SKILL.md", ROOT / "docs" / "design-spec.md",
                 ROOT / "docs" / "modules" / "5.1-progressive-disclosure.md",
                 ROOT / "docs" / "modules" / "5.3-verification-pipeline.md",
                 *sorted((ROOT / "runtime").glob("*.md"))]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn("doc-lint.sh", text)
                self.assertNotIn("hook-config.md", text)
                self.assertNotIn("40 条机械规则", text)
                self.assertNotIn("Hook 自动化为可选配置", text)


if __name__ == "__main__":
    unittest.main()
