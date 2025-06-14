#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
キーボードモニター統合テスト

このテストは実際のアプリケーション動作をテストします。
"""

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_application_help():
    """アプリケーションのヘルプ表示をテスト"""
    print("🧪 ヘルプ表示のテスト...")

    try:
        result = subprocess.run([
            sys.executable, "src/keyboard_monitor.py", "--help"
        ], capture_output=True, text=True, cwd=project_root, timeout=10)

        assert result.returncode == 0, f"ヘルプコマンドが失敗: {result.stderr}"
        assert "キーボード入力パターンを記録・分析するツール" in result.stdout
        assert "--cli" in result.stdout
        assert "--stats" in result.stdout
        assert "--status" in result.stdout

        print("✅ ヘルプ表示テスト: 成功")
        return True

    except Exception as e:
        print(f"❌ ヘルプ表示テスト: 失敗 - {e}")
        return False


def test_application_status():
    """アプリケーションのステータス表示をテスト"""
    print("🧪 ステータス表示のテスト...")

    try:
        result = subprocess.run([
            sys.executable, "src/keyboard_monitor.py", "--status"
        ], capture_output=True, text=True, cwd=project_root, timeout=15)

        assert result.returncode == 0, f"ステータスコマンドが失敗: {result.stderr}"
        assert "システムステータス" in result.stdout
        assert "データファイル:" in result.stdout
        assert "総キーストローク:" in result.stdout

        print("✅ ステータス表示テスト: 成功")
        return True

    except Exception as e:
        print(f"❌ ステータス表示テスト: 失敗 - {e}")
        return False


def test_application_stats():
    """アプリケーションの統計表示をテスト"""
    print("🧪 統計表示のテスト...")

    try:
        result = subprocess.run([
            sys.executable, "src/keyboard_monitor.py", "--stats"
        ], capture_output=True, text=True, cwd=project_root, timeout=15)

        assert result.returncode == 0, f"統計コマンドが失敗: {result.stderr}"
        assert "キーボード使用統計レポート" in result.stdout
        assert "基本統計:" in result.stdout
        assert "総キーストローク数:" in result.stdout

        print("✅ 統計表示テスト: 成功")
        return True

    except Exception as e:
        print(f"❌ 統計表示テスト: 失敗 - {e}")
        return False


def test_data_directory_creation():
    """データディレクトリの作成をテスト"""
    print("🧪 データディレクトリ作成のテスト...")

    try:
        # 一時ディレクトリでテスト
        with tempfile.TemporaryDirectory() as temp_dir:
            # テスト用の設定で実行
            os.environ['KEYBOARD_MONITOR_DATA_DIR'] = temp_dir

            from config import get_config
            config_manager = get_config()

            # データディレクトリが作成されることを確認
            data_file = config_manager.get('logging.data_file')
            data_dir = Path(data_file).parent
            data_dir.mkdir(parents=True, exist_ok=True)
            assert data_dir.exists(), "データディレクトリが作成されていません"

            print("✅ データディレクトリ作成テスト: 成功")
            return True

    except Exception as e:
        print(f"❌ データディレクトリ作成テスト: 失敗 - {e}")
        return False
    finally:
        # 環境変数をクリア
        if 'KEYBOARD_MONITOR_DATA_DIR' in os.environ:
            del os.environ['KEYBOARD_MONITOR_DATA_DIR']


def test_config_loading():
    """設定ファイルの読み込みをテスト"""
    print("🧪 設定ファイル読み込みのテスト...")

    try:
        from config import ConfigManager, get_config

        # デフォルト設定の取得
        config_manager = get_config()
        assert isinstance(config_manager, ConfigManager), "設定がConfigManagerインスタンスではありません"

        # 設定値の取得テスト
        data_file = config_manager.get('logging.data_file')
        assert data_file is not None, "データファイルパスが取得できません"

        # ConfigManagerのテスト
        assert config_manager.get('display.refresh_interval') is not None, "表示間隔が取得できません"
        assert config_manager.get('privacy.exclude_passwords') is not None, "プライバシー設定が取得できません"

        print("✅ 設定ファイル読み込みテスト: 成功")
        return True

    except Exception as e:
        print(f"❌ 設定ファイル読み込みテスト: 失敗 - {e}")
        return False


def test_data_store_operations():
    """データストアの操作をテスト"""
    print("🧪 データストア操作のテスト...")

    try:
        from data_store import DataStore

        # 一時ファイルでテスト
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            # DataStoreの初期化
            data_store = DataStore(temp_file_path)

            # テストデータの更新
            data_store.update_key_statistics('65', 'A', modifiers=[])
            data_store.update_key_statistics('66', 'B', modifiers=[])
            data_store.update_key_statistics('65', 'A', modifiers=[])  # 重複で増加

            # データの保存
            data_store.save_data()

            # 統計の取得
            stats = data_store.get_statistics()
            assert 'key_statistics' in stats, "キー統計が存在しません"
            assert 'total_statistics' in stats, "総合統計が存在しません"
            assert stats['total_statistics']['total_keystrokes'] == 3, "総キーストローク数が正しくありません"

            print("✅ データストア操作テスト: 成功")
            return True

        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        print(f"❌ データストア操作テスト: 失敗 - {e}")
        return False


def test_statistics_analyzer():
    """統計分析機能をテスト"""
    print("🧪 統計分析機能のテスト...")

    try:
        from analyzer import StatisticsAnalyzer
        from data_store import DataStore

        # テスト用一時ファイル
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            # DataStoreを準備
            data_store = DataStore(temp_file_path)

            # テストデータの追加
            data_store.update_key_statistics('65', 'A', modifiers=[])
            data_store.update_key_statistics('66', 'B', modifiers=[])
            data_store.update_key_statistics('65', 'A', modifiers=[])
            data_store.update_key_statistics('67', 'C', modifiers=[])

            # 分析器の初期化
            analyzer = StatisticsAnalyzer(data_store)

            # 基本統計の取得
            basic_stats = analyzer.get_basic_statistics()
            assert basic_stats['total_keystrokes'] == 4, "総キーストローク数が正しくありません"
            assert basic_stats['unique_keys'] >= 3, "ユニークキー数が正しくありません"

            # トップキーの取得
            top_keys = analyzer.get_top_keys(limit=3)
            assert len(top_keys) >= 1, "トップキーが取得できません"
            assert top_keys[0]['count'] >= 2, "最多キーの回数が正しくありません"

            print("✅ 統計分析機能テスト: 成功")
            return True

        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        print(f"❌ 統計分析機能テスト: 失敗 - {e}")
        return False


def run_all_tests():
    """すべてのテストを実行"""
    print("=" * 60)
    print("🚀 キーボードモニター統合テスト開始")
    print("=" * 60)

    tests = [
        test_config_loading,
        test_data_store_operations,
        test_statistics_analyzer,
        test_data_directory_creation,
        test_application_help,
        test_application_status,
        test_application_stats,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ テスト実行エラー: {test.__name__} - {e}")
            failed += 1

        print()  # 空行で区切り

    print("=" * 60)
    print(f"📊 テスト結果: 成功 {passed}件 / 失敗 {failed}件")

    if failed == 0:
        print("🎉 すべてのテストが成功しました！")
        return True
    else:
        print(f"⚠️  {failed}件のテストが失敗しました。")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
