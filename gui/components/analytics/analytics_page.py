"""
統合分析ページ

全ての分析カードを統合したメインページ
データの読み込み、表示、エクスポート機能を提供
"""

import json
import threading
from datetime import datetime
from tkinter import filedialog, messagebox
from typing import Any, Dict, Optional

import customtkinter as ctk

# from .basic_stats_card import BasicStatsCard  # ヘッダー表示に変更したため不要
from .data_analyzer import DataAnalyzer
from .integrated_sequence_card import IntegratedSequenceCard
from .key_frequency_card import KeyFrequencyCard
from .modifier_analysis_card import ModifierAnalysisCard


class AnalyticsPage(ctk.CTkFrame):
    """分析ページのメインクラス"""

    def __init__(self, parent, data_file_path: Optional[str] = None, **kwargs):
        super().__init__(parent, **kwargs)

        # データファイルパスの設定
        if data_file_path is None:
            # デフォルトパスを使用
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent.parent
            data_file_path = str(project_root / "data" / "keyboard_log.json")

        # データアナライザーの初期化
        self.data_analyzer = DataAnalyzer(data_file_path)
        self.current_data = None

        # 自動更新状態の初期化
        self.auto_refresh_enabled = False

        # UIの初期化
        self._setup_ui()

        # 初期データ読み込み
        self._load_initial_data()

    def _setup_ui(self):
        """UIセットアップ"""
        # メインフレーム
        self.configure(fg_color="transparent")

        # ヘッダーフレーム
        self._create_header()

        # コンテンツフレーム
        self._create_content_area()

    def _create_header(self):
        """ヘッダー部分の作成"""
        header_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray15"))
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # タイトル
        title_label = ctk.CTkLabel(
            header_frame,
            text="📈 キーボード使用統計",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("gray10", "gray90")
        )
        title_label.pack(side="left", padx=20, pady=15)

        # ボタンフレーム
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=20, pady=10)

        # データ更新ボタン
        self.refresh_button = ctk.CTkButton(
            button_frame,
            text="統計更新",
            command=self._refresh_data,
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.refresh_button.pack(side="left", padx=5)

        # エクスポートボタン
        self.export_button = ctk.CTkButton(
            button_frame,
            text="データエクスポート",
            command=self._export_data_simple,
            width=140,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("green", "darkgreen")
        )
        self.export_button.pack(side="left", padx=5)

        # ステータスラベル
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60")
        )
        self.status_label.pack(side="bottom", padx=20, pady=(0, 10))

    def _create_content_area(self):
        """コンテンツエリアの作成"""
        # スクロール可能なメインフレーム
        self.main_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.main_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # グリッドレイアウト用のフレーム
        self.grid_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)

        # 分析カードの作成
        self._create_analysis_cards()

    def _create_analysis_cards(self):
        """分析カードの作成"""
        # 基本統計はヘッダーのステータスバーに表示するため、カードは非表示
        # self.basic_stats_card = BasicStatsCard(self.grid_frame, title="📊 基本統計")
        # self.basic_stats_card.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # 1行目：上位キー分析カード（左）+ モディファイア詳細カード（右）
        self.key_frequency_card = KeyFrequencyCard(self.grid_frame)
        self.key_frequency_card.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.modifier_analysis_card = ModifierAnalysisCard(self.grid_frame)
        self.modifier_analysis_card.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # 2行目：統合シーケンス分析カード（全幅）
        self.sequence_card = IntegratedSequenceCard(self.grid_frame)
        self.sequence_card.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # グリッドの列を均等に配置（2列）
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)

    def _load_initial_data(self):
        """初期データの読み込み"""
        self._update_status("データを読み込み中...")

        # バックグラウンドで読み込み
        def load_data():
            try:
                # デバッグ情報を取得
                debug_info = self.data_analyzer.debug_data_loading()
                print(f"=== デバッグ情報 ===")
                print(f"データファイルパス: {debug_info['data_file_path']}")
                print(f"ファイル存在: {debug_info['file_exists']}")
                print(f"ファイルサイズ: {debug_info['file_size']} bytes")
                print(f"データキー: {debug_info['data_keys']}")
                print(f"総計統計キー: {debug_info.get('total_stats_keys', [])}")
                print(f"キー統計数: {debug_info.get('key_stats_count', 0)}")
                if debug_info['error']:
                    print(f"エラー: {debug_info['error']}")
                print("==================")

                # データファイルの存在確認
                if not self.data_analyzer.has_data():
                    # データがない場合は空のUIを表示
                    self.current_data = self.data_analyzer.load_data()
                    self._show_no_data_message()
                    self._update_status("データファイルが見つかりません。キーボードモニターを実行してデータを生成してください。")
                    return

                self.current_data = self.data_analyzer.load_data()
                print(f"読み込んだデータ: {list(self.current_data.keys()) if self.current_data else 'None'}")

                # エラーが含まれているかチェック
                if "error" in self.current_data:
                    error_msg = self.current_data["error"]
                    self.after(0, lambda: [
                        self._update_status(f"データ読み込みエラー: {error_msg}"),
                        self._show_error_message(f"データの読み込みに失敗しました:\n{error_msg}")
                    ])
                    return

                self._update_ui_with_data()
                # 基本統計をステータスバーに表示
                self._update_status_with_basic_stats()

            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda: [
                    self._update_status(f"データ読み込みエラー: {error_msg}"),
                    self._show_error_message(f"データの読み込みに失敗しました:\n{error_msg}")
                ])

        thread = threading.Thread(target=load_data, daemon=True)
        thread.start()

    def _refresh_data(self):
        """データの再読み込み"""
        # ボタンを無効化
        self.refresh_button.configure(state="disabled", text="読み込み中...")

        def refresh():
            try:
                self.current_data = self.data_analyzer.load_data()
                self._update_ui_with_data()

                # メインスレッドでUI更新
                self.after(0, lambda: [
                    self.refresh_button.configure(state="normal", text="🔄 データ更新"),
                    self._update_status(f"データ更新完了 ({datetime.now().strftime('%H:%M:%S')})")
                ])

            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda: [
                    self.refresh_button.configure(state="normal", text="🔄 データ更新"),
                    self._update_status(f"更新エラー: {error_msg}"),
                    messagebox.showerror("エラー", f"データの更新に失敗しました:\n{error_msg}")
                ])

        thread = threading.Thread(target=refresh, daemon=True)
        thread.start()

    def _update_ui_with_data(self):
        """データでUIを更新"""
        if not self.current_data:
            self._show_no_data_message()
            return

        def update_ui():
            try:
                # 基本統計（ヘッダーのステータスバーに表示するため、カード更新は不要）
                # try:
                #     basic_stats = self.data_analyzer.get_basic_statistics()
                #     self.basic_stats_card.update_data(basic_stats)
                # except Exception as e:
                #     print(f"基本統計の更新でエラー: {e}")
                #     self.basic_stats_card.update_data({
                #         "total_keystrokes": 0,
                #         "recording_period": "エラー",
                #         "recording_days": "0日間",
                #         "daily_average": "0.0回/日"
                #     })

                # キー頻度
                try:
                    key_frequency = self.data_analyzer.get_key_frequency()
                    print(f"キー頻度データ: {key_frequency}")
                    print(f"キー頻度データ数: {len(key_frequency)}")
                    if key_frequency:
                        sorted_keys = sorted(key_frequency.items(), key=lambda x: x[1], reverse=True)
                        print(f"上位5キー: {sorted_keys[:5]}")
                    self.key_frequency_card.update_data(key_frequency)
                except Exception as e:
                    print(f"キー頻度の更新でエラー: {e}")
                    import traceback
                    traceback.print_exc()
                    self.key_frequency_card.update_data({})

                # 修飾キー分析
                try:
                    modifier_data = self.data_analyzer.get_modifier_usage()
                    print(f"修飾キー分析データ: {modifier_data}")
                    self.modifier_analysis_card.update_data(modifier_data)
                except Exception as e:
                    print(f"修飾キー分析の更新でエラー: {e}")
                    import traceback
                    traceback.print_exc()
                    self.modifier_analysis_card.update_data({})

                # 統合シーケンス分析
                try:
                    sequence_data = self.data_analyzer.get_integrated_sequence_analysis()
                    print(f"シーケンス分析データキー数: {len(sequence_data)}")
                    print(f"シーケンス分析データの最初の3キー: {list(sequence_data.keys())[:3] if sequence_data else []}")
                    self.sequence_card.update_data(sequence_data)
                except Exception as e:
                    print(f"シーケンス分析の更新でエラー: {e}")
                    import traceback
                    traceback.print_exc()
                    self.sequence_card.update_data({})

            except Exception as e:
                print(f"UI更新で予期しないエラー: {e}")
                self._update_status(f"UI更新エラー: {str(e)}")

        # メインスレッドでUI更新
        self.after(0, update_ui)

    def _toggle_auto_refresh(self):
        """自動更新のトグル"""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        if self.auto_refresh_enabled:
            if hasattr(self, 'auto_refresh_button'):
                self.auto_refresh_button.configure(text="自動更新: ON", fg_color=("green", "darkgreen"))
            self._start_auto_refresh()
        else:
            if hasattr(self, 'auto_refresh_button'):
                self.auto_refresh_button.configure(text="自動更新: OFF", fg_color=("gray", "gray30"))
            self._stop_auto_refresh()

    def refresh_if_needed(self):
        """必要に応じてデータを更新"""
        # ファイルの更新時刻をチェックして自動更新する場合の実装
        # 現在は手動更新のみ
        pass

    def _export_data_simple(self):
        """簡単なデータエクスポート機能"""
        if not self.current_data:
            messagebox.showwarning("警告", "エクスポートするデータがありません。")
            return

        file_path = filedialog.asksaveasfilename(
            title="分析データをエクスポート",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"データをエクスポートしました:\n{file_path}")
            except Exception as e:
                messagebox.showerror("エラー", f"エクスポートに失敗しました:\n{str(e)}")

    def _show_no_data_message(self):
        """データなしメッセージを表示"""
        try:
            # 基本統計はヘッダーのステータスバーに表示するため、カード更新は不要
            # self.basic_stats_card.update_data({
            #     "total_keystrokes": 0,
            #     "recording_period": "データなし",
            #     "recording_days": "0日間",
            #     "daily_average": "0.0回/日"
            # })

            # ステータスバーにデータなし表示
            self._update_status("キー入力 0回    データなし")

            self.key_frequency_card.update_data({})
            self.modifier_analysis_card.update_data({})
            self.sequence_card.update_data({})

        except Exception as e:
            print(f"UIの初期化でエラー: {e}")

    def get_current_data(self) -> Optional[Dict[str, Any]]:
        """現在のデータを取得"""
        return self.current_data

    def _update_status(self, message: str):
        """ステータスメッセージを更新"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.configure(text=message)
        except Exception as e:
            print(f"ステータス更新エラー: {e}")

    def _show_error_message(self, message: str):
        """エラーメッセージを表示"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.configure(text=f"エラー: {message}", text_color="red")
            print(f"エラー: {message}")
        except Exception as e:
            print(f"エラーメッセージ表示エラー: {e}")

    def _start_auto_refresh(self):
        """自動更新を開始（プレースホルダー）"""
        # 将来の実装用プレースホルダー
        pass

    def _stop_auto_refresh(self):
        """自動更新を停止（プレースホルダー）"""
        # 将来の実装用プレースホルダー
        pass

    def _update_status_with_basic_stats(self):
        """基本統計をステータスバーに表示"""
        try:
            basic_stats = self.data_analyzer.get_basic_statistics()
            total_keystrokes = basic_stats.get("total_keystrokes", 0)
            recording_period = basic_stats.get("recording_period", "記録なし")

            # フォーマット：「キー入力 xxxx回    2025-06-01~2025-06-27」
            if recording_period != "記録なし":
                # 日付フォーマットを簡潔に変更（yyyy/mm/dd → yyyy-mm-dd）
                period_formatted = recording_period.replace("/", "-").replace(" ～ ", "~")
                status_text = f"キー入力 {total_keystrokes:,}回    {period_formatted}"
            else:
                status_text = f"キー入力 {total_keystrokes:,}回    記録期間なし"

            self._update_status(status_text)
        except Exception as e:
            print(f"基本統計ステータス更新エラー: {e}")
            self._update_status("データ読み込み完了")
