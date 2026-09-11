"""Guard recorded source copies; these tests do not establish legal permission."""

import ast
import hashlib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent


class ExampleSourceTests(unittest.TestCase):
    def test_license_and_notice_copies_match_checked_upstream_files(self):
        expected = {
            "backstage-LICENSE.txt": "e3620220d6f8a43cb5c968720f86d4e7c6e97847ee61a9c7694039896efb869b",
            "backstage-NOTICE.txt": "36395569b3867d0769a40ffb908709c0b5fbfd79bf4b827856dd34feeed644ba",
            "requests-LICENSE.txt": "09e8a9bcec8067104652c168685ab0931e7868f9c8284b66f5ae6edae5f1130b",
            "requests-NOTICE.txt": "f5110972dedad2b4e9d314518daf3b7d72d6e02e499acd802181de6f74571dcc",
            "django-LICENSE.txt": "b846415d1b514e9c1dff14a22deb906d794bc546ca6129f950a18cd091e2a669",
        }
        for name, digest in expected.items():
            with self.subTest(file=name):
                data = (ROOT / "examples" / "licenses" / name).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), digest)

    def test_verified_samples_keep_fixed_sources_and_partial_scope(self):
        registry = (ROOT / "examples" / "SOURCES.md").read_text(encoding="utf-8")
        samples = {
            "changelog": ("147c8511ddbfa5e8f71bbf5c18ede0c4ceb3bba4", "requests-2310", "历史更新说明"),
            "adr": ("1134d4b38c40583cdcd00637a7c29de02351f9d8", "backstage-adr003", "不是完整 Nygard ADR"),
            "how-to": ("9e7cc2b628fe8fd3895986af9b7fc9525034c1b0", "django-csv", "未安装或运行 Django"),
        }
        for name, (commit, anchor, limitation) in samples.items():
            with self.subTest(template=name):
                text = (ROOT / "templates" / (name + ".md")).read_text(encoding="utf-8")
                self.assertIn("/blob/" + commit + "/", text)
                self.assertIn("/blob/" + commit + "/", registry)
                self.assertIn("../examples/SOURCES.md#" + anchor, text)
                self.assertIn("非官方中文", text)
                self.assertIn(limitation, text)
                self.assertIn("**示例使用范围**", text)
                self.assertNotIn("其他示例仍是未核验草稿", text)

    def test_templates_only_keep_registered_samples_or_format_guidance(self):
        # Inventory the actual sample sections, not every occurrence of “示例”:
        # format rules and module requirements must remain usable without samples.
        expected = {
            "adr": ["### 示例（已核验局部：Backstage ADR003）"],
            "changelog": ["### 示例（已核验：Requests 2.31.0 Security 条目）"],
            "how-to": ["### 示例（完整操作单元：扫描本仓库 README）",
                       "### 示例（已核验局部：Django 5.2 CSV 输出）"],
            "reference": ["构造示意：假想配置仅含下列两键"],
            "tech-design": ["来源：[doc-lint.py]", "来源同上，按源码解释当前实现",
                            "SDD 格式因合同/法规而异，不提供通用示例"],
        }
        for path in sorted((ROOT / "templates").glob("*.md")):
            if path.name == "_index.md":
                continue
            text = path.read_text(encoding="utf-8")
            sections = re.findall(
                r"(?m)^### 示例[^\n]*\n[\s\S]*?(?=^### 示例|^---\n|\Z)", text)

            markers = expected.get(path.stem, [])
            with self.subTest(template=path.stem):
                self.assertEqual(len(sections), len(markers))
                for section, marker in zip(sections, markers):
                    self.assertIn(marker, section)
                self.assertNotRegex(text, r"示例来源待核验|未核验草稿|其余草稿")
                if not markers:
                    self.assertIn("通过变体结构、锚定节、模块与类型验证标准使用", text)
                    self.assertNotRegex(text, r"(?m)^`{3,}markdown$")

    def test_registry_describes_public_license_and_local_adaptations(self):
        registry = (ROOT / "examples" / "SOURCES.md").read_text(encoding="utf-8")
        for link in ("../LICENSE", "../runtime/doc-lint.py", "../docs/design-spec.md",
                     "../README.md"):
            self.assertIn("](" + link + ")", registry)
            self.assertTrue((ROOT / "examples" / link).is_file())
        self.assertIn("MIT", registry)
        self.assertIn("不作为目标项目事实", registry)
        self.assertIn("未核验的模板样本正文已移除", registry)
        self.assertIn("样本未执行", registry)
        self.assertIn("第三方片段继续受其原许可约束", registry)
        for stale in ("references/", "89bb448", "项目许可未定", "首批", "发布缺口"):
            self.assertNotIn(stale, registry)
        for name in ("tech-design", "how-to"):
            text = (ROOT / "templates" / (name + ".md")).read_text(encoding="utf-8")
            self.assertIn("本包当前源码", text)
            self.assertNotIn("89bb448", text)

    def test_django_code_is_unmodified_except_document_indentation(self):
        text = (ROOT / "templates" / "how-to.md").read_text(encoding="utf-8")
        section = text.split("### 示例（已核验局部：Django 5.2 CSV 输出）", 1)[1].split("\n---", 1)[0]
        match = re.search(r"(?m)^```python\n(.*?)^```$", section, re.S)
        if match is None:
            self.fail("Missing Django Python example")
        code = match.group(1)
        # Upstream docs/howto/outputting-csv.txt lines 18-33, dedented by four spaces.
        self.assertEqual(hashlib.sha256(code.encode("utf-8")).hexdigest(),
                         "4faa297cd5c7547826b5a8423f691bad9bad9c9fa7abf3b46a60701207e19974")
        ast.parse(code)  # Syntax only; do not import Django or execute the view.


if __name__ == "__main__":
    unittest.main()
