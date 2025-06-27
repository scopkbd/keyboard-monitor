#!/usr/bin/env python3
"""
統合分析ページ単独起動スクリプト

統合分析ページを単独で起動するためのスクリプト
"""

import os
import sys
from pathlib import Path

import customtkinter as ctk

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.components.analytics.analytics_page import AnalyticsPage


class AnalyticsApp(ctk.CTk):
    """統合分析ページ専用アプリケーション"""

    def __init__(self):
        super().__init__()

        # ウィンドウ設定
        self.title("キーボードモニター - 統合分析ダッシュボード")
        self.geometry("1400x1000")
        self.minsize(1200, 800)

        # テーマ設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # データファイルパスの設定
        data_file = project_root / "data" / "keyboard_log.json"

        # 統合分析ページを作成
        self.analytics_page = AnalyticsPage(self, data_file_path=str(data_file))
        self.analytics_page.pack(fill="both", expand=True)

        # ウィンドウを中央に配置
        self.center_window()

    def center_window(self):
        """ウィンドウを画面中央に配置"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


def main():
    """メイン関数"""
    print("キーボードモニター統合分析ダッシュボードを起動中...")

    try:
        app = AnalyticsApp()
        app.mainloop()
    except Exception as e:
        print(f"アプリケーション起動エラー: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
