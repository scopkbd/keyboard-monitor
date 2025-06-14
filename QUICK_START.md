# クイックスタートガイド

> キーボードモニター v1.0 - 改善されたユーザーインターフェースで素早く始める

## ✨ v1.0の新機能

- **🎯 スムーズなコマンド入力**: `q`、`t`などの短いコマンドも確実に動作
- **⚡ リアルタイム表示最適化**: 入力中は表示更新が自動停止
- **🎨 画面ちらつき防止**: カーソル位置制御による効率的な表示更新
- **🛡️ 堅牢な例外処理**: 安全で確実な操作

## 🚀 5分で始める

### 1. 前提条件の確認

```powershell
# Python バージョン確認
python --version  # 3.8+ が必要

# Git の確認
git --version
```

### 2. セットアップ

```powershell
# プロジェクトディレクトリに移動（既にクローン済みの場合）
cd keyboard-monitor

# または新規セットアップの場合
# git clone <your-repository-url>
# cd keyboard-monitor

# 依存関係のインストール
pip install -r requirements.txt

# 初回セットアップ
python src/keyboard_monitor.py --setup
```

### 3. アプリケーションの起動

```powershell
# インタラクティブモードで起動
python src/keyboard_monitor.py --cli
```

### 4. 基本的な使い方

```text
# アプリケーション内で実行
> start     # 記録開始
> stats     # 統計表示
> stop      # 記録停止
> quit      # 終了
```

## 📁 重要なファイル・ディレクトリ

| パス | 説明 | 重要度 |
|------|------|--------|
| `README.md` | メインドキュメント | ⭐⭐⭐ |
| `src/keyboard_monitor.py` | メインアプリケーション | ⭐⭐⭐ |
| `data/DATA_GUIDE.md` | データファイル説明 | ⭐⭐ |
| `doc/` | 技術仕様書 | ⭐⭐ |
| `tests/TESTING_GUIDE.md` | テスト方法 | ⭐ |

## 🔧 よくあるトラブル

### 権限エラー

```powershell
# 管理者権限でPowerShellを起動して実行
```

### ライブラリエラー

```powershell
# 依存関係の再インストール
pip install -r requirements.txt --force-reinstall
```

### データファイルエラー

```powershell
# データディレクトリのリセット
Remove-Item data/*.json -Force
python src/keyboard_monitor.py --setup
```

## 📖 詳細ドキュメント

- **使い方**: `README.md`
- **技術仕様**: `doc/SPECIFICATIONS.md`
- **アーキテクチャ**: `doc/ARCHITECTURE.md`
- **CLI詳細**: `doc/CLI_INTERFACE.md`

## 🤝 開発に参加

1. **問題報告**: `REPORT/` ディレクトリを参照
2. **テスト実行**: `tests/TESTING_GUIDE.md` を参照
3. **ログ確認**: `logs/LOGGING_GUIDE.md` を参照

---

💡 **ヒント**: 各ディレクトリには詳細なガイドファイルがあります！
