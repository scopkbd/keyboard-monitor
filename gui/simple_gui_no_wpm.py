"""
WPM削除版の簡単なGUIテスト

ダッシュボードのみで動作確認
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import customtkinter as ctk

from analyzer import StatisticsAnalyzer
from config import get_config
from data_store import DataStore
from logger import KeyboardLogger

# dashboard_no_wmpをimport
sys.path.insert(0, str(Path(__file__).parent / "components"))
from dashboard_no_wmp import Dashboard


class SimpleGUI:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("🎯 キーボードモニター（WPM削除版）")
        self.root.geometry("900x700")

        # バックエンド初期化
        config = get_config()
        self.data_store = DataStore(str(config.get_data_file_path()))
        self.keyboard_logger = KeyboardLogger(self.data_store)
        self.statistics_analyzer = StatisticsAnalyzer(self.data_store)

        # ダッシュボード作成
        self.dashboard = Dashboard(
            self.root,
            self.keyboard_logger,
            self.statistics_analyzer
        )
        self.dashboard.pack(fill="both", expand=True, padx=10, pady=10)

    def run(self):
        try:
            self.root.mainloop()
        finally:
            if self.keyboard_logger.is_running():
                self.keyboard_logger.stop_logging()

if __name__ == "__main__":
    app = SimpleGUI()
    app.run()
