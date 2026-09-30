### Multi-phase or multi-PR plan

**自分が責任を持つのは計画であり、コードではない。計画は、オーナーがボックスを 1 つずつ実行し、オペレーターが証拠から監査するチェックリストである。** 計画が成果物である。実装はしない。

1. 変更が 1 つか 2 つのファイルで、方針が明らかなら、計画を省く。そう述べて止まる。
2. 書く前に、未解決の問題をプロトタイプで決着させる。それぞれについて `playbooks/prototype.md` を実行する。ブランチ、SHA、スクリーンショットを Appendix A 用に保管する。オペレーターに尋ねるのは、どんな実行でも決着しないプロダクト上の判断や好みの判断だけにする。選択肢を示す（**never-block-on-the-human** 原則スキル）。
3. 探索はサブエージェントで行う。設定済みの `judgment and prose` ロールは [`../references/provider-dispatch.md`](../references/provider-dispatch.md) を通して解決する。`poteto-agent` は、修飾のない `inherit-parent` / `auto` のネイティブヘルパーにだけ使う。Claude Code 組み込みの `Plan` エージェントは決して使わない。このスキルを無視するからである（**guard-the-context-window** 原則スキル）。各エクスプローラー（探索役）は、ファイルの位置、慣習、テストコマンド、エントリポイントを返す。中身をインラインで丸ごと返さない。子は親のハーネスを検出せず、ルートを選ばない。選択されたエフォートを保つ。脱落は脱落のままにする。フォールバックや暗黙のタイムアウトを追加しない。
4. 下のスケルトンを計画ファイルにコピーし、すべてのプレースホルダを埋める。オペレーターがパスを指定しない限り、ファイルは作業リポジトリの `docs/` 配下に書く。すべての見出しとすべてのサブブロックを、示した順序のまま保つ。PR ごとに 1 セクション。1 つの PR は、それ自身の証拠を持つ 1 つの変更である（**sequence-verifiable-units** 原則スキル）。実行プレイブックを **How to read this** で名指しする。`playbooks/autopilot-full.md` と `playbooks/autopilot-stack.md` のどちらを使うかは、`playbooks/autopilot-stack.md` 末尾の規則に従って選ぶ。常設のプログラムは `playbooks/orchestrate.md` を使う。
5. 全文を `/technical-writing` に従って書き、次に `/unslop` をかける。本文は Diátaxis の 1 モード、すなわちハウツーである。付録が説明とリファレンスを担う。各見出しはタスクか指摘を述べる。長いダッシュは使わない。文中のコロンは使わない。
6. インストール済みプラグイン配下で `node skills/poteto-mode/scripts/check-plan.mjs <plan.md>` を実行し、出力されたすべての行を直す（**encode-lessons-in-structure** 原則スキル）。このスクリプトは、スケルトンの形、すべての検証ブロックにある検証規則、句読点の規則を強制する。プレイブックのファイルはチェッカーの入力ではない。ステップ 4 で作った計画ファイルをチェックする。
7. 引き渡す。計画のパスとスクリプトの出力を投稿し、止まる。実行は、オペレーターの明示的な開始指示があってから、計画が名指しする実行プレイブックのもとで始まる。

**検証。** テストだけでは検証として十分ではない。PR は、ユニット、ライブ、パフォーマンスのボックスがすべてチェックされたときにだけ検証済みとなる（**prove-it-works** 原則スキル）。この文が検証規則である。すべての検証ブロックはこの文で始まる。ライブブロックは必須である。設定済みの `swarm workers` ロール上の 10 本のレーンが、PR のヘッドで、**swarm** スキルに従い、ドライバースキルを通して実際のサーフェスを操作する。ロールは実行時に [`../references/provider-dispatch.md`](../references/provider-dispatch.md) を通して一度だけ解決され、各レーンのレシートには選択されたプロバイダ、モデル、エフォートが記録される。各レーンは 1 つのボックスであり、具体的なシナリオ、保存するスクリーンショット、合格条件を持つ。レーンの 1 つは **トランクに対するリグレッションレーン** である。同じ要となるシナリオをトランクとヘッドで実行する。トランクにその機能がない場合、レーンはその事実を記録し、トランクの結果をでっち上げる代わりに、差分が追加する挙動と、ユーザーが待つ最終状態をゲートの対象にする。パフォーマンスゲートは両側で判定する。トランクとヘッドの両方が、名指しされたメトリクスを出さなければならない。トランクにその機能がない場合は、差分が追加する処理も切り出し、その処理と、ユーザーが待つエンドツーエンドの状態に絶対的な予算を設定する。異なるシナリオ間の比率を主張しない。パフォーマンスブロックには、メトリクス、交互に実行するプローブ、先に測定するトランクのベースライン、不合格となる数値を含む規則を記す。インタラクションを変える PR はレビューゲート付きである。オペレーターがマージ前に、スクリーンショットと動画を添えてチャットでレビューする。インタラクションを変えない PR は `**Review gate.** None. <PR id> is not review-gated.` と書き、その下にボックスを置かない。

