"""
ダッシュボードコンポーネント

リアルタイム統計とシステム状態を表示するメインダッシュボード（WPM削除版）
"""

import customtkinter as ctk
from typing import Dict, Any
import threading
import time


class Dashboard(ctk.CTkFrame):
    """メインダッシュボードコンポーネント（WPM機能なし）"""

    def __init__(self, parent, keyboard_logger, statistics_analyzer):
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
        # グリッド設定
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1)

        # タイトル
        self._create_title()
        
        # 制御パネル
        self._create_control_panel()
        
        # 統計パネル
        self._create_stats_panel()
        
        # アクティビティログ
        self._create_activity_log()

    def _create_title(self):
        """タイトルの作成"""
        title = ctk.CTkLabel(
            self,
            text="📊 キーボードモニター ダッシュボード",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, pady=(20, 10))

    def _create_control_panel(self):
        """記録制御パネルの作成"""
        control_frame = ctk.CTkFrame(self)
        control_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20), padx=20, sticky="ew")
        
        # 中央配置のためのグリッド設定
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=0)
        control_frame.grid_columnconfigure(2, weight=1)
        
        # メイン記録ボタン（中央配置）
        self.start_button = ctk.CTkButton(
            control_frame,
            text="▶️ 記録開始",
            command=self._toggle_recording,
            width=200,
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=15
        )
        self.start_button.grid(row=0, column=1, padx=20, pady=20)
        
        # ステータス表示（ボタンの下）
        self.status_label = ctk.CTkLabel(
            control_frame,
            text="準備完了 - 記録を開始してください",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.status_label.grid(row=1, column=1, padx=20, pady=(0, 20))

    def _create_stats_panel(self):
        """統計パネルの作成"""
        # 左側: セッション統計
        session_frame = ctk.CTkFrame(self)
        session_frame.grid(row=2, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")

        session_title = ctk.CTkLabel(
            session_frame,
            text="📈 セッション統計",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        session_title.pack(pady=(15, 10))

        # 統計値表示ラベル（WPM削除）
        self.session_stats = {
            'keystrokes': ctk.CTkLabel(session_frame, text="キーストローク: 0"),
            'duration': ctk.CTkLabel(session_frame, text="継続時間: 00:00:00"),
            'accuracy': ctk.CTkLabel(session_frame, text="効率: 0%")
        }

        for label in self.session_stats.values():
            label.pack(pady=5)

        # 右側: 全体統計
        total_frame = ctk.CTkFrame(self)
        total_frame.grid(row=2, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")

        total_title = ctk.CTkLabel(
            total_frame,
            text="🏆 全体統計",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        total_title.pack(pady=(15, 10))

        # 全体統計値表示（WPM削除）
        self.total_stats = {
            'total_keys': ctk.CTkLabel(total_frame, text="総キーストローク: 0"),
            'sessions': ctk.CTkLabel(total_frame, text="セッション数: 0"),
            'most_used': ctk.CTkLabel(total_frame, text="最頻出キー: -")
        }

        for label in self.total_stats.values():
            label.pack(pady=5)

    def _create_activity_log(self):
        """アクティビティログの作成"""
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        log_title = ctk.CTkLabel(
            log_frame,
            text="📋 最近のアクティビティ",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        log_title.pack(pady=(15, 10))

        # ログ表示テキストボックス
        self.activity_log = ctk.CTkTextbox(
            log_frame,
            height=120,
            wrap="word"
        )
        self.activity_log.pack(fill="x", padx=15, pady=(0, 15))
        self.activity_log.insert("1.0", "アプリケーションが開始されました。\n")

    def _toggle_recording(self):
        """記録の開始/停止を切り替え"""
        if self.keyboard_logger.is_running():
            # 停止
            self.keyboard_logger.stop_logging()
            self.start_button.configure(
                text="▶️ 記録開始",
                fg_color=["#3B8ED0", "#1F6AA5"],  # デフォルトの青色
                hover_color=["#36719F", "#144870"]
            )
            self.status_label.configure(
                text="記録停止 - セッションをリセットしました",
                text_color="orange"
            )
            self._log_activity("🛑 キーボード記録を停止しました。")
        else:
            # 開始
            self.keyboard_logger.start_logging()
            self.start_button.configure(
                text="⏹️ 記録停止",
                fg_color=["#DC143C", "#B91C1C"],  # 赤色
                hover_color=["#B91C1C", "#991B1B"]
            )
            self.status_label.configure(
                text="🔴 記録中 - キーストロークを監視しています",
                text_color="green"
            )
            self._log_activity("🎯 キーボード記録を開始しました。")

    def _start_updates(self):
        """定期的な統計更新を開始"""
        self.is_updating = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()

    def _update_loop(self):
        """統計データの定期更新ループ"""
        while self.is_updating:
            try:
                self._update_stats()
                time.sleep(1)  # 1秒ごとに更新
            except Exception as e:
                print(f"統計更新エラー: {e}")
                time.sleep(5)  # エラー時は5秒待機

    def _update_stats(self):
        """統計データの更新"""
        try:
            # セッション統計をKeyboardLoggerから直接取得
            session_stats = self.keyboard_logger.get_session_statistics()
            
            # 全体統計をStatisticsAnalyzerから取得
            overall_stats = self.statistics_analyzer.get_basic_statistics()

            # UI要素を安全に更新（メインスレッドで実行）
            self.after(0, self._update_ui_stats, session_stats, overall_stats)

        except Exception as e:
            print(f"統計データ取得エラー: {e}")

    def _update_ui_stats(self, session_stats: Dict[str, Any], overall_stats: Dict[str, Any]):
        """UI統計表示の更新（メインスレッド実行）"""
        try:
            # セッション統計の更新
            session_keys = session_stats.get('keystrokes', 0)
            self.session_stats['keystrokes'].configure(text=f"キーストローク: {session_keys:,}")

            # 継続時間の表示
            elapsed_seconds = session_stats.get('elapsed_seconds', 0)
            hours, remainder = divmod(int(elapsed_seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.session_stats['duration'].configure(text=f"継続時間: {duration}")

            # 効率計算（仮実装）
            efficiency = 85.0  # 仮の値
            self.session_stats['accuracy'].configure(text=f"効率: {efficiency:.0f}%")

            # 全体統計の更新
            total_keys = overall_stats.get('total_keystrokes', 0)
            self.total_stats['total_keys'].configure(text=f"総キーストローク: {total_keys:,}")

            sessions_count = overall_stats.get('session_count', 0)
            self.total_stats['sessions'].configure(text=f"セッション数: {sessions_count}")

            most_used = overall_stats.get('most_frequent_key', '-')
            self.total_stats['most_used'].configure(text=f"最頻出キー: {most_used}")

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
