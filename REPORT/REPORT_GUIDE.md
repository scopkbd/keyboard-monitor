# エージェントモード開発レポート管理

## 概要

このディレクトリは、キーボードモニター開発時にエージェントモードで発生した問題や改善点を記録するためのディレクトリです。開発プロセスの透明性と継続的改善をサポートします。

## ディレクトリ構成

```
REPORT/
├── REPORT_GUIDE.md           # このファイル
├── TEMPLATE.md               # 各種テンプレート
├── INDEX.md                  # 全レポートのインデックス
├── issues/                   # 問題報告
│   ├── ISSUES_INDEX.md
│   ├── critical/             # 重要度：高
│   ├── normal/              # 重要度：中
│   └── minor/               # 重要度：低
├── improvements/            # 改善提案
│   ├── IMPROVEMENTS_INDEX.md
│   ├── features/            # 新機能提案
│   ├── performance/         # パフォーマンス改善
│   └── usability/          # ユーザビリティ改善
├── analysis/               # 分析結果
│   ├── ANALYSIS_INDEX.md
│   ├── code_quality/       # コード品質分析
│   ├── performance/        # パフォーマンス分析
│   └── architecture/       # アーキテクチャ分析
└── logs/                   # 操作ログ
    ├── LOGS_INDEX.md
    ├── daily/              # 日次ログ
    ├── sessions/           # セッション別ログ
    └── errors/             # エラーログ
```

## 基本的なファイル命名規則

### 従来の命名規則（REPORT/README.mdより）

- 問題報告: `YYYY-MM-DD_issue_[問題概要].md`
- 改善提案: `YYYY-MM-DD_improvement_[提案概要].md`
- 分析結果: `YYYY-MM-DD_analysis_[分析対象].md`

### 拡張された命名規則

```
YYYY-MM-DD_[category]_[priority]_[brief_description].md
```

### 例
```
issues/critical/2025-06-10_bug_high_memory_leak.md
improvements/features/2025-06-10_feature_medium_gui_interface.md
analysis/performance/2025-06-10_analysis_low_startup_time.md
logs/daily/2025-06-10_log_development_session.md
```

## 優先度レベル

- **critical/high**: 即座に対応が必要
- **medium/normal**: 次の開発サイクルで対応
- **low/minor**: 時間がある時に対応

## 状態管理

各ファイルの先頭に状態を記載：

```markdown
---
status: open/in_progress/resolved/closed
priority: high/medium/low
assignee: agent/human/both
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [bug, performance, ui, backend]
---
```

## 重要な注意事項

⚠️ **プライバシーとセキュリティ**
- このディレクトリのファイルは開発過程の記録として残します
- 機密情報や個人情報は含めないようにしてください
- 個人を特定できるデータは記録禁止
- パスワードや認証情報は絶対に記載しない

📝 **記録の品質**
- 問題や改善点は具体的かつ客観的に記録
- 再現可能な手順を含める
- 関連するコードやファイルへの参照を提供
- 状態管理（open/in_progress/resolved）を適切に更新
