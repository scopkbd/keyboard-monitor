"""
統合シーケンス分析カードコンポーネント

3列レイアウト：前任キー | メインキー | 後続キー
上位5キーの前後関係を視覚的に表示
"""

from typing import Any, Dict, List, Tuple

import customtkinter as ctk


class IntegratedSequenceCard(ctk.CTkFrame):
    """統合シーケンス分析を表示するカードコンポーネント"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # カードの設定
        self.configure(corner_radius=10, fg_color=("gray95", "gray10"))

        # タイトル
        self.title_label = ctk.CTkLabel(
            self,
            text="統合シーケンス分析",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("gray10", "gray90")
        )
        self.title_label.pack(pady=(15, 10), padx=15, anchor="w")

        # 説明
        self.desc_label = ctk.CTkLabel(
            self,
            text="よく使用されるキーの前後に押されるキーを分析",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        self.desc_label.pack(pady=(0, 10), padx=15, anchor="w")

        # メインコンテンツフレーム
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # ヘッダーフレーム
        self.header_frame = ctk.CTkFrame(self.content_frame, fg_color=("gray85", "gray25"))
        self.header_frame.pack(fill="x", pady=(0, 10))

        # ヘッダーラベル
        self._create_header()

        # スクロール可能なコンテンツフレーム
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            height=300,
            fg_color="transparent"
        )
        self.scrollable_frame.pack(fill="both", expand=True)

    def _create_header(self):
        """ヘッダーの作成"""
        # 3列のヘッダーを作成
        headers = ["前任キー（上位3）", "メインキー", "後続キー（上位3）"]
        colors = ["#FF9800", "#2196F3", "#4CAF50"]

        for i, (header, color) in enumerate(zip(headers, colors)):
            header_label = ctk.CTkLabel(
                self.header_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=color
            )
            header_label.grid(row=0, column=i, padx=10, pady=10, sticky="ew")

        # グリッドの列を均等に配置
        for i in range(3):
            self.header_frame.grid_columnconfigure(i, weight=1)

    def update_data(self, sequence_data: Dict[str, Any]):
        """シーケンス分析データを更新して表示"""
        try:
            print(f"IntegratedSequenceCard: 受信データキー数 = {len(sequence_data)}")
            print(f"IntegratedSequenceCard: データキー = {list(sequence_data.keys())}")

            # 既存のウィジェットをクリア
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            if not sequence_data:
                # データがない場合
                no_data_label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text="データがありません",
                    font=ctk.CTkFont(size=12),
                    text_color=("gray50", "gray50")
                )
                no_data_label.pack(pady=20)
                return

            # 各キーの分析結果を表示
            for i, (main_key, analysis) in enumerate(sequence_data.items()):
                if i >= 5:  # 上位5キーまで
                    break

                self._create_key_analysis_row(main_key, analysis, i)

        except Exception as e:
            print(f"IntegratedSequenceCard update_data エラー: {e}")
            import traceback
            traceback.print_exc()

    def _create_key_analysis_row(self, main_key: str, analysis: Dict[str, Any], index: int):
        """個別キーの分析行を作成"""
        # 行のメインフレーム
        row_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=("gray90", "gray20") if index % 2 == 0 else ("gray85", "gray25")
        )
        row_frame.pack(fill="x", pady=5, padx=5)

        # 3列のレイアウト
        # 列1: 前任キー
        predecessors = analysis.get('predecessors', [])
        pred_frame = self._create_key_list_frame(
            row_frame,
            predecessors,
            "#FF9800",
            "前任キー"
        )
        pred_frame.grid(row=0, column=0, padx=10, pady=15, sticky="nsew")

        # 列2: メインキー
        main_frame = self._create_main_key_frame(
            row_frame,
            main_key,
            analysis.get('count', 0),
            index + 1
        )
        main_frame.grid(row=0, column=1, padx=10, pady=15, sticky="nsew")

        # 列3: 後続キー
        successors = analysis.get('successors', [])
        succ_frame = self._create_key_list_frame(
            row_frame,
            successors,
            "#4CAF50",
            "後続キー"
        )
        succ_frame.grid(row=0, column=2, padx=10, pady=15, sticky="nsew")

        # グリッドの列を均等に配置
        for i in range(3):
            row_frame.grid_columnconfigure(i, weight=1)

    def _create_key_list_frame(self, parent, key_list: List[Tuple[str, int]], color: str, title: str):
        """キーリストフレームを作成"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")

        # 上位3キーを表示
        top_keys = key_list[:3] if key_list else []

        for i, (key, count) in enumerate(top_keys):
            # キー表示フレーム
            key_frame = ctk.CTkFrame(frame, fg_color=("gray80", "gray30"))
            key_frame.pack(fill="x", pady=2)

            # 順位表示
            rank_label = ctk.CTkLabel(
                key_frame,
                text=f"{i+1}.",
                font=ctk.CTkFont(size=10),
                text_color=("gray40", "gray60"),
                width=20
            )
            rank_label.pack(side="left", padx=(5, 0), pady=5)

            # キー名
            key_display = self._format_key_name(key)
            key_label = ctk.CTkLabel(
                key_frame,
                text=key_display,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=color
            )
            key_label.pack(side="left", padx=5, pady=5)

            # 回数
            count_label = ctk.CTkLabel(
                key_frame,
                text=f"({count})",
                font=ctk.CTkFont(size=9),
                text_color=("gray50", "gray50")
            )
            count_label.pack(side="right", padx=(0, 5), pady=5)

        # データがない場合
        if not top_keys:
            no_data_label = ctk.CTkLabel(
                frame,
                text="データなし",
                font=ctk.CTkFont(size=10),
                text_color=("gray50", "gray50")
            )
            no_data_label.pack(pady=10)

        return frame

    def _create_main_key_frame(self, parent, main_key: str, count: int, rank: int):
        """メインキーフレームを作成"""
        frame = ctk.CTkFrame(parent, fg_color=("gray75", "gray35"))

        # 順位表示
        rank_label = ctk.CTkLabel(
            frame,
            text=f"#{rank}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self._get_rank_color(rank)
        )
        rank_label.pack(pady=(10, 5))

        # メインキー名
        key_display = self._format_key_name(main_key)
        key_label = ctk.CTkLabel(
            frame,
            text=key_display,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2196F3"
        )
        key_label.pack(pady=5)

        # 使用回数
        count_label = ctk.CTkLabel(
            frame,
            text=f"{count:,} 回",
            font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70")
        )
        count_label.pack(pady=(0, 10))

        return frame

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

    def _get_rank_color(self, rank: int) -> str:
        """順位に応じた色を取得"""
        if rank == 1:
            return "#FFD700"  # ゴールド
        elif rank == 2:
            return "#C0C0C0"  # シルバー
        elif rank == 3:
            return "#CD7F32"  # ブロンズ
        elif rank <= 5:
            return "#4CAF50"  # グリーン
        else:
            return ("gray20", "gray80")  # デフォルト
