"""
Keyboard Logger Module

キーボード入力を監視・記録するモジュール
"""

import logging
import os
import sys
import threading
import time
from collections import deque
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

# プロジェクトのsrcディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode
except ImportError:
    raise ImportError("pynput ライブラリが必要です。'pip install pynput' を実行してください。")

from config import get_config
from data_store import DataStore


class KeyboardLogger:
    """キーボードロガークラス"""

    # Virtual Key Code マッピング（主要なキー）
    VK_CODE_MAP = {
        # アルファベット
        'a': '65', 'b': '66', 'c': '67', 'd': '68', 'e': '69', 'f': '70',
        'g': '71', 'h': '72', 'i': '73', 'j': '74', 'k': '75', 'l': '76',
        'm': '77', 'n': '78', 'o': '79', 'p': '80', 'q': '81', 'r': '82',
        's': '83', 't': '84', 'u': '85', 'v': '86', 'w': '87', 'x': '88',
        'y': '89', 'z': '90',

        # 数字
        '0': '48', '1': '49', '2': '50', '3': '51', '4': '52',
        '5': '53', '6': '54', '7': '55', '8': '56', '9': '57',

        # 特殊キー
        Key.space: '32',
        Key.enter: '13',
        Key.backspace: '8',
        Key.tab: '9',
        Key.shift: '16',
        Key.shift_l: '160',
        Key.shift_r: '161',
        Key.ctrl: '17',
        Key.ctrl_l: '162',
        Key.ctrl_r: '163',
        Key.alt: '18',
        Key.alt_l: '164',
        Key.alt_r: '165',
        Key.cmd: '91',
        Key.cmd_l: '91',
        Key.cmd_r: '92',

        # ファンクションキー
        Key.f1: '112', Key.f2: '113', Key.f3: '114', Key.f4: '115',
        Key.f5: '116', Key.f6: '117', Key.f7: '118', Key.f8: '119',
        Key.f9: '120', Key.f10: '121', Key.f11: '122', Key.f12: '123',

        # 矢印キー
        Key.left: '37', Key.up: '38', Key.right: '39', Key.down: '40',

        # その他のキー
        Key.esc: '27',
        Key.delete: '46',
        Key.home: '36',
        Key.end: '35',
        Key.page_up: '33',
        Key.page_down: '34',
        Key.caps_lock: '20',
        Key.num_lock: '144',
        Key.scroll_lock: '145',
        Key.print_screen: '44',
        Key.pause: '19',
        Key.insert: '45',
    }

    # キー名マッピング
    KEY_NAME_MAP = {
        Key.space: 'Space',
        Key.enter: 'Enter',
        Key.backspace: 'Backspace',
        Key.tab: 'Tab',
        Key.shift: 'Shift',
        Key.shift_l: 'Left Shift',
        Key.shift_r: 'Right Shift',
        Key.ctrl: 'Ctrl',
        Key.ctrl_l: 'Left Ctrl',
        Key.ctrl_r: 'Right Ctrl',
        Key.alt: 'Alt',
        Key.alt_l: 'Left Alt',
        Key.alt_r: 'Right Alt',
        Key.cmd: 'Win',
        Key.cmd_l: 'Left Win',
        Key.cmd_r: 'Right Win',
        Key.esc: 'Escape',
        Key.delete: 'Delete',
        Key.home: 'Home',
        Key.end: 'End',
        Key.page_up: 'Page Up',
        Key.page_down: 'Page Down',
        Key.caps_lock: 'Caps Lock',
        Key.num_lock: 'Num Lock',
        Key.scroll_lock: 'Scroll Lock',
        Key.print_screen: 'Print Screen',
        Key.pause: 'Pause',
        Key.insert: 'Insert',
        Key.left: 'Left Arrow',
        Key.up: 'Up Arrow',
        Key.right: 'Right Arrow',
        Key.down: 'Down Arrow',
    }

    def __init__(self, data_store: DataStore):
        """
        キーボードロガーの初期化

        Args:
            data_store: データストレージインスタンス
        """
        self.data_store = data_store
        self.config = get_config()
        self.logger = logging.getLogger(__name__)

        # 状態管理
        self.is_logging = False
        self.listener: Optional[keyboard.Listener] = None
        self.logger_thread: Optional[threading.Thread] = None

        # モディファイアキーの状態
        self.pressed_modifiers = set()

        # キーシーケンスの追跡
        self.key_sequence = deque(maxlen=self.config.get("logging.max_sequence_length", 1000))
        self.previous_key = None

        # 統計情報
        self.session_stats = {
            'keystrokes': 0,
            'start_time': None,
            'last_key': None,
            'last_key_time': None
        }

        # イベントコールバック
        self.on_key_event: Optional[Callable] = None
        self.on_statistics_update: Optional[Callable] = None

    def start_logging(self) -> bool:
        """
        キーロギングを開始する

        Returns:
            開始が成功したかどうか
        """
        if self.is_logging:
            self.logger.warning("キーロギングは既に開始されています")
            return True

        try:
            # セッション統計をリセット
            self.session_stats = {
                'keystrokes': 0,
                'start_time': datetime.now(),
                'last_key': None,
                'last_key_time': None
            }

            # キーボードリスナーを開始
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )

            self.listener.start()
            self.is_logging = True

            self.logger.info("キーロギングを開始しました")
            return True

        except Exception as e:
            self.logger.error(f"キーロギングの開始に失敗しました: {e}")
            return False

    def stop_logging(self) -> bool:
        """
        キーロギングを停止する

        Returns:
            停止が成功したかどうか
        """
        if not self.is_logging:
            self.logger.warning("キーロギングは開始されていません")
            return True

        try:
            if self.listener:
                self.listener.stop()
                self.listener = None

            self.is_logging = False

            # データを保存
            self.data_store.save_data(create_backup=True)

            self.logger.info("キーロギングを停止しました")
            return True

        except Exception as e:
            self.logger.error(f"キーロギングの停止に失敗しました: {e}")
            return False

    def _on_key_press(self, key) -> None:
        """キー押下イベントハンドラ"""
        try:
            # モディファイアキーの状態を更新
            self._update_modifier_state(key, pressed=True)

            # キーコードとキー名を取得
            key_code = self._get_key_code(key)
            key_name = self._get_key_name(key)

            if key_code is None:
                return  # 未対応のキー

            # モディファイア組み合わせ文字列を生成
            modifiers = self._get_modifier_combination()

            # 統計を更新
            self.data_store.update_key_statistics(
                key_code=key_code,
                key_name=key_name,
                modifiers=modifiers,
                previous_key=self.previous_key
            )

            # シーケンス分析の更新
            self._update_sequence_analysis(key_code)

            # セッション統計を更新
            self.session_stats['keystrokes'] += 1
            self.session_stats['last_key'] = f"{key_name} ({modifiers})" if modifiers != 'none' else key_name
            self.session_stats['last_key_time'] = datetime.now()

            # 前のキーを更新
            self.previous_key = key_code

            # イベントコールバックを呼び出し
            if self.on_key_event:
                self.on_key_event({
                    'key_code': key_code,
                    'key_name': key_name,
                    'modifiers': modifiers,
                    'timestamp': datetime.now()
                })

            # 統計更新コールバックを呼び出し
            if self.on_statistics_update:
                self.on_statistics_update(self.session_stats.copy())

        except Exception as e:
            self.logger.error(f"キー押下処理中にエラーが発生しました: {e}")

    def _on_key_release(self, key) -> None:
        """キー離上イベントハンドラ"""
        try:
            # モディファイアキーの状態を更新
            self._update_modifier_state(key, pressed=False)

        except Exception as e:
            self.logger.error(f"キー離上処理中にエラーが発生しました: {e}")

    def _update_modifier_state(self, key, pressed: bool) -> None:
        """モディファイアキーの状態を更新する"""
        modifier_keys = {
            Key.ctrl, Key.ctrl_l, Key.ctrl_r,
            Key.shift, Key.shift_l, Key.shift_r,
            Key.alt, Key.alt_l, Key.alt_r,
            Key.cmd, Key.cmd_l, Key.cmd_r
        }

        if key in modifier_keys:
            modifier_name = self._get_modifier_name(key)
            if pressed:
                self.pressed_modifiers.add(modifier_name)
            else:
                self.pressed_modifiers.discard(modifier_name)

    def _get_modifier_name(self, key) -> str:
        """モディファイアキーの名前を取得する"""
        if key in [Key.ctrl, Key.ctrl_l, Key.ctrl_r]:
            return 'ctrl'
        elif key in [Key.shift, Key.shift_l, Key.shift_r]:
            return 'shift'
        elif key in [Key.alt, Key.alt_l, Key.alt_r]:
            return 'alt'
        elif key in [Key.cmd, Key.cmd_l, Key.cmd_r]:
            return 'win'
        return ''

    def _get_modifier_combination(self) -> str:
        """現在のモディファイア組み合わせ文字列を取得する"""
        if not self.pressed_modifiers:
            return 'none'

        # アルファベット順でソート
        sorted_modifiers = sorted(list(self.pressed_modifiers))
        return '+'.join(sorted_modifiers)

    def _get_key_code(self, key) -> Optional[str]:
        """キーのVirtual Key Codeを取得する"""
        # KeyCodeの場合（文字キー）
        if isinstance(key, KeyCode):
            if hasattr(key, 'char') and key.char:
                return self.VK_CODE_MAP.get(key.char.lower())
            elif hasattr(key, 'vk') and key.vk:
                return str(key.vk)

        # 特殊キーの場合
        return self.VK_CODE_MAP.get(key)

    def _get_key_name(self, key) -> str:
        """キーの表示名を取得する"""
        # KeyCodeの場合（文字キー）
        if isinstance(key, KeyCode):
            if hasattr(key, 'char') and key.char:
                return key.char.upper() if key.char.isalpha() else key.char
            elif hasattr(key, 'vk') and key.vk:
                return f"Key_{key.vk}"

        # 特殊キーの場合
        if key in self.KEY_NAME_MAP:
            return self.KEY_NAME_MAP[key]

        # その他の場合
        return str(key).replace('Key.', '').replace('_', ' ').title()

    def _update_sequence_analysis(self, key_code: str) -> None:
        """シーケンス分析を更新する"""
        if not self.config.is_sequence_tracking_enabled():
            return

        self.key_sequence.append(key_code)

        # Bigram分析
        if self.config.get("analysis.track_bigrams") and len(self.key_sequence) >= 2:
            bigram = list(self.key_sequence)[-2:]
            self.data_store.update_sequence_statistics(bigram, "bigrams")

        # Trigram分析
        if self.config.get("analysis.track_trigrams") and len(self.key_sequence) >= 3:
            trigram = list(self.key_sequence)[-3:]
            self.data_store.update_sequence_statistics(trigram, "trigrams")

    def get_session_statistics(self) -> Dict[str, Any]:
        """セッション統計を取得する"""
        stats = self.session_stats.copy()

        if stats['start_time']:
            elapsed = datetime.now() - stats['start_time']
            stats['elapsed_time'] = elapsed
            stats['elapsed_seconds'] = elapsed.total_seconds()

            # WPM計算（大まかな推定）
            if elapsed.total_seconds() > 0:
                # 平均的に1単語 = 5文字として計算
                words = stats['keystrokes'] / 5
                minutes = elapsed.total_seconds() / 60
                stats['wpm'] = words / minutes if minutes > 0 else 0

        return stats

    def get_real_time_statistics(self) -> Dict[str, Any]:
        """リアルタイム統計を取得する"""
        total_stats = self.data_store.get_statistics()
        session_stats = self.get_session_statistics()

        return {
            'session': session_stats,
            'total': total_stats['total_statistics'],
            'top_keys': self.data_store.get_top_keys(limit=5),
            'modifier_stats': self.data_store.get_modifier_analysis()
        }

    def set_callbacks(self, on_key_event: Optional[Callable] = None,
                     on_statistics_update: Optional[Callable] = None) -> None:
        """
        イベントコールバックを設定する

        Args:
            on_key_event: キーイベント発生時のコールバック
            on_statistics_update: 統計更新時のコールバック
        """
        self.on_key_event = on_key_event
        self.on_statistics_update = on_statistics_update

    def is_running(self) -> bool:
        """ロギングが実行中かどうかを確認する"""
        return self.is_logging

    def get_status(self) -> Dict[str, Any]:
        """ロガーの状態を取得する"""
        return {
            'is_logging': self.is_logging,
            'session_stats': self.get_session_statistics(),
            'pressed_modifiers': list(self.pressed_modifiers),
            'sequence_length': len(self.key_sequence)
        }