**ドライバースキル。** サーフェスに応じて選ぶ。ブラウザ、Electron、Web UI は Claude Code の **verify** スキルを使う。CLI と TUI は Claude Code の **run** スキルを使う。ネイティブモバイルは、リポジトリにあるシミュレーター操作スキルを使う。Codex では [`../references/codex-tools.md`](../references/codex-tools.md) に従って置き換える。2 つのサーフェスに触れる PR は両方にレーンを持つ。ドライバースキルのないサーフェスは Appendix C のリスクとし、そのライブブロックにも各レーンがどう操作するかを記す。

Claude Code では、30 分ごとの監査ティックを、ダイナミックモードの実際の `/loop` としてセットする。Codex では [`../references/codex-tools.md`](../references/codex-tools.md) に従って周期をセットする。周期を記憶に任せてはならない。スキル相対のリンクはこのプレイブック本文の中にとどめる。計画ファイルにコピーしない。

````markdown
# <Program> plan

<Under ten lines. What changes, for whom, the rule the program enforces, and the PR ids in order.>

## How to read this

One box is one unit of work. Every box names the evidence that checks it. A nested box is a sub-step of the box above it. Check a box only when its evidence exists, a file, a log line, a screenshot, a test run, or a SHA. The body is a how-to. The appendices explain and record.

The program runs `skills/poteto-mode/playbooks/<execution playbook>.md` under the installed plugin. <Who merges, and which PR ids are the operator's items that stop at merge-ready.>

Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

## Program checklist

### Arm the program

- [ ] State the protocol and this plan to the operator, then stop. Start execution only on the operator's explicit go.
- [ ] On the operator's go, write the program objective into the standing orders and your todolist with this exact text. "<The plan path, the PR ids in order, the verification rule, who merges, and the done condition.>"
- [ ] Read these from the installed plugin at program start. Re-read them at every tick.
  - [ ] `skills/poteto-mode/playbooks/<execution playbook>.md`
  - [ ] `skills/swarm/SKILL.md`
  - [ ] `<driver skill path>`
  - [ ] `skills/poteto-mode/playbooks/opening-a-pr.md`
  - [ ] `skills/<each other leaf skill the program uses>/SKILL.md`
- [ ] Arm the 30-minute audit tick as a real cadence. Never leave the cadence to memory.
- [ ] Use this tick prompt, verbatim. "Re-read the execution playbook from the installed plugin and the standing orders. Audit the operation against both and fix drift in this tick. Probe every active lane and judge progress by side effects only. Stand down a lane only on affirmative failure evidence, and dispatch its replacement in the same tick. Then send the operator a status message, whether or not anything changed, with the queue table of PR, owner, state, and head SHA, the verdicts since the last tick, what merged, open operator gates, and blockers."
- [ ] On the operator's hold or stand-down, send every owner a zero-writes order at once.

### Spawn owners

- [ ] Spawn one owner per PR with the full lifecycle the execution playbook names.
- [ ] Follow this dependency graph. Start dependent work only after its parent merges, or rebase its branch onto the parent's exact tip when the execution playbook stacks. A same-repository child PR targets its parent branch. A fork child PR targets trunk while retaining local parent ancestry. Freeze the bottom-to-top order because fork PR bases do not encode it.
  - [ ] <PR id> and <PR id> are independent and first. Both branch from `main`.
  - [ ] <PR id> after <PR id>.
- [ ] Hold the file boundaries. <PR id or class> touches only `<glob>`.
- [ ] Hold the review gate. <PR ids> change an interaction. They wait for the operator's review in chat with screenshots and a video before merge.

### PR mechanics, for every PR

- [ ] Resolve the forge once. Default to `gh`; if `command -v origin` succeeds and Origin can resolve the repository, use `origin pr` for every PR operation. Record any fallback to `gh`. Record the intended PR base repository as canonical `<base-repo>` and validate it through the active forge. Do not infer it from the checkout's default remote. Capture it as a shell variable and pass `--repo "$base_repo"` to every `gh pr` command. Resolve and validate `<head-url>` through Shipping step 1 and capture it as `head_url` for the live-lane fetch. When the head repository is a fork, validate its identity and record its owner and repository name as `<fork-owner>` and `<head-name>`. Never require `gt`.
- [ ] Open the PR before self-proof and follow the readiness rule in `skills/poteto-mode/playbooks/opening-a-pr.md`. Open it ready by default. When repository instructions require a draft until named evidence exists, keep it draft until that evidence is recorded. Use `origin pr create --status open --base "$base_branch"` or `gh pr create --base "$base_branch" --repo "$base_repo"` for a ready same-repository PR. A same-repository stack child targets its parent branch. Every fork PR targets trunk. With GitHub, capture the approved PR title and body as `<title>` and `<body>`, then create it with `gh api --method POST "repos/$base_repo/pulls" -f "title=$title" -f "body=$body" -f "head=$fork_owner:$branch" -f "head_repo=$head_name" -f "base=$trunk" --jq .html_url`; add `-F draft=true` when repository instructions require a draft. Otherwise use the resolved Origin command. Stacked fork branches retain local parent ancestry.
- [ ] Run the repo's lint and typecheck once before the PR-facing push. Push with hooks on.
- [ ] Run `/deslop` before each commit and `/no-comments` before review.
- [ ] Triage every Bugbot and security-reviewer comment per `skills/poteto-mode/references/bugbot-triage.md` under the installed plugin.
- [ ] Before babysit, rebase each independent PR and stack root onto current trunk. Rebase each unmerged stack child onto its parent's exact tip. After its parent merges, use Shipping's explicit old-base-to-trunk rebase before the child's merge-ready report.

