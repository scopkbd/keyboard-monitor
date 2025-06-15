#!/usr/bin/env python3
"""
テスト用ダッシュボード - リアルタイム統計表示（WPMなし版）
"""

import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from src.config import ConfigManager
    from src.data_store import DataStore
    from src.logger import KeyboardLogger
except ImportError as e:
    print(f"インポートエラー: {e}")
    print("srcモジュールのパスを確認してください")
    sys.exit(1)


class TestDashboard:
    """WPMを含まないテスト用ダッシュボード"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("キーボードモニター - テストダッシュボード")
        self.root.geometry("600x400")

        # CustomTkinterのアイコンをタスクバーにも表示
        try:
            import customtkinter as ctk_module
            ctk_directory = os.path.dirname(os.path.dirname(os.path.abspath(ctk_module.__file__)))
            icon_path = os.path.join(ctk_directory, "customtkinter", "assets", "icons", "CustomTkinter_icon_Windows.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"アイコン設定エラー: {e}")

        # キーボードロガーのインスタンス
        self.logger = None
        self.config = ConfigManager()

        # データファイルのパスを設定から取得
        data_file = self.config.get('logging.data_file')
        self.data_store = DataStore(data_file)

        # 更新フラグ
        self.running = False
        self.update_thread = None

        self.setup_ui()

    def setup_ui(self):
        """UIをセットアップ"""

        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # タイトル
        title_label = ttk.Label(main_frame, text="キーボード モニター",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 制御ボタンフレーム
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        self.start_button = ttk.Button(control_frame, text="記録開始",
                                      command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(control_frame, text="記録停止",
                                     command=self.stop_monitoring, state="disabled")
        self.stop_button.pack(side=tk.LEFT)

        # 統計表示フレーム
        stats_frame = ttk.LabelFrame(main_frame, text="リアルタイム統計", padding="10")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # セッション統計
        session_frame = ttk.LabelFrame(stats_frame, text="セッション統計", padding="5")
        session_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Label(session_frame, text="キー入力数:").grid(row=0, column=0, sticky=tk.W)
        self.session_keys_label = ttk.Label(session_frame, text="0", font=("Arial", 12, "bold"))
        self.session_keys_label.grid(row=0, column=1, sticky=tk.E)

        ttk.Label(session_frame, text="記録時間:").grid(row=1, column=0, sticky=tk.W)
        self.session_time_label = ttk.Label(session_frame, text="0分0秒", font=("Arial", 12, "bold"))
        self.session_time_label.grid(row=1, column=1, sticky=tk.E)

        # 全体統計
        total_frame = ttk.LabelFrame(stats_frame, text="全体統計", padding="5")
        total_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(total_frame, text="総キー入力数:").grid(row=0, column=0, sticky=tk.W)
        self.total_keys_label = ttk.Label(total_frame, text="0", font=("Arial", 12, "bold"))
        self.total_keys_label.grid(row=0, column=1, sticky=tk.E)

        ttk.Label(total_frame, text="総記録時間:").grid(row=1, column=0, sticky=tk.W)
        self.total_time_label = ttk.Label(total_frame, text="0分0秒", font=("Arial", 12, "bold"))
        self.total_time_label.grid(row=1, column=1, sticky=tk.E)

        # ステータス表示
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Label(status_frame, text="状態:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, text="停止中",
                                     font=("Arial", 10, "bold"), foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))

        # カラム重みの設定
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        session_frame.columnconfigure(1, weight=1)
        total_frame.columnconfigure(1, weight=1)

    def start_monitoring(self):
        """モニタリング開始"""
        try:
            if self.logger is None:
                self.logger = KeyboardLogger(self.data_store)

            self.logger.start_logging()

            # UI更新
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="記録中", foreground="green")

            # リアルタイム更新開始
            self.running = True
            self.update_thread = threading.Thread(target=self.update_stats_loop, daemon=True)
            self.update_thread.start()

            print("記録開始")

        except (ImportError, AttributeError, RuntimeError) as e:
            print(f"記録開始エラー: {e}")

    def stop_monitoring(self):
        """モニタリング停止"""
        try:
            if self.logger and self.logger.is_running:
                self.logger.stop_logging()

            # リアルタイム更新停止
            self.running = False

            # UI更新
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.status_label.config(text="停止中", foreground="red")

            print("記録停止")

        except (AttributeError, RuntimeError) as e:
            print(f"記録停止エラー: {e}")

    def update_stats_loop(self):
        """統計情報の更新ループ"""
        while self.running and self.logger and self.logger.is_running:
            try:
                self.update_stats()
                time.sleep(1)  # 1秒ごとに更新
            except (AttributeError, RuntimeError) as e:
                print(f"統計更新エラー: {e}")
                break

    def update_stats(self):
        """統計情報の更新"""
        if not self.logger:
            return

        try:
            # セッション統計取得
            session_stats = self.logger.get_session_statistics()

            # セッション統計更新
            self.session_keys_label.config(text=str(session_stats.get('total_keys', 0)))

            # 時間のフォーマット
            session_time = session_stats.get('recording_time', 0)
            session_time_str = self.format_time(session_time)
            self.session_time_label.config(text=session_time_str)

            # 全体統計は簡易的に表示（データストアから取得しない）
            # 実際の実装では data_store から取得する
            self.total_keys_label.config(text="N/A")
            self.total_time_label.config(text="N/A")

        except (AttributeError, KeyError) as e:
            print(f"統計取得エラー: {e}")

    def format_time(self, seconds):
        """秒を分:秒の形式にフォーマット"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}分{seconds}秒"

    def run(self):
        """アプリケーション実行"""
        try:
            print("テストダッシュボード開始")
            print("記録開始ボタンを押してキーボード入力を開始してください")

            # ウィンドウ終了時の処理
            def on_closing():
                if self.logger and self.logger.is_running:
                    self.stop_monitoring()
                self.root.destroy()

            self.root.protocol("WM_DELETE_WINDOW", on_closing)
            self.root.mainloop()

        except KeyboardInterrupt:
            print("\nプログラムを終了します...")
        except (ImportError, RuntimeError) as e:
            print(f"エラー: {e}")
        finally:
            if self.logger and self.logger.is_running:
                self.stop_monitoring()


def main():
    """メイン関数"""
    print("=== キーボードモニター テストダッシュボード ===")
    print("WPM機能を削除したテスト版です")

    dashboard = TestDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
