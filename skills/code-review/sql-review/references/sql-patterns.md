# SQL レビューの判定基準と修正例

SKILL.md の手順 2 の各観点について、何を問題と判断するかと、修正例を示す。
SQL は PostgreSQL の構文で書いてある。MySQL など他の DBMS では同等の機能に読み替える。

## 目次

1. [実行計画（EXPLAIN）の読み方](#1-実行計画explainの読み方)
2. [インデックスの種類と使い方](#2-インデックスの種類と使い方)
3. [インデックスが効かない書き方](#3-インデックスが効かない書き方)
4. [取得量を減らす](#4-取得量を減らす)
5. [JOIN とサブクエリ](#5-join-とサブクエリ)
6. [N+1 クエリ](#6-n1-クエリ)
7. [集約](#7-集約)
8. [書き込みの一括化](#8-書き込みの一括化)
9. [スキーマとマイグレーション](#9-スキーマとマイグレーション)
10. [実行状況を調べるクエリ](#10-実行状況を調べるクエリ)

## 1. 実行計画（EXPLAIN）の読み方

```sql
-- 見積もりだけ
EXPLAIN SELECT id, email FROM users WHERE email = 'user@example.com';

-- 実際に実行して実測値とバッファ読み取り量を取る（SELECT にだけ使う）
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, email FROM users WHERE email = 'user@example.com';
```

| 項目 | 読み方 |
| --- | --- |
| Seq Scan | テーブル全体を読む。大きいテーブルでは遅い。小さいテーブルや大半の行を返す条件では妥当 |
| Index Scan | インデックスで行を絞り、テーブルを読む |
| Index Only Scan | インデックスだけで完結する。`Heap Fetches` が少なければ最も速い |
| Nested Loop | 外側が小さいか、内側をインデックスで引けるなら妥当。外側の行数が多く内側をインデックスで引けないと遅い |
| Hash Join | 大きい集合同士の結合に向く |
| Merge Join | 両方がソート済みのときに向く |
| cost | 見積もりコスト。絶対値ではなく、変更前後や代替案との比較に使う |
| rows | 見積もり行数。`EXPLAIN ANALYZE` の実測 `rows` と大きく違えば、統計が古いか条件の選択率を誤っている |
| actual time | 実測時間。ループ回数（`loops`）を掛けた値が実際の合計 |

見積もりと実測の乖離が大きい場合は、統計が古い可能性がある。根拠に「要確認: 統計の鮮度」と書いて指摘を続け、`ANALYZE <table>` による更新はユーザーの許可があれば行う。
パーティション化済みテーブルへのクエリは、パーティションキーの条件を関数適用なしで持っているかを確認する。ないと計画に全パーティションが並ぶ。

### ヒント句とプランナー設定

差分に MySQL の `USE INDEX` や `FORCE INDEX`、PostgreSQL の `SET enable_nestloop = OFF` の変更があれば、計画を固定または誘導している。`max_parallel_workers_per_gather` のような並列度の設定は、ワーカー数がほかのクエリに与える影響を確認する。
統計の更新やインデックスの追加で同じ計画を得られないかを先に確認する。固定した計画はデータ分布が変わると劣化し、セッション設定は同じセッションのほかのクエリにも影響する。
残す場合は、影響範囲（クエリ単位か、セッション単位か）と、固定が必要な理由を根拠に書く。

## 2. インデックスの種類と使い方

| 種類 | 向いている条件 |
| --- | --- |
| B-Tree | 既定。等価と範囲の条件、`ORDER BY` |
| Hash | 等価条件だけ |
| GIN | 全文検索、配列、JSONB |
| GiST | 幾何データ、全文検索 |
| BRIN | 物理的な並びと値に相関がある巨大テーブル（時系列の追記など） |

```sql
-- 単一列
CREATE INDEX idx_users_email ON users(email);

-- 複合インデックス。列順が重要で、先頭列が条件にないと効きにくい
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- 部分インデックス。条件に合う行だけをインデックスに含めて小さく保つ
CREATE INDEX idx_active_users ON users(email)
WHERE status = 'active';

-- 式インデックス。WHERE で列に関数を適用する場合に使う
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- カバリングインデックス。SELECT する列を含めて Index Only Scan を狙う
CREATE INDEX idx_users_email_covering ON users(email)
INCLUDE (name, created_at);
```

インデックスは `INSERT`、`UPDATE`、`DELETE` のたびに更新されるので、追加するほど書き込みが遅くなる。
追加を提案するときは、同じ先頭列を持つ既存インデックスで賄えないか、ほかのクエリも同じインデックスを使えるかを確認する。

| 確認項目 | 判断 |
| --- | --- |
| 結合に使う外部キー列にインデックスがあるか | 親を少数に絞って子を引く結合で、ないと子テーブルを全件読む。親の削除や更新でも子の検索が走る |
| `ORDER BY ... LIMIT` の並び順に合うインデックスがあるか | ないと全件を並べ替えてから先頭を取る。列順が一致し、方向がすべて同じかすべて逆のインデックスで先頭だけ読める。方向を合わせる必要があるのは ASC と DESC が混在する場合だけ |
| 等価条件と並び替えを組み合わせたクエリに、等価条件の列を先頭、範囲条件や `ORDER BY` の列を後ろに置いた複合インデックスがあるか | `WHERE status = 'paid' ORDER BY created_at DESC LIMIT 20` には `(status, created_at)`。`status` だけの単独インデックスでは並べ替えが残る。条件の値が固定なら部分インデックス `ON orders(created_at) WHERE status = 'paid'` でもよい |
| 値の種類が少ない列（`status` など）に単独インデックスを足していないか | 選択性が低く使われにくい。部分インデックスか、絞り込み列を先頭にした複合インデックスを検討する |

## 3. インデックスが効かない書き方

| 書き方 | 理由 | 修正 |
| --- | --- | --- |
| `WHERE LOWER(email) = ...` のように列に関数を適用 | インデックスは列の値で作られており、関数を適用した値では引けない | 式インデックスを作るか、正規化した値を格納する |
| 暗黙の型変換。MySQL で文字列の列を数値と比較する、PostgreSQL で `bigint` の列に `numeric` のパラメータをバインドするなど | 列側に変換が入りインデックスを使えない | 比較する値の型を列に合わせる |
| `LIKE '%abc%'` のような前方ワイルドカード | B-Tree は先頭からしか辿れない | `pg_trgm` 拡張の GIN インデックス（`gin_trgm_ops`）を使う |
| `LIKE 'abc%'` でインデックスが使われない | 照合順序が C でないと B-Tree は前方一致に使われない | `text_pattern_ops` を指定したインデックスを作る |
| `OR` でつないだ別の列の条件 | 単一インデックスで両方を絞れない | 各列にインデックスを置いて Bitmap Scan を狙うか、`UNION` に分ける（重複の扱いが変わるので「仕様変更が必要」） |
| 複合インデックスの先頭列を条件に使わない | 先頭列から順にしか辿れない | 列順を変えるか、条件に合う別のインデックスを作る |

```sql
-- 修正前: 列への関数適用でインデックスが効かない
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

-- 修正案 1: 式インデックスを作る
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- 修正案 2: 正規化した値を格納して等価比較にする（仕様変更が必要。既存データの正規化と書き込み側の変更を伴う）
SELECT * FROM users WHERE email = 'user@example.com';
```

## 4. 取得量を減らす

### 不要な列

```sql
-- 修正前: 使わない列まで取得する。大きい列を含む多数行の取得で I/O が増える
SELECT * FROM users WHERE status = 'active';

-- 修正後: 必要な列だけにする。カバリングインデックスがあれば Index Only Scan を狙える
SELECT id, email, name FROM users WHERE status = 'active';
```

### 大きい OFFSET

`OFFSET` は読み飛ばす行もすべて読むので、ページが進むほど遅くなる。

```sql
-- 修正前
SELECT * FROM users
ORDER BY created_at DESC
LIMIT 20 OFFSET 100000;

-- 修正後: 直前のページの最後の値を条件にする（カーソル方式。仕様変更が必要。API のページ指定が変わる）
SELECT * FROM users
WHERE created_at < '2024-01-15 10:30:00'
ORDER BY created_at DESC
LIMIT 20;

-- 同じ created_at が複数ある場合は、一意な列を組み合わせる
SELECT * FROM users
WHERE (created_at, id) < ('2024-01-15 10:30:00', 12345)
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- 並び順と列順が一致するインデックスが必要（方向はすべて同じなら逆向きでも使える）
CREATE INDEX idx_users_cursor ON users(created_at, id);
```

### 全件 COUNT

```sql
-- 修正前: 全行を数える
SELECT COUNT(*) FROM orders;

-- 概算でよい場合（仕様変更が必要）: 統計情報を使う
SELECT reltuples::bigint AS estimate
FROM pg_class
WHERE relname = 'orders';

-- 業務上、期間で絞った件数で足りる場合（仕様変更が必要）:
-- 絞った列にインデックスがあれば Index Only Scan になりうる
CREATE INDEX idx_orders_created ON orders(created_at);
SELECT COUNT(*) FROM orders
WHERE created_at > NOW() - INTERVAL '7 days';
```

## 5. JOIN とサブクエリ

### 絞り込みの位置

プランナーは `WHERE` の条件を結合より前に押し下げるので、内部結合では条件を `ON` と `WHERE` のどちらに置いても、カンマ結合と `JOIN ... ON` のどちらで書いても、性能には影響しない。
グループ化列やウィンドウ関数の `PARTITION BY` 列だけを参照する外側の条件も、集約サブクエリの中へ押し下げられる。
押し下げられない次の形だけを指摘する。

| 形 | 理由 | 修正 |
| --- | --- | --- |
| `LIMIT` を含むサブクエリや CTE への外側の条件 | 行数を確定してからでないと絞れない | 条件をサブクエリの中に移す。結果が変わるので「仕様変更が必要」とし、「要確認: 意図」を併記する |
| PostgreSQL 11 以前の CTE、または複数回参照される CTE | 実体化され、外側の条件が入らない | 12 以降は `WITH x AS NOT MATERIALIZED (...)` を指定する。11 以前はサブクエリに書き換える。どちらも複数回参照なら計算の重複との損得を実行計画で比べる。揮発性関数やデータ変更を含む CTE を除き結果は変わらないので「仕様変更が必要」は付けない |

### 相関サブクエリ

`SELECT` 句などスカラー位置の相関サブクエリは、外側の行ごとに実行される（実行計画の SubPlan と `loops`）。外側の行数が多い場合は、内側にインデックスがあっても `loops` と実測を見て判断する。
`WHERE EXISTS (...)` と相関のない `IN (...)` は準結合に変換されるので、相関サブクエリとしては対象外とする。結合列のインデックスは 2 節で確認し、準結合になったかは実行計画で確かめる。
`NOT IN` は相関の有無にかかわらず SubPlan になり、`work_mem` に収まらないと行ごとに走査する。`NOT EXISTS` への書き換えを検討する。両側の列が `NOT NULL` ならば結果は同じで、NULL を取りうる場合だけ「仕様変更が必要」とする。

```sql
-- 修正前
SELECT u.name, u.email,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_count
FROM users u;

-- 修正後: 結合して集約する
SELECT u.name, u.email, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name, u.email;
```

## 6. N+1 クエリ

親を 1 回取得した後、親の件数ぶん子を取得するクエリが発行される。
ORM の遅延ロードで起きやすく、SQL ではなくアプリケーションコードのループに現れる。

```python
# 修正前: users の件数 + 1 回のクエリが発行される
users = db.query("SELECT * FROM users LIMIT 10")
for user in users:
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user.id)
```

```sql
-- 修正案 1: 結合して 1 回で取得する
SELECT
    u.id, u.name,
    o.id AS order_id, o.total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

-- 修正案 2: 親の ID をまとめて子を 1 回で取得する
SELECT * FROM orders
WHERE user_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
```

```python
# 修正案 2 をアプリケーション側で行う例
users = db.query("SELECT * FROM users LIMIT 10")
user_ids = [u.id for u in users]
# プレースホルダ 1 つにリストは展開されないので、配列として渡す（PostgreSQL は = ANY）
orders = db.query("SELECT * FROM orders WHERE user_id = ANY(?)", user_ids)
orders_by_user = {}
for order in orders:
    orders_by_user.setdefault(order.user_id, []).append(order)
```

ORM では、`includes`、`preload`、`eager_load`、`select_related`、`prefetch_related` など、そのフレームワークの事前読み込み機能を使う。

## 7. 集約

```sql
-- 修正前: 行の条件を HAVING に置いている。PostgreSQL は自動で WHERE に移すので性能差はほぼない。
-- DBMS によっては集約後に捨てるので、WHERE に置くのが確実
SELECT user_id, status, COUNT(*) AS order_count
FROM orders
GROUP BY user_id, status
HAVING status = 'completed' AND COUNT(*) > 10;

-- 修正後: 行の条件は WHERE で先に絞る。HAVING は集約結果の条件にだけ使う。返す列は変えない
SELECT user_id, status, COUNT(*) AS order_count
FROM orders
WHERE status = 'completed'
GROUP BY user_id, status
HAVING COUNT(*) > 10;

-- WHERE の列を先頭にしたインデックスがあれば Index Only Scan になりうる
CREATE INDEX idx_orders_status_user ON orders(status, user_id);
```

同じ集約を繰り返し参照する場合は、マテリアライズドビューで事前計算する。
結果の鮮度が変わるので「仕様変更が必要」とし、更新タイミングと鮮度の要件を確認してから提案する。

`REFRESH MATERIALIZED VIEW CONCURRENTLY` で更新中も参照できるが、一意インデックスが必要になる。

## 8. 書き込みの一括化

一括化は、autocommit なら複数の文が 1 文で成功または失敗するようになり、トランザクションの単位が変わる。
ORM のループ内 `save` や `update` を `insert_all`、`update_all` などに置き換えると、さらにバリデーションとコールバックが動かなくなる。
この節の修正案にはすべて「仕様変更が必要」を付ける。

```sql
-- 修正前: 1 行ずつ INSERT
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com');

-- 修正後: 複数行をまとめる
INSERT INTO users (name, email) VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com');

-- 大量の場合: クライアントから流し込む COPY（psql の \copy やドライバの copy API）を使う
COPY users (name, email) FROM STDIN CSV HEADER;
```

```sql
-- 修正前: ID ごとに UPDATE
UPDATE users SET status = 'active' WHERE id = 1;
UPDATE users SET status = 'active' WHERE id = 2;

-- 修正後: IN でまとめる
UPDATE users
SET status = 'active'
WHERE id IN (1, 2);

-- 行ごとに値が違う場合: 一時テーブルと結合して更新する
CREATE TEMP TABLE temp_user_updates (id INT, new_status VARCHAR);
INSERT INTO temp_user_updates VALUES (1, 'active'), (2, 'inactive');

UPDATE users u
SET status = t.new_status
FROM temp_user_updates t
WHERE u.id = t.id;
```

## 9. スキーマとマイグレーション

| 確認項目 | 問題になる理由 |
| --- | --- |
| 差分で追加・変更したインデックスが、既存のインデックスと重複していないか | 書き込みコストと容量だけが増える。既存の未使用インデックスの削除を提案する場合は、下記「インデックス削除の条件」を満たす場合に限る |
| 追加・変更する列の型が、結合や比較の相手の列と一致し、値に対して過大でないか | 不一致は 3 節の暗黙の型変換を招く。過大な型は行とインデックスを大きくする |
| 差分で削除・変更するインデックス、列、制約に依存する既存クエリや外部キーがないか | 同じ先頭列を持つ残りのインデックスで賄えなければ、依存するクエリは Seq Scan に落ちる。外部キーの参照側インデックスを消すと、PostgreSQL では親の削除・更新時に子テーブルを全件読む。MySQL では外部キーが必要とするインデックスは削除できない。利用箇所をリポジトリ全体で検索して根拠に書く |
| 大きいテーブルへのインデックス作成や削除が書き込みを止めないか | PostgreSQL の通常の `CREATE INDEX` は書き込みを止め、`DROP INDEX` は読み取りも含めてテーブルへのアクセスを止める。`CONCURRENTLY` を付ければ止めないが、トランザクション内では使えないので単独のマイグレーションに分ける。作成に失敗すると INVALID なインデックスが残るので、`DROP INDEX CONCURRENTLY` してから再作成する。MySQL の InnoDB は既定でオンラインに作成する |
| 全行の書き換えを伴う DDL がないか | 互換のない型変更（`int` から `bigint` など）や、揮発性のデフォルト値付きの列追加は、書き換えの間ロックする。PostgreSQL 10 以前はデフォルト値付きの列追加がすべて書き換えを伴う。新しい列に段階的に移行する |
| 全行の検証を伴う制約追加がないか | `CHECK` と外部キーは `NOT VALID` で追加してから `VALIDATE CONSTRAINT` で検証する。`NOT NULL` は `CHECK (col IS NOT NULL) NOT VALID` を検証してから `SET NOT NULL` にする（PostgreSQL 12 以降） |
| `VACUUM FULL` や `CONCURRENTLY` なしの `REINDEX` がないか | `VACUUM FULL` はテーブルを排他ロックする。`REINDEX` は書き込みと、そのインデックスを使う読み取りを止める。`REINDEX CONCURRENTLY`（PostgreSQL 12 以降）か、停止時間を取れる時間帯に限る |

インデックス削除の条件。次をすべて満たす場合に限る。

- 主キー、一意制約、排他制約、外部キーを支えるインデックスではない
- プライマリとすべてのレプリカの統計ビューで未使用である
- 統計の観測期間（`stats_reset` 以降）に、月次バッチなど低頻度の処理が含まれている

## 10. 実行状況を調べるクエリ

接続先（SKILL.md の定義）がある場合に、指摘の根拠として使う。

```sql
-- 平均実行時間が長いクエリ（pg_stat_statements が有効な場合）
-- PostgreSQL 12 以前は total_time、mean_time
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Seq Scan が多いテーブル。インデックス不足の候補
SELECT
    schemaname,
    relname,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / seq_scan AS avg_seq_tup_read
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 10;

-- 使われていないインデックス。削除の候補。制約を支えるインデックスは除く
SELECT
    s.schemaname,
    s.relname,
    s.indexrelname,
    s.idx_scan,
    s.idx_tup_read,
    s.idx_tup_fetch
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.idx_scan = 0
  AND NOT i.indisunique
  AND NOT i.indisprimary
  AND NOT i.indisexclusion
ORDER BY pg_relation_size(s.indexrelid) DESC;
-- 外部キー列のインデックスは除外されないので、pg_constraint（contype = 'f'）の conkey と照合して除く

-- 統計の観測期間。この時刻以降の累計しか持たないので、月次バッチなどを含む期間かを確認する
SELECT datname, stats_reset FROM pg_stat_database WHERE datname = current_database();
```

統計はサーバーごとに取られるので、レプリカでだけ使うインデックスはプライマリで未使用に見える。すべてのレプリカで確認する。
`log_min_duration_statement` によるスロークエリログがあれば、実行頻度と実測時間の根拠に使える。
