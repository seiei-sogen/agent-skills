# HTML syntax highlighting skill

- [x] 1. Use **plugin-dev:skill-development** skill (Claude Code's authoring guidance SKILL.md files).
  - Codex adaptation: skill-creator and writing-for-agents-matt-p.
- [x] 2. Validate skill: frontmatter `name` and `description`, referenced files exist, cross-skill links resolve.
- [x] 3. Test cases structural. Skip subjective.
- [x] 4. Run **Opening PR**.
  - skip: This task delivers local skills and a rendered example. No publication is needed.

- [x] Ground.
- [x] Sketch. Arena phases: Frame, Fan out, Cross-judge, Pick, Graft, Verify.
- [x] Agree. Proceed with the smallest complete design.
- [x] Implement the shared HTML skill and easy-to-understand integration.
- [x] Scrap only if the design fails the real artifact check.
  - skip: The shared HTML transformation passes its behavior checks.
- [x] Generate and inspect an easy-to-understand example with highlighted code.
  - Independent skill trial followed easy-to-understand into create-html, copied its runtime and generated four language examples offline. Parent added a full TypeScript example through the same renderer.
  - Chromium offline rendering passed at 1280px and 390px. No page overflow or network requests. Five code blocks; the full TypeScript example uses ten computed text colors. Its extracted code runs and returns the two displayed names.

Scope: new skill instructions, its renderer and dependency metadata if needed, a behavioral check, easy-to-understand's delegation, and one generated demonstration. Existing Ruby and AsciiDoc skills are reference material only.

Throughput checkpoint: one shared renderer is the unit of reuse. Investigate existing patterns independently, then compare two design sketches. Implement sequentially because the caller and demonstration depend on the renderer contract. No timing claims.
