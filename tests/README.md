# テストディレクトリ

キーボードモニターv1.0のテストスイートとテストツールが含まれています。

## 📁 ファイル構成

### 🧪 コアテストファイル

- **`test_keyboard_monitor.py`** - メインアプリケーションのユニットテスト
- **`integration_test.py`** - 統合テストスイート
- **`phase1_test.py`** - フェーズ1機能の完成度テスト
- **`final_report.py`** - プロジェクト完成度の最終レポート生成

### 🤖 自動化テストファイル

- **`safe_integration_test.py`** - モックベース安全統合テスト（推奨）
- **`automated_keyboard_test.py`** - キーボードエミュレーション自動化テスト

### 📖 ドキュメント

- **`TESTING_GUIDE.md`** - テスト実行ガイド
- **`README.md`** - このファイル（テストディレクトリの説明）

## 🚀 テスト実行方法

### 基本テスト

```bash
# メインユニットテスト実行
python tests/test_keyboard_monitor.py

# 安全な統合テスト実行（推奨）
python tests/safe_integration_test.py

# 統合テスト実行
python tests/integration_test.py

# フェーズ1完成度テスト
python tests/phase1_test.py
```

### 自動化テスト

```bash
# キーボードエミュレーション自動化テスト
python tests/automated_keyboard_test.py

# 注意: pynputが必要です
pip install pynput
```

### レポート生成

```bash
# プロジェクト完成度レポート生成
python tests/final_report.py
```
python tests/phase1_test.py
```

### カバレッジレポート生成

```bash
# カバレッジ測定付きテスト実行
pip install coverage
coverage run -m pytest tests/
coverage html
```

### 最終レポート生成

```bash
# プロジェクト完成度レポート生成
python tests/final_report.py
```

## 📊 テスト結果

最新のテスト結果は`htmlcov/index.html`で確認できます。

## 🔧 開発者向け情報

### テスト環境要件

- Python 3.8+
- pytest (オプション)
- coverage (カバレッジレポート用)

### テスト追加ガイドライン

1. **ファイル命名**: `test_*.py` の形式
2. **クラス命名**: `Test*` で開始
3. **メソッド命名**: `test_*` で開始
4. **ドキュメント**: 各テストに適切なdocstringを追加

### CI/CD対応

このテストスイートはGitHub Actionsやその他のCI/CDシステムで自動実行できるよう設計されています。