# MISSION.md フォーマット

`MISSION.md` はワークスペースのルートにあります。これは、ユーザーがこのトピックを学んでいる _理由_ を記録します。すべての教育上の決定（次に何を教えるか、どのリソースを提示するか、どの演習を作成するか）は、このドキュメントに遡って説明できる必要があります。

## テンプレート

```md
# Mission: {Topic}

## Why
{1-3 sentences. The concrete real-world goal the user is chasing. What changes in their life or work when they have this skill? Avoid abstract framings like "to understand X"; push for the underlying outcome.}

## Success looks like
- {A specific, observable thing the user will be able to do}
- {Another specific thing}
- {…}

## Constraints
- {Time, budget, prior commitments, learning preferences, anything that bounds the approach}

## Out of scope
- {Adjacent topics the user explicitly does not want to chase right now, protecting the zone of proximal development}
```

## ルール

- **ワークスペースごとに一つのミッション。** ユーザーが二つの無関係なことを学びたい場合、それは二つのワークスペースになります。
- **抽象より具体。** 「10月までにハーフマラソンを完走する」は「体を鍛える」より具体的です。「RustのCLIをチームに提供する」は「Rustを学ぶ」より具体的です。
- **曖昧さを突き返す。** ユーザーが理由を明確に言えない場合は、何かを書く前にインタビューしてください。悪いミッションは、ミッションがないよりも悪いです。
- **現実が変わったら修正する。** ミッションは変わる。ユーザーの目標が移動したら、このファイルを更新すること：古いミッションを残して将来のセッションを導くことはしない。
- **短く保つ。** `MISSION.md`が画面を越えて進む場合、それはコンパスでなくなり、計画になったということ。
