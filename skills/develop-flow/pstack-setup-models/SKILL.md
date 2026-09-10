---
name: pstack-setup-models
description: pstack のモデル設定を、実行中の Claude Code または Codex に合う方法で開始する。pstack の初期設定やモデル構成の更新を依頼されたときに使う。
---

# pstack のモデルを設定する

実行中のホストを確認し、open-pstack 本体の `pstack:setup-pstack` を次の方法で呼び出す。

- Claude Code では `/pstack:setup-pstack` を実行する。
- Codex では `pstack:setup-pstack` スキルを使う。

呼び出したスキルの対話と検証を、モデル設定が保存されるか、設定を保存せず終了するまで続ける。

`pstack:setup-pstack` が見つからない場合は、open-pstack が未導入または未読み込みであることと、導入元の `https://github.com/ericlitman/open-pstack` を伝える。
