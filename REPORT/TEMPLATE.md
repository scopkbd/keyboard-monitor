# レポートテンプレート集

## 1. 問題報告テンプレート

```markdown
---
status: open
priority: [high/medium/low]
assignee: [agent/human/both]
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [bug, performance, ui, backend, security]
---

# [問題のタイトル]

## 概要
問題の簡潔な説明

## 詳細
### 発生条件
- 環境:
- 手順:
- 期待結果:
- 実際の結果:

### エラーメッセージ
```
エラーメッセージをここに記載
```

### 影響範囲
- 機能への影響:
- ユーザーへの影響:
- システムへの影響:

## 解決案
### 案1: [案の名前]
- 概要:
- メリット:
- デメリット:
- 実装工数:

### 案2: [案の名前]
（必要に応じて）

## 関連リンク
- 関連コード:
- 関連ドキュメント:
- 参考資料:
```

## 2. 改善提案テンプレート

```markdown
---
status: proposed
priority: [high/medium/low]
assignee: [agent/human/both]
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [feature, enhancement, performance, usability]
category: [features/performance/usability]
---

# [改善提案のタイトル]

## 動機・背景
なぜこの改善が必要なのか

## 提案内容
### 概要
改善内容の簡潔な説明

### 詳細仕様
- 機能の詳細:
- UI/UX変更:
- API変更:
- データ構造変更:

## 期待効果
- ユーザビリティ向上:
- パフォーマンス向上:
- 保守性向上:
- その他:

## 実装方針
### 技術的アプローチ
- 使用技術:
- アーキテクチャ変更:
- 依存関係:

### 実装ステップ
1. 第1段階:
2. 第2段階:
3. 第3段階:

## リスク評価
- 技術的リスク:
- スケジュールリスク:
- 互換性リスク:

## 代替案
（必要に応じて）
```

## 3. 分析結果テンプレート

```markdown
---
status: completed
priority: [high/medium/low]
assignee: [agent/human/both]
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [analysis, performance, code_quality, architecture]
category: [code_quality/performance/architecture]
---

# [分析のタイトル]

## 分析目的
何を目的として分析を行ったか

## 分析対象
- 対象ファイル/モジュール:
- 対象期間:
- 分析範囲:

## 分析方法
### 使用ツール
- ツール1:
- ツール2:

### 評価指標
- 指標1:
- 指標2:

## 分析結果
### 数値データ
| 項目 | 値 | 基準値 | 評価 |
|------|----|----|------|
| パフォーマンス | | | |
| メモリ使用量 | | | |

### 発見事項
1. 良好な点:
2. 改善点:
3. 注意点:

## 考察
分析結果から得られる知見

## 改善提案
- 短期的改善案:
- 長期的改善案:

## 次のアクション
1. 優先対応事項:
2. 継続監視事項:
```

## 4. セッションログテンプレート

```markdown
---
session_id: YYYY-MM-DD_HHMMSS
start_time: YYYY-MM-DD HH:MM:SS
end_time: YYYY-MM-DD HH:MM:SS
duration: [時間]
tags: [development, testing, debugging, documentation]
---

# 開発セッション - YYYY-MM-DD

## セッション概要
このセッションで実施した作業の概要

## 実施タスク
### タスク1: [タスク名]
- 目的:
- 実施内容:
- 使用ツール:
- 結果:
- 所要時間:

### タスク2: [タスク名]
（必要に応じて）

## 発見事項
- 新しい知見:
- 問題点:
- 改善案:

## トラブルと解決方法
### 問題1: [問題の概要]
- 詳細:
- 解決方法:
- 今後の予防策:

## 次回への引き継ぎ
- 継続タスク:
- 注意事項:
- 参考資料:

## 学習事項
セッション中に学んだこと、気づいたこと
```

## 5. 分析レポートテンプレート

```markdown
---
status: completed
type: [performance/quality/usage/process/security]
target: [target_component]
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [analysis, metrics, optimization]
---

# [分析タイトル] - YYYY-MM-DD

## 📋 分析概要
- **分析対象**: 具体的な分析対象
- **分析期間**: YYYY-MM-DD ~ YYYY-MM-DD
- **分析目的**: 分析を実施する理由・目標
- **使用ツール**: 分析に使用したツール・方法

## 📊 分析結果

### データサマリー
| 項目 | 値 | 前回比較 | 備考 |
|------|----|---------|----- |
| 測定値1 | XXX | +Y% | |
| 測定値2 | XXX | -Y% | |

### 主要発見事項
1. **発見事項1**: 詳細な説明
2. **発見事項2**: 詳細な説明
3. **発見事項3**: 詳細な説明

### グラフ・チャート

```text
[ここにグラフデータやチャートの説明]
```

## 🤔 考察・解釈

### パターン分析
観察されたパターンや傾向の分析

### 原因推定
結果を引き起こしている要因の分析

### 影響評価
システム・ユーザー・開発への影響度評価

## 💡 改善提案

### 短期的対策（1-2週間）
1. 対策1: 具体的な実装方法
2. 対策2: 具体的な実装方法

### 長期的戦略（1-3ヶ月）
1. 戦略1: 実装方針と期待効果
2. 戦略2: 実装方針と期待効果

### 優先度付け
| 提案 | 優先度 | 実装コスト | 期待効果 |
|------|--------|------------|----------|
| 提案1 | High | Low | High |
| 提案2 | Medium | Medium | Medium |

## 📋 次のアクション

### 実装計画
- [ ] アクション1 (担当者: XXX, 期限: YYYY-MM-DD)
- [ ] アクション2 (担当者: XXX, 期限: YYYY-MM-DD)

### 追加調査項目
- [ ] 調査項目1
- [ ] 調査項目2

### モニタリング項目
- 継続的に監視すべき指標
- 次回分析のタイミング

## 📚 参考資料
- 関連ドキュメント
- 参考文献
- ツール・データソース
```

## 6. インデックス更新ガイド

### 問題報告インデックス更新
新しい問題を追加する際の手順:

1. **ISSUES_INDEX.md**の該当セクション（優先度別）に追加
2. **統計情報**を更新（総数・未対応数など）
3. **ステータス変更時**は移動とカウント更新

### 改善提案インデックス更新
新しい提案を追加する際の手順:

1. **IMPROVEMENTS_INDEX.md**の該当セクション（ステータス別）に追加
2. **統計情報**を更新
3. **カテゴリ別分類**にも分類

### 分析結果インデックス更新
新しい分析を追加する際の手順:

1. **ANALYSIS_INDEX.md**の該当セクション（タイプ別）に追加
2. **統計情報**を更新
3. **分析スケジュール**の実施記録を更新

### セッション管理インデックス更新
新しいセッションを追加する際の手順:

1. **SESSION_INDEX.md**の該当セクション（進行中/完了）に追加
2. **セッション統計**を更新（総数・時間・平均など）
3. **週次・月次レビュー**を定期的に実施

## 7. 相互参照ガイド

### インデックス間の連携
- 問題報告 → 改善提案: 問題解決のための提案
- 改善提案 → 分析結果: 実装効果の測定
- 分析結果 → セッション記録: 分析実施の作業記録
- セッション記録 → 問題報告: 作業中に発見した問題

### リンク管理
各インデックスファイルで相互参照リンクを維持:
- `../issues/ISSUES_INDEX.md`
- `../improvements/IMPROVEMENTS_INDEX.md`
- `../analysis/ANALYSIS_INDEX.md`
- `../logs/SESSION_INDEX.md`
