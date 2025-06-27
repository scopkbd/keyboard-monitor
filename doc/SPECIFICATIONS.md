# キーボードモニター - 技術仕様書

## 概要

このドキュメントは、キーボードモニターソフトウェアの詳細な技術仕様を記載しています。

## データ構造設計

### 基本データ構造

#### メインデータファイル: `keyboard_log.json`

```json
{
  "total_statistics": {
    "total_keystrokes": 25000,
    "first_record_date": "2025-06-01",
    "last_record_date": "2025-06-10"
  },
  "key_statistics": {
    "65": {
      "key_name": "A",
      "count": 850,
      "modifier_combinations": {
        "none": {"count": 750, "preceded_by": {"83": 120, "68": 95}},
        "ctrl": {"count": 60, "preceded_by": {"67": 30, "86": 20}},
        "shift": {"count": 15, "preceded_by": {"32": 10, "16": 5}},
        "alt": {"count": 8, "preceded_by": {"9": 5, "115": 3}},
        "win": {"count": 12, "preceded_by": {"76": 8, "82": 4}},
        "ctrl+shift": {"count": 25, "preceded_by": {"90": 15, "89": 10}},
        "ctrl+alt": {"count": 18, "preceded_by": {"46": 12, "8": 6}},
        "ctrl+win": {"count": 5, "preceded_by": {"76": 3, "82": 2}},
        "shift+alt": {"count": 3, "preceded_by": {"9": 2, "115": 1}},
        "shift+win": {"count": 2, "preceded_by": {"76": 1, "82": 1}},
        "alt+win": {"count": 1, "preceded_by": {"82": 1}},
        "ctrl+shift+alt": {"count": 2, "preceded_by": {"46": 1, "8": 1}},
        "ctrl+shift+win": {"count": 1, "preceded_by": {"76": 1}},
        "ctrl+alt+win": {"count": 1, "preceded_by": {"82": 1}},
        "shift+alt+win": {"count": 0, "preceded_by": {}},
        "ctrl+shift+alt+win": {"count": 0, "preceded_by": {}}
      }
    }
  }
}
```

### key_statistics詳細仕様

`key_statistics`は、各キーの詳細な使用統計を管理するオブジェクトです。

**構造説明**:
- **キー**: Virtual Key Code（文字列形式）
  - 例: "65" (Aキー), "13" (Enterキー), "32" (スペースキー)
  - Windows Virtual Key Codeを使用してキーを一意識別

**各キーのデータ項目**:
- `key_name` (string): 人間が読める形式のキー名
  - 例: "A", "Enter", "Space", "Shift", "Ctrl"
- `count` (integer): 総押下回数
- `modifier_combinations` (object): モディファイアキーとの組み合わせ
  - `none`: モディファイアキーなしでの押下統計
  - `ctrl`, `shift`, `alt`: 各モディファイアキーとの組み合わせ統計
  - `preceded_by`: そのモディファイア組み合わせでの直前キー統計

### Virtual Key Code 一覧

**主要なVirtual Key Code例**:
```
アルファベット: A=65, B=66, ..., Z=90
数字: 0=48, 1=49, ..., 9=57
特殊キー: Space=32, Enter=13, Backspace=8, Tab=9
修飾キー: Shift=16, Ctrl=17, Alt=18, Win=91/92
ファンクションキー: F1=112, F2=113, ..., F12=123
矢印キー: Left=37, Up=38, Right=39, Down=40
```

### モディファイアキー組み合わせ仕様

**modifier_combinations（モディファイア組み合わせ）**:
- **分離記録の理由**: Ctrl+CとCは全く異なる操作
- **none**: 通常の文字入力（モディファイアキーなし）
- **単一モディファイア**: `ctrl`, `shift`, `alt`, `win`
- **2キー組み合わせ**: `ctrl+shift`, `ctrl+alt`, `ctrl+win`, `shift+alt`, `shift+win`, `alt+win`
- **3キー組み合わせ**: `ctrl+shift+alt`, `ctrl+shift+win`, `ctrl+alt+win`, `shift+alt+win`
- **4キー組み合わせ**: `ctrl+shift+alt+win`
- **preceded_by**: そのモディファイア組み合わせでの直前キー統計

## 技術実装仕様

### アーキテクチャ設計
- **シングルプロセス設計**: CLIモードで単一プロセス内でキーロガーとユーザーインターフェースを管理
- **マルチスレッド構成**:
  - メインスレッド: ユーザーインターフェース（コマンド入力処理）
  - バックグラウンドスレッド: キーボード入力監視とログ記録
- **リアルタイム通信**: スレッド間でのステータス共有とコマンド伝達

### モディファイアキー検出実装

```python
# pynputでのモディファイア状態取得例
from pynput import keyboard

def on_key_press(key):
    modifiers = []
    if keyboard.Listener._current_listener._is_pressed(keyboard.Key.ctrl):
        modifiers.append('ctrl')
    if keyboard.Listener._current_listener._is_pressed(keyboard.Key.shift):
        modifiers.append('shift')
    if keyboard.Listener._current_listener._is_pressed(keyboard.Key.alt):
        modifiers.append('alt')
    if keyboard.Listener._current_listener._is_pressed(keyboard.Key.cmd):
        modifiers.append('win')

    # 組み合わせキーのソート（一貫性のため）
    modifier_key = '+'.join(sorted(modifiers)) if modifiers else 'none'
```

### データ更新フロー

1. **キー押下検出** → モディファイア状態確認
2. **直前キーの記録更新**
3. **モディファイア別統計更新**
4. **シーケンス履歴更新**（バッファ管理）

### メモリ効率化

- 低頻度組み合わせの閾値設定
- シーケンスバッファサイズ制限
- 定期的なデータ圧縮

## データ管理の特徴

1. **累積統計**: `count`でキーの使用頻度を長期追跡
2. **効率的検索**: Virtual Key Codeをキーとした高速アクセス
3. **キー関連性分析**: 直前キーとの関係性記録でタイピングパターン分析
4. **モディファイア管理**: Ctrl/Shift/Alt/Winとの組み合わせを分離記録
5. **シーケンス分析**: 2文字・3文字の連続パターン（bigram/trigram）記録

## ファイル構成

```
keyboard-monitor/
├── src/
│   ├── keyboard_monitor.py    # メインアプリケーション
│   ├── logger.py             # キーロガークラス
│   ├── statistics.py         # 統計分析クラス
│   └── config.py             # 設定管理
├── data/                     # ログファイル保存ディレクトリ
├── tests/                    # テストファイル
├── doc/                      # ドキュメント
│   ├── SPECIFICATIONS.md     # 技術仕様書（このファイル）
│   ├── ARCHITECTURE.md       # アーキテクチャ設計書
│   └── API.md               # API仕様書
├── requirements.txt          # 依存関係
└── README.md                # ユーザー向けドキュメント
```

## セキュリティ考慮事項

### 制限事項
- **ローカル使用のみ**: ネットワーク送信機能なし
- **暗号化**: ログファイルは平文で保存（将来的に暗号化対応検討）
- **権限**: 管理者権限が必要な場合がある

### 注意事項
- 個人利用目的のみ
- 他人のコンピューターでの使用禁止
- パスワードやセンシティブな情報の記録に注意
