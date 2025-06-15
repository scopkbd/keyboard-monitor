"""
改良版ダッシュボード - カード風レイアウト

よりモダンで直感的なUI設計
"""

import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import customtkinter as ctk

from analyzer import StatisticsAnalyzer
from config import get_config
from data_store import DataStore
from logger import KeyboardLogger


class ModernDashboard(ctk.CTkFrame):
    """モダンなカード風ダッシュボード"""

    def __init__(self, parent, keyboard_logger: KeyboardLogger, statistics_analyzer: StatisticsAnalyzer):
        super().__init__(parent)

        self.keyboard_logger = keyboard_logger
        self.statistics_analyzer = statistics_analyzer

        # 更新制御
        self.is_updating = True
        self.update_thread = None

        # UI作成
        self.setup_ui()
        self._start_updates()

    def setup_ui(self):
        """UI要素の作成"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # タイトル
        self._create_header()

        # メイン制御カード
        self._create_main_control_card()

        # 統計カード
        self._create_stats_cards()

        # アクティビティログ
        self._create_activity_log()

    def _create_header(self):
        """ヘッダーの作成"""
        header_frame = ctk.CTkFrame(self, height=80)
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_propagate(False)

        title = ctk.CTkLabel(
            header_frame,
            text="🎯 キーボードモニター",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(expand=True)

    def _create_main_control_card(self):
        """メイン制御カードの作成"""
        control_card = ctk.CTkFrame(self, height=120)
        control_card.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        control_card.grid_propagate(False)
        control_card.grid_columnconfigure(0, weight=1)

        # メインボタン
        self.main_button = ctk.CTkButton(
            control_card,
            text="▶️ 記録開始",
            command=self._toggle_recording,
            width=250,
            height=50,
            font=ctk.CTkFont(size=20, weight="bold"),
            corner_radius=25
        )
        self.main_button.grid(row=0, column=0, pady=(15, 5))

        # ステータス表示
        self.status_label = ctk.CTkLabel(
            control_card,
            text="準備完了",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.status_label.grid(row=1, column=0, pady=(0, 15))

    def _create_stats_cards(self):
        """統計カードの作成"""
        stats_container = ctk.CTkFrame(self)
        stats_container.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        stats_container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # セッション統計カード
        self._create_stat_card(stats_container, "📊 セッション", 0, {
            'keystrokes': "キーストローク",
            'duration': "継続時間",
            'wpm': "WPM",
            'last_key': "最後のキー"
        })

        # 全体統計カード
        self._create_stat_card(stats_container, "🏆 全体", 1, {
            'total_keys': "総キーストローク",
            'sessions': "セッション数",
            'avg_wpm': "平均WPM",
            'most_used': "最頻出キー"
        })

        # リアルタイム統計カード
        self._create_stat_card(stats_container, "⚡ リアルタイム", 2, {
            'current_speed': "現在の速度",
            'efficiency': "効率",
            'streak': "連続記録",
            'peak_wpm': "最高WPM"
        })

        # 分析カード
        self._create_stat_card(stats_container, "🔍 分析", 3, {
            'top_combo': "多用組み合わせ",
            'hand_balance': "手の使用率",
            'finger_load': "指の負荷",
            'typing_rhythm': "タイピングリズム"
        })

    def _create_stat_card(self, parent, title: str, column: int, stats: Dict[str, str]):
        """統計カードの作成"""
        card = ctk.CTkFrame(parent)
        card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")

        # カードタイトル
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        # 統計値表示
        stat_labels = {}
        for key, label_text in stats.items():
            label = ctk.CTkLabel(card, text=f"{label_text}: -")
            label.pack(pady=2)
            stat_labels[key] = label

        # カード別の統計ラベルを保存
        if column == 0:
            self.session_stats = stat_labels
        elif column == 1:
            self.total_stats = stat_labels
        elif column == 2:
            self.realtime_stats = stat_labels
        elif column == 3:
            self.analysis_stats = stat_labels

    def _create_activity_log(self):
        """アクティビティログの作成"""
        log_frame = ctk.CTkFrame(self, height=120)
        log_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")
        log_frame.grid_propagate(False)

        log_title = ctk.CTkLabel(
            log_frame,
            text="📋 アクティビティログ",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        log_title.pack(pady=(10, 5))

        self.activity_log = ctk.CTkTextbox(log_frame, height=80, wrap="word")
        self.activity_log.pack(fill="x", padx=15, pady=(0, 10))
        self.activity_log.insert("1.0", "アプリケーション準備完了\n")

    def _toggle_recording(self):
        """記録の開始/停止切り替え"""
        if self.keyboard_logger.is_running():
            # 停止
            self.keyboard_logger.stop_logging()
            self.main_button.configure(
                text="▶️ 記録開始",
                fg_color=["#1f538d", "#14375e"]
            )
            self.status_label.configure(text="記録停止 - データを保存しました")
            self._log_activity("⏹️ 記録を停止しました")
        else:
            # 開始
            self.keyboard_logger.start_logging()
            self.main_button.configure(
                text="⏹️ 記録停止",
                fg_color=["#d63031", "#a71e20"]
            )
            self.status_label.configure(text="🔴 記録中...")
            self._log_activity("▶️ 記録を開始しました")

    def _start_updates(self):
        """定期的な統計更新を開始"""
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()

    def _update_loop(self):
        """統計データの定期更新ループ"""
        while self.is_updating:
            try:
                self._update_stats()
                time.sleep(1)
            except Exception as e:
                print(f"統計更新エラー: {e}")
                time.sleep(5)

    def _update_stats(self):
        """統計データの更新"""
        try:
            session_stats = self.keyboard_logger.get_session_statistics()
            overall_stats = self.statistics_analyzer.get_basic_statistics()

            self.after(0, self._update_ui_stats, session_stats, overall_stats)
        except Exception as e:
            print(f"統計データ取得エラー: {e}")

    def _update_ui_stats(self, session_stats: Dict[str, Any], overall_stats: Dict[str, Any]):
        """UI統計表示の更新"""
        try:
            # セッション統計
            self.session_stats['keystrokes'].configure(
                text=f"キーストローク: {session_stats.get('keystrokes', 0):,}"
            )

            elapsed_seconds = session_stats.get('elapsed_seconds', 0)
            hours, remainder = divmod(int(elapsed_seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.session_stats['duration'].configure(text=f"継続時間: {duration}")

            wpm = session_stats.get('wpm', 0.0)
            self.session_stats['wpm'].configure(text=f"WPM: {wpm:.1f}")

            last_key = session_stats.get('last_key', '-')
            self.session_stats['last_key'].configure(text=f"最後のキー: {last_key}")

            # 全体統計
            self.total_stats['total_keys'].configure(
                text=f"総キーストローク: {overall_stats.get('total_keystrokes', 0):,}"
            )
            self.total_stats['sessions'].configure(
                text=f"セッション数: {overall_stats.get('session_count', 0)}"
            )
            self.total_stats['avg_wpm'].configure(
                text=f"平均WPM: {overall_stats.get('average_wpm', 0.0):.1f}"
            )
            self.total_stats['most_used'].configure(
                text=f"最頻出キー: {overall_stats.get('most_frequent_key', '-')}"
            )

        except Exception as e:
            print(f"UI統計更新エラー: {e}")

    def _log_activity(self, message: str):
        """アクティビティログにメッセージを追加"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        def add_to_log():
            self.activity_log.insert("end", log_entry)
            self.activity_log.see("end")

        self.after(0, add_to_log)

    def destroy(self):
        """コンポーネント破棄時のクリーンアップ"""
        self.is_updating = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
        super().destroy()


# テスト用アプリケーション
class ModernTestApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("🎯 モダンキーボードモニター")
        self.root.geometry("1000x700")

        # バックエンド初期化
        config = get_config()
        data_store = DataStore(str(config.get_data_file_path()))
        self.keyboard_logger = KeyboardLogger(data_store)
        self.statistics_analyzer = StatisticsAnalyzer(data_store)

        # モダンダッシュボード
        self.dashboard = ModernDashboard(
            self.root,
            self.keyboard_logger,
            self.statistics_analyzer
        )
        self.dashboard.pack(fill="both", expand=True)

    def run(self):
        try:
            self.root.mainloop()
        finally:
            if self.keyboard_logger.is_running():
                self.keyboard_logger.stop_logging()


if __name__ == "__main__":
    app = ModernTestApp()
    app.run()
