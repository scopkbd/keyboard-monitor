#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新しい保存システムの統合テスト

フェーズ1の実装をテストします
"""

import os
import sys
import tempfile
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_new_save_system():
    """新しい保存システムのテスト"""
    print("🧪 新しい保存システムのテスト開始...")
    
    try:
        # 設定の確認
        from config import get_config
        config = get_config()
        
        idle_delay = config.get_idle_save_delay()
        continuous_interval = config.get_continuous_save_interval()
        batch_size = config.get_keystroke_batch_save()
        
        print(f"✅ 新しい設定値:")
        print(f"   - アイドル保存遅延: {idle_delay}秒")
        print(f"   - 連続保存間隔: {continuous_interval}秒")
        print(f"   - バッチ保存サイズ: {batch_size}回")
        
        # SaveManagerのテスト
        from save_manager import SaveManager
        from data_store import DataStore
        
        # 一時ファイルでテスト
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            # DataStoreとSaveManagerの初期化
            data_store = DataStore(temp_file_path)
            save_manager = SaveManager(config, data_store)
            
            print("✅ SaveManager初期化成功")
            
            # 基本機能のテスト
            save_manager.start()
            print("✅ SaveManager開始成功")
            
            # 模擬キーストローク
            session_stats = {'keystrokes': 5}
            save_manager.on_keystroke(session_stats)
            print("✅ キーストローク処理成功")
            
            # 統計情報の取得
            stats = save_manager.get_save_statistics()
            print(f"✅ 保存統計: キーストローク数 = {stats['keystroke_count_since_save']}")
            
            # 強制保存テスト
            result = save_manager.force_save()
            print(f"✅ 強制保存: {'成功' if result else '失敗'}")
            
            save_manager.stop()
            print("✅ SaveManager停止成功")
            
        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
        print("✅ 新しい保存システムテスト: 成功")
        return True
        
    except Exception as e:
        print(f"❌ 新しい保存システムテスト: 失敗 - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyboard_monitor_integration():
    """KeyboardMonitorとの統合テスト"""
    print("🧪 KeyboardMonitor統合テスト開始...")
    
    try:
        from keyboard_monitor import KeyboardMonitor
        
        # KeyboardMonitorの初期化
        app = KeyboardMonitor()
        print("✅ KeyboardMonitor初期化成功")
        
        # SaveManagerがちゃんと組み込まれているかチェック
        assert hasattr(app, 'save_manager'), "SaveManagerが組み込まれていません"
        assert app.save_manager is not None, "SaveManagerがNoneです"
        
        print("✅ SaveManager統合確認")
        
        # 設定値のテスト
        config = app.config
        assert config.get_idle_save_delay() == 1.0, "アイドル保存遅延が正しくありません"
        assert config.get_continuous_save_interval() == 300, "連続保存間隔が正しくありません"
        assert config.get_keystroke_batch_save() == 100, "バッチ保存サイズが正しくありません"
        
        print("✅ 設定値確認")
        
        print("✅ KeyboardMonitor統合テスト: 成功")
        return True
        
    except Exception as e:
        print(f"❌ KeyboardMonitor統合テスト: 失敗 - {e}")
        import traceback
        traceback.print_exc()
        return False

def run_phase1_tests():
    """フェーズ1テストの実行"""
    print("=" * 60)
    print("🚀 フェーズ1: 新しい保存システム基本実装テスト")
    print("=" * 60)
    
    tests = [
        test_new_save_system,
        test_keyboard_monitor_integration,
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
    print(f"📊 フェーズ1テスト結果: 成功 {passed}件 / 失敗 {failed}件")
    
    if failed == 0:
        print("🎉 フェーズ1の実装が成功しました！")
        print()
        print("✨ 実装された機能:")
        print("  • 新しい設定項目 (idle_save_delay, continuous_save_interval)")
        print("  • SaveManagerクラス (アイドル・連続保存管理)")
        print("  • KeyboardMonitorとの統合")
        print("  • 既存システムとの互換性維持")
        return True
    else:
        print(f"⚠️  {failed}件のテストが失敗しました。")
        return False

if __name__ == "__main__":
    success = run_phase1_tests()
    sys.exit(0 if success else 1)
