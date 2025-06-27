#!/usr/bin/env python3
"""
分析ページの統合テスト

新しく実装した分析コンポーネントが正常に動作するかテスト
"""

import os
import sys
from pathlib import Path

import customtkinter as ctk

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from gui.components.analytics import AnalyticsPage
    print("✓ AnalyticsPageのインポート成功")
except ImportError as e:
    print(f"✗ AnalyticsPageのインポートに失敗: {e}")
    sys.exit(1)


class AnalyticsTestApp(ctk.CTk):
    """分析ページテスト用アプリケーション"""

    def __init__(self):
        super().__init__()

        # ウィンドウ設定
        self.title("Keyboard Monitor - Analytics Test")
        self.geometry("1200x900")

        # テーマ設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # アナリティクスページを作成
        try:
            # データファイルパスの設定
            data_file = project_root / "data" / "keyboard_log.json"
            self.analytics_page = AnalyticsPage(self, data_file_path=str(data_file))
            self.analytics_page.pack(fill="both", expand=True)
            print("✓ AnalyticsPageの作成成功")
        except Exception as e:
            print(f"✗ AnalyticsPageの作成に失敗: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """メイン関数"""
    print("=== Keyboard Monitor Analytics Test ===")
    print(f"Python version: {sys.version}")
    print(f"Project root: {project_root}")

    # データファイルの存在確認
    data_file = project_root / "data" / "keyboard_log.json"
    if data_file.exists():
        print(f"✓ データファイル確認: {data_file}")
    else:
        print(f"⚠ データファイルが見つかりません: {data_file}")
        print("  サンプルデータで動作確認を行います")

    # アプリケーション起動
    try:
        app = AnalyticsTestApp()
        print("✓ アプリケーション起動")
        print("\n=== テスト実行中 ===")
        print("1. 各分析カードが正常に表示されるか確認してください")
        print("2. データ更新ボタンが動作するか確認してください")
        print("3. エクスポートボタンが動作するか確認してください")
        print("4. スクロールが正常に動作するか確認してください")
        print("\nウィンドウを閉じるとテストが終了します")

        app.mainloop()
        print("✓ テスト完了")

    except Exception as e:
        print(f"✗ アプリケーションエラー: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
