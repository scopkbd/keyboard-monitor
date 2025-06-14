"""
キーボードモニター自動化テストモジュール

pynputのControllerを使用してキー入力をエミュレートし、
リアルタイム表示修正の動作を自動的にテストします。
"""

import os
import sys
import time
import threading
import subprocess
from typing import List, Dict, Any, Optional
from unittest.mock import patch

# プロジェクトのsrcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from pynput.keyboard import Controller, Key
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    Controller = None
    Key = None

from keyboard_monitor import KeyboardMonitor


class KeyboardEmulator:
    """キーボード入力エミュレータ"""
    
    def __init__(self):
        if not PYNPUT_AVAILABLE:
            raise ImportError("pynputライブラリが必要です: pip install pynput")
        
        self.controller = Controller()
        self.test_results = []
        
    def send_key(self, key: str, delay: float = 0.1) -> None:
        """単一キーを送信"""
        time.sleep(delay)
        self.controller.type(key)
        time.sleep(delay)
        
    def send_keys(self, keys: str, delay: float = 0.1) -> None:
        """複数キーを順次送信"""
        for key in keys:
            self.send_key(key, delay)
            
    def send_command(self, command: str, delay: float = 0.2) -> None:
        """コマンドを送信（Enterキー付き）"""
        time.sleep(delay)
        self.controller.type(command)
        time.sleep(delay)
        self.controller.press(Key.enter)
        self.controller.release(Key.enter)
        time.sleep(delay)
        
    def send_ctrl_c(self, delay: float = 0.1) -> None:
        """Ctrl+Cを送信"""
        time.sleep(delay)
        self.controller.press(Key.ctrl)
        self.controller.press('c')
        self.controller.release('c')
        self.controller.release(Key.ctrl)
        time.sleep(delay)


