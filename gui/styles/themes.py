"""
テーマ管理システム

CustomTkinterのテーマとカラーパレットを管理
"""

import customtkinter as ctk
from typing import Dict, Any, Tuple


class ThemeManager:
    """テーマ管理クラス"""

    def __init__(self):
        """テーママネージャーの初期化"""
        self.current_theme = "dark"
        self.current_accent = "blue"

        # カラーパレット定義
        self.color_palettes = {
            "dark": {
                "bg_color": ["#212121", "#212121"],
                "fg_color": ["#2b2b2b", "#2b2b2b"],
                "text_color": ["#ffffff", "#ffffff"],
                "text_color_disabled": ["#6b6b6b", "#6b6b6b"],
                "button_color": ["#3B8ED0", "#1F6AA5"],
                "button_hover_color": ["#36719F", "#144870"],
                "entry_color": ["#343434", "#343434"],
                "frame_color": ["#2b2b2b", "#2b2b2b"],
                "scrollbar_color": ["#3B8ED0", "#1F6AA5"],
                "progress_color": ["#3B8ED0", "#1F6AA5"],
            },
            "light": {
                "bg_color": ["#f9f9fa", "#f9f9fa"],
                "fg_color": ["#f0f0f0", "#f0f0f0"],
                "text_color": ["#212121", "#212121"],
                "text_color_disabled": ["#909090", "#909090"],
                "button_color": ["#3B8ED0", "#1F6AA5"],
                "button_hover_color": ["#36719F", "#144870"],
                "entry_color": ["#ffffff", "#ffffff"],
                "frame_color": ["#f0f0f0", "#f0f0f0"],
                "scrollbar_color": ["#3B8ED0", "#1F6AA5"],
                "progress_color": ["#3B8ED0", "#1F6AA5"],
            }
        }

        # アクセントカラー定義
        self.accent_colors = {
            "blue": {
                "primary": ["#3B8ED0", "#1F6AA5"],
                "secondary": ["#36719F", "#144870"],
                "accent": "#4A9EE7"
            },
            "green": {
                "primary": ["#2FA572", "#105A2A"],
                "secondary": ["#238B5C", "#0F4F24"],
                "accent": "#32C574"
            },
            "orange": {
                "primary": ["#FF8C42", "#CC5A00"],
                "secondary": ["#E67A3A", "#B8520C"],
                "accent": "#FFA552"
            },
            "purple": {
                "primary": ["#8E44AD", "#5B2C6F"],
                "secondary": ["#7D3C98", "#4A235A"],
                "accent": "#A569BD"
            },
            "red": {
                "primary": ["#E74C3C", "#C0392B"],
                "secondary": ["#CB4335", "#A93226"],
                "accent": "#EC7063"
            }
        }

        # 特殊用途カラー
        self.status_colors = {
            "success": "#27AE60",
            "warning": "#F39C12",
            "error": "#E74C3C",
            "info": "#3498DB",
            "recording": "#E74C3C",
            "stopped": "#95A5A6"
        }

    def get_current_palette(self) -> Dict[str, Any]:
        """現在のカラーパレットを取得"""
        base_palette = self.color_palettes[self.current_theme].copy()
        accent_palette = self.accent_colors[self.current_accent]

        # アクセントカラーを適用
        base_palette["button_color"] = accent_palette["primary"]
        base_palette["button_hover_color"] = accent_palette["secondary"]
        base_palette["scrollbar_color"] = accent_palette["primary"]
        base_palette["progress_color"] = accent_palette["primary"]

        return base_palette

    def set_theme(self, theme: str):
        """テーマを変更"""
        if theme in self.color_palettes:
            self.current_theme = theme
            # CustomTkinterの外観モードを変更
            ctk.set_appearance_mode(theme)

    def set_accent_color(self, accent: str):
        """アクセントカラーを変更"""
        if accent in self.accent_colors:
            self.current_accent = accent

    def get_status_color(self, status: str) -> str:
        """ステータス用カラーを取得"""
        return self.status_colors.get(status, self.status_colors["info"])

    def get_chart_colors(self) -> list:
        """グラフ用カラーパレットを取得"""
        if self.current_theme == "dark":
            return [
                "#3B8ED0", "#2FA572", "#FF8C42", "#8E44AD", "#E74C3C",
                "#F39C12", "#1ABC9C", "#9B59B6", "#34495E", "#16A085"
            ]
        else:
            return [
                "#2980B9", "#27AE60", "#E67E22", "#8E44AD", "#C0392B",
                "#D68910", "#138D75", "#7D3C98", "#2C3E50", "#148F77"
            ]

    def apply_widget_theme(self, widget: ctk.CTkBaseClass, style_type: str = "default"):
        """ウィジェットにテーマを適用"""
        palette = self.get_current_palette()

        try:
            if style_type == "accent_button":
                widget.configure(
                    fg_color=palette["button_color"],
                    hover_color=palette["button_hover_color"]
                )
            elif style_type == "success_button":
                widget.configure(
                    fg_color=self.status_colors["success"],
                    hover_color="#229954"
                )
            elif style_type == "warning_button":
                widget.configure(
                    fg_color=self.status_colors["warning"],
                    hover_color="#D68910"
                )
            elif style_type == "error_button":
                widget.configure(
                    fg_color=self.status_colors["error"],
                    hover_color="#C0392B"
                )
            elif style_type == "recording_indicator":
                widget.configure(
                    fg_color=self.status_colors["recording"],
                    text_color="white"
                )
            elif style_type == "stopped_indicator":
                widget.configure(
                    fg_color=self.status_colors["stopped"],
                    text_color="white"
                )
        except Exception as e:
            print(f"テーマ適用エラー: {e}")

    def get_matplotlib_style(self) -> Dict[str, Any]:
        """matplotlib用のスタイル設定を取得"""
        if self.current_theme == "dark":
            return {
                'figure.facecolor': '#2b2b2b',
                'axes.facecolor': '#2b2b2b',
                'axes.edgecolor': '#ffffff',
                'axes.labelcolor': '#ffffff',
                'text.color': '#ffffff',
                'xtick.color': '#ffffff',
                'ytick.color': '#ffffff',
                'grid.color': '#555555',
                'grid.alpha': 0.3
            }
        else:
            return {
                'figure.facecolor': '#f0f0f0',
                'axes.facecolor': '#ffffff',
                'axes.edgecolor': '#000000',
                'axes.labelcolor': '#000000',
                'text.color': '#000000',
                'xtick.color': '#000000',
                'ytick.color': '#000000',
                'grid.color': '#cccccc',
                'grid.alpha': 0.5
            }


