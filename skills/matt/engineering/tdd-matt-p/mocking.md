# モックすべきタイミング

モックは**システム境界**でのみ行う:

- 外部API（支払い、メールなど）
- データベース（場合による - テスト用DBを推奨）
- 時間/ランダム性
- ファイルシステム（場合による）

モックしてはいけないもの:

- 自分自身のクラス/モジュール
- 内部コラボレーター
- 自分で制御できるもの

## モック可能性のための設計

システム境界では、モックしやすいインターフェースを設計する:

**1. 依存性注入を使用する**

外部依存関係は内部で作成するのではなく、外部から渡す:

```typescript
// Easy to mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// Hard to mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. 汎用フェッチャーよりSDKスタイルのインターフェイスを優先する**

条件付きロジックを持つ1つの汎用関数ではなく、各外部操作ごとに具体的な関数を作成する:

```typescript
// GOOD: Each function is independently mockable
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD: Mocking requires conditional logic inside the mock
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

SDKアプローチの意味:
- 各モックは1つの特定の形を返す
- テストセットアップに条件付きロジックがない
- テストがどのエンドポイントを使用するかを確認しやすい
- エンドポイントごとの型安全性