### Verdict and merge, for every PR

- [ ] At the merge-ready head SHA, run the swarm per `skills/swarm/SKILL.md`. One gates lane. The ten live lanes from the PR's **Verify, live** block. The perf lane from its **Verify, perf** block. One audit lane that reads the diff and the receipts and distrusts the PR body.
- [ ] Clean only when every lane is `PASS`. Findings go back to the owner. A new head gets a fresh swarm and a fresh verdict.
- [ ] <The merge or append rule from the execution playbook, with the verdict SHA, current landing SHA, recorded patch base, and patch ID rule from `skills/poteto-mode/playbooks/shipping.md`.>

### Boot recipe, for every live lane

Each live lane is one `swarm workers` lane at the PR head, resolved through provider dispatch, in its own worktree or output directory, with its own receipt. Drive the surface only through the driver skill this plan names.

- [ ] `git fetch -- "$head_url" "refs/heads/$head_branch" && git checkout --detach "$head_sha"` in the lane's worktree.
- [ ] <Start the backend and the surface. Wait for ready.>
- [ ] <Deliver input only through the driver skill's commands. Name the read-only diagnostics.>
- [ ] Save every screenshot to `<scratch path>/swarm-<pr-id>/worker-<n>/<slug>.png` and return the paths with the receipt path.

## <Task as a verb phrase> (<PR id>)

**Depends on.** <PR id, or None.>

**Files.**

- [ ] Edit `<path>`.
- [ ] Create `<path>`.
- [ ] Delete `<path>`.

**Build.**

- [ ] <One change. Name the symbol and the file.>

**You see.**

- [ ] <One observable result, with the exact log line or screen state.>

**Verify, unit.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] <Test file and the case it gains.> Run `<command>`.

**Verify, live.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked. Ten lanes on the configured `swarm workers` role at the PR head, per the boot recipe.

- [ ] Lane 1. Regression lane against trunk. Run <the same load-bearing scenario> at trunk and head. If trunk lacks the feature, record that and gate <the behavior the diff adds plus the end state the user waits for>. Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 2. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 3. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 4. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 5. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 6. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 7. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 8. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 9. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 10. <Scenario.> Save `<slug>.png`. Pass when <predicate>.

**Verify, perf.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] Metric. <What is measured at both trunk and head. If trunk lacks the feature, also name the diff-added work and the end-to-end state the user waits for.>
- [ ] Probe. <The command or procedure, run at trunk and at the head, interleaved. Both sides must produce the metric.>
- [ ] Baseline. Record the trunk <value> first.
- [ ] Rule. <Head against trunk, with the number that fails, such as 20. If the scenarios differ, add absolute budgets for the diff-added work and the user-visible end state instead of an invalid ratio.>

**Review gate.** The operator reviews before merge.

- [ ] Copy lane <n> screenshots into `<media path>/<pr-id>-review-<slug>.png`.
- [ ] Record a 30 to 60 second video of the change on a live lane. Save it as `<media path>/<pr-id>-review.mp4`.
- [ ] Post the screenshots and the video in chat. Stop at merge-ready. Wait for the operator's click.

**Merge.**

- [ ] Root's clean verdict at the exact head SHA.
- [ ] Bugbot triage done.
- [ ] After the verdict, an owner merge uses Shipping step 4 to move the PR from its recorded patch base onto current trunk. An appended stack child keeps its recorded parent tip until that parent lands. Record the current landing SHA. Preserve the verdict only when the patch ID stays unchanged.
- [ ] <The owner squash-merges its own PR, or the root appends it to the frozen bottom-to-top stack and the operator lands it in order. State whether same-repository child PRs target parent branches or fork child PRs target trunk while retaining local parent ancestry.>

## Close the program

- [ ] Every box above is checked with its evidence.
- [ ] Reply to the operator with the report the execution playbook names.

## Appendix A. Prototype evidence

<Each open question a prototype answered, with the branch, the SHA, and the artifact links. Each question that stays unproven.>

## Appendix B. Alternatives rejected

<Each approach weighed and why it lost.>

## Appendix C. Risks

<Each risk with the PR it lands in and what the owner watches.>

## Appendix D. Links and reading list

<Docs to read before editing. Which PRs get `skills/how/SKILL.md` and `skills/interrogate/SKILL.md`. The trail per `skills/show-me-your-work/SKILL.md`.>
````

**返答:** 計画のパス、依存関係とレビューゲート付きの集合を添えた PR の ID、プロトタイプが証明したことと未証明のまま残ること、チェックスクリプトの出力。
