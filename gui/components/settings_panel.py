"""
設定パネルコンポーネント

アプリケーションの各種設定を管理するコンポーネント
"""

import customtkinter as ctk
from typing import Dict, Any
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox


class SettingsPanel(ctk.CTkFrame):
    """設定パネルコンポーネント"""

    def __init__(self, parent, config, **kwargs):
        super().__init__(parent, **kwargs)

        self.config = config
        self.settings_changed = False

        self._setup_ui()
        self._load_current_settings()

    def _setup_ui(self):
        """UI要素のセットアップ"""
        # グリッド設定
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ヘッダー
        header = ctk.CTkLabel(
            self,
            text="⚙️ 設定",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.grid(row=0, column=0, pady=(20, 30), sticky="w")

        # 設定タブビュー
        self.settings_tabs = ctk.CTkTabview(self)
        self.settings_tabs.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # 各設定タブの作成
        self._create_general_tab()
        self._create_recording_tab()
        self._create_display_tab()
        self._create_advanced_tab()

        # 保存・リセットボタン
        self._create_action_buttons()

    def _create_general_tab(self):
        """一般設定タブの作成"""
        tab = self.settings_tabs.add("一般")

        # 自動起動設定
        startup_frame = ctk.CTkFrame(tab)
        startup_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            startup_frame,
            text="スタートアップ設定",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.auto_start_var = ctk.BooleanVar()
        auto_start_cb = ctk.CTkCheckBox(
            startup_frame,
            text="Windowsスタートアップ時に自動起動",
            variable=self.auto_start_var,
            command=self._on_setting_changed
        )
        auto_start_cb.pack(anchor="w", padx=15, pady=(0, 15))

        self.minimize_to_tray_var = ctk.BooleanVar()
        minimize_cb = ctk.CTkCheckBox(
            startup_frame,
            text="起動時にシステムトレイに最小化",
            variable=self.minimize_to_tray_var,
            command=self._on_setting_changed
        )
        minimize_cb.pack(anchor="w", padx=15, pady=(0, 15))

        # 言語・地域設定
        lang_frame = ctk.CTkFrame(tab)
        lang_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            lang_frame,
            text="言語・地域設定",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        lang_container = ctk.CTkFrame(lang_frame, fg_color="transparent")
        lang_container.pack(anchor="w", padx=15, pady=(0, 15))

        ctk.CTkLabel(lang_container, text="言語:").pack(side="left")
        self.language_var = ctk.StringVar(value="日本語")
        lang_menu = ctk.CTkOptionMenu(
            lang_container,
            variable=self.language_var,
            values=["日本語", "English"],
            command=self._on_setting_changed
        )
        lang_menu.pack(side="left", padx=(10, 0))

    def _create_recording_tab(self):
        """記録設定タブの作成"""
        tab = self.settings_tabs.add("記録")

        # データ保存設定
        save_frame = ctk.CTkFrame(tab)
        save_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            save_frame,
            text="データ保存設定",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        # 保存間隔
        interval_container = ctk.CTkFrame(save_frame, fg_color="transparent")
        interval_container.pack(anchor="w", padx=15, pady=(0, 10))

        ctk.CTkLabel(interval_container, text="自動保存間隔:").pack(side="left")
        self.save_interval_var = ctk.StringVar(value="5分")
        interval_menu = ctk.CTkOptionMenu(
            interval_container,
            variable=self.save_interval_var,
            values=["1分", "5分", "10分", "30分", "1時間"],
            command=self._on_setting_changed
        )
        interval_menu.pack(side="left", padx=(10, 0))

        # バックアップ設定
        self.auto_backup_var = ctk.BooleanVar()
        backup_cb = ctk.CTkCheckBox(
            save_frame,
            text="自動バックアップを有効化",
            variable=self.auto_backup_var,
            command=self._on_setting_changed
        )
        backup_cb.pack(anchor="w", padx=15, pady=(0, 10))

        # バックアップ保持期間
        backup_container = ctk.CTkFrame(save_frame, fg_color="transparent")
        backup_container.pack(anchor="w", padx=15, pady=(0, 15))

        ctk.CTkLabel(backup_container, text="バックアップ保持期間:").pack(side="left")
        self.backup_days_var = ctk.StringVar(value="30日")
        backup_menu = ctk.CTkOptionMenu(
            backup_container,
            variable=self.backup_days_var,
            values=["7日", "30日", "90日", "1年", "無制限"],
            command=self._on_setting_changed
        )
        backup_menu.pack(side="left", padx=(10, 0))

        # 除外設定
        exclude_frame = ctk.CTkFrame(tab)
        exclude_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            exclude_frame,
            text="記録除外設定",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.exclude_passwords_var = ctk.BooleanVar()
        pwd_cb = ctk.CTkCheckBox(
            exclude_frame,
            text="パスワードフィールドでの記録を除外",
            variable=self.exclude_passwords_var,
            command=self._on_setting_changed
        )
        pwd_cb.pack(anchor="w", padx=15, pady=(0, 10))

        # 除外アプリケーション
        app_container = ctk.CTkFrame(exclude_frame, fg_color="transparent")
        app_container.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(app_container, text="除外アプリケーション:").pack(anchor="w")

        self.excluded_apps = ctk.CTkTextbox(app_container, height=80)
        self.excluded_apps.pack(fill="x", pady=(5, 0))
        self.excluded_apps.insert("1.0", "notepad.exe\ncalc.exe")

    def _create_display_tab(self):
        """表示設定タブの作成"""
        tab = self.settings_tabs.add("表示")

        # テーマ設定
        theme_frame = ctk.CTkFrame(tab)
        theme_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            theme_frame,
            text="テーマ設定",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        theme_container = ctk.CTkFrame(theme_frame, fg_color="transparent")
        theme_container.pack(anchor="w", padx=15, pady=(0, 15))

        ctk.CTkLabel(theme_container, text="外観モード:").pack(side="left")
        self.appearance_var = ctk.StringVar(value="ダーク")
        appearance_menu = ctk.CTkOptionMenu(
            theme_container,
            variable=self.appearance_var,
            values=["ダーク", "ライト", "システム"],
            command=self._on_appearance_changed
        )
        appearance_menu.pack(side="left", padx=(10, 0))

        # 通知設定
        notify_frame = ctk.CTkFrame(tab)
        notify_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            notify_frame,
            text="通知設定",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.show_notifications_var = ctk.BooleanVar()
        notify_cb = ctk.CTkCheckBox(
            notify_frame,
            text="デスクトップ通知を表示",
            variable=self.show_notifications_var,
            command=self._on_setting_changed
        )
        notify_cb.pack(anchor="w", padx=15, pady=(0, 10))

        # 通知タイミング
        timing_container = ctk.CTkFrame(notify_frame, fg_color="transparent")
        timing_container.pack(anchor="w", padx=15, pady=(0, 15))

        ctk.CTkLabel(timing_container, text="通知タイミング:").pack(side="left")
        self.notify_timing_var = ctk.StringVar(value="重要なイベント")
        timing_menu = ctk.CTkOptionMenu(
            timing_container,
            variable=self.notify_timing_var,
            values=["すべて", "重要なイベント", "エラーのみ", "なし"],
            command=self._on_setting_changed
        )
        timing_menu.pack(side="left", padx=(10, 0))

        # グラフ設定
        chart_frame = ctk.CTkFrame(tab)
        chart_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            chart_frame,
            text="グラフ表示設定",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.animated_charts_var = ctk.BooleanVar()
        animated_cb = ctk.CTkCheckBox(
            chart_frame,
            text="アニメーション効果を有効化",
            variable=self.animated_charts_var,
            command=self._on_setting_changed
        )
        animated_cb.pack(anchor="w", padx=15, pady=(0, 15))

    def _create_advanced_tab(self):
        """高度な設定タブの作成"""
        tab = self.settings_tabs.add("高度な設定")

        # パフォーマンス設定
        perf_frame = ctk.CTkFrame(tab)
        perf_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            perf_frame,
            text="パフォーマンス設定",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        # CPU使用率制限
        cpu_container = ctk.CTkFrame(perf_frame, fg_color="transparent")
        cpu_container.pack(anchor="w", padx=15, pady=(0, 10))

        ctk.CTkLabel(cpu_container, text="CPU使用率制限:").pack(side="left")
        self.cpu_limit_var = ctk.StringVar(value="標準")
        cpu_menu = ctk.CTkOptionMenu(
            cpu_container,
            variable=self.cpu_limit_var,
            values=["低", "標準", "高", "無制限"],
            command=self._on_setting_changed
        )
        cpu_menu.pack(side="left", padx=(10, 0))

        # メモリ使用量制限
        mem_container = ctk.CTkFrame(perf_frame, fg_color="transparent")
        mem_container.pack(anchor="w", padx=15, pady=(0, 15))

        ctk.CTkLabel(mem_container, text="メモリ使用量制限:").pack(side="left")
        self.memory_limit_var = ctk.StringVar(value="512MB")
        mem_menu = ctk.CTkOptionMenu(
            mem_container,
            variable=self.memory_limit_var,
            values=["256MB", "512MB", "1GB", "2GB", "無制限"],
            command=self._on_setting_changed
        )
        mem_menu.pack(side="left", padx=(10, 0))

        # データ管理設定
        data_frame = ctk.CTkFrame(tab)
        data_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            data_frame,
            text="データ管理",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        # データエクスポート
        export_container = ctk.CTkFrame(data_frame, fg_color="transparent")
        export_container.pack(anchor="w", padx=15, pady=(0, 10))

        export_btn = ctk.CTkButton(
            export_container,
            text="📤 データをエクスポート",
            command=self._export_data,
            width=150
        )
        export_btn.pack(side="left")

        # データインポート
        import_btn = ctk.CTkButton(
            export_container,
            text="📥 データをインポート",
            command=self._import_data,
            width=150
        )
        import_btn.pack(side="left", padx=(10, 0))

        # データクリア
        clear_container = ctk.CTkFrame(data_frame, fg_color="transparent")
        clear_container.pack(anchor="w", padx=15, pady=(0, 15))

        clear_btn = ctk.CTkButton(
            clear_container,
            text="🗑️ すべてのデータをクリア",
            command=self._clear_all_data,
            width=180,
            fg_color="red",
            hover_color="darkred"
        )
        clear_btn.pack(side="left")

    def _create_action_buttons(self):
        """保存・リセットボタンの作成"""
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")

        # 変更状態表示
        self.status_label = ctk.CTkLabel(
            button_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=15, pady=10)

        # ボタン
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(side="right", padx=15, pady=10)

        reset_btn = ctk.CTkButton(
            button_container,
            text="🔄 デフォルトに戻す",
            command=self._reset_to_defaults,
            width=140
        )
        reset_btn.pack(side="left", padx=(0, 10))

        self.save_btn = ctk.CTkButton(
            button_container,
            text="💾 設定を保存",
            command=self._save_settings,
            width=120
        )
        self.save_btn.pack(side="left")

    def _load_current_settings(self):
        """現在の設定値を読み込み"""
        try:
            # 設定値を各UIコンポーネントに設定
            # 実際の設定読み込み処理を実装
            pass
        except Exception as e:
            print(f"設定読み込みエラー: {e}")

    def _on_setting_changed(self, *args):
        """設定変更時のコールバック"""
        self.settings_changed = True
        self.status_label.configure(text="⚠️ 未保存の変更があります")
        self.save_btn.configure(fg_color="orange")

    def _on_appearance_changed(self, value):
        """外観モード変更時のコールバック"""
        appearance_map = {
            "ダーク": "dark",
            "ライト": "light",
            "システム": "system"
        }
        ctk.set_appearance_mode(appearance_map.get(value, "dark"))
        self._on_setting_changed()

    def _save_settings(self):
        """設定を保存"""
        try:
            # 実際の設定保存処理を実装
            settings_data = self._collect_settings()
            # self.config.save(settings_data)

            self.settings_changed = False
            self.status_label.configure(text="✅ 設定が保存されました")
            self.save_btn.configure(fg_color=["#3B8ED0", "#1F6AA5"])

        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存に失敗しました: {e}")

    def _reset_to_defaults(self):
        """設定をデフォルト値にリセット"""
        if messagebox.askyesno("確認", "すべての設定をデフォルト値に戻しますか？"):
            try:
                # デフォルト値の設定
                self._load_default_settings()
                self._on_setting_changed()

            except Exception as e:
                messagebox.showerror("エラー", f"設定のリセットに失敗しました: {e}")

    def _collect_settings(self) -> Dict[str, Any]:
        """現在のUI状態から設定データを収集"""
        return {
            'auto_start': self.auto_start_var.get(),
            'minimize_to_tray': self.minimize_to_tray_var.get(),
            'language': self.language_var.get(),
            'save_interval': self.save_interval_var.get(),
            'auto_backup': self.auto_backup_var.get(),
            'backup_days': self.backup_days_var.get(),
            'exclude_passwords': self.exclude_passwords_var.get(),
            'excluded_apps': self.excluded_apps.get("1.0", "end-1c"),
            'appearance': self.appearance_var.get(),
            'show_notifications': self.show_notifications_var.get(),
            'notify_timing': self.notify_timing_var.get(),
            'animated_charts': self.animated_charts_var.get(),
            'cpu_limit': self.cpu_limit_var.get(),
            'memory_limit': self.memory_limit_var.get()
        }

    def _load_default_settings(self):
        """デフォルト設定値を読み込み"""
        # デフォルト値の設定
        self.auto_start_var.set(False)
        self.minimize_to_tray_var.set(True)
        self.language_var.set("日本語")
        self.save_interval_var.set("5分")
        self.auto_backup_var.set(True)
        self.backup_days_var.set("30日")
        self.exclude_passwords_var.set(True)
        self.excluded_apps.delete("1.0", "end")
        self.excluded_apps.insert("1.0", "notepad.exe\ncalc.exe")
        self.appearance_var.set("ダーク")
        self.show_notifications_var.set(True)
        self.notify_timing_var.set("重要なイベント")
        self.animated_charts_var.set(True)
        self.cpu_limit_var.set("標準")
        self.memory_limit_var.set("512MB")

    def _export_data(self):
        """データエクスポート"""
        filename = filedialog.asksaveasfilename(
            title="データのエクスポート",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                # 実際のエクスポート処理を実装
                messagebox.showinfo("完了", f"データを {filename} にエクスポートしました。")
            except Exception as e:
                messagebox.showerror("エラー", f"エクスポートに失敗しました: {e}")

    def _import_data(self):
        """データインポート"""
        filename = filedialog.askopenfilename(
            title="データのインポート",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                # 実際のインポート処理を実装
                messagebox.showinfo("完了", f"{filename} からデータをインポートしました。")
            except Exception as e:
                messagebox.showerror("エラー", f"インポートに失敗しました: {e}")

    def _clear_all_data(self):
        """すべてのデータをクリア"""
        if messagebox.askyesno("警告",
                              "すべてのキーボード記録データが削除されます。\n"
                              "この操作は取り消せません。\n\n"
                              "本当に実行しますか？"):
            try:
                # 実際のデータクリア処理を実装
                messagebox.showinfo("完了", "すべてのデータをクリアしました。")
            except Exception as e:
                messagebox.showerror("エラー", f"データクリアに失敗しました: {e}")