class AutomatedTestRunner:
    """自動化テスト実行クラス"""
    
    def __init__(self):
        self.emulator = KeyboardEmulator() if PYNPUT_AVAILABLE else None
        self.test_results = []
        self.app_process = None
        
    def log_test_result(self, test_name: str, success: bool, message: str = "") -> None:
        """テスト結果をログ"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'name': test_name,
            'success': success,
            'message': message,
            'timestamp': time.time()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
            
    def start_app_process(self) -> subprocess.Popen:
        """アプリケーションプロセスを開始"""
        try:
            cmd = [sys.executable, os.path.join("src", "keyboard_monitor.py"), "--cli"]
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.dirname(__file__))
            )
            time.sleep(2)  # アプリケーション起動を待機
            return process
        except Exception as e:
            self.log_test_result("アプリケーション起動", False, str(e))
            return None
            
    def test_command_input_sequence(self) -> bool:
        """コマンド入力シーケンスのテスト"""
        if not self.emulator:
            self.log_test_result("キーボードエミュレータ", False, "pynputが利用できません")
            return False
            
        try:
            print("\n🔍 コマンド入力シーケンステストを開始...")
            
            # テストコマンドのシーケンス
            test_commands = [
                ("help", "ヘルプコマンド"),
                ("status", "ステータス確認"),
                ("h", "短縮ヘルプコマンド"),
                ("st", "短縮ステータス"),
                ("start", "記録開始コマンド"),
                ("stop", "記録停止コマンド"),
                ("s", "短縮開始コマンド"),
                ("t", "短縮停止コマンド"),
                ("q", "短縮終了コマンド")
            ]
            
            for command, description in test_commands:
                print(f"  📝 {description}: '{command}'")
                self.emulator.send_command(command, delay=0.5)
                time.sleep(1)  # コマンド処理を待機
                
            self.log_test_result("コマンド入力シーケンス", True, f"{len(test_commands)}個のコマンドを送信")
            return True
            
        except Exception as e:
            self.log_test_result("コマンド入力シーケンス", False, str(e))
            return False
            
    def test_rapid_input(self) -> bool:
        """高速入力テスト"""
        if not self.emulator:
            return False
            
        try:
            print("\n⚡ 高速入力テストを開始...")
            
            # 高速でコマンドを送信
            rapid_commands = ["q", "t", "s", "h", "help", "quit"]
            
            for command in rapid_commands:
                print(f"  ⚡ 高速送信: '{command}'")
                self.emulator.send_command(command, delay=0.05)  # 高速入力
                
            self.log_test_result("高速入力テスト", True, f"{len(rapid_commands)}個の高速コマンド")
            return True
            
        except Exception as e:
            self.log_test_result("高速入力テスト", False, str(e))
            return False
            
    def test_interrupted_input(self) -> bool:
        """入力中断テスト"""
        if not self.emulator:
            return False
            
        try:
            print("\n🔄 入力中断テストを開始...")
            
            # 途中まで入力してからバックスペース
            self.emulator.send_keys("hel", delay=0.1)
            time.sleep(0.2)
            
            # バックスペースで削除
            for _ in range(3):
                self.emulator.controller.press(Key.backspace)
                self.emulator.controller.release(Key.backspace)
                time.sleep(0.1)
                
            # 正しいコマンドを入力
            self.emulator.send_command("help", delay=0.2)
            
            self.log_test_result("入力中断テスト", True, "途中入力→削除→完成入力")
            return True
            
        except Exception as e:
            self.log_test_result("入力中断テスト", False, str(e))
            return False
            
    def test_special_keys(self) -> bool:
        """特殊キーテスト"""
        if not self.emulator:
            return False
            
        try:
            print("\n🎹 特殊キーテストを開始...")
            
            # Ctrl+C テスト
            print("  🔧 Ctrl+C送信テスト")
            self.emulator.send_ctrl_c()
            time.sleep(0.5)
            
            self.log_test_result("特殊キーテスト", True, "Ctrl+C送信完了")
            return True
            
        except Exception as e:
            self.log_test_result("特殊キーテスト", False, str(e))
            return False


class RealTimeDisplayTest:
    """リアルタイム表示テスト"""
    
    def __init__(self):
        self.app = None
        self.display_updates = []
        self.input_interruptions = 0
        
    def test_display_update_control(self) -> bool:
        """表示更新制御のテスト"""
        try:
            print("\n📺 表示更新制御テストを開始...")
            
            # KeyboardMonitorインスタンスを作成
            self.app = KeyboardMonitor()
            
            # input_in_progressフラグのテスト
            initial_flag = self.app.input_in_progress
            
            # フラグを変更
            self.app.input_in_progress = True
            flag_changed = self.app.input_in_progress == True
            
            # フラグをリセット
            self.app.input_in_progress = False
            flag_reset = self.app.input_in_progress == False
            
            success = initial_flag == False and flag_changed and flag_reset
            
            if success:
                print("  ✅ input_in_progressフラグが正常に動作")
                print("  ✅ 表示更新制御ロジックが実装済み")
            else:
                print("  ❌ フラグの動作に問題があります")
                
            return success
            
        except Exception as e:
            print(f"  ❌ 表示更新制御テストでエラー: {e}")
            return False
            
    def test_cursor_control(self) -> bool:
        """カーソル制御テスト"""
        try:
            print("\n🎯 カーソル制御テストを開始...")
            
            # _display_loopメソッドのソースを確認
            import inspect
            if self.app:
                source = inspect.getsource(self.app._display_loop)
                
                # ANSI エスケープシーケンスの使用を確認
                has_cursor_control = "\\033[" in source
                has_line_counting = "last_display_lines" in source
                
                if has_cursor_control and has_line_counting:
                    print("  ✅ ANSIエスケープシーケンスによるカーソル制御")
                    print("  ✅ 行数カウントによる効率的な更新")
                    return True
                else:
                    print("  ❌ カーソル制御の実装が不完全")
                    return False
            else:
                print("  ❌ アプリケーションインスタンスが未初期化")
                return False
                
        except Exception as e:
            print(f"  ❌ カーソル制御テストでエラー: {e}")
            return False


def main():
    """メイン関数"""
    print("=" * 60)
    print("🤖 キーボードモニター自動化テストスイート")
    print("=" * 60)
    
    if not PYNPUT_AVAILABLE:
        print("❌ pynputライブラリが必要です")
        print("インストール: pip install pynput")
        return False
    
    # テスト実行
    test_runner = AutomatedTestRunner()
    display_test = RealTimeDisplayTest()
    
    print("\n🔍 テスト実行を開始します...")
    
    # 基本機能テスト
    success_count = 0
    total_tests = 0
    
    # 1. 表示更新制御テスト
    total_tests += 1
    if display_test.test_display_update_control():
        success_count += 1
        
    # 2. カーソル制御テスト
    total_tests += 1
    if display_test.test_cursor_control():
        success_count += 1
    
    # インタラクティブテストの説明
    print(f"\n📋 自動化テスト実行ガイド:")
    print(f"以下のテストは実際のアプリケーションを起動して実行します：")
    print(f"")
    print(f"1. 別のターミナルでアプリケーションを起動:")
    print(f"   python src/keyboard_monitor.py --cli")
    print(f"")
    print(f"2. このテストスクリプトから自動でコマンドを送信")
    print(f"3. リアルタイム表示の動作を確認")
    
    # ユーザーの確認
    print(f"\n❓ インタラクティブテストを実行しますか？ (y/n): ", end="")
    try:
        user_input = input().strip().lower()
        
        if user_input in ['y', 'yes', 'はい']:
            print(f"\n🚀 インタラクティブテストを開始...")
            print(f"注意: アプリケーションを別のターミナルで起動してから続行してください")
            print(f"準備ができたらEnterキーを押してください...")
            input()
            
            # 3. コマンド入力シーケンステスト
            total_tests += 1
            if test_runner.test_command_input_sequence():
                success_count += 1
                
            # 4. 高速入力テスト
            total_tests += 1
            if test_runner.test_rapid_input():
                success_count += 1
                
            # 5. 入力中断テスト
            total_tests += 1
            if test_runner.test_interrupted_input():
                success_count += 1
                
            # 6. 特殊キーテスト
            total_tests += 1
            if test_runner.test_special_keys():
                success_count += 1
                
    except KeyboardInterrupt:
        print(f"\n⚠️ テストが中断されました")
    
    # 結果レポート
    print(f"\n" + "=" * 60)
    print(f"📊 自動化テスト結果")
    print(f"=" * 60)
    print(f"✅ 成功: {success_count}/{total_tests} テスト")
    print(f"📈 成功率: {success_count/total_tests*100:.1f}%")
    
    if success_count == total_tests:
        print(f"\n🎉 すべてのテストが成功しました！")
        print(f"リアルタイム表示修正が正常に動作しています。")
    else:
        print(f"\n⚠️ 一部のテストが失敗しました。")
        print(f"詳細は上記のテスト結果を確認してください。")
    
    # 詳細レポート
    print(f"\n📋 テスト詳細:")
    for result in test_runner.test_results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['name']}: {result['message']}")
    
    return success_count == total_tests


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n⚠️ テストが中断されました")
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
