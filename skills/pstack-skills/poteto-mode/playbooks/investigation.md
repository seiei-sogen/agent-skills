### Investigation

**答えの責任は自分にある。計画し、ルーティングし、書く。**

調査の要求は読み取り専用である。引用付きの説明または推奨を生み、コード変更は生まない。

1. **how** スキルを通じてルーティングする。動機を問う質問には、**why** スキルも通す。
2. スループットチェックポイントは 1 行にとどめる: `throughput checkpoint: n/a, read-only investigation`。
3. `how` の形の出力（Overview / Key Concepts / How It Works / Where Things Live / Gotchas）を生む。要求が代替案の間の決定なら、トレードオフの表を付けた推奨を生む。
4. 返答に **unslop** スキルを適用する。

PR なし、babysit なし、`architect` なし。ただし調査がコード変更に先行する場合は例外である。その場合はユーザーに引き渡し、Bug fix または Feature へ再ルーティングする。

**返答:** 調査の出力。「本当に確かか」という問いへの答えには、理由付きの自分の本当の判断を含める。前提が間違っているなら反論する（Autonomy を参照）。
