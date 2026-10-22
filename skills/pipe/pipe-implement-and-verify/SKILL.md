---
name: pipe-implement-and-verify
description: 品質ゲートを通過した AsciiDoc 要件定義書・設計文書・実装計画から、計画タスクを上から実装・検証し、動いているアプリで EARS 規則と Gherkin シナリオを実証して、結果を実装計画へ記録する。実装計画の確定後、差分レビューの前に使う。commit、push、PR 作成は行わない。
---

# 実装計画を実装し、動いているアプリで実証する

品質ゲートを通過した設計文書と実装計画に従ってコードを実装・検証し、要件を動いているアプリで実証する。
commit、push、PR 作成は行わない。

## 子スキル

各工程を始める前に、対応する `SKILL.md` を最後まで読む。

- `poteto-mode-start`
- `principle-anti-bad-excess`
- `pstack:tdd`。Skill ツールで呼べない場合は pstack プラグインの `skills/tdd/SKILL.md` を読む
- `superpowers:test-driven-development`
- `agent-browser`

Quint モデルがある対象を実装する場合は、`quint-execute-spec` を利用できることを確認し、実装を始める前にその `SKILL.md` を読む。
pstack の `create-verification-skill` で作った実証スキル（`verify-auto-reserve`、`verify-ar-web` など `verify-` で始まるスキル）がある場合は、「動いているアプリで実証する」の規則で選び、実証の前にその `SKILL.md` と機能マップを最後まで読む。

子スキルが見つからない場合は同等手順で代替せず、見つからないスキル名を報告して停止する。
指示が衝突する場合は、現在のユーザー指示、このスキルの工程固有の指示、子スキルの通常指示の順に優先する。

## 入力と成果物

入力は次の3件とする。

- 品質ゲートを通過した `req-<topic>.adoc` 1件
- 同じ対象の `design-<issue-token>-<topic>.adoc` 1件。設計文書が参照する Quint モデルも読む
- 同じ対象の `implementation-plan-<issue-token>-<topic>.adoc` 1件

入力が不足している場合は、必要なパスを確認してから始める。3件が同じ要件の成果物だと確認できない場合は停止する。

成果物は、計画タスクを実装したコードとテスト、および進捗、検証結果、実証結果を反映した実装計画とする。

## poteto-mode で実装を進める

入力を確定した後、実装を始める前に `poteto-mode-start` を使う。
このスキルへの依頼全体を対象タスクとして渡す。poteto-mode がすでに有効な場合は再度呼び出さず、その状態を引き継ぐ。

## 計画タスクを実装する

品質ゲートを通過した設計文書と実装計画に従い、タスクを上から実行する。Quint モデルがある対象は `quint-execute-spec` を使い、設計文書に記録した操作・不変条件と実装の対応を検証する。
テストは、要件の振る舞いが壊れたときに検出できる最小限の数だけ書く。テストの要否、シーム、理由はユーザーに確認せず決め、実装計画へ記録する。実装計画にあるテストも同じ基準で判定し直す。

- テストの候補ごとに `principle-anti-bad-excess` の分類を当てる。要件の振る舞いが壊れても、ほかのテスト、型チェック、lint のどれでも検出できない場合、それを検出するテストは必要の更新として書く。すでに検出できる振る舞いを重ねて確かめるテストは充実として書かず、実装計画に提案として残す。要件と関係のないテストは過剰として切る。
- 書くと決めた振る舞いには、`pstack:tdd` の基準で悪いテストにならないシームを選ぶ。良いテストを書けるシームがない場合は、`pstack:tdd` の「If a Failing Test Is Impractical」に従って最も近い実行可能な確認で代え、検出できずに残るリスクを実装計画に記録する。
- 書くと決めたテストは、`superpowers:test-driven-development` の基準と手順で実装する。同スキルの「When to Use」にある常にテストを書く規則、人間への確認、「Verification Checklist」の「Every new function/method has a test」は、この判定で置き換える。

1. 各タスクに必要なコードと周辺文脈を読み、検証する振る舞いと公開インターフェースを確認する。
2. 上の基準でテストの要否を決める。テストを書く振る舞いは `superpowers:test-driven-development` の赤→緑で1件ずつ実装し、テストを書かない振る舞いは計画どおり実装する。
3. 対象を絞った検証から始め、変更全体に必要な lint、型チェック、テスト、ビルドへ広げる。
4. 今回の変更が原因の失敗を修正し、同じ検証を再実行する。
5. 完了した計画タスクと実際の検証結果を実装計画へ反映する。

