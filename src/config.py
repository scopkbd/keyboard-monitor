"""
Configuration Management Module

キーボードモニターの設定を管理するモジュール
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """設定管理クラス"""

    DEFAULT_CONFIG = {
        "logging": {
            "data_file": "./data/keyboard_log.json",
            "backup_interval": 3600,  # 秒
            "auto_save": True,
            "save_interval": 300,  # 秒 (従来の設定、互換性のため残す)
            "idle_save_delay": 1.0,  # 入力停止後の保存遅延（秒）
            "continuous_save_interval": 300,  # 連続入力時の保存間隔（秒）
            "keystroke_batch_save": 100  # バッチ保存のキーストローク数（フォールバック）
        },
        "display": {
            "refresh_interval": 1.0,  # 秒
            "color_output": True,
            "show_realtime": True,
            "max_display_keys": 10
        },
        "privacy": {
            "exclude_passwords": True,
            "anonymize_data": False,
            "exclude_sensitive_apps": []
        },
        "analysis": {
            "track_modifiers": True
        },
        "system": {
            "log_level": "INFO",
            "max_log_size": 10485760,  # 10MB
            "max_log_files": 5
        }
    }

    def __init__(self, config_file: str = "config.json"):
        """
        設定管理クラスの初期化

        Args:
            config_file: 設定ファイルのパス
        """
        self.config_file = Path(config_file)
        self.config = self.DEFAULT_CONFIG.copy()
        self.logger = logging.getLogger(__name__)

        # 設定ファイルの読み込み
        self.load_config()

    def load_config(self) -> None:
        """設定ファイルを読み込む"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)

                # デフォルト設定をユーザー設定で更新
                self._merge_config(self.config, user_config)
                self.logger.info(f"設定ファイルを読み込みました: {self.config_file}")
            else:
                self.logger.info("設定ファイルが見つかりません。デフォルト設定を使用します。")
                self.save_config()  # デフォルト設定を保存

        except json.JSONDecodeError as e:
            self.logger.error(f"設定ファイルの形式が正しくありません: {e}")
            self.logger.info("デフォルト設定を使用します。")
        except Exception as e:
            self.logger.error(f"設定ファイルの読み込みに失敗しました: {e}")
            self.logger.info("デフォルト設定を使用します。")

    def save_config(self) -> None:
        """設定ファイルを保存する"""
        try:
            # 設定ディレクトリを作成
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            self.logger.info(f"設定ファイルを保存しました: {self.config_file}")

        except Exception as e:
            self.logger.error(f"設定ファイルの保存に失敗しました: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        設定値を取得する

        Args:
            key: ドット記法での設定キー（例: "logging.data_file"）
            default: デフォルト値

        Returns:
            設定値
        """
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        設定値を設定する

        Args:
            key: ドット記法での設定キー
            value: 設定値
        """
        keys = key.split('.')
        config_ref = self.config

        # 最後のキー以外をたどる
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]

        # 最後のキーに値を設定
        config_ref[keys[-1]] = value

        self.logger.info(f"設定を更新しました: {key} = {value}")

    def get_data_file_path(self) -> Path:
        """データファイルのパスを取得する"""
        return Path(self.get("logging.data_file"))

    def get_backup_interval(self) -> int:
        """バックアップ間隔（秒）を取得する"""
        return self.get("logging.backup_interval")

    def get_save_interval(self) -> int:
        """保存間隔（秒）を取得する"""
        return self.get("logging.save_interval")

    def get_idle_save_delay(self) -> float:
        """アイドル状態での保存遅延（秒）を取得する"""
        return self.get("logging.idle_save_delay")

    def get_continuous_save_interval(self) -> int:
        """連続入力時の保存間隔（秒）を取得する"""
        return self.get("logging.continuous_save_interval")

    def get_keystroke_batch_save(self) -> int:
        """バッチ保存のキーストローク数を取得する"""
        return self.get("logging.keystroke_batch_save")

    def is_auto_save_enabled(self) -> bool:
        """自動保存が有効かどうか"""
        return self.get("logging.auto_save")

    def get_display_refresh_interval(self) -> float:
        """表示更新間隔（秒）を取得する"""
        return self.get("display.refresh_interval")

    def is_color_output_enabled(self) -> bool:
        """カラー出力が有効かどうか"""
        return self.get("display.color_output")

    def is_realtime_display_enabled(self) -> bool:
        """リアルタイム表示が有効かどうか"""
        return self.get("display.show_realtime")

    def get_max_display_keys(self) -> int:
        """表示する最大キー数を取得する"""
        return self.get("display.max_display_keys")

    def is_modifier_tracking_enabled(self) -> bool:
        """モディファイアキー追跡が有効かどうか"""
        return self.get("analysis.track_modifiers")

    def get_log_level(self) -> str:
        """ログレベルを取得する"""
        return self.get("system.log_level")

    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> None:
        """
        設定をマージする（ユーザー設定がデフォルト設定を上書き）

        Args:
            default: デフォルト設定
            user: ユーザー設定
        """
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value

    def validate_config(self) -> bool:
        """
        設定の妥当性を検証する

        Returns:
            設定が妥当かどうか
        """
        try:
            # データファイルパスの検証
            data_file = self.get_data_file_path()
            data_file.parent.mkdir(parents=True, exist_ok=True)

            # 各種間隔の検証
            if self.get_backup_interval() <= 0:
                self.logger.warning("バックアップ間隔が無効です。デフォルト値を使用します。")
                self.set("logging.backup_interval", 3600)

            if self.get_save_interval() <= 0:
                self.logger.warning("保存間隔が無効です。デフォルト値を使用します。")
                self.set("logging.save_interval", 300)

            if self.get_display_refresh_interval() <= 0:
                self.logger.warning("表示更新間隔が無効です。デフォルト値を使用します。")
                self.set("display.refresh_interval", 1.0)

            return True

        except Exception as e:
            self.logger.error(f"設定の検証に失敗しました: {e}")
            return False

    def reset_to_default(self) -> None:
        """設定をデフォルトにリセットする"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
        self.logger.info("設定をデフォルトにリセットしました。")

    def export_config(self, file_path: str) -> None:
        """
        設定をファイルにエクスポートする

        Args:
            file_path: エクスポート先のファイルパス
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"設定をエクスポートしました: {file_path}")
        except Exception as e:
            self.logger.error(f"設定のエクスポートに失敗しました: {e}")

    def import_config(self, file_path: str) -> bool:
        """
        設定をファイルからインポートする

        Args:
            file_path: インポート元のファイルパス

        Returns:
            インポートが成功したかどうか
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            # 現在の設定にマージ
            self._merge_config(self.config, imported_config)
            self.save_config()

            self.logger.info(f"設定をインポートしました: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"設定のインポートに失敗しました: {e}")
            return False


# 設定管理インスタンスのシングルトン
_config_manager = None

def get_config() -> ConfigManager:
    """設定管理インスタンスを取得する"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
