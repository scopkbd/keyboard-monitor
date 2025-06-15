"""
Keyboard Monitor - Main Application

キーボードモニターのメインアプリケーション
"""

import argparse
import logging
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# プロジェクトのsrcディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from colorama import Back, Fore, Style, init
    init()  # Windows での色出力を有効化
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # カラー出力をダミー関数で置き換え
    class DummyColor:
        def __getattr__(self, name):
            return ""
    Fore = Back = Style = DummyColor()

# プロジェクトモジュールのインポート（リネーム後）
from analyzer import StatisticsAnalyzer
from config import ConfigManager, get_config
from data_store import DataStore
from logger import KeyboardLogger
from save_manager import SaveManager


class KeyboardMonitor:
    """キーボードモニターメインクラス"""

    def __init__(self):
        """アプリケーションの初期化"""
        self.config = get_config()
        self.logger = self._setup_logging()

        # データストレージの初期化
        data_file = self.config.get_data_file_path()
        self.data_store = DataStore(str(data_file))

        # キーボードロガーの初期化
        self.keyboard_logger = KeyboardLogger(self.data_store)

        # 統計分析器の初期化
        self.statistics_analyzer = StatisticsAnalyzer(self.data_store)

        # 保存管理器の初期化
        self.save_manager = SaveManager(self.config, self.data_store, self.logger)

        # CLI関連の状態
        self.cli_running = False
        self.input_in_progress = False  # 入力中フラグ
        self.display_thread: Optional[threading.Thread] = None

        # コールバックの設定
        self.keyboard_logger.set_callbacks(
            on_statistics_update=self._on_statistics_update
        )

        self.logger.info("キーボードモニターを初期化しました")

    def _setup_logging(self) -> logging.Logger:
        """ロギングの設定"""
        log_level = getattr(logging, self.config.get_log_level().upper(), logging.INFO)

        # ログディレクトリの作成
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # ロガーの設定
        logger = logging.getLogger('keyboard_monitor')
        logger.setLevel(log_level)

        # コンソールハンドラ
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # ファイルハンドラ
        file_handler = logging.FileHandler(
            log_dir / "keyboard_monitor.log",
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)

        # フォーマッタ
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # ハンドラを追加
        if not logger.handlers:
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

        return logger

    def start_cli_mode(self) -> None:
        """CLIインタラクティブモードを開始"""
        # 初期画面をクリア
        os.system('cls' if os.name == 'nt' else 'clear')

        print(self._get_welcome_message())

        # リアルタイム表示が有効な場合の説明
        if self.config.is_realtime_display_enabled():
            print(f"{Fore.GREEN}リアルタイム表示が有効です。コマンド入力中は表示更新が一時停止します。{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}注意: 'start'コマンドでキーロギングを開始すると画面上部に統計が表示されます。{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.YELLOW}リアルタイム表示は無効です。'config set realtime_display true'で有効にできます。{Style.RESET_ALL}\n")

        self.cli_running = True

        # リアルタイム表示スレッドを開始
        if self.config.is_realtime_display_enabled():
            self.display_thread = threading.Thread(
                target=self._display_loop,
                daemon=True
            )
            self.display_thread.start()

        try:
            self._cli_command_loop()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Ctrl+Cが検出されました。終了処理中...{Style.RESET_ALL}")
            self.cli_running = False
        except Exception as e:
            print(f"\n{Fore.RED}予期しないエラーが発生しました: {e}{Style.RESET_ALL}")
            self.logger.error(f"CLI mode error: {e}")
            self.cli_running = False
        finally:
            self._cleanup()

    def _cli_command_loop(self) -> None:
        """CLIコマンドループ（表示に干渉しない入力処理）"""
        while self.cli_running:
            try:
                # 入力開始前にフラグを設定
                self.input_in_progress = True
                command = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip().lower()
                # 入力完了後にフラグをクリア
                self.input_in_progress = False

                if not command:
                    continue

                if command in ['quit', 'q', 'exit']:
                    print(f"{Fore.GREEN}アプリケーションを終了します...{Style.RESET_ALL}")
                    self.cli_running = False
                    break
                elif command in ['start', 's']:
                    self._handle_start_command()
                elif command in ['stop', 't']:
                    self._handle_stop_command()
                elif command in ['status', 'st']:
                    self._handle_status_command()
                elif command in ['stats', 'stat']:
                    self._handle_stats_command()
                elif command in ['help', 'h']:
                    self._handle_help_command()
                elif command.startswith('config'):
                    self._handle_config_command(command)
                else:
                    print(f"{Fore.RED}不明なコマンド: {command}{Style.RESET_ALL}")
                    print("'help' でコマンド一覧を表示できます。")

            except EOFError:
                print(f"\n{Fore.GREEN}EOFが検出されました。アプリケーションを終了します...{Style.RESET_ALL}")
                self.input_in_progress = False
                self.cli_running = False
                break
            except KeyboardInterrupt:
                print(f"\n{Fore.GREEN}Ctrl+Cが検出されました。アプリケーションを終了します...{Style.RESET_ALL}")
                self.input_in_progress = False
                self.cli_running = False
                break
            except Exception as e:
                self.input_in_progress = False
                self.logger.error(f"コマンド処理中にエラーが発生しました: {e}")
                print(f"{Fore.RED}エラーが発生しました: {e}{Style.RESET_ALL}")

    def _handle_start_command(self) -> None:
        """startコマンドの処理"""
        if self.keyboard_logger.is_running():
            print(f"{Fore.YELLOW}キーロギングは既に開始されています{Style.RESET_ALL}")
        else:
            if self.keyboard_logger.start_logging():
                # 保存管理も開始
                self.save_manager.start()
                print(f"{Fore.GREEN}キーロギングを開始しました{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}キーロギングの開始に失敗しました{Style.RESET_ALL}")

    def _handle_stop_command(self) -> None:
        """stopコマンドの処理"""
        if not self.keyboard_logger.is_running():
            print(f"{Fore.YELLOW}キーロギングは開始されていません{Style.RESET_ALL}")
        else:
            if self.keyboard_logger.stop_logging():
                # 保存管理も停止
                self.save_manager.stop()
                print(f"{Fore.GREEN}キーロギングを停止しました{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}キーロギングの停止に失敗しました{Style.RESET_ALL}")

    def _handle_status_command(self) -> None:
        """statusコマンドの処理"""
        status = self.keyboard_logger.get_status()
        real_time_stats = self.keyboard_logger.get_real_time_statistics()

        print(f"\n{Fore.CYAN}=== システムステータス ==={Style.RESET_ALL}")

        # ロギング状態
        if status['is_logging']:
            print(f"状態: {Fore.GREEN}[記録中]{Style.RESET_ALL}")
        else:
            print(f"状態: {Fore.RED}[停止中]{Style.RESET_ALL}")

        # セッション統計
        session_stats = status['session_stats']
        if session_stats.get('start_time'):
            print(f"開始時刻: {session_stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"セッションキーストローク: {session_stats['keystrokes']:,} 回")

            if 'elapsed_time' in session_stats:
                elapsed = session_stats['elapsed_time']
                print(f"経過時間: {elapsed}")        # 総統計
        total_stats = real_time_stats['total']
        print(f"総キーストローク: {total_stats['total_keystrokes']:,} 回")

        if total_stats['first_record_date']:
            print(f"記録期間: {total_stats['first_record_date']} ～ {total_stats['last_record_date']}")

        print()

    def _handle_stats_command(self) -> None:
        """statsコマンドの処理"""
        print(f"\n{Fore.CYAN}=== キーボード使用統計 ==={Style.RESET_ALL}")

        # 基本統計
        basic_stats = self.statistics_analyzer.get_basic_statistics()
        print(f"総キーストローク: {basic_stats['total_keystrokes']:,} 回")
        print(f"記録期間: {basic_stats['recording_days']} 日")
        print(f"1日平均: {basic_stats['average_keystrokes_per_day']:.1f} 回")
        print(f"ユニークキー数: {basic_stats['unique_keys']} 個")

        # 上位キー
        print(f"\n{Fore.YELLOW}使用頻度上位キー:{Style.RESET_ALL}")
        top_keys = self.statistics_analyzer.get_top_keys_analysis(limit=10)

        for i, key in enumerate(top_keys, 1):
            progress_bar = key['progress_bar']
            print(f"  {i:2}. {key['key_name']:8}: {key['count']:6,} 回 "
                  f"({key['percentage']:5.1f}%) {Fore.GREEN}{progress_bar}{Style.RESET_ALL}")

        # モディファイア分析
        print(f"\n{Fore.YELLOW}モディファイア組み合わせ:{Style.RESET_ALL}")
        modifier_analysis = self.statistics_analyzer.get_modifier_analysis()

        for combo in modifier_analysis['combinations'][:5]:
            progress_bar = combo['progress_bar']
            print(f"  {combo['display_name']:15}: {combo['count']:6,} 回 "
                  f"({combo['percentage']:5.1f}%) {Fore.BLUE}{progress_bar}{Style.RESET_ALL}")

        # シーケンス分析
        print(f"\n{Fore.YELLOW}頻出シーケンス (Bigram):{Style.RESET_ALL}")
        bigram_analysis = self.statistics_analyzer.get_sequence_analysis('bigrams', limit=5)

        for seq in bigram_analysis['top_sequences']:
            progress_bar = seq['progress_bar']
            print(f"  {seq['sequence']:8}: {seq['count']:4,} 回 "
                  f"({seq['percentage']:5.1f}%) {Fore.MAGENTA}{progress_bar}{Style.RESET_ALL}")

        print()

    def _handle_help_command(self) -> None:
        """helpコマンドの処理"""
        print(f"\n{Fore.CYAN}=== 利用可能なコマンド ==={Style.RESET_ALL}")
        print(f"  {Fore.GREEN}start, s{Style.RESET_ALL}     : キーボード記録開始")
        print(f"  {Fore.GREEN}stop, t{Style.RESET_ALL}      : キーボード記録停止")
        print(f"  {Fore.GREEN}status, st{Style.RESET_ALL}   : 現在の状況表示")
        print(f"  {Fore.GREEN}stats, stat{Style.RESET_ALL}  : 統計情報表示")
        print(f"  {Fore.GREEN}help, h{Style.RESET_ALL}      : このヘルプを表示")
        print(f"  {Fore.GREEN}quit, q{Style.RESET_ALL}      : アプリケーション終了")
        print()

    def _handle_config_command(self, command: str) -> None:
        """configコマンドの処理"""
        parts = command.split()
        if len(parts) < 2:
            print(f"{Fore.RED}使用方法: config <get|set> [key] [value]{Style.RESET_ALL}")
            return

        action = parts[1]

        if action == 'get' and len(parts) == 3:
            key = parts[2]
            value = self.config.get(key)
            print(f"{key}: {value}")
        elif action == 'set' and len(parts) == 4:
            key = parts[2]
            value = parts[3]
            # 型変換を試行
            try:
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif '.' in value and all(part.isdigit() for part in value.split('.')):
                    value = float(value)
            except ValueError:
                pass

            self.config.set(key, value)
            self.config.save_config()
            print(f"{Fore.GREEN}設定を更新しました: {key} = {value}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}使用方法: config <get|set> [key] [value]{Style.RESET_ALL}")

    def _display_loop(self) -> None:
        """リアルタイム表示ループ（入力に干渉しない）"""
        last_display_lines = 0

        while self.cli_running:
            if self.keyboard_logger.is_running() and not self.input_in_progress:
                # 以前の表示をクリア（カーソル位置制御を使用）
                if last_display_lines > 0:
                    # カーソルを上に移動して前の表示を上書き
                    print(f"\033[{last_display_lines}A", end="")

                # 新しい表示を生成
                display_content = self._get_real_time_display()
                print(display_content)

                # 表示行数をカウント
                last_display_lines = display_content.count('\n') + 1

            elif not self.keyboard_logger.is_running():
                # ロギングが停止している場合は画面クリア
                if last_display_lines > 0:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    last_display_lines = 0

            time.sleep(self.config.get_display_refresh_interval())

    def _get_real_time_display(self) -> str:
        """リアルタイム表示文字列を生成（固定サイズ）"""
        status = self.keyboard_logger.get_status()
        real_time_stats = self.keyboard_logger.get_real_time_statistics()

        display = []
        display.append(f"{Fore.CYAN}{'='*50}")
        display.append(f"   キーボードモニター v1.0 - リアルタイム表示")
        display.append(f"{'='*50}{Style.RESET_ALL}")
        display.append("")

        # 状態表示
        if status['is_logging']:
            display.append(f"状態: {Fore.GREEN}[記録中]{Style.RESET_ALL}")
        else:
            display.append(f"状態: {Fore.RED}[停止中]{Style.RESET_ALL}")

        # セッション統計（固定行数）
        session_stats = status['session_stats']
        if session_stats.get('start_time'):
            display.append(f"開始時刻: {session_stats['start_time'].strftime('%H:%M:%S')}")

            if 'elapsed_time' in session_stats:
                elapsed = session_stats['elapsed_time']
                hours, remainder = divmod(elapsed.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                display.append(f"経過時間: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
            else:
                display.append("経過時間: --:--:--")

            display.append(f"セッション: {session_stats['keystrokes']:,} 回")

            if session_stats.get('last_key'):
                display.append(f"最後のキー: {session_stats['last_key']}")
            else:
                display.append("最後のキー: なし")
        else:
            display.append("開始時刻: 未開始")
            display.append("経過時間: --:--:--")
            display.append("セッション: 0 回")
            display.append("最後のキー: なし")

        # 総統計
        total_stats = real_time_stats['total']
        display.append(f"総キーストローク: {total_stats['total_keystrokes']:,} 回")

        # 上位キー（固定5行）
        display.append("")
        display.append(f"{Fore.YELLOW}使用頻度上位キー:{Style.RESET_ALL}")

        top_keys = real_time_stats['top_keys'][:5]
        for i in range(5):
            if i < len(top_keys):
                key = top_keys[i]
                display.append(f"  {i+1}. {key['key_name']:8}: {key['count']:6,} 回")
            else:
                display.append(f"  {i+1}. {'':8}  {'':6}   ")

        # コマンドヘルプ（固定行）
        display.append("")
        display.append(f"{Fore.CYAN}コマンド: start, stop, stats, quit{Style.RESET_ALL}")
        display.append("")  # 余白行

        display.append("")
        display.append(f"{Fore.CYAN}コマンド: start, stop, stats, quit{Style.RESET_ALL}")

        return "\n".join(display)

    def _get_welcome_message(self) -> str:
        """ウェルカムメッセージを生成"""
        return f"""
{Fore.CYAN}{'='*50}
   キーボードモニター v1.0
   キーボード入力パターン分析ツール
{'='*50}{Style.RESET_ALL}

{Fore.GREEN}✨ 改善版: リアルタイム表示とコマンド入力の統合{Style.RESET_ALL}

使用方法:
  • 'start' または 's' : キーボード記録開始
  • 'stop' または 't'  : キーボード記録停止
  • 'stats'           : 統計情報表示
  • 'help'            : ヘルプ表示
  • 'quit' または 'q'  : 終了

{Fore.CYAN}💡 新機能:{Style.RESET_ALL}
  • コマンド入力中は表示更新が自動停止
  • 'q' や 't' などの短いコマンドも正常に動作
  • 画面全体をクリアせずに表示更新

{Fore.YELLOW}注意: 管理者権限が必要な場合があります{Style.RESET_ALL}
"""

    def _on_statistics_update(self, session_stats: Dict[str, Any]) -> None:
        """統計更新時のコールバック"""
        # 新しい保存管理システムを使用
        if self.config.is_auto_save_enabled():
            self.save_manager.on_keystroke(session_stats)

    def _cleanup(self) -> None:
        """クリーンアップ処理"""
        print(f"{Fore.YELLOW}クリーンアップ処理中...{Style.RESET_ALL}")

        # フラグを確実に停止
        self.cli_running = False

        # キーボード記録が動作中なら停止
        if self.keyboard_logger and self.keyboard_logger.is_running():
            print(f"{Fore.YELLOW}キーボード記録を停止中...{Style.RESET_ALL}")
            self.keyboard_logger.stop_logging()

        # 保存管理の停止
        if self.save_manager:
            print(f"{Fore.YELLOW}保存管理を停止中...{Style.RESET_ALL}")
            self.save_manager.stop()

        # 表示スレッドの停止を待つ
        if hasattr(self, 'display_thread') and self.display_thread and self.display_thread.is_alive():
            print(f"{Fore.YELLOW}表示スレッドの停止を待機中...{Style.RESET_ALL}")
            self.display_thread.join(timeout=2.0)

        print(f"{Fore.GREEN}クリーンアップ完了{Style.RESET_ALL}")
        self.logger.info("アプリケーションを終了します")

    def show_statistics(self, date_filter: Optional[str] = None) -> None:
        """統計情報を表示（非インタラクティブモード用）"""
        report = self.statistics_analyzer.get_comprehensive_report()

        print(f"{Fore.CYAN}{'='*50}")
        print(f"   キーボード使用統計レポート")
        print(f"{'='*50}{Style.RESET_ALL}")

        basic = report['basic_statistics']
        print(f"\n基本統計:")
        print(f"  総キーストローク数: {basic['total_keystrokes']:,}")
        print(f"  記録期間: {basic['recording_days']} 日")
        print(f"  1日平均: {basic['average_keystrokes_per_day']:.1f} 回")

        print(f"\n{Fore.YELLOW}使用頻度上位キー:{Style.RESET_ALL}")
        for i, key in enumerate(report['top_keys'], 1):
            print(f"  {i:2}. {key['key_name']:8}: {key['count']:6,} 回 ({key['percentage']:5.1f}%)")

        print(f"\n{Fore.YELLOW}改善提案:{Style.RESET_ALL}")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")

        print(f"\nレポート生成日時: {report['generated_at']}")

    def show_status(self) -> None:
        """ステータス情報を表示（非インタラクティブモード用）"""
        basic_stats = self.statistics_analyzer.get_basic_statistics()

        print(f"{Fore.CYAN}{'='*50}")
        print(f"   システムステータス")
        print(f"{'='*50}{Style.RESET_ALL}")

        print(f"データファイル: {self.config.get_data_file_path()}")
        print(f"総キーストローク: {basic_stats['total_keystrokes']:,} 回")
        print(f"記録期間: {basic_stats['recording_days']} 日")

        if basic_stats['first_record_date']:
            print(f"最初の記録: {basic_stats['first_record_date']}")
            print(f"最後の記録: {basic_stats['last_record_date']}")

        print(f"ロギング状態: {'停止中' if not self.keyboard_logger.is_running() else '実行中'}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="キーボード入力パターンを記録・分析するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python keyboard_monitor.py --cli              # インタラクティブモード
  python keyboard_monitor.py --stats            # 統計表示
  python keyboard_monitor.py --status           # ステータス表示
        """
    )

    parser.add_argument(
        '--cli', '-c',
        action='store_true',
        help='CLIインタラクティブモードで起動'
    )

    parser.add_argument(
        '--stats', '-s',
        nargs='?',
        const='',
        help='統計情報を表示（日付指定可能）'
    )

    parser.add_argument(
        '--status', '-st',
        action='store_true',
        help='システムステータスを表示'
    )

    parser.add_argument(
        '--setup',
        action='store_true',
        help='初回セットアップを実行'
    )

    args = parser.parse_args()

    try:
        app = KeyboardMonitor()

        if args.setup:
            print("初回セットアップを実行しています...")
            print("設定ファイルとディレクトリを作成しました。")
            print("'python keyboard_monitor.py --cli' でアプリケーションを開始できます。")

        elif args.cli:
            app.start_cli_mode()

        elif args.stats is not None:
            app.show_statistics(args.stats if args.stats else None)

        elif args.status:
            app.show_status()

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}操作がキャンセルされました{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}エラーが発生しました: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
