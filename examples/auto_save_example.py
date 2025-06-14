#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動保存・バックアップ機能の実装例

backup_intervalとsave_intervalを活用した定期処理の実装
"""

import threading
import time
from typing import Optional


class AutoSaveManager:
    """自動保存・バックアップ管理クラス"""

    def __init__(self, config, data_store, logger):
        self.config = config
        self.data_store = data_store
        self.logger = logger

        self.save_timer: Optional[threading.Timer] = None
        self.backup_timer: Optional[threading.Timer] = None
        self.running = False

    def start(self):
        """自動保存・バックアップを開始"""
        if self.running:
            return

        self.running = True
        self.logger.info("自動保存・バックアップ機能を開始しました")

        # 自動保存タイマーを開始
        if self.config.is_auto_save_enabled():
            self._schedule_next_save()

        # 自動バックアップタイマーを開始
        self._schedule_next_backup()

    def stop(self):
        """自動保存・バックアップを停止"""
        self.running = False

        if self.save_timer:
            self.save_timer.cancel()
            self.save_timer = None

        if self.backup_timer:
            self.backup_timer.cancel()
            self.backup_timer = None

        self.logger.info("自動保存・バックアップ機能を停止しました")

    def _schedule_next_save(self):
        """次回の自動保存をスケジュール"""
        if not self.running:
            return

        save_interval = self.config.get_save_interval()
        self.save_timer = threading.Timer(save_interval, self._auto_save)
        self.save_timer.daemon = True
        self.save_timer.start()

    def _auto_save(self):
        """自動保存を実行"""
        try:
            if self.config.is_auto_save_enabled() and self.running:
                self.data_store.save_data()
                self.logger.info(f"定期自動保存を実行しました (間隔: {self.config.get_save_interval()}秒)")

            # 次回の保存をスケジュール
            self._schedule_next_save()

        except Exception as e:
            self.logger.error(f"自動保存中にエラーが発生しました: {e}")
            self._schedule_next_save()  # エラーが発生してもタイマーを継続

    def _schedule_next_backup(self):
        """次回のバックアップをスケジュール"""
        if not self.running:
            return

        backup_interval = self.config.get_backup_interval()
        self.backup_timer = threading.Timer(backup_interval, self._auto_backup)
        self.backup_timer.daemon = True
        self.backup_timer.start()

    def _auto_backup(self):
        """自動バックアップを実行"""
        try:
            if self.running:
                self.data_store.save_data(create_backup=True)
                self.logger.info(f"定期バックアップを実行しました (間隔: {self.config.get_backup_interval()}秒)")

            # 次回のバックアップをスケジュール
            self._schedule_next_backup()

        except Exception as e:
            self.logger.error(f"自動バックアップ中にエラーが発生しました: {e}")
            self._schedule_next_backup()  # エラーが発生してもタイマーを継続


# KeyboardMonitorクラスへの統合例
"""
class KeyboardMonitor:
    def __init__(self):
        # 既存の初期化コード...

        # 自動保存管理の追加
        self.auto_save_manager = AutoSaveManager(
            self.config,
            self.data_store,
            self.logger
        )

    def start_cli_mode(self):
        # 自動保存・バックアップを開始
        self.auto_save_manager.start()

        try:
            # 既存のCLIコード...
            self._cli_command_loop()
        finally:
            self._cleanup()

    def _cleanup(self):
        # 自動保存・バックアップを停止
        self.auto_save_manager.stop()

        # 既存のクリーンアップコード...
"""
