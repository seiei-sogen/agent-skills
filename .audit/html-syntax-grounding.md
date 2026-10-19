# Grounding

The request is a reusable HTML generation skill with detailed syntax highlighting, first integrated into easy-to-understand. This is local implementation, not publication.

skills/code-review/easy-to-understand/SKILL.md is a small prompt. It chooses the explanation target and emits an easy-*.html file. There is no existing renderer API. Preserve the accessible Japanese explanations, diagrams, filename prefix, and background contrast.

skills/develop-flow/asciidoc-to-colorful-html owns an AsciiDoc conversion flow with embedded CSS and no runtime network dependencies. It is reference material, not a new caller in this task. skills/code-review/easy-to-understand-ruby has specialized layouts and templates; leave it unchanged.

No existing highlighting dependency was found. Node 26 is available. Shiki 4.5.0 requires Node >=20 and supports build-time highlighted HTML. Installed easy-to-understand is a read-only Nix store link, so integration must resolve from the repository for this demonstration.

Rubric for design selection: reusable by HTML-producing skills; detailed real grammar highlighting; preserved code text and page layout; standalone output without runtime CDN; small maintained implementation and repeatable verification.
