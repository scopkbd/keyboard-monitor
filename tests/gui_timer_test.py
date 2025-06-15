"""
GUI タイマー動作確認テスト

修正されたタイマーがGUIで正しく動作することを確認
"""

import os
import sys
import time
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from config import get_config
from data_store import DataStore
from logger import KeyboardLogger


def test_gui_timer():
    """GUI向けタイマーテスト"""
    print("GUI タイマー動作テスト開始...")

    # 初期化
    config = get_config()
    data_store = DataStore(str(config.get_data_file_path()))
    keyboard_logger = KeyboardLogger(data_store)

    print("\n=== シナリオ1: 記録開始→待機→停止 ===")

    # 記録開始
    keyboard_logger.start_logging()
    print(f"記録開始: {keyboard_logger.is_running()}")

    # 統計を複数回チェック（GUIの更新を模擬）
    for i in range(5):
        stats = keyboard_logger.get_session_statistics()
        elapsed = stats.get('elapsed_seconds', 0)
        keystrokes = stats.get('keystrokes', 0)
        print(f"  {i+1}秒後: 経過時間={elapsed:.1f}秒, キーストローク={keystrokes}")
        time.sleep(1)

    # 記録停止
    keyboard_logger.stop_logging()
    print(f"記録停止: {keyboard_logger.is_running()}")

    # 停止後の統計確認（複数回チェック）
    for i in range(3):
        stats = keyboard_logger.get_session_statistics()
        elapsed = stats.get('elapsed_seconds', 0)
        keystrokes = stats.get('keystrokes', 0)
        print(f"  停止後{i+1}回目: 経過時間={elapsed:.1f}秒, キーストローク={keystrokes}")
        time.sleep(1)

    print("\n=== シナリオ2: 再開→停止 ===")

    # 再度記録開始
    keyboard_logger.start_logging()
    print(f"再記録開始: {keyboard_logger.is_running()}")

    # 少し待機
    time.sleep(2)
    stats = keyboard_logger.get_session_statistics()
    elapsed = stats.get('elapsed_seconds', 0)
    print(f"  2秒後: 経過時間={elapsed:.1f}秒")

    # 再度停止
    keyboard_logger.stop_logging()
    stats = keyboard_logger.get_session_statistics()
    elapsed = stats.get('elapsed_seconds', 0)
    print(f"  停止後: 経過時間={elapsed:.1f}秒")

    print("\n✅ GUIタイマーテスト完了")

if __name__ == "__main__":
    test_gui_timer()
