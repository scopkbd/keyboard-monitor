"""
キー頻度分析カードコンポーネント

最も頻繁に使用されるキーをランキング形式で表示
"""

from typing import Any, Dict

import customtkinter as ctk


class KeyFrequencyCard(ctk.CTkFrame):
    """キー頻度を表示するカードコンポーネント"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # カードの設定
        self.configure(
            corner_radius=10,
            fg_color=("gray95", "gray10"),
            width=280,
            height=180
        )

        # タイトル
        self.title_label = ctk.CTkLabel(
            self,
            text="上位キー",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "gray90")
        )
        self.title_label.pack(pady=(12, 8), padx=12, anchor="w")

        # スクロール可能なフレーム
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            height=180,
            fg_color="transparent"
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # データ表示用のフレーム
        self.content_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

    def update_data(self, key_frequency: Dict[str, int]):
        """キー頻度データを更新して表示"""
        try:
            print(f"KeyFrequencyCard: 受信データ = {key_frequency}")
            print(f"KeyFrequencyCard: データキー数 = {len(key_frequency)}")

            # 既存のウィジェットをクリア
            for widget in self.content_frame.winfo_children():
                widget.destroy()

            if not key_frequency:
                # データがない場合
                no_data_label = ctk.CTkLabel(
                    self.content_frame,
                    text="データがありません",
                    font=ctk.CTkFont(size=12),
                    text_color=("gray50", "gray50")
                )
                no_data_label.pack(pady=20)
                return

            # 頻度順にソート（上位10位まで表示）
            sorted_keys = sorted(key_frequency.items(), key=lambda x: x[1], reverse=True)
            top_keys = sorted_keys[:10]

            print(f"KeyFrequencyCard: ソート後上位10キー = {top_keys}")

            # 最大値を取得（プログレスバーの基準用）
            max_count = top_keys[0][1] if top_keys else 1
            total_keystrokes = sum(key_frequency.values())

            # ヘッダー
            header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, 5))

            ctk.CTkLabel(
                header_frame,
                text="順位",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=40,
                anchor="center"
            ).pack(side="left", padx=(0, 5))

            ctk.CTkLabel(
                header_frame,
                text="キー",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=60,
                anchor="center"
            ).pack(side="left", padx=5)

            ctk.CTkLabel(
                header_frame,
                text="回数",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=60,
                anchor="center"
            ).pack(side="left", padx=5)

            ctk.CTkLabel(
                header_frame,
                text="頻度",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="center"
            ).pack(side="left", fill="x", expand=True, padx=(5, 0))

            # 各キーの情報を表示
            for rank, (key, count) in enumerate(top_keys, 1):
                # キー表示用の文字列を作成
                display_key = self._format_key_name(key)
                percentage = (count / total_keystrokes) * 100

                # 行のフレーム
                row_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)

                # 順位
                rank_label = ctk.CTkLabel(
                    row_frame,
                    text=f"{rank}.",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    width=40,
                    anchor="center"
                )
                rank_label.pack(side="left", padx=(0, 5))

                # キー名
                key_label = ctk.CTkLabel(
                    row_frame,
                    text=display_key,
                    font=ctk.CTkFont(size=11, weight="bold" if rank <= 3 else "normal"),
                    width=60,
                    anchor="center"
                )
                key_label.pack(side="left", padx=5)

                # 回数
                count_label = ctk.CTkLabel(
                    row_frame,
                    text=f"{count:,}",
                    font=ctk.CTkFont(size=11, weight="bold" if rank <= 3 else "normal"),
                    width=60,
                    anchor="center"
                )
                count_label.pack(side="left", padx=5)

                # 使用率とプログレスバー
                freq_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                freq_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))

                # 使用率テキスト
                percentage_text = f"{percentage:.1f}%"
                perc_label = ctk.CTkLabel(
                    freq_frame,
                    text=percentage_text,
                    font=ctk.CTkFont(size=10),
                    text_color=("gray30", "gray70"),
                    anchor="e"
                )
                perc_label.pack(side="right", padx=(0, 5))

                # プログレスバー
                progress_bar = ctk.CTkProgressBar(
                    freq_frame,
                    width=80,
                    height=8
                )
                progress_bar.pack(side="right", padx=(5, 10), pady=3)
                progress_bar.set(percentage / 100)

        except Exception as e:
            print(f"KeyFrequencyCard update_data エラー: {e}")
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