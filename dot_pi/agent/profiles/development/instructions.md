# Pi 機能開発ルール

- このProfileは、ユーザーが何かしらの開発・実装の意欲があるときに呼び出される想定である。
- 開発・実装には `scaffold` という仕様策定から詳細設計／実装の一連の流れを通る方法と、 `jig` という中小規模の開発をスピーディに終わらせるための方法の2種類がある。

## 方法の分岐

### Scaffold

- ユーザーからの要望が、仕様策定・基本設計・詳細設計/実装の一連の流れを通るべき、大きな要望であれば、`/scaffold` スキルによる実装を行う。
- `scaffold` は大きなスキルだが確実なデリバリーを目的とする。

### Jig

- ユーザーからの要望の影響範囲が小さく、スピードを優先すべきであれば `/jig` スキルにて実装を進める。

## ゴール

- ユーザーからの要望に応じた開発タスクの完了をもって、セッションの完全なゴールとする。

## サブエージェントのモデル選定

- `scaffold`、`jig`のいずれでもサブエージェントが管理・実装を行う想定である。そのため、モデル選定表をここに記載する。

| 担当           | モデルID                   | thinking | 区分 |
| -------------- | -------------------------- | -------- | ---- |
| coding-manager | `openai-codex/gpt-6.1-sol` | `medium` | 基本 |
| coder          | `openai-codex/gpt-6-luna`  | `xhigh`  | 基本 |
| coder          | `openai-codex/gpt-6.1-sol` | `medium` | 上位 |
| tester         | `openai-codex/gpt-6-luna`  | `xhigh`  | 基本 |
| tester         | `openai-codex/gpt-6.1-sol` | `medium` | 上位 |

- `Feature Issue` に全担当の指定、`Task Issue` に実際の `coder`/`tester`指定を記録する。`Task Issue`のmanager指定は親`Feature Issue`を参照し、重複させない。親セッションのモデルは本表で指定しない。
- 区分について：原則基本を使う。表内上位は理由があれば選んでよい。
- 担当・model・thinkingが完全一致する組み合わせだけを使う。

# Pi 機能開発時の注意事項

## Issue投稿と承認の境界

- このフローの規定された担当/範囲に限り、Issue新規投稿・本文更新・close、Projects登録・状態更新・作成・field/view変更、親子/依存関係設定、通常pushは追加ユーザー承認不要とする。
- coder/tester自身のpush・merge・Issue/Projects操作は禁止し、必要操作はmanager/親が行う。Task→Featureはmanager、Feature→Epicは親が、必要な検証合格後に統合する。
- Epic→mainのマージは対象と検証結果を示してユーザー承認後に親が行う。mainへの通常pushは追加承認不要だが、未承認マージを正当化しない。
- 削除、force push、未コミット変更の上書き、権限/認証変更、依存インストール、CI/CD・OS・セキュリティ設定、タグ/リリース公開、本番データ変更、メール/フォーム等の送信、購入等には本例外を広げない。
- 仕様・基本設計・受け入れ要件の内容承認と実装開始指示は維持する。投稿できることと、内容が承認済みであることを混同しない。

### 新規Issueの作成方法

1. Epic/Feature/Taskのv2専用テンプレートと共通モデルポリシーを使い、入力draftファイルを作成する。`draft`は作業名でありCLIサブコマンドではない。
2. `gh-issueflow validate <draft> --template <template>`で検証する。
3. `gh-issueflow preview <draft> --template <template> --json`で投稿先・タイトル・本文・担当指定と内容固定digestを確認する。
4. 対応済みCLIの`gh-issueflow submit-auto <draft> --template <template> --expected-digest <SHA-256> --repo <OWNER/REPO>`で投稿する。
5. 成否と実Issue番号を確認して親子/依存関係とProjectを設定し、読み戻す。

- 配布テンプレートは`epic.yml`、`feature.yml`、`task-v2.yml`、共通ポリシーは`policies/models-v2.yml`。実際の配布先を確認する。現行環境の所在や版が不明なら投稿しない。
- 正式な自動投稿・表内上位の承認記録不要に対応したCLIが稼働するまで、新規投稿を停止する。隔離worktreeでの実装・テストだけで稼働版更新済みと扱わない。
- 検証、投稿先照合、秘密情報候補の拒否、内容固定は維持する。入力/template/policyが変われば再検証/再previewし新digestを使う。expected-digestはユーザー承認の証拠ではない。
- 検証不合格・CLI利用不能では停止する。架空の承認記録で旧submitを通したり、直接`gh issue create`へ黙って切り替えたりしない。成否不明では確認前に再投稿しない。
- 既存Issue本文更新は新規投稿と区別して、対象・変更内容を確認し更新後に読み戻す。v1の承認付き投稿は従来経路として維持するが、新フローv2と混用しない。

## 共通編集規約と配布

- `any`型禁止。ファイル編集前にReadで現在内容を確認する。
- 完了宣言前に`superpowers:verification-before-completion`を読み、実際のtest/type-check/lint等の出力を確認して提示する。存在しないコマンドを実行済みと捏造しない。
- コミット/PRへAI帰属表記を付けない。既存のgit hookは本作業で変更しない。
- 関連skill: 新機能/仕様変更は`superpowers:brainstorming`、実装前のテストは`superpowers:test-driven-development`、不具合は`superpowers:systematic-debugging`、worktreeは`superpowers:using-git-worktrees`、レビューは`superpowers:requesting-code-review`。調査並列化skillは実際に独立した調査と委任許可がある場合に使う。
- 担当定義の配布先は各プロジェクトの`.pi/agents/coding-manager.md`、`.pi/agents/coder.md`、`.pi/agents/tester.md`。共通ルール例外・モデル/工具/能力・CLI稼働版を確認してから運用する。copi保存、検証用定義、恒久有効化は区別する。
- 進行中の旧フロー作業を黙って切り替えない。未処理・取得時点・依存条件・適用先を明示して移行する。
