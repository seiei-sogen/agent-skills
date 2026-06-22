# agent-skills

Reusable agent skills.

## Install with npx skill

`npx skill` installs one skill at a time into `.codebuddy/skills/<name>`.

```bash
SKILL_BASE_URL=https://github.com/seiei-sogen/agent-skills/tree/main npx skill skills/bullet-list-rewriter
SKILL_BASE_URL=https://github.com/seiei-sogen/agent-skills/tree/main npx skill skills/natural-japanese-rewriter
SKILL_BASE_URL=https://github.com/seiei-sogen/agent-skills/tree/main npx skill skills/sentence-linebreak-skill
```

## Available Skills

- `skills/bullet-list-rewriter`: 日本語の並列情報を必要に応じて箇条書きへ整える。
- `skills/natural-japanese-rewriter`: LLMくさい日本語や翻訳調の日本語を自然で読みやすく整える。
- `skills/sentence-linebreak-skill`: Markdown と AsciiDoc の文章に一文ごとの hard line break を追加する。
