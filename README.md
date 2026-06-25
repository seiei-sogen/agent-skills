# agent-skills

Reusable agent skills.

## Install for Codex

Codex does not load skills from `.codebuddy/skills`.
Install each skill under `$CODEX_HOME/skills` instead.
If `CODEX_HOME` is unset, Codex uses `~/.codex`.

From a local clone of this repository:

Bash / zsh:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"

cp -R skills/bullet-list-rewriter "$CODEX_HOME/skills/bullet-list-rewriter"
cp -R skills/iterative-review-improve "$CODEX_HOME/skills/iterative-review-improve"
cp -R skills/natural-japanese-rewriter "$CODEX_HOME/skills/natural-japanese-rewriter"
cp -R skills/sentence-linebreak-skill "$CODEX_HOME/skills/sentence-linebreak"
```

fish:

```fish
set -q CODEX_HOME; or set CODEX_HOME $HOME/.codex
mkdir -p "$CODEX_HOME"/skills

cp -R skills/bullet-list-rewriter "$CODEX_HOME"/skills/bullet-list-rewriter
cp -R skills/iterative-review-improve "$CODEX_HOME"/skills/iterative-review-improve
cp -R skills/natural-japanese-rewriter "$CODEX_HOME"/skills/natural-japanese-rewriter
cp -R skills/sentence-linebreak-skill "$CODEX_HOME"/skills/sentence-linebreak
```

For local development, use symlinks instead of copies:

Bash / zsh:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"

ln -sfn "$PWD/skills/bullet-list-rewriter" "$CODEX_HOME/skills/bullet-list-rewriter"
ln -sfn "$PWD/skills/iterative-review-improve" "$CODEX_HOME/skills/iterative-review-improve"
ln -sfn "$PWD/skills/natural-japanese-rewriter" "$CODEX_HOME/skills/natural-japanese-rewriter"
ln -sfn "$PWD/skills/sentence-linebreak-skill" "$CODEX_HOME/skills/sentence-linebreak"
```

fish:

```fish
set -q CODEX_HOME; or set CODEX_HOME $HOME/.codex
mkdir -p "$CODEX_HOME"/skills

ln -sfn "$PWD"/skills/bullet-list-rewriter "$CODEX_HOME"/skills/bullet-list-rewriter
ln -sfn "$PWD"/skills/iterative-review-improve "$CODEX_HOME"/skills/iterative-review-improve
ln -sfn "$PWD"/skills/natural-japanese-rewriter "$CODEX_HOME"/skills/natural-japanese-rewriter
ln -sfn "$PWD"/skills/sentence-linebreak-skill "$CODEX_HOME"/skills/sentence-linebreak
```

Start a new Codex session after installing.
The sentence linebreak skill is installed as `sentence-linebreak`, matching the `name:` field in its `SKILL.md`.

## Install for CodeBuddy with npx skill

`npx skill` installs one skill at a time into `.codebuddy/skills/<name>`.
This is useful for CodeBuddy-style skill loading, but it does not make the skill available to Codex.

```bash
SKILL_BASE_URL=https://github.com/seiei-sogen/agent-skills/tree/main npx skill skills/bullet-list-rewriter
SKILL_BASE_URL=https://github.com/seiei-sogen/agent-skills/tree/main npx skill skills/natural-japanese-rewriter
SKILL_BASE_URL=https://github.com/seiei-sogen/agent-skills/tree/main npx skill skills/sentence-linebreak-skill
```

## Available Skills

- `skills/bullet-list-rewriter` (`bullet-list-rewriter`): 日本語の列挙、条件、手順、注意点などを、意味とトーンを保ったまま箇条書きへ再構成する。
- `skills/iterative-review-improve` (`iterative-review-improve`): 入力に対してレビューと改善を5回繰り返し、最終的な改善版を作る。
- `skills/natural-japanese-rewriter` (`natural-japanese-rewriter`): LLMくさい日本語や硬い翻訳調の日本語を、原意と技術的意味を保って自然に直す。
- `skills/sentence-linebreak-skill` (`sentence-linebreak`): Markdown と AsciiDoc の文章に一文ごとの `<br>` / ` +` を追加する。