class CustomWidgets:
    """カスタムウィジェット定義"""

    @staticmethod
    def create_stat_card(parent, title: str, value: str, icon: str,
                        theme_manager: ThemeManager) -> ctk.CTkFrame:
        """統計カードウィジェットを作成"""
        card = ctk.CTkFrame(parent, corner_radius=10)

        # アイコン
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=28)
        )
        icon_label.pack(pady=(15, 5))

        # 値
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        value_label.pack()

        # タイトル
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12)
        )
        title_label.pack(pady=(0, 15))

        # 更新メソッドを追加
        def update_value(new_value: str):
            value_label.configure(text=new_value)

        card.update_value = update_value
        card.value_label = value_label

        return card

    @staticmethod
    def create_status_indicator(parent, text: str, status: str,
                               theme_manager: ThemeManager) -> ctk.CTkFrame:
        """ステータスインジケーターを作成"""
        indicator = ctk.CTkFrame(parent, corner_radius=20, height=40)

        status_color = theme_manager.get_status_color(status)

        # ステータスドット
        dot_label = ctk.CTkLabel(
            indicator,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color=status_color
        )
        dot_label.pack(side="left", padx=(10, 5), pady=10)

        # ステータステキスト
        text_label = ctk.CTkLabel(
            indicator,
            text=text,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        text_label.pack(side="left", padx=(0, 10), pady=10)

        # 更新メソッドを追加
        def update_status(new_text: str, new_status: str):
            text_label.configure(text=new_text)
            new_color = theme_manager.get_status_color(new_status)
            dot_label.configure(text_color=new_color)

        indicator.update_status = update_status

        return indicator

    @staticmethod
    def create_progress_card(parent, title: str, progress: float,
                            theme_manager: ThemeManager) -> ctk.CTkFrame:
        """進捗カードを作成"""
        card = ctk.CTkFrame(parent, corner_radius=10)

        # タイトル
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(15, 5))

        # 進捗バー
        progress_bar = ctk.CTkProgressBar(
            card,
            width=200,
            height=20
        )
        progress_bar.pack(pady=(5, 5))
        progress_bar.set(progress)

        # パーセンテージ表示
        percent_label = ctk.CTkLabel(
            card,
            text=f"{progress * 100:.1f}%",
            font=ctk.CTkFont(size=12)
        )
        percent_label.pack(pady=(0, 15))

        # 更新メソッドを追加
        def update_progress(new_progress: float):
            progress_bar.set(new_progress)
            percent_label.configure(text=f"{new_progress * 100:.1f}%")

        card.update_progress = update_progress

        return card


# テーマ設定のデフォルト値
DEFAULT_THEME_CONFIG = {
    "theme": "dark",
    "accent_color": "blue",
    "chart_animation": True,
    "transparency_effects": False,
    "high_contrast": False
}


def apply_global_theme(theme: str, accent: str = "blue"):
    """グローバルテーマを適用"""
    theme_manager = ThemeManager()
    theme_manager.set_theme(theme)
    theme_manager.set_accent_color(accent)

    # CustomTkinterの設定を更新
    ctk.set_appearance_mode(theme)

    return theme_manager
