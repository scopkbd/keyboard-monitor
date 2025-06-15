#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データ保存機能の詳細テスト

フェーズ1「データ保存機能実装」の完成度を検証します
"""

import os
import sys
import tempfile
import time
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_basic_save_operations():
    """基本保存操作のテスト"""
    print("🧪 基本保存操作テスト...")

    from data_store import DataStore

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        temp_file_path = temp_file.name

    try:
        data_store = DataStore(temp_file_path)

        # 大量データの保存テスト
        for i in range(100):
            data_store.update_key_statistics(str(65 + (i % 26)), f'Key_{i%26}', 'none')

        result = data_store.save_data(create_backup=True)
        print(f"✅ 大量データ保存: {result}")

        # 統計情報の確認
        stats = data_store.get_statistics()
        total_keys = stats['total_statistics']['total_keystrokes']
        print(f"✅ 保存されたキーストローク数: {total_keys}")

        return True

    except Exception as e:
        print(f"❌ 基本保存操作エラー: {e}")
        return False
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_backup_functionality():
    """バックアップ機能のテスト"""
    print("🧪 バックアップ機能テスト...")

    from data_store import DataStore

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, "test_data.json")

        try:
            data_store = DataStore(temp_file_path)

            # データ追加と複数回のバックアップ
            for i in range(3):
                data_store.update_key_statistics(str(65 + i), f'Key_{i}', 'none')
                data_store.save_data(create_backup=True)
                time.sleep(0.1)  # タイムスタンプの重複を避ける

            # バックアップファイルの確認
            backup_dir = Path(temp_file_path).parent / "backup"
            backup_files = list(backup_dir.glob("*.json.gz"))

            print(f"✅ 作成されたバックアップ数: {len(backup_files)}")

            if len(backup_files) >= 3:
                print("✅ バックアップ機能: 正常")
                return True
            else:
                print("❌ バックアップ機能: 不完全")
                return False

        except Exception as e:
            print(f"❌ バックアップ機能エラー: {e}")
            return False

def test_data_integrity():
    """データ整合性テスト"""
    print("🧪 データ整合性テスト...")

    from data_store import DataStore

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        temp_file_path = temp_file.name

    try:
        # データの保存と読み込み
        data_store1 = DataStore(temp_file_path)
        data_store1.update_key_statistics('65', 'A', 'none')
        data_store1.update_key_statistics('66', 'B', 'ctrl')
        data_store1.save_data()

        # 別のインスタンスで読み込み
        data_store2 = DataStore(temp_file_path)
        stats = data_store2.get_statistics()

        total_keys = stats['total_statistics']['total_keystrokes']
        if total_keys == 2:
            print("✅ データ整合性: 正常")
            return True
        else:
            print(f"❌ データ整合性: 異常 (期待:2, 実際:{total_keys})")
            return False

    except Exception as e:
        print(f"❌ データ整合性エラー: {e}")
        return False
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_advanced_features():
    """高度な機能のテスト"""
    print("🧪 高度な機能テスト...")

    from data_store import DataStore

    missing_features = []

    # エクスポート機能の確認
    try:
        data_store = DataStore("dummy.json")
        if not hasattr(data_store, 'export_to_csv'):
            missing_features.append("CSV エクスポート機能")
        if not hasattr(data_store, 'export_to_excel'):
            missing_features.append("Excel エクスポート機能")
    except:
        pass

    # データ圧縮・最適化機能の確認
    try:
        if not hasattr(data_store, 'optimize_data'):
            missing_features.append("データ最適化機能")
        if not hasattr(data_store, 'compress_old_data'):
            missing_features.append("古いデータ圧縮機能")
    except:
        pass

    # 容量管理機能の確認
    try:
        if not hasattr(data_store, 'get_storage_info'):
            missing_features.append("容量情報取得機能")
        if not hasattr(data_store, 'cleanup_old_data'):
            missing_features.append("古いデータクリーンアップ機能")
    except:
        pass

    if missing_features:
        print("❌ 未実装の高度な機能:")
        for feature in missing_features:
            print(f"   - {feature}")
        return False
    else:
        print("✅ 高度な機能: すべて実装済み")
        return True

def run_data_save_feature_tests():
    """データ保存機能テストの実行"""
    print("=" * 60)
    print("🚀 データ保存機能実装テスト")
    print("=" * 60)

    tests = [
        test_basic_save_operations,
        test_backup_functionality,
        test_data_integrity,
        test_advanced_features,
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
    print(f"📊 データ保存機能テスト結果: 成功 {passed}件 / 失敗 {failed}件")

    if failed == 0:
        print("🎉 データ保存機能の実装が完了しています！")
        return True
    else:
        print(f"⚠️  {failed}件のテストが失敗しました。")
        print("📝 次に実装すべき機能:")
        print("  • エクスポート機能（CSV, Excel）")
        print("  • データ最適化・圧縮機能")
        print("  • 容量管理・監視機能")
        print("  • 高度なデータ分析機能")
        return False

if __name__ == "__main__":
    success = run_data_save_feature_tests()
    sys.exit(0 if success else 1)
