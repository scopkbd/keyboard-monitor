#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Save Manager Module

キーボードモニターの保存管理を行うモジュール
新しい保存仕様（アイドル時・連続入力時）を実装
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional


class SaveManager:
    """
    保存管理クラス
    
    アイドル状態での保存と連続入力時の保存を管理する
    """

    def __init__(self, config, data_store, logger: Optional[logging.Logger] = None):
        """
        保存管理クラスの初期化

        Args:
            config: 設定管理インスタンス
            data_store: データストアインスタンス
            logger: ロガーインスタンス
        """
        self.config = config
        self.data_store = data_store
        self.logger = logger or logging.getLogger(__name__)

        # タイマー管理
        self.idle_timer: Optional[threading.Timer] = None
        self.continuous_timer: Optional[threading.Timer] = None
        self._timer_lock = threading.Lock()

        # 時刻管理
        self.last_keystroke_time: Optional[datetime] = None
        self.continuous_session_start: Optional[datetime] = None
        self.keystroke_count_since_save = 0

        # 動作状態
        self.is_running = False
        
        # 統計情報
        self.save_stats = {
            'idle_saves': 0,
            'continuous_saves': 0,
            'batch_saves': 0,
            'total_saves': 0
        }

        self.logger.info("SaveManagerを初期化しました")

    def start(self) -> None:
        """保存管理を開始"""
        if self.is_running:
            self.logger.warning("SaveManagerは既に開始されています")
            return

        self.is_running = True
        self.continuous_session_start = datetime.now()
        self.keystroke_count_since_save = 0
        
        self.logger.info("SaveManager保存管理を開始しました")

    def stop(self) -> None:
        """保存管理を停止"""
        if not self.is_running:
            return

        self.is_running = False
        
        # アクティブなタイマーをキャンセル
        with self._timer_lock:
            if self.idle_timer:
                self.idle_timer.cancel()
                self.idle_timer = None
            if self.continuous_timer:
                self.continuous_timer.cancel()
                self.continuous_timer = None

        # 最終保存を実行
        self._perform_save("shutdown")
        
        self.logger.info(f"SaveManager保存管理を停止しました - 統計: {self.save_stats}")

    def on_keystroke(self, session_stats: Dict[str, Any]) -> None:
        """
        キーストローク発生時の処理

        Args:
            session_stats: セッション統計情報
        """
        if not self.is_running:
            return

        current_time = datetime.now()
        self.last_keystroke_time = current_time
        self.keystroke_count_since_save += 1

        # アイドルタイマーのリセット・再スケジュール
        self._schedule_idle_save()

        # 連続入力タイマーの管理
        self._manage_continuous_save_timer()

        # バッチ保存のフォールバック（従来の仕組み）
        batch_size = self.config.get_keystroke_batch_save()
        if self.keystroke_count_since_save >= batch_size:
            self._perform_save("batch")

    def _schedule_idle_save(self) -> None:
        """アイドル状態での保存をスケジュール"""
        with self._timer_lock:
            # 既存のアイドルタイマーをキャンセル
            if self.idle_timer:
                self.idle_timer.cancel()

            # 新しいアイドルタイマーを設定
            idle_delay = self.config.get_idle_save_delay()
            self.idle_timer = threading.Timer(idle_delay, self._idle_save_callback)
            self.idle_timer.daemon = True
            self.idle_timer.start()

    def _idle_save_callback(self) -> None:
        """アイドル保存のコールバック"""
        try:
            if self.is_running and self.keystroke_count_since_save > 0:
                self._perform_save("idle")
                self.logger.debug(f"アイドル保存を実行しました (遅延: {self.config.get_idle_save_delay()}秒)")
        except Exception as e:
            self.logger.error(f"アイドル保存中にエラーが発生しました: {e}")
        finally:
            with self._timer_lock:
                self.idle_timer = None

    def _manage_continuous_save_timer(self) -> None:
        """連続入力保存タイマーの管理"""
        if not self.continuous_session_start:
            self.continuous_session_start = datetime.now()

        # 連続入力時間をチェック
        continuous_duration = datetime.now() - self.continuous_session_start
        continuous_interval = timedelta(seconds=self.config.get_continuous_save_interval())

        if continuous_duration >= continuous_interval:
            self._perform_save("continuous")
            self.continuous_session_start = datetime.now()

    def _perform_save(self, save_type: str) -> bool:
        """
        実際の保存処理を実行

        Args:
            save_type: 保存タイプ ('idle', 'continuous', 'batch', 'shutdown')

        Returns:
            保存が成功したかどうか
        """
        try:
            if self.keystroke_count_since_save == 0 and save_type != "shutdown":
                return True  # 保存する必要がない

            # データを保存
            success = self.data_store.save_data()
            
            if success:
                # 統計を更新
                self.save_stats[f'{save_type}_saves'] += 1
                self.save_stats['total_saves'] += 1
                self.keystroke_count_since_save = 0
                
                self.logger.info(f"{save_type}保存を実行しました (キーストローク: {self.keystroke_count_since_save})")
                return True
            else:
                self.logger.warning(f"{save_type}保存に失敗しました")
                return False

        except Exception as e:
            self.logger.error(f"{save_type}保存中にエラーが発生しました: {e}")
            return False

    def get_save_statistics(self) -> Dict[str, Any]:
        """
        保存統計情報を取得

        Returns:
            保存統計情報
        """
        return {
            **self.save_stats,
            'last_keystroke_time': self.last_keystroke_time,
            'continuous_session_start': self.continuous_session_start,
            'keystroke_count_since_save': self.keystroke_count_since_save,
            'is_running': self.is_running
        }

    def force_save(self) -> bool:
        """
        強制的に保存を実行

        Returns:
            保存が成功したかどうか
        """
        return self._perform_save("manual")
