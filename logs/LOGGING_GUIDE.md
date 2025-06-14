# ログ管理ガイド

## 概要

このディレクトリにはアプリケーションの動作ログが保存されます。問題の診断、パフォーマンス監視、デバッグに活用できます。

## ログファイル構成

### メインログファイル

- `keyboard_monitor.log`: 一般的な動作ログ（INFO以上）
- `error.log`: エラー詳細ログ（WARNING以上）
- `debug.log`: デバッグ情報（開発時のみ、DEBUG以上）

### 自動生成ファイル

- `keyboard_monitor.log.1`, `.log.2` ... : ローテーションされた古いログ
- `performance.log`: パフォーマンス計測ログ（オプション）
- `session_YYYYMMDD_HHMMSS.log`: セッション別ログ（詳細モード時）

## ログレベル詳細

| レベル | 説明 | 用途 | 例 |
|--------|------|------|-----|
| `DEBUG` | 詳細なデバッグ情報 | 開発・問題調査 | 関数呼び出し、変数値 |
| `INFO` | 一般的な動作情報 | 正常動作の確認 | アプリ開始/終了、設定読み込み |
| `WARNING` | 注意が必要な状況 | 潜在的問題の検出 | 設定値異常、リソース不足 |
| `ERROR` | エラー発生 | 問題の特定 | 例外発生、処理失敗 |
| `CRITICAL` | 重大なエラー | 緊急対応が必要 | システム停止、データ破損 |

## ログ設定

### 設定ファイル（config.json）

```json
{
  "system": {
    "log_level": "INFO",
    "max_log_size": 10485760,
    "max_log_files": 5,
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

### 動的ログレベル変更

```python
# CLIモードでのコマンド例
> config set system.log_level DEBUG
> config set system.log_level INFO
```

## ログの確認方法

### リアルタイム監視

```powershell
# PowerShellでリアルタイム表示
Get-Content -Path "logs\keyboard_monitor.log" -Wait -Tail 10

# エラーログのみ監視
Get-Content -Path "logs\error.log" -Wait
```

### ログ検索

```powershell
# 特定の日付のエラーを検索
Select-String -Path "logs\*.log" -Pattern "2025-06-10.*ERROR"

# キーワード検索
Select-String -Path "logs\*.log" -Pattern "keyboard.*error" -CaseSensitive:$false
```

### ログ分析

```powershell
# エラー件数の集計
(Select-String -Path "logs\*.log" -Pattern "ERROR").Count

# 警告レベル以上の件数
(Select-String -Path "logs\*.log" -Pattern "(WARNING|ERROR|CRITICAL)").Count
```

## トラブルシューティング

### よくある問題

#### 1. ログファイルが作成されない

**症状**: `logs/`ディレクトリが空、またはログファイルが存在しない

**原因と対策**:
- ディレクトリ権限の問題 → 管理者権限で実行
- 設定ファイルのパス間違い → 設定確認
- ログレベルが高すぎる → `DEBUG`に変更して確認

#### 2. ログファイルが巨大になる

**症状**: ログファイルのサイズが異常に大きい

**対策**:
```powershell
# ログレベルを上げる（出力量を減らす）
config set system.log_level WARNING

# ローテーション設定を確認
config get system.max_log_size
config get system.max_log_files
```

#### 3. デバッグ情報が出力されない

**症状**: 問題調査のための詳細情報が不足

**対策**:
```powershell
# デバッグモードに変更
config set system.log_level DEBUG

# アプリケーション再起動後に確認
```

## メンテナンス

### ログローテーション

ログファイルは自動的にローテーションされますが、手動でのメンテナンスも可能です：

```powershell
# 古いログファイルの削除（30日以上）
Get-ChildItem logs\*.log* | Where-Object LastWriteTime -lt (Get-Date).AddDays(-30) | Remove-Item

# ログディレクトリサイズの確認
Get-ChildItem logs\ -Recurse | Measure-Object -Property Length -Sum
```

### バックアップ

重要なログは定期的にバックアップすることを推奨します：

```powershell
# 月次バックアップの作成
$backupPath = "backup\logs\$(Get-Date -Format 'yyyy-MM')"
New-Item -ItemType Directory -Path $backupPath -Force
Copy-Item logs\*.log $backupPath\
```

## ログからの学習

### パフォーマンス分析

ログからアプリケーションのパフォーマンスを分析：

```powershell
# 起動時間の分析
Select-String -Path "logs\*.log" -Pattern "キーボードモニターを初期化しました"

# エラー頻度の分析
Select-String -Path "logs\*.log" -Pattern "ERROR" | Group-Object { $_.Line.Substring(0,10) }
```

### 使用パターンの把握

```powershell
# セッション時間の分析
Select-String -Path "logs\*.log" -Pattern "(キーロギングを開始|キーロギングを停止)"
```

## 開発者向け情報

### カスタムログの追加

```python
import logging

# カスタムロガーの作成
custom_logger = logging.getLogger('keyboard_monitor.custom')
custom_logger.info("カスタムメッセージ")
```

### ログフォーマットのカスタマイズ

```python
# より詳細なフォーマット
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
```
