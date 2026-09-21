<p>
  <img src="assets/doc-writing-logo.png" alt="doc-writing black-and-white notebook and pen logo" width="64" height="64">
</p>

# doc-writing

**English** | [简体中文](README.zh-CN.md)

A skill for writing, completing, and checking technical and review documentation, intended for models and frameworks that support the Agent Skills standard. Provide source material and a goal, and the assistant selects a document structure, checks facts, drafts the content, and reviews its wording and organization.

Use it to write requirements, pre-implementation architecture proposals, technical designs, API documentation, deployment manuals, usage guides, and architecture explanations, as well as review materials such as test reports and decision records. It also supports reviewing and updating existing documents. The skill's rules, templates, and detailed guides are currently in Chinese; this README provides an English introduction.

The installation and invocation examples below use Claude Code. The packaged entry currently uses Claude-specific path variables and tool conventions; other frameworks require an adapted entry, skill discovery, and tool mappings. Support for the standard alone does not establish out-of-the-box compatibility, and compatibility with every framework has not been verified.

## Quick start

Once installed in Claude Code, enter the following in a session opened in your target project:

```text
/doc-writing Using the following material, write a Chinese code contribution guide for project contributors. Return the text in chat only: developers create a feature branch and submit a pull request; each pull request must explain the purpose of the changes; a maintainer merges it after automated tests pass and one maintainer approves.
```

You should receive an operational guide organized around branching, submitting a pull request, testing, and review. Replace the example material with your project's actual information. The assistant selects the template and variant to match your goal.

To save the result, specify a destination:

```text
/doc-writing Based on this project's README.md, write a Chinese quick-start guide for engineers joining the project. Save it to docs/quickstart.md.
```

This request uses the existing `README.md` as source material and authorizes writing to the specified path. To review the draft first, ask for the text in chat only instead. Writing a document does not authorize executing deployments, payments, or other operations described in it, or committing and publishing the result; those actions require separate authorization.

<a id="安装"></a>

## Installation

You need a version of Claude Code that supports skills. Open your target project's root directory. If the destination directory does not already exist, run:

```bash
mkdir -p .claude/skills
git clone https://github.com/blankhoney/doc-writing.git .claude/skills/doc-writing
```

Use `/skills` in the project session to check that `doc-writing` is available, then invoke `/doc-writing` manually. If the current session does not discover the new directory, reopen the session and check again.

For use across all your projects, clone the repository into `~/.claude/skills/doc-writing/` instead. If the installation directory already exists, compare versions before updating and preserve any local customizations.

Keep the relative locations of `SKILL.md`, `runtime/`, `templates/`, `docs/design-spec.md`, `docs/modules/`, and `examples/` intact. The candidate scanner requires Python 3.9 or later and uses only the standard library—no pip installation is needed. Without Python, the assistant can still draft and perform model-based checks, while reporting that the scanner was not run.

See the [documentation entry point](docs/guide/README.md) (Chinese) for the installation layout.

## What you can create

| Task | Document type | Main output |
|---|---|---|
| Define feature goals and acceptance criteria | PRD | Problem, goals, non-goals, and acceptance conditions |
| Propose a design and explain trade-offs | Technical design | Approach, rationale, component responsibilities, and costs |
| Describe API usage | API documentation | Authentication, endpoints, parameters, and error handling |
| Explain the impact of a release | Changelog | Changes, impact, and migration steps where needed |
| Report test results or plan testing | Test report | Scope, results, evidence, or a test plan |
| Document deployment and on-call operations | Deployment guide / Runbook | Prerequisites, steps, verification, and recovery |
| Record an existing decision | ADR | Decision, rationale, and consequences |
| Teach a task or help readers complete one | Tutorial / How-to | A tutorial or actionable task guide |
| Look up a contract or understand a mechanism | Reference / Explanation | Parameter reference, conceptual explanation, or architecture overview |

Describe your task in natural language, or specify a document type explicitly. See the [template index](templates/_index.md) (Chinese) for all types and variants.

To review an existing document without changing it:

```text
/doc-writing Review docs/architecture.md for structure, terminology, and accuracy against the implementation. List specific locations and suggested changes. Do not modify any files.
```

## How it works

