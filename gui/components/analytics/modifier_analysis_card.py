"""
修飾キー分析カードコンポーネント

Shift、Ctrl、Altなどの修飾キーの使用状況を表示
"""

import math
from typing import Any, Dict

import customtkinter as ctk


class ModifierAnalysisCard(ctk.CTkFrame):
    """修飾キー使用状況を表示するカードコンポーネント"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # カードの設定（KeyFrequencyCardと同じサイズと設定）
        self.configure(
            corner_radius=10,
            fg_color=("gray95", "gray10"),
            width=280,
            height=180
        )

        # タイトル
        self.title_label = ctk.CTkLabel(
            self,
            text="モディファイア詳細",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "gray90")
        )
        self.title_label.pack(pady=(12, 8), padx=12, anchor="w")

        # メインコンテンツフレーム
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def update_data(self, modifier_data: Dict[str, Any]):
        """修飾キーデータを更新して表示"""
        try:
            print(f"ModifierAnalysisCard: 受信データ = {modifier_data}")

            # 既存のウィジェットをクリア
            for widget in self.content_frame.winfo_children():
                widget.destroy()

            if not modifier_data:
                # データがない場合
                no_data_label = ctk.CTkLabel(
                    self.content_frame,
                    text="データがありません",
                    font=ctk.CTkFont(size=12),
                    text_color=("gray50", "gray50")
                )
                no_data_label.pack(pady=20)
                return

            # 詳細分析を表示
            self._create_detailed_analysis(modifier_data)

        except Exception as e:
            print(f"ModifierAnalysisCard update_data エラー: {e}")
            import traceback
            traceback.print_exc()
            # エラー時は「エラー」表示
            error_label = ctk.CTkLabel(
                self.content_frame,
                text="データ表示エラー",
                font=ctk.CTkFont(size=12),
                text_color=("red", "red")
            )
            error_label.pack(pady=20)

    def _create_detailed_analysis(self, modifier_data: Dict[str, Any]):
        """詳細分析の作成 - 4列グリッド形式で各修飾キーを横並び表示"""
        # 各修飾キーごとの上位キーランキングを4列グリッドで表示
        self._create_modifier_key_rankings_grid(self.content_frame, modifier_data)

    def _create_modifier_key_rankings_grid(self, parent, modifier_data: Dict[str, Any]):
        """各修飾キーごとの上位キーランキングを4列グリッドで表示"""
        modifier_key_rankings = modifier_data.get('modifier_key_rankings', {})

        if not modifier_key_rankings:
            no_data_label = ctk.CTkLabel(
                parent,
                text="データがありません",
                font=ctk.CTkFont(size=12),
                text_color=("gray50", "gray50")
            )
            no_data_label.pack(pady=20)
            return

        # ランキング表示フレーム
        rankings_frame = ctk.CTkFrame(parent, fg_color=("gray85", "gray25"))
        rankings_frame.pack(fill="both", expand=True)

        rankings_title = ctk.CTkLabel(
            rankings_frame,
            text="各修飾キーでよく使うキー（上位5個）",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray10", "gray90")
        )
        rankings_title.pack(pady=(8, 5), padx=8, anchor="w")

        # 4列グリッドを作成
        grid_frame = ctk.CTkFrame(rankings_frame, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # 修飾キー情報
        modifier_info = [
            ("shift", "Shift", "#4CAF50"),
            ("ctrl", "Ctrl", "#2196F3"),
            ("alt", "Alt", "#FF9800"),
            ("super", "Super", "#9C27B0")
        ]

        for col, (modifier_key, display_name, color) in enumerate(modifier_info):
            # 各修飾キーのカラムフレーム
            column_frame = ctk.CTkFrame(grid_frame, fg_color=("gray90", "gray20"))
            column_frame.grid(row=0, column=col, padx=3, pady=3, sticky="nsew")

            # 修飾キー名のヘッダー
            header_label = ctk.CTkLabel(
                column_frame,
                text=display_name,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=color
            )
            header_label.pack(pady=(6, 3))

            # そのキーのランキングを表示
            rankings = modifier_key_rankings.get(modifier_key, [])

            if not rankings:
                # データがない場合
                no_data_label = ctk.CTkLabel(
                    column_frame,
                    text="データなし",
                    font=ctk.CTkFont(size=9),
                    text_color=("gray50", "gray50")
                )
                no_data_label.pack(pady=10)
            else:
                # 上位キーを表示
                for ranking in rankings:
                    rank = ranking.get("rank", 0)
                    key_name = ranking.get("key_name", "Unknown")
                    count = ranking.get("count", 0)

                    # ランキング行
                    rank_frame = ctk.CTkFrame(column_frame, fg_color="transparent")
                    rank_frame.pack(fill="x", padx=4, pady=1)

                    # 順位に応じた色
                    rank_color = self._get_ranking_color(rank)

                    # コンパクトに表示: 順位. キー名 (回数)
                    if len(key_name) > 8:
                        display_name = key_name[:7] + "…"
                    else:
                        display_name = key_name

                    rank_text = f"{rank}. {display_name}"
                    if count > 0:
                        rank_text += f" ({count})"

                    rank_label = ctk.CTkLabel(
                        rank_frame,
                        text=rank_text,
                        font=ctk.CTkFont(size=8, weight="bold" if rank <= 3 else "normal"),
                        text_color=rank_color,
                        anchor="w"
                    )
                    rank_label.pack(side="left", padx=2)

        # グリッドの列を均等に配置（4列）
        for i in range(4):
            grid_frame.grid_columnconfigure(i, weight=1)

    def _get_ranking_color(self, rank: int) -> str:
        """ランキング順位に応じた色を取得"""
        if rank == 1:
            return "#FFD700"  # ゴールド
        elif rank == 2:
            return "#C0C0C0"  # シルバー
        elif rank == 3:
            return "#CD7F32"  # ブロンズ
        else:
            return ("gray30", "gray70")  # デフォルト

    def _format_key_name(self, key: str) -> str:
        """キー名を表示用にフォーマット"""
        # 特殊キーの表示名マッピング
        special_keys = {
            'space': 'Space',
            'backspace': 'BS',
            'enter': 'Enter',
            'shift': 'Shift',
            'ctrl': 'Ctrl',
            'alt': 'Alt',
            'tab': 'Tab',
            'escape': 'Esc',
            'delete': 'Del',
            'insert': 'Ins',
            'home': 'Home',
            'end': 'End',
            'page_up': 'PgUp',
            'page_down': 'PgDn',
            'up': '↑',
            'down': '↓',
            'left': '←',
            'right': '→',
            'caps_lock': 'Caps',
            'num_lock': 'Num',
            'scroll_lock': 'Scrl'
        }

        # 小文字に変換してチェック
        key_lower = key.lower()
        if key_lower in special_keys:
            return special_keys[key_lower]

        # ファンクションキー
        if key_lower.startswith('f') and key_lower[1:].isdigit():
            return key.upper()

        # 通常のキー（大文字で表示）
        return key.upper()
