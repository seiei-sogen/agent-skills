# CONTEXT.md フォーマット

## 構造

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence description of the term}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

## ルール

- **意見を持て。** 同じ概念に複数の単語がある場合は、最良のものを選び、その他は`_Avoid_`の下にリストしてください。
- **定義は簡潔に。** 最大1、2文で。何を『する』かではなく、何であるかを定義してください。
- **このプロジェクトの文脈に特有の用語のみを含めてください。** 一般的なプログラミングの概念（タイムアウト、エラータイプ、ユーティリティパターンなど）は、プロジェクトで広く使われていても含めるべきではありません。用語を追加する前に次の質問をしてください：これはこの文脈に固有の概念か、それとも一般的なプログラミング概念か？前者のみが含まれます。
- **自然なクラスターが現れたら、用語を小見出しでグループ化します。** すべての用語が単一のまとまりのある領域に属する場合は、フラットなリストで構いません。

## 単一コンテキスト vs 複数コンテキストのリポジトリ

**単一コンテキスト（ほとんどのリポジトリ）:** リポジトリのルートに1つの`CONTEXT.md`。

**複数コンテキスト:** リポジトリのルートにある1つの`CONTEXT-MAP.md`がコンテキストを列挙し、それらの配置場所や相互関係を示します:

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md): receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md): generates invoices and processes payments
- [Fulfillment](./src/fulfillment/CONTEXT.md): manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices
- **Ordering ↔ Billing**: Shared types for `CustomerId` and `Money`
```

スキルはどの構造が適用されるかを推測します:

- もし存在`CONTEXT-MAP.md`なら、文脈を見つけるために読んでください
- もし根の根`CONTEXT.md`のみ、単一の文脈が存在する場合
- どちらも存在しない場合は、最初の項が解決されたときに怠惰に根`CONTEXT.md`を作成します

複数の文脈が存在する場合は、現在のトピックがどの文脈に関連しているかを推測してください。分かりにくい場合は質問してください。