- **Structure follows the reader's task.** Select a document type, variant, and relevant modules; retain required sections and choose the depth the task needs. Technical designs distinguish architecture proposals from implementation designs; implementation designs cover interfaces, failure handling, dependencies, and package layout as needed.
- **Rules are loaded before the work that needs them.** Read common constraints first, then the original preparation, research, writing, and verification instructions at their respective stages. Read the complete selected template; load table, code-block, diagram, and example guidance when applicable. Wording rules precede the first draft or outline, and architecture constraints precede architecture decisions.
- **Project material supplies the facts.** Code, configuration, recorded decisions, and execution logs support their respective claims.
- **Format follows the information.** Use steps for actions, field tables for parameters, diagrams for component dependencies, and prose for reasoning.
- **The model makes the judgments.** It checks scope, evidence, terminology, and usability; the script adds locations of wording and formatting candidates.
- **Feedback guides revision.** Check versions, remove repetition within each reading unit, and use an independent reader to check comprehension and usability for important documents.

See [architecture and writing methods](docs/guide/architecture.md) (Chinese) for the full process and two relationship diagrams.

## Documentation

The detailed guides below are in Chinese.

| Document | Purpose |
|---|---|
| [Documentation entry point](docs/guide/README.md) | Installation, first use, and further reading |
| [Usage guide](docs/guide/usage.md) | Supply material, save documents, revise content, or review without editing |
| [Architecture and writing methods](docs/guide/architecture.md) | Understand the roles of rules, templates, the model, and the scanner |
| [Extending templates](docs/guide/templates.md) | Add types, variants, or modules; register examples and verify extensions |
| [Contributing](CONTRIBUTING.md) | Maintain rules and tests, and contribute changes |

<a id="候选扫描器"></a>

## Candidate scanner

To inspect wording and formatting candidates independently, run this from the repository root:

```bash
python3 runtime/doc-lint.py -- README.md
```

The scanner reads files and reports candidate locations. The user or assistant decides whether to change the text. Its wording and formatting rules target Chinese text; scanning the English README does not amount to an English style review.

| Item | Behavior |
|---|---|
| Input | One or more UTF-8 files; supports BOM, CRLF, and paths containing spaces |
| Rule source | Reads the G1 disallowed-pattern list directly from `docs/modules/constraints-writing.md` |
| Formatting checks | Chinese punctuation, spacing, and parentheses; warnings by default |
| Output | `file:line:warning/category:matched text`, followed by completion statistics |
| Exit codes | `0`: scan completed; `2`: an argument, input, or rule-loading error occurred |
| File access | Read-only; no network access and no execution of code or commands found in documents |

You can repeat `--skip-format` to select `punctuation`, `spacing`, or `parentheses`. For example, if your project has its own Chinese–English spacing convention:

```bash
python3 runtime/doc-lint.py --skip-format spacing -- README.md
```

When calling the scanner from another directory, use the actual absolute path to the script. Relative document paths resolve from your terminal's current working directory. The script locates its rules relative to itself. `${CLAUDE_SKILL_DIR}` is a skill-entry variable, not a predefined shell variable.

Candidates require contextual judgment: wording inside a quotation may need to stay unchanged. A completed scan reports execution status, not document quality; the model still reviews the full text.

### Per-line suppression

To preserve an original quotation, add a reason on the preceding physical line:

```markdown
<!-- doc-lint: ignore-next-line Preserve the original quotation. -->
> Original quoted text that must remain unchanged.
```

The comment suppresses script candidates only on the next physical line. A blank line also consumes the suppression. The output records the reason and count; the model must still check the quotation's authenticity and other applicable writing requirements.

## Maintenance and tests

Run from the repository root:

```bash
python3 -B -m unittest discover -s tests -v
```

Tests cover candidate scanning, the command-line interface, package structure, and preservation of registered examples. See [manual invocation checks](tests/SMOKE.md) for real writing-task validation and [extending templates](docs/guide/templates.md) for the complete extension procedure; both are in Chinese.

## License

Original project code, rules, and documentation are licensed under the [MIT License](LICENSE). Example excerpts from Requests, Backstage, Django, and Kubernetes enhancements retain their respective project licenses and attribution. The PEP 380 excerpt retains Gregory Ewing's public-domain dedication. See the [source registry](examples/SOURCES.md) and [examples/licenses/](examples/licenses/).
