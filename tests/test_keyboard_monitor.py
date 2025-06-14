"""
Test module for keyboard_monitor.py

キーボードモニターのメインアプリケーションのテスト
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# テスト対象モジュールをインポート
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import ConfigManager
from data_store import DataStore
from keyboard_monitor import KeyboardMonitor


class TestKeyboardMonitor(unittest.TestCase):
    """KeyboardMonitorクラスのテストケース"""

    def setUp(self):
        """テスト前の準備"""
        # 一時ディレクトリでテスト実行
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # テスト用ディレクトリを作成
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)

        # テスト用設定ファイルを作成
        self._create_test_config()

    def tearDown(self):
        """テスト後のクリーンアップ"""
        os.chdir(self.original_cwd)
        # 一時ディレクトリの削除は省略（安全のため）

    def _create_test_config(self):
        """テスト用設定ファイルを作成"""
        config_data = {
            "data_file": "data/test_keyboard_log.json",
            "log_level": "INFO",
            "auto_save": True,
            "auto_save_interval": 60,
            "realtime_display": False,
            "display_refresh_interval": 1.0
        }

        import json
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)

    @patch('keyboard_monitor.KeyboardLogger')
    @patch('keyboard_monitor.StatisticsAnalyzer')
    @patch('keyboard_monitor.DataStore')
    def test_init(self, mock_data_store, mock_analyzer, mock_logger):
        """初期化のテスト"""
        # アプリケーションの初期化
        app = KeyboardMonitor()

        # 初期化が正常に完了することを確認
        self.assertIsNotNone(app.config)
        self.assertIsNotNone(app.logger)
        self.assertIsNotNone(app.data_store)
        self.assertIsNotNone(app.keyboard_logger)
        self.assertIsNotNone(app.statistics_analyzer)
        self.assertFalse(app.cli_running)
        self.assertIsNone(app.display_thread)

    @patch('keyboard_monitor.KeyboardLogger')
    @patch('keyboard_monitor.StatisticsAnalyzer')
    @patch('keyboard_monitor.DataStore')
    def test_setup_logging(self, mock_data_store, mock_analyzer, mock_logger):
        """ロギング設定のテスト"""
        app = KeyboardMonitor()
        logger = app._setup_logging()

        # ロガーが正常に設定されることを確認
        self.assertEqual(logger.name, 'keyboard_monitor')
        self.assertTrue(len(logger.handlers) >= 2)  # コンソール + ファイル

    @patch('keyboard_monitor.KeyboardLogger')
    @patch('keyboard_monitor.StatisticsAnalyzer')
    @patch('keyboard_monitor.DataStore')
    def test_handle_start_command(self, mock_data_store, mock_analyzer, mock_logger):
        """startコマンドのテスト"""
        app = KeyboardMonitor()

        # モックの設定
        app.keyboard_logger.is_running.return_value = False
        app.keyboard_logger.start_logging.return_value = True

        # 標準出力をキャプチャ
        with patch('builtins.print') as mock_print:
            app._handle_start_command()

        # start_loggingが呼ばれることを確認
        app.keyboard_logger.start_logging.assert_called_once()

        # 成功メッセージが出力されることを確認
        mock_print.assert_called()

    @patch('keyboard_monitor.KeyboardLogger')
    @patch('keyboard_monitor.StatisticsAnalyzer')
    @patch('keyboard_monitor.DataStore')
    def test_handle_stop_command(self, mock_data_store, mock_analyzer, mock_logger):
        """stopコマンドのテスト"""
        app = KeyboardMonitor()

        # モックの設定
        app.keyboard_logger.is_running.return_value = True
        app.keyboard_logger.stop_logging.return_value = True

        # 標準出力をキャプチャ
        with patch('builtins.print') as mock_print:
            app._handle_stop_command()

        # stop_loggingが呼ばれることを確認
        app.keyboard_logger.stop_logging.assert_called_once()

        # 成功メッセージが出力されることを確認
        mock_print.assert_called()

    @patch('keyboard_monitor.KeyboardLogger')
    @patch('keyboard_monitor.StatisticsAnalyzer')
    @patch('keyboard_monitor.DataStore')
    def test_handle_status_command(self, mock_data_store, mock_analyzer, mock_logger):
        """statusコマンドのテスト"""
        app = KeyboardMonitor()

        # モックデータの設定
        mock_status = {
            'is_logging': False,
            'session_stats': {}
        }
        mock_real_time_stats = {
            'total': {
                'total_keystrokes': 0,
                'first_record_date': None,
                'last_record_date': None
            }
        }

        app.keyboard_logger.get_status.return_value = mock_status
        app.keyboard_logger.get_real_time_statistics.return_value = mock_real_time_stats

        # 標準出力をキャプチャ
        with patch('builtins.print') as mock_print:
            app._handle_status_command()

        # get_statusとget_real_time_statisticsが呼ばれることを確認
        app.keyboard_logger.get_status.assert_called_once()
        app.keyboard_logger.get_real_time_statistics.assert_called_once()

        # ステータス情報が出力されることを確認
        mock_print.assert_called()

    @patch('keyboard_monitor.KeyboardLogger')
    @patch('keyboard_monitor.StatisticsAnalyzer')
    @patch('keyboard_monitor.DataStore')
    def test_handle_stats_command(self, mock_data_store, mock_analyzer, mock_logger):
        """statsコマンドのテスト"""
        app = KeyboardMonitor()

        # モックデータの設定
        mock_basic_stats = {
            'total_keystrokes': 1000,
            'recording_days': 7,
            'average_keystrokes_per_day': 142.9,
            'unique_keys': 26
        }

        mock_top_keys = [
            {'key_name': 'A', 'count': 100, 'percentage': 10.0, 'progress_bar': '████████'}
        ]

        mock_modifier_analysis = {
            'combinations': [
                {'display_name': 'None', 'count': 800, 'percentage': 80.0, 'progress_bar': '████████'}
            ]
        }

        mock_sequence_analysis = {
            'top_sequences': [
                {'sequence': 'TH', 'count': 50, 'percentage': 5.0, 'progress_bar': '████'}
            ]
        }

        app.statistics_analyzer.get_basic_statistics.return_value = mock_basic_stats
        app.statistics_analyzer.get_top_keys_analysis.return_value = mock_top_keys
        app.statistics_analyzer.get_modifier_analysis.return_value = mock_modifier_analysis
        app.statistics_analyzer.get_sequence_analysis.return_value = mock_sequence_analysis

        # 標準出力をキャプチャ
        with patch('builtins.print') as mock_print:
            app._handle_stats_command()

        # 各統計メソッドが呼ばれることを確認
        app.statistics_analyzer.get_basic_statistics.assert_called_once()
        app.statistics_analyzer.get_top_keys_analysis.assert_called_once_with(limit=10)
        app.statistics_analyzer.get_modifier_analysis.assert_called_once()
        app.statistics_analyzer.get_sequence_analysis.assert_called_once_with('bigrams', limit=5)

        # 統計情報が出力されることを確認
        mock_print.assert_called()

    @patch('keyboard_monitor.KeyboardLogger')
    @patch('keyboard_monitor.StatisticsAnalyzer')
    @patch('keyboard_monitor.DataStore')
    def test_cleanup(self, mock_data_store, mock_analyzer, mock_logger):
        """クリーンアップ処理のテスト"""
        app = KeyboardMonitor()
        app.cli_running = True
        app.keyboard_logger.is_running.return_value = True

        app._cleanup()

        # cli_runningがFalseになることを確認
        self.assertFalse(app.cli_running)

        # stop_loggingが呼ばれることを確認
        app.keyboard_logger.stop_logging.assert_called_once()

    @patch('keyboard_monitor.KeyboardLogger')
    @patch('keyboard_monitor.StatisticsAnalyzer')
    @patch('keyboard_monitor.DataStore')
    def test_get_welcome_message(self, mock_data_store, mock_analyzer, mock_logger):
        """ウェルカムメッセージ生成のテスト"""
        app = KeyboardMonitor()
        message = app._get_welcome_message()

        # ウェルカムメッセージに必要な要素が含まれることを確認
        self.assertIn('キーボードモニター', message)
        self.assertIn('v1.0', message)
        self.assertIn('start', message)
        self.assertIn('quit', message)


class TestKeyboardMonitorIntegration(unittest.TestCase):
    """統合テスト"""

    def setUp(self):
        """テスト前の準備"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # テスト用ディレクトリを作成
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        os.chdir(self.original_cwd)

    @patch('keyboard_monitor.input', side_effect=['help', 'quit'])
    @patch('keyboard_monitor.KeyboardLogger')
    @patch('keyboard_monitor.StatisticsAnalyzer')
    @patch('keyboard_monitor.DataStore')
    def test_cli_command_loop(self, mock_data_store, mock_analyzer, mock_logger, mock_input):
        """CLIコマンドループの統合テスト"""
        # テスト用設定ファイルを作成
        config_data = {
            "data_file": "data/test_keyboard_log.json",
            "log_level": "INFO",
            "auto_save": True,
            "realtime_display": False
        }

        import json
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)

        app = KeyboardMonitor()
        app.cli_running = True

        # 標準出力をキャプチャ
        with patch('builtins.print'):
            app._cli_command_loop()

        # cli_runningがFalseになることを確認（quitで終了）
        self.assertFalse(app.cli_running)


if __name__ == '__main__':
    # テストスイートの実行
    unittest.main(verbosity=2)
