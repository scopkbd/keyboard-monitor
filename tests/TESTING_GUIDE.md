# テスト実行ガイド

## 概要

このディレクトリには、キーボードモニターの品質保証のための各種テストが含まれます。ユニットテスト、統合テスト、自動化テスト、安全性テストを通じて継続的な開発をサポートします。

## テスト環境のセットアップ

### 依存関係のインストール
```powershell
pip install pytest pytest-cov pytest-mock pynput
```

### 注意事項
- 自動化テストはキーボード入力をエミュレートするため、実行中は他の作業を避けてください
- 管理者権限が必要な場合があります（pynputによる入力シミュレーション）

## テスト実行方法

### 推奨実行順序
```powershell
# 1. 基本テスト（安全）
python tests/test_keyboard_monitor.py

# 2. 統合テスト
python tests/integration_test.py

# 3. 安全な統合テスト（モックベース）
python tests/safe_integration_test.py

# 4. 自動化テスト（要注意：キーボード入力をエミュレート）
python tests/automated_keyboard_test.py

# 5. フェーズ1完成度テスト
python tests/phase1_test.py

# 6. レポート生成
python tests/final_report.py
```

### 個別テスト実行
```powershell
# pytest使用（推奨）
pytest tests/test_keyboard_monitor.py -v

# 直接実行
python tests/test_keyboard_monitor.py
```

### 自動化テストの実行
```powershell
# 自動化テスト（キーボード入力シミュレーション）
# 注意：実行中は他の作業を避けてください
python tests/automated_keyboard_test.py
```

## テストファイル構成

現在のテストディレクトリ構成：

```text
tests/
├── README.md                    # テスト概要とクイックスタート
├── TESTING_GUIDE.md            # このファイル（詳細ガイド）
├── automated_keyboard_test.py   # 自動化テスト（pynputによるキーボードエミュレーション）
├── final_report.py             # テスト結果レポート生成
├── integration_test.py         # 統合テスト
├── phase1_test.py              # フェーズ1完成度テスト
├── safe_integration_test.py    # 安全な統合テスト（モックベース）
└── test_keyboard_monitor.py    # コア機能のユニットテスト
```

### テストファイル詳細

#### コアテスト
- `test_keyboard_monitor.py`: ユニットテスト（基本機能のテスト）
- `integration_test.py`: 統合テスト（コンポーネント間の連携テスト）
- `phase1_test.py`: フェーズ1完成度テスト（要件達成度確認）

#### 自動化・安全性テスト
- `automated_keyboard_test.py`: キーボード入力の自動化テスト（pynput使用）
- `safe_integration_test.py`: モックを使用した安全な統合テスト

#### レポート・分析
- `final_report.py`: 総合テスト結果の分析・レポート生成

## 安全性とベストプラクティス

### 自動化テスト実行時の注意
- `automated_keyboard_test.py`実行中は他のアプリケーションを操作しない
- テスト用の専用環境での実行を推奨
- 管理者権限が必要な場合があります

### テスト実行環境
- Windows環境での動作を前提
- Python 3.8以上
- 必要なパッケージ：pytest, pynput, unittest.mock

## トラブルシューティング

### よくある問題

#### pynputの権限エラー
```powershell
# 管理者権限でPowerShellを起動して実行
```

#### テストの並列実行
- 自動化テストは単独で実行してください
- 他のテストは`pytest`で並列実行可能

#### モックエラー
- `safe_integration_test.py`でモック関連エラーが発生した場合、依存関係を確認

## テスト開発ガイドライン

### 命名規則
- ファイル名: `test_[機能名].py` または `[目的]_test.py`
- メソッド名: `test_[機能名]_[条件]_[期待結果]`

### テストパターン
```python
def test_function_name_valid_input_returns_expected():
    # Arrange（準備）
    input_data = "test_input"
    expected = "expected_output"

    # Act（実行）
    result = function_under_test(input_data)

    # Assert（検証）
    assert result == expected
```