タスクの完了時は、`Satisfies` の EARS 規則を満たし、`Done when` の Gherkin シナリオまたは測定・確認条件を実際に検証した結果を記録する。

計画外の変更が必要になったら、要件・設計文書・Quint モデル・計画の整合を確認して更新してから実装する。Quint の不変条件を通すためだけにモデルを弱めず、要件の根拠と検査結果を確認する。対象外の既存問題は修正せず記録に留める。

## 動いているアプリで実証する

全タスクの実装と検証を終えたら、動いているアプリで要件を実証する。

実証スキルは、対象リポジトリの `.claude/skills/` または `.agents/skills/` にある `verify-` で始まるスキルから、変更する機能を扱うものを選ぶ。対象リポジトリが `auto_reserve` か `auto_reserve_front` のときは、EARS 規則と Gherkin シナリオごとに、期待結果を観測する場所が「操作対象」に当たる側の実証スキルを次の表から選ぶ。

| 側 | 実証スキル | 場所 | 操作対象 |
| --- | --- | --- | --- |
| バックエンド | `verify-auto-reserve` | `/home/agir_wsl/develop/ghq_repos/github.com.fujita-kazuhiko/hello-ai/auto_reserve/.claude/skills/verify-auto-reserve` | AutoReserve API、Respo API、admin 画面 |
| フロント | `verify-ar-web` | `/home/agir_wsl/develop/ghq_repos/github.com.fujita-kazuhiko/hello-ai/auto_reserve_front/.claude/skills/verify-ar-web` | ar_web の Web 画面 |

表の場所は `SKILL.md` を読む先である。実証スキルは、使う checkout のルートで実行する。このスキルを実行している側は、実装した checkout を使う。実証スキルのフォルダは git の管理外なので checkout にないことがある。その場合は、`SKILL.md` の同梱スクリプトのパスを表の場所に読み替えて呼び、作業ディレクトリはその checkout のルートのままにする。

バックエンドの変更がフロントの画面に現れる要件と、フロントの変更がバックエンドの変更に依存する要件では、両方の実証スキルを使う。

- このスキルを実行していない側（もう一方の側）は、そのリポジトリの `git worktree list` に出る checkout から、要件のためにその側へ変更が要るかで選んで実証スキルを実行する。変更が要らず既存のコードのまま期待結果が出るなら、既定ブランチの checkout を使う。変更が要るなら、それを含む checkout を使い、どの checkout にもなければ、その側は起動せず未検証とする。
- ar_web の API 接続先は、ar_web の README にある `NEXT_PUBLIC_API_BASE_URL` に、`verify-auto-reserve` の Doctor を通したバックエンドの origin へ `/api` を付けた値を入れて指定する。この値を付けて ar_web を新しく起動する。同じ checkout に別の接続先の既存サーバーがあって起動できない場合は、止めずに接続先の不足として未検証とする。
- ar_web がそのバックエンドへ接続したことを、`verify-auto-reserve` の `server.log` に ar_web の操作に対応するリクエストが記録されたことで確かめる。ほかの接続先で得た ar_web の結果は、バックエンドの変更の証拠にしない。

起動、Doctor、証拠、後片付けは実証スキルの手順に従う。実証スキルに手順がない画面操作は `agent-browser` で行い、証拠はその画面を受け持つ実証スキルの Evidence の場所へ残す。画面のない要件は API の応答や実行コマンドの出力で確かめる。実証スキルがない場合は `agent-browser` だけで行う。

要件定義書の EARS 規則と Gherkin シナリオごとに、その規則・シナリオが示す入口を機能マップにないものも含めてすべて実際に操作し、pass、fail、未検証、使った実証スキルまたはツール、証拠の場所を実装計画に記録する。

未検証にするのは、起動・認証・接続先の不足や、実証スキルが許す方法を試しても検証用データを用意できず操作できない場合と、もう一方の側に必要な変更がどの checkout にもない場合だけとし、その理由を書く。fail は原因を直し、対象を絞った検証と実証をやり直す。最大3巡で fail が0件になったら完了とする。3巡後も fail が残る場合は停止し、残った fail を報告する。

## 完了報告

次を簡潔に報告する。

- 実装した計画タスクと、更新した要件定義書、設計文書、Quint モデル、実装計画
- 実行した検証と結果
- EARS 規則・Gherkin シナリオごとの pass、fail、未検証の件数と、未検証の理由
- 残課題。なければ「なし」
