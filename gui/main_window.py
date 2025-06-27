"""
GUI Main Application

キーボードモニター GUI版のメインアプリケーション
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    import tkinter as tk
    from tkinter import messagebox

    import customtkinter as ctk
except ImportError as e:
    print(f"GUI依存関係が不足しています: {e}")
    print("以下のコマンドで依存関係をインストールしてください:")
    print("pip install -r requirements-gui.txt")
    sys.exit(1)

from statistics import StatisticsAnalyzer

from components.analytics.analytics_page import AnalyticsPage
# GUIコンポーネントのインポート
from components.dashboard import Dashboard
from components.settings_panel import SettingsPanel
from styles.themes import ThemeManager

# 既存のバックエンドモジュールをインポート
from config import get_config
from data_store import DataStore
from logger import KeyboardLogger
from save_manager import SaveManager


class KeyboardMonitorGUI:
    """キーボードモニター GUI メインクラス"""

    def __init__(self):
        """GUIアプリケーションの初期化"""
        # アプリケーションユーザーモデルIDを設定（タスクバー識別用）
        self._set_app_user_model_id()

        # CustomTkinter の外観設定
        ctk.set_appearance_mode("dark")  # デフォルトはダークモード
        ctk.set_default_color_theme("blue")

        # メインウィンドウの作成
        self.root = ctk.CTk()
        self.root.title("キーボードモニター")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # アプリケーションアイコンの設定
        try:
            # CustomTkinterのアイコンファイルを使用
            import customtkinter as ctk_module
            ctk_directory = os.path.dirname(ctk_module.__file__)
            icon_path = os.path.join(ctk_directory, "assets", "icons", "CustomTkinter_icon_Windows.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                print(f"アイコン設定成功: {icon_path}")

                # Windows固有の追加設定でタスクバーアイコンを強制更新
                self._set_taskbar_icon(icon_path)
            else:
                print(f"アイコンファイルが見つかりません: {icon_path}")
        except Exception as e:
            print(f"アイコン設定エラー: {e}")
            # フォールバック: コメントアウトされた元の設定
            # self.root.iconbitmap("gui/styles/icons/app_icon.ico")

        # バックエンドコンポーネントの初期化
        self.config = get_config()
        self.data_store = DataStore(str(self.config.get_data_file_path()))
        self.keyboard_logger = KeyboardLogger(self.data_store)
        self.save_manager = SaveManager(self.config, self.data_store)
        self.statistics_analyzer = StatisticsAnalyzer(self.data_store)

        # テーマ管理
        self.theme_manager = ThemeManager()

        # GUI初期化
        self._setup_ui()
        self._setup_bindings()

        # 現在のページ
        self.current_page = None

        # アプリケーションユーザーモデルIDの設定
        self._set_app_user_model_id()

    def _setup_ui(self):
        """UI要素のセットアップ"""
        # メインフレームの構成
        self._create_sidebar()
        self._create_main_content()
        self._create_status_bar()

        # デフォルトページの表示
        self.show_dashboard()

    def _create_sidebar(self):
        """サイドバーの作成"""
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_rowconfigure(4, weight=1)  # 空きスペース

        # ロゴ/タイトル
        title = ctk.CTkLabel(
            self.sidebar,
            text="キーボード\nモニター",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 30))

        # ナビゲーションボタン
        self.nav_buttons = {}

        # ダッシュボード
        dashboard_btn = ctk.CTkButton(
            self.sidebar,
            text="🏠 ダッシュボード",
            command=self.show_dashboard,
            height=40,
            anchor="w"
        )
        dashboard_btn.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.nav_buttons['dashboard'] = dashboard_btn

        # 統合分析
        stats_btn = ctk.CTkButton(
            self.sidebar,
            text="📊 統合分析",
            command=self.show_statistics,
            height=40,
            anchor="w"
        )
        stats_btn.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.nav_buttons['statistics'] = stats_btn

        # 設定
        settings_btn = ctk.CTkButton(
            self.sidebar,
            text="⚙️ 設定",
            command=self.show_settings,
            height=40,
            anchor="w"
        )
        settings_btn.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.nav_buttons['settings'] = settings_btn

    def _create_main_content(self):
        """メインコンテンツエリアの作成"""
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # グリッド設定
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def _create_status_bar(self):
        """ステータスバーの作成"""
        self.status_frame = ctk.CTkFrame(self.root, height=30)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=0)

        # ステータス情報
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="準備完了",
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # 記録状態表示
        self.recording_status = ctk.CTkLabel(
            self.status_frame,
            text="● 停止中",
            text_color="red",
            anchor="e"
        )
        self.recording_status.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        self.status_frame.grid_columnconfigure(0, weight=1)

    def _setup_bindings(self):
        """イベントバインディングの設定"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_dashboard(self):
        """ダッシュボード画面の表示"""
        self._clear_main_content()
        self.current_page = Dashboard(
            self.main_frame,
            self.keyboard_logger,
            self.statistics_analyzer
        )
        self.current_page.pack(fill="both", expand=True)
        self._highlight_nav_button('dashboard')
        self.update_status("ダッシュボード表示中")

    def show_statistics(self):
        """統計・分析画面の表示"""
        self._clear_main_content()

        # データファイルパスを取得
        data_file_path = self.data_store.data_file

        # 統合分析ページを作成
        self.current_page = AnalyticsPage(
            self.main_frame,
            data_file_path=str(data_file_path)
        )
        self.current_page.pack(fill="both", expand=True)
        self._highlight_nav_button('statistics')
        self.update_status("統合分析ページ表示中")

    def show_settings(self):
        """設定画面の表示"""
        self._clear_main_content()
        self.current_page = SettingsPanel(
            self.main_frame,
            self.config
        )
        self.current_page.pack(fill="both", expand=True)
        self._highlight_nav_button('settings')
        self.update_status("設定画面表示中")

    def _clear_main_content(self):
        """メインコンテンツエリアのクリア"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def _highlight_nav_button(self, active_button):
        """ナビゲーションボタンのハイライト"""
        for name, button in self.nav_buttons.items():
            if name == active_button:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color=("gray90", "gray20"))

    def update_status(self, message):
        """ステータスバーの更新"""
        self.status_label.configure(text=message)

    def update_recording_status(self, is_recording):
        """記録状態の更新"""
        if is_recording:
            self.recording_status.configure(text="● 記録中", text_color="green")
        else:
            self.recording_status.configure(text="● 停止中", text_color="red")

    def on_closing(self):
        """アプリケーション終了時の処理"""
        if messagebox.askokcancel("終了確認", "アプリケーションを終了しますか？"):
            # バックエンドの清理
            if self.keyboard_logger.is_running():
                self.keyboard_logger.stop_logging()
            self.save_manager.stop()

            # ウィンドウを閉じる
            self.root.destroy()

    def _set_taskbar_icon(self, icon_path):
        """Windows固有のタスクバーアイコン設定"""
        try:
            import ctypes

            # ウィンドウが作成されるまで待機
            self.root.update()

            # ウィンドウハンドルを取得
            hwnd = self.root.winfo_id()

            # User32.dllとShell32.dllを読み込み
            user32 = ctypes.windll.user32
            shell32 = ctypes.windll.shell32

            # アイコンハンドルを取得
            hinstance = ctypes.windll.kernel32.GetModuleHandleW(None)
            icon_handle = shell32.ExtractIconW(hinstance, icon_path, 0)

            if icon_handle and icon_handle != 1:
                # ウィンドウアイコンを設定（タスクバーに反映される）
                WM_SETICON = 0x0080
                ICON_SMALL = 0
                ICON_BIG = 1

                # 小アイコン（タスクバー用）と大アイコン（ウィンドウ用）を設定
                user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, icon_handle)
                user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, icon_handle)

                print(f"タスクバーアイコン設定成功")
            else:
                print(f"アイコンハンドル取得失敗: {icon_handle}")

        except Exception as e:
            print(f"タスクバーアイコン設定エラー: {e}")

    def _set_app_user_model_id(self):
        """アプリケーションユーザーモデルIDを設定してタスクバーでの識別を改善"""
        try:
            import ctypes

            # アプリケーション固有のIDを設定
            app_id = "KeyboardMonitor.GUI.Application"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            print(f"AppUserModelID設定: {app_id}")

        except Exception as e:
            print(f"AppUserModelID設定エラー: {e}")

    def run(self):
        """GUIアプリケーションの実行"""
        self.root.mainloop()


def main():
    """メイン関数"""
    print("🚀 キーボードモニター - 統合分析ダッシュボード起動中...")
    print("📊 統合分析機能: 有効")

    try:
        app = KeyboardMonitorGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("エラー", f"アプリケーション開始エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
