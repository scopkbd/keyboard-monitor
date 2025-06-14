"""
Data Storage Module

キーボード使用データの永続化を管理するモジュール
"""

import gzip
import json
import logging
import os
import shutil
from datetime import date, datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional


class DataStore:
    """データストレージクラス"""

    def __init__(self, data_file: str):
        """
        データストレージクラスの初期化

        Args:
            data_file: データファイルのパス
        """
        self.data_file = Path(data_file)
        self.backup_dir = self.data_file.parent / "backup"
        self.logger = logging.getLogger(__name__)
        self._lock = Lock()  # スレッドセーフティのためのロック

        # データファイルとバックアップディレクトリを初期化
        self._initialize_storage()

        # データ構造を初期化
        self.data = self._get_empty_data_structure()

        # 既存データの読み込み
        self.load_data()

    def _initialize_storage(self) -> None:
        """ストレージディレクトリを初期化する"""
        try:
            # データディレクトリを作成
            self.data_file.parent.mkdir(parents=True, exist_ok=True)

            # バックアップディレクトリを作成
            self.backup_dir.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            self.logger.error(f"ストレージの初期化に失敗しました: {e}")
            raise

    def _get_empty_data_structure(self) -> Dict[str, Any]:
        """空のデータ構造を取得する"""
        return {
            "total_statistics": {
                "total_keystrokes": 0,
                "first_record_date": None,
                "last_record_date": None,
                "version": "1.0"
            },
            "key_statistics": {},
            "key_sequences": {
                "bigrams": {},
                "trigrams": {}
            }
        }

    def load_data(self) -> bool:
        """
        データファイルを読み込む

        Returns:
            読み込みが成功したかどうか
        """
        with self._lock:
            try:
                if self.data_file.exists():
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        loaded_data = json.load(f)

                    # データの妥当性を検証
                    if self._validate_data(loaded_data):
                        self.data = loaded_data
                        self.logger.info(f"データファイルを読み込みました: {self.data_file}")
                        return True
                    else:
                        self.logger.warning("データファイルの形式が正しくありません。バックアップから復元を試みます。")
                        return self._restore_from_backup()
                else:
                    self.logger.info("データファイルが存在しません。新しいデータ構造を作成します。")
                    self.data = self._get_empty_data_structure()
                    return True

            except json.JSONDecodeError as e:
                self.logger.error(f"JSONファイルの解析に失敗しました: {e}")
                return self._restore_from_backup()
            except Exception as e:
                self.logger.error(f"データファイルの読み込みに失敗しました: {e}")
                return self._restore_from_backup()

    def save_data(self, create_backup: bool = False) -> bool:
        """
        データファイルを保存する

        Args:
            create_backup: バックアップを作成するかどうか

        Returns:
            保存が成功したかどうか
        """
        with self._lock:
            try:
                # バックアップの作成
                if create_backup:
                    self._create_backup()

                # 一時ファイルに書き込み
                temp_file = self.data_file.with_suffix('.tmp')

                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)

                # 原子的に置き換え
                shutil.move(str(temp_file), str(self.data_file))

                self.logger.debug(f"データファイルを保存しました: {self.data_file}")
                return True

            except Exception as e:
                self.logger.error(f"データファイルの保存に失敗しました: {e}")
                # 一時ファイルが残っている場合は削除
                temp_file = self.data_file.with_suffix('.tmp')
                if temp_file.exists():
                    temp_file.unlink()
                return False

    def update_key_statistics(self, key_code: str, key_name: str,
                            modifiers: str, previous_key: Optional[str] = None) -> None:
        """
        キー統計を更新する

        Args:
            key_code: Virtual Key Code（文字列）
            key_name: キー名
            modifiers: モディファイア組み合わせ文字列
            previous_key: 直前のキーコード
        """
        with self._lock:
            # 総統計を更新
            self.data["total_statistics"]["total_keystrokes"] += 1

            today = date.today().isoformat()
            if self.data["total_statistics"]["first_record_date"] is None:
                self.data["total_statistics"]["first_record_date"] = today
            self.data["total_statistics"]["last_record_date"] = today

            # キー統計の初期化（必要に応じて）
            if key_code not in self.data["key_statistics"]:
                self.data["key_statistics"][key_code] = {
                    "key_name": key_name,
                    "count": 0,
                    "modifier_combinations": {}
                }

            key_stats = self.data["key_statistics"][key_code]
            key_stats["count"] += 1

            # モディファイア組み合わせ統計の更新
            if modifiers not in key_stats["modifier_combinations"]:
                key_stats["modifier_combinations"][modifiers] = {
                    "count": 0,
                    "preceded_by": {}
                }

            modifier_stats = key_stats["modifier_combinations"][modifiers]
            modifier_stats["count"] += 1

            # 直前キーの統計更新
            if previous_key is not None:
                if previous_key not in modifier_stats["preceded_by"]:
                    modifier_stats["preceded_by"][previous_key] = 0
                modifier_stats["preceded_by"][previous_key] += 1

    def update_sequence_statistics(self, sequence: List[str], sequence_type: str) -> None:
        """
        シーケンス統計を更新する

        Args:
            sequence: キーシーケンス
            sequence_type: シーケンスタイプ（'bigrams' または 'trigrams'）
        """
        with self._lock:
            if sequence_type not in self.data["key_sequences"]:
                self.data["key_sequences"][sequence_type] = {}

            # シーケンスキーを作成
            sequence_key = "_".join(sequence)
            sequence_display = "->".join([self._get_key_name(key) for key in sequence])

            if sequence_key not in self.data["key_sequences"][sequence_type]:
                self.data["key_sequences"][sequence_type][sequence_key] = {
                    "sequence": sequence_display,
                    "count": 0
                }

            self.data["key_sequences"][sequence_type][sequence_key]["count"] += 1

    def get_statistics(self, date_range: Optional[tuple] = None) -> Dict[str, Any]:
        """
        統計データを取得する

        Args:
            date_range: 日付範囲（開始日, 終了日）

        Returns:
            統計データ
        """
        with self._lock:
            # 基本的には全データを返す（日付フィルタリングは将来実装）
            return self.data.copy()

    def get_top_keys(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        使用頻度上位のキーを取得する

        Args:
            limit: 取得する上位件数

        Returns:
            上位キーのリスト
        """
        with self._lock:
            key_stats = []

            for key_code, stats in self.data["key_statistics"].items():
                key_stats.append({
                    "key_code": key_code,
                    "key_name": stats["key_name"],
                    "count": stats["count"]
                })

            # カウント順でソート
            key_stats.sort(key=lambda x: x["count"], reverse=True)

            return key_stats[:limit]

    def get_modifier_analysis(self) -> Dict[str, int]:
        """
        モディファイア組み合わせの統計を取得する

        Returns:
            モディファイア組み合わせ別の統計
        """
        with self._lock:
            modifier_stats = {}

            for key_stats in self.data["key_statistics"].values():
                for modifier, mod_stats in key_stats["modifier_combinations"].items():
                    if modifier not in modifier_stats:
                        modifier_stats[modifier] = 0
                    modifier_stats[modifier] += mod_stats["count"]

            return modifier_stats

    def get_sequence_analysis(self, sequence_type: str = "bigrams") -> List[Dict[str, Any]]:
        """
        シーケンス分析結果を取得する

        Args:
            sequence_type: シーケンスタイプ

        Returns:
            シーケンス統計のリスト
        """
        with self._lock:
            if sequence_type not in self.data["key_sequences"]:
                return []

            sequences = []
            for seq_key, seq_stats in self.data["key_sequences"][sequence_type].items():
                sequences.append({
                    "sequence_key": seq_key,
                    "sequence": seq_stats["sequence"],
                    "count": seq_stats["count"]
                })

            # カウント順でソート
            sequences.sort(key=lambda x: x["count"], reverse=True)

            return sequences

    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """
        データの妥当性を検証する

        Args:
            data: 検証するデータ

        Returns:
            データが妥当かどうか
        """
        try:
            # 必須キーの存在確認
            required_keys = ["total_statistics", "key_statistics", "key_sequences"]
            for key in required_keys:
                if key not in data:
                    self.logger.error(f"必須キー '{key}' が見つかりません")
                    return False

            # 総統計の検証
            total_stats = data["total_statistics"]
            if not isinstance(total_stats.get("total_keystrokes"), int):
                self.logger.error("total_keystrokes が整数ではありません")
                return False

            return True

        except Exception as e:
            self.logger.error(f"データ検証中にエラーが発生しました: {e}")
            return False

    def _create_backup(self) -> None:
        """バックアップファイルを作成する"""
        try:
            if self.data_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.backup_dir / f"keyboard_log_{timestamp}.json.gz"

                # 圧縮してバックアップ
                with open(self.data_file, 'rb') as f_in:
                    with gzip.open(backup_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                self.logger.info(f"バックアップを作成しました: {backup_file}")

                # 古いバックアップファイルを削除（最新10個を保持）
                self._cleanup_old_backups()

        except Exception as e:
            self.logger.error(f"バックアップの作成に失敗しました: {e}")

    def _cleanup_old_backups(self, keep_count: int = 10) -> None:
        """古いバックアップファイルを削除する"""
        try:
            backup_files = list(self.backup_dir.glob("keyboard_log_*.json.gz"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # 指定した数を超えるファイルを削除
            for old_backup in backup_files[keep_count:]:
                old_backup.unlink()
                self.logger.debug(f"古いバックアップを削除しました: {old_backup}")

        except Exception as e:
            self.logger.error(f"バックアップクリーンアップに失敗しました: {e}")

    def _restore_from_backup(self) -> bool:
        """バックアップから復元する"""
        try:
            backup_files = list(self.backup_dir.glob("keyboard_log_*.json.gz"))

            if not backup_files:
                self.logger.warning("バックアップファイルが見つかりません。新しいデータ構造を作成します。")
                self.data = self._get_empty_data_structure()
                return True

            # 最新のバックアップファイルを取得
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            latest_backup = backup_files[0]

            # バックアップから復元
            with gzip.open(latest_backup, 'rb') as f_in:
                with open(self.data_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            self.logger.info(f"バックアップから復元しました: {latest_backup}")

            # 復元したデータを再読み込み
            return self.load_data()

        except Exception as e:
            self.logger.error(f"バックアップからの復元に失敗しました: {e}")
            self.data = self._get_empty_data_structure()
            return True

    def _get_key_name(self, key_code: str) -> str:
        """キーコードからキー名を取得する"""
        if key_code in self.data["key_statistics"]:
            return self.data["key_statistics"][key_code]["key_name"]
        return f"Key_{key_code}"

    def export_data(self, export_file: str, format_type: str = "json") -> bool:
        """
        データをエクスポートする

        Args:
            export_file: エクスポート先ファイル
            format_type: エクスポート形式（'json' または 'csv'）

        Returns:
            エクスポートが成功したかどうか
        """
        with self._lock:
            try:
                export_path = Path(export_file)
                export_path.parent.mkdir(parents=True, exist_ok=True)

                if format_type == "json":
                    with open(export_path, 'w', encoding='utf-8') as f:
                        json.dump(self.data, f, indent=2, ensure_ascii=False)
                elif format_type == "csv":
                    # CSV形式でのエクスポート（簡単な統計のみ）
                    import csv
                    with open(export_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Key_Code', 'Key_Name', 'Count'])

                        for key_code, stats in self.data["key_statistics"].items():
                            writer.writerow([key_code, stats["key_name"], stats["count"]])
                else:
                    raise ValueError(f"サポートされていない形式: {format_type}")

                self.logger.info(f"データをエクスポートしました: {export_path}")
                return True

            except Exception as e:
                self.logger.error(f"データのエクスポートに失敗しました: {e}")
                return False
