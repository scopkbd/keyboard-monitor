# データディレクトリ使用ガイド

## 概要

このディレクトリにはキーボードの使用統計データが保存されます。個人のタイピングデータが含まれるため、適切に管理してください。

## データファイル構成

### メインファイル

- `keyboard_log.json`: メインデータファイル（統計情報）
- `config.json`: ユーザー設定ファイル

### 自動生成ファイル

- `backup/`: 自動バックアップファイル
  - `keyboard_log_YYYYMMDD_HHMMSS.json.gz`: 圧縮バックアップ
- `temp/`: 一時ファイル（自動削除）

## データ構造

```json
{
  "total_statistics": {
    "total_keystrokes": 0,
    "first_record_date": null,
    "last_record_date": null
  },
  "key_statistics": {},
  "key_sequences": {}
}
```

## 容量管理

- メインファイル: 通常 1-10MB
- バックアップ: 最大10世代保持
- 自動クリーンアップ: 30日以上古いバックアップは削除
