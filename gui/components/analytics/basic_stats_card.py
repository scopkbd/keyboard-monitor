"""
基本統計カードコンポーネント

総キーストローク数と記録期間を表示する
"""

from typing import Any, Dict

import customtkinter as ctk


class BasicStatsCard(ctk.CTkFrame):
    """基本統計をヘッダー形式で表示するコンパクトなコンポーネント"""

    def __init__(self, parent, title: str = "📈 キーボード使用統計", **kwargs):
        super().__init__(parent, **kwargs)

        # ヘッダー形式の設定（高さを抑制）
        self.configure(corner_radius=8, fg_color=("gray90", "gray15"), height=50)

        # 横並びのメインフレーム
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=8)

        # タイトル（左側）
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("gray10", "gray90")
        )
        self.title_label.pack(side="left", anchor="w")

        # 統計情報（右側）
        self.stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.stats_frame.pack(side="right", anchor="e")

    def update_data(self, stats: Dict[str, Any]):
        """統計データを更新して表示"""
        try:
            # 既存のウィジェットをクリア
            for widget in self.stats_frame.winfo_children():
                widget.destroy()

            # 統計項目のデータ（2項目のみ）
            total_keystrokes = stats.get("total_keystrokes", 0)
            recording_period = stats.get("recording_period", "記録なし")

            # 数値のフォーマット処理を安全に行う
            try:
                if isinstance(total_keystrokes, (int, float)):
                    formatted_total = f"{int(total_keystrokes):,}回"
                else:
                    formatted_total = str(total_keystrokes)
            except:
                formatted_total = str(total_keystrokes)

            # コンパクトなヘッダー形式で表示
            stats_text = f"📊 {formatted_total} | 📅 {recording_period}"
            stats_label = ctk.CTkLabel(
                self.stats_frame,
                text=stats_text,
                font=ctk.CTkFont(size=13, weight="normal"),
                text_color=("gray30", "gray70")
            )
            stats_label.pack(side="right", anchor="e")

        except Exception as e:
            print(f"基本統計ヘッダーの更新でエラー: {e}")
            self._show_error_message()

    def _show_error_message(self):
        """エラーメッセージを表示"""
        error_label = ctk.CTkLabel(
            self.stats_frame,
            text="統計データエラー",
            font=ctk.CTkFont(size=11),
            text_color="red"
        )
        error_label.pack(side="right", anchor="e")
