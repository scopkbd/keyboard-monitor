"""
データ分析ロジック

keyboard_log.jsonのデータを分析して統計情報を生成する
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class DataAnalyzer:
    """キーボードデータの分析クラス"""

    def __init__(self, data_file_path: str):
        """
        初期化

        Args:
            data_file_path: keyboard_log.jsonファイルのパス
        """
        self.data_file_path = Path(data_file_path)
        self._data_cache = None
        self._cache_timestamp = None

    def _load_data(self) -> Dict[str, Any]:
        """データファイルを読み込み"""
        try:
            # ファイルの更新チェック
            if self.data_file_path.exists():
                file_mtime = self.data_file_path.stat().st_mtime
                if self._data_cache is None or self._cache_timestamp != file_mtime:
                    with open(self.data_file_path, 'r', encoding='utf-8') as f:
                        self._data_cache = json.load(f)
                    self._cache_timestamp = file_mtime

                return self._data_cache
            else:
                return {"total_statistics": {}, "key_statistics": {}}
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"データ読み込みエラー: {e}")
            return {"total_statistics": {}, "key_statistics": {}}

    def load_data(self) -> Dict[str, Any]:
        """
        データファイルを読み込む（公開メソッド）

        Returns:
            読み込んだデータまたは空のデータ構造

        Raises:
            FileNotFoundError: データファイルが見つからない場合
            json.JSONDecodeError: JSONの形式が不正な場合
            Exception: その他の読み込みエラー
        """
        try:
            return self._load_data()
        except Exception as e:
            print(f"データ読み込みでエラーが発生しました: {e}")
            # エラーが発生した場合は空のデータ構造を返す
            return {
                "total_statistics": {},
                "key_statistics": {},
                "error": str(e)
            }

    def calculate_basic_stats(self) -> Dict[str, Any]:
        """基本統計を計算"""
        data = self._load_data()
        total_stats = data.get("total_statistics", {})

        # デフォルト値
        basic_stats = {
            "total_keystrokes": 0,
            "recording_period": "記録なし"
        }

        if not total_stats:
            return basic_stats

        total_keystrokes = total_stats.get("total_keystrokes", 0)
        first_date_str = total_stats.get("first_record_date")
        last_date_str = total_stats.get("last_record_date")

        basic_stats["total_keystrokes"] = total_keystrokes

        if first_date_str and last_date_str:
            try:
                start_date = datetime.strptime(first_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(last_date_str, "%Y-%m-%d")

                basic_stats["recording_period"] = f"{start_date.strftime('%Y/%m/%d')} ～ {end_date.strftime('%Y/%m/%d')}"

            except ValueError as e:
                print(f"日付解析エラー: {e}")

        return basic_stats

    def analyze_key_frequency(self) -> Dict[str, List[Dict[str, Any]]]:
        """キー頻度分析を実行"""
        data = self._load_data()
        key_stats = data.get("key_statistics", {})

        if not key_stats:
            return {"overall_top5": [], "no_modifier_top5": []}

        # 全体ランキング
        overall_ranking = []
        for key_code, key_data in key_stats.items():
            key_name = key_data.get("key_name", f"Key{key_code}")
            count = key_data.get("count", 0)
            overall_ranking.append({
                "key_name": key_name,
                "count": count,
                "percentage": 0.0  # 後で計算
            })

        overall_ranking.sort(key=lambda x: x["count"], reverse=True)

        # 全体に対する割合を計算
        total_count = sum(item["count"] for item in overall_ranking)
        if total_count > 0:
            for item in overall_ranking:
                item["percentage"] = (item["count"] / total_count) * 100

        # 修飾キーなしランキング
        no_modifier_ranking = []
        for key_code, key_data in key_stats.items():
            key_name = key_data.get("key_name", f"Key{key_code}")
            modifier_combos = key_data.get("modifier_combinations", {})
            none_combo = modifier_combos.get("none", {})
            count = none_combo.get("count", 0)

            if count > 0:
                no_modifier_ranking.append({
                    "key_name": key_name,
                    "count": count,
                    "percentage": 0.0
                })

        no_modifier_ranking.sort(key=lambda x: x["count"], reverse=True)

        # 修飾キーなしの割合を計算
        total_no_modifier = sum(item["count"] for item in no_modifier_ranking)
        if total_no_modifier > 0:
            for item in no_modifier_ranking:
                item["percentage"] = (item["count"] / total_no_modifier) * 100

        return {
            "overall_top5": overall_ranking[:5],
            "no_modifier_top5": no_modifier_ranking[:5]
        }

    def analyze_modifier_usage(self) -> Dict[str, Any]:
        """モディファイア使用分析を実行 - ユーザーの実際の使用パターンを忠実に反映"""
        data = self._load_data()
        key_stats = data.get("key_statistics", {})

        if not key_stats:
            return {
                "modifier_usage": {"none": 0, "shift": 0, "ctrl": 0, "alt": 0, "super": 0},
                "usage_ratios": {"none": 100.0, "shift": 0.0, "ctrl": 0.0, "alt": 0.0, "super": 0.0},
                "raw_counts": {"none": 0, "shift": 0, "ctrl": 0, "alt": 0, "super": 0},
                "top_shortcuts": []
            }

        # モディファイア別の使用回数を集計
        modifier_counts = {"none": 0, "shift": 0, "ctrl": 0, "alt": 0, "super": 0}

        # ユーザーが実際に使用したすべての修飾キー組み合わせを抽出
        shortcuts = self._extract_all_shortcuts(key_stats)

        # 基本的な修飾キー使用回数を集計（統計用）
        for key_code, key_data in key_stats.items():
            modifier_combos = key_data.get("modifier_combinations", {})
            for modifier, mod_data in modifier_combos.items():
                count = mod_data.get("count", 0)
                # 基本修飾キーの場合のみ統計に加算
                if modifier in modifier_counts:
                    modifier_counts[modifier] += count
                # 複合修飾キー（ctrl+shift等）は適切に分解して加算
                elif "+" in modifier:
                    self._add_compound_modifier_counts(modifier, count, modifier_counts)

        # 使用率を計算
        total = sum(modifier_counts.values())
        ratios = {}
        if total > 0:
            for modifier, count in modifier_counts.items():
                ratios[modifier] = (count / total) * 100
        else:
            ratios = {"none": 100.0, "shift": 0.0, "ctrl": 0.0, "alt": 0.0, "super": 0.0}

        # 各修飾キーごとの上位キーランキングを取得
        modifier_key_rankings = self.analyze_modifier_key_rankings()

        return {
            "modifier_usage": modifier_counts,
            "usage_ratios": ratios,
            "raw_counts": modifier_counts,
            "top_shortcuts": shortcuts,  # すべての実際の使用パターン
            "modifier_key_rankings": modifier_key_rankings  # 各修飾キーごとの上位キー
        }

    def create_integrated_sequence_analysis(self) -> List[Dict[str, Any]]:
        """統合シーケンス分析データを作成"""
        data = self._load_data()
        key_stats = data.get("key_statistics", {})

        if not key_stats:
            return []

        # 上位5キーを取得
        top_keys = []
        for key_code, key_data in key_stats.items():
            key_name = key_data.get("key_name", f"Key{key_code}")
            count = key_data.get("count", 0)
            top_keys.append((key_code, key_name, count))

        top_keys.sort(key=lambda x: x[2], reverse=True)
        top_keys = top_keys[:5]

        analysis_data = []

        for rank, (key_code, key_name, total_count) in enumerate(top_keys, 1):
            # 直前キー分析（preceded_by）
            predecessors = self._get_top_predecessors(key_code, key_stats, 3)

            # 直後キー分析（このキーが他のキーのpreceded_byに登録されているものを検索）
            successors = self._get_top_successors(key_code, key_stats, 3)

            analysis_data.append({
                "key_name": key_name,
                "total_count": total_count,
                "rank": rank,
                "predecessors": predecessors,
                "successors": successors
            })

        return analysis_data

    def analyze_modifier_key_rankings(self) -> Dict[str, List[Dict[str, Any]]]:
        """各修飾キーと組み合わせて使用される上位キーのランキングを分析"""
        data = self._load_data()
        key_stats = data.get("key_statistics", {})

        if not key_stats:
            return {
                "shift": [],
                "ctrl": [],
                "alt": [],
                "super": []
            }

        # 各修飾キーごとの上位キーを集計
        modifier_rankings = {
            "shift": {},
            "ctrl": {},
            "alt": {},
            "super": {}
        }

        # 各キーの修飾キー組み合わせを調査
        for key_code, key_data in key_stats.items():
            key_name = key_data.get("key_name", self._get_key_name_from_code(key_code))
            modifier_combos = key_data.get("modifier_combinations", {})

            for modifier, mod_data in modifier_combos.items():
                count = mod_data.get("count", 0)

                # 基本修飾キーの場合
                if modifier in modifier_rankings:
                    if key_name not in modifier_rankings[modifier]:
                        modifier_rankings[modifier][key_name] = 0
                    modifier_rankings[modifier][key_name] += count

                # 複合修飾キー（ctrl+shift等）の場合は分解して処理
                elif "+" in modifier:
                    parts = [part.strip() for part in modifier.split("+")]
                    for part in parts:
                        if part in modifier_rankings:
                            if key_name not in modifier_rankings[part]:
                                modifier_rankings[part][key_name] = 0
                            modifier_rankings[part][key_name] += count

        # 各修飾キーのランキングを作成（上位5個）
        result = {}
        for modifier, key_counts in modifier_rankings.items():
            # 頻度順でソート
            sorted_keys = sorted(key_counts.items(), key=lambda x: x[1], reverse=True)

            # 上位5個を取得
            top_keys = []
            for rank, (key_name, count) in enumerate(sorted_keys[:5], 1):
                top_keys.append({
                    "rank": rank,
                    "key_name": key_name,
                    "count": count
                })

            result[modifier] = top_keys

        return result

    def _get_top_predecessors(self, target_key_code: str, key_stats: Dict, top_n: int = 3) -> List[Dict[str, Any]]:
        """指定キーの直前に押されるキーのトップN"""
        if target_key_code not in key_stats:
            return []

        key_data = key_stats[target_key_code]
        modifier_combos = key_data.get("modifier_combinations", {})
        none_combo = modifier_combos.get("none", {})
        preceded_by = none_combo.get("preceded_by", {})

        if not preceded_by:
            return []

        predecessors = []
        for pred_code, count in preceded_by.items():
            pred_name = self._get_key_name_by_code(str(pred_code), key_stats)
            predecessors.append({
                "key_name": pred_name,
                "count": count
            })

        predecessors.sort(key=lambda x: x["count"], reverse=True)
        return predecessors[:top_n]

    def _get_top_successors(self, target_key_code: str, key_stats: Dict, top_n: int = 3) -> List[Dict[str, Any]]:
        """指定キーの直後に押されるキーのトップN"""
        successors = {}

        # 全キーのpreceded_byを調べて、target_key_codeが含まれているものを探す
        for key_code, key_data in key_stats.items():
            key_name = key_data.get("key_name", f"Key{key_code}")
            modifier_combos = key_data.get("modifier_combinations", {})
            none_combo = modifier_combos.get("none", {})
            preceded_by = none_combo.get("preceded_by", {})

            # target_key_codeがpreceded_byに含まれているかチェック
            if target_key_code in preceded_by:
                count = preceded_by[target_key_code]
                successors[key_name] = count

        # 頻度順でソート
        successor_list = []
        for key_name, count in successors.items():
            successor_list.append({
                "key_name": key_name,
                "count": count
            })

        successor_list.sort(key=lambda x: x["count"], reverse=True)
        return successor_list[:top_n]

    def _get_key_name_by_code(self, key_code: str, key_stats: Dict) -> str:
        """キーコードからキー名を取得"""
        if key_code in key_stats:
            return key_stats[key_code].get("key_name", f"Key{key_code}")

        # 特殊キーのマッピング
        special_keys = {
            "13": "Enter",
            "32": "Space",
            "8": "Backspace",
            "9": "Tab",
            "27": "Escape",
            "16": "Shift",
            "17": "Ctrl",
            "18": "Alt"
        }
        return special_keys.get(key_code, f"Key{key_code}")

    def export_data(self, format_type: str = "json") -> str:
        """統計データをエクスポート"""
        analysis_result = {
            "basic_stats": self.calculate_basic_stats(),
            "key_frequency": self.analyze_key_frequency(),
            "modifier_usage": self.analyze_modifier_usage(),
            "sequence_analysis": self.create_integrated_sequence_analysis(),
            "export_timestamp": datetime.now().isoformat()
        }

        if format_type.lower() == "json":
            return json.dumps(analysis_result, indent=2, ensure_ascii=False)
        elif format_type.lower() == "csv":
            # CSVフォーマットの実装（簡易版）
            lines = ["Type,Key,Count,Percentage"]
            for item in analysis_result["key_frequency"]["overall_top5"]:
                lines.append(f"Overall,{item['key_name']},{item['count']},{item['percentage']:.1f}")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def get_basic_statistics(self) -> Dict[str, Any]:
        """基本統計を取得（互換性メソッド）"""
        return self.calculate_basic_stats()

    def get_key_frequency(self) -> Dict[str, int]:
        """キー頻度を取得（互換性メソッド）"""
        try:
            data = self._load_data()
            key_stats = data.get("key_statistics", {})

            if not key_stats:
                return {}

            # 直接キー統計からキー名と回数を取得
            frequency_dict = {}
            for key_code, key_data in key_stats.items():
                # キー名を取得（key_nameフィールドまたはキーコードから推定）
                key_name = key_data.get("key_name", "")
                if not key_name:
                    # key_nameがない場合、キーコードから推定
                    key_name = self._get_key_name_from_code(key_code)

                count = key_data.get("count", 0)
                frequency_dict[key_name] = count

            print(f"DataAnalyzer: 生成されたキー頻度データ = {frequency_dict}")
            return frequency_dict

        except Exception as e:
            print(f"キー頻度取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _get_key_name_from_code(self, key_code: str) -> str:
        """キーコードからキー名を推定"""
        # 数字のキーコードを文字に変換
        try:
            # 数字コードの場合
            if key_code.isdigit():
                code = int(key_code)
                # アルファベット（A=65, Z=90）
                if 65 <= code <= 90:
                    return chr(code)
                # 数字（0=48, 9=57）
                elif 48 <= code <= 57:
                    return chr(code)
                # スペース
                elif code == 32:
                    return "Space"
                # Enter
                elif code == 13:
                    return "Enter"
                # Backspace
                elif code == 8:
                    return "Backspace"
                # Tab
                elif code == 9:
                    return "Tab"
                # その他は数字コードをそのまま表示
                else:
                    return f"Key{code}"
            # 文字列の場合はそのまま返す
            else:
                return key_code
        except:
            return key_code or "Unknown"

    def get_modifier_usage(self) -> Dict[str, Any]:
        """修飾キー使用状況を取得（互換性メソッド）- 完全な分析データを返す"""
        try:
            return self.analyze_modifier_usage()
        except Exception as e:
            print(f"修飾キー使用状況取得エラー: {e}")
            return {
                "modifier_usage": {"none": 0, "shift": 0, "ctrl": 0, "alt": 0, "super": 0},
                "usage_ratios": {"none": 100.0, "shift": 0.0, "ctrl": 0.0, "alt": 0.0, "super": 0.0},
                "raw_counts": {"none": 0, "shift": 0, "ctrl": 0, "alt": 0, "super": 0},
                "top_shortcuts": []
            }

    def get_integrated_sequence_analysis(self) -> Dict[str, Any]:
        """統合シーケンス分析を取得（互換性メソッド）"""
        try:
            analysis_list = self.create_integrated_sequence_analysis()
            # リスト形式を辞書形式に変換
            result = {}
            for item in analysis_list:
                key_name = item.get('key_name', 'unknown')
                result[key_name] = {
                    'count': item.get('total_count', 0),
                    'predecessors': item.get('predecessors', []),
                    'successors': item.get('successors', [])
                }
            return result
        except Exception as e:
            print(f"統合シーケンス分析取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def has_data(self) -> bool:
        """データが存在するかチェック"""
        try:
            print(f"has_data: ファイルパス確認 {self.data_file_path}")
            print(f"has_data: ファイル存在 {self.data_file_path.exists()}")

            data = self._load_data()
            print(f"has_data: 読み込んだデータキー {list(data.keys()) if data else 'None'}")

            total_stats = data.get("total_statistics", {})
            key_stats = data.get("key_statistics", {})

            print(f"has_data: total_stats存在 {bool(total_stats)}")
            print(f"has_data: key_stats存在 {bool(key_stats)}")

            result = bool(total_stats or key_stats)
            print(f"has_data: 結果 {result}")
            return result

        except Exception as e:
            print(f"has_data: エラー {e}")
            return False

    def get_data_file_path(self) -> str:
        """データファイルのパスを取得"""
        return str(self.data_file_path)

    def debug_data_loading(self) -> Dict[str, Any]:
        """デバッグ用：データ読み込み状況を詳細に確認"""
        debug_info = {
            "data_file_path": str(self.data_file_path),
            "file_exists": self.data_file_path.exists(),
            "file_size": 0,
            "cache_status": "not_cached" if self._data_cache is None else "cached",
            "data_keys": [],
            "error": None
        }

        try:
            if self.data_file_path.exists():
                debug_info["file_size"] = self.data_file_path.stat().st_size

                # ファイルを直接読み込んでテスト
                with open(self.data_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    debug_info["data_keys"] = list(data.keys())
                    debug_info["total_stats_keys"] = list(data.get("total_statistics", {}).keys())
                    debug_info["key_stats_count"] = len(data.get("key_statistics", {}))

        except Exception as e:
            debug_info["error"] = str(e)

        return debug_info

    def _extract_all_shortcuts(self, key_stats: Dict) -> List[Dict]:
        """ユーザーが実際に使用したすべての修飾キー組み合わせを抽出"""
        shortcuts = []

        for key_code, key_data in key_stats.items():
            key_name = key_data.get("key_name", f"Key{key_code}")
            modifier_combos = key_data.get("modifier_combinations", {})

            for modifier, mod_data in modifier_combos.items():
                if modifier == "none":
                    continue  # 修飾キーなしはスキップ

                # 修飾キー自体とその修飾キーの組み合わせはスキップ
                if self._is_modifier_key_itself(key_name, modifier):
                    continue

                count = mod_data.get("count", 0)
                if count > 0:  # 1回でも使用されていれば表示
                    display_combo = self._format_shortcut_display(modifier, key_name)
                    shortcuts.append({
                        "combination": display_combo,
                        "count": count,
                        "key_name": key_name,
                        "modifier": modifier
                    })

        return sorted(shortcuts, key=lambda x: x["count"], reverse=True)

    def _is_modifier_key_itself(self, key_name: str, modifier: str) -> bool:
        """修飾キー自体かどうかを判定（Shift+Shift等の重複を避ける）"""
        modifier_keys = {
            "shift": ["Left Shift", "Right Shift"],
            "ctrl": ["Left Ctrl", "Right Ctrl"],
            "alt": ["Left Alt", "Right Alt"],
            "super": ["Left Super", "Right Super", "Super", "Left Win", "Right Win", "Windows"]  # 新旧データ互換性のため
        }

        # シンプルな修飾キーの場合
        if modifier in modifier_keys:
            return key_name in modifier_keys[modifier]

        # 複合修飾キーの場合（ctrl+shift等）
        if "+" in modifier:
            modifier_parts = modifier.split("+")
            for part in modifier_parts:
                if part.strip() in modifier_keys and key_name in modifier_keys[part.strip()]:
                    return True

        return False

    def _format_shortcut_display(self, modifier: str, key_name: str) -> str:
        """ショートカットの表示形式を統一（判定フィルタなし）"""
        # 修飾キー名の正規化
        modifier_names = {
            "ctrl": "Ctrl",
            "shift": "Shift",
            "alt": "Alt",
            "super": "Super",
            "win": "Super",  # 既存データ互換性のため
            "ctrl+shift": "Ctrl+Shift",
            "shift+ctrl": "Ctrl+Shift",  # 順序統一
            "ctrl+alt": "Ctrl+Alt",
            "alt+ctrl": "Ctrl+Alt",      # 順序統一
            "shift+alt": "Shift+Alt",
            "alt+shift": "Shift+Alt",    # 順序統一
            "ctrl+super": "Ctrl+Super",
            "super+ctrl": "Ctrl+Super",      # 順序統一
            "ctrl+win": "Ctrl+Super",        # 既存データ互換性
            "win+ctrl": "Ctrl+Super",        # 既存データ互換性
            "shift+super": "Shift+Super",
            "super+shift": "Shift+Super",    # 順序統一
            "shift+win": "Shift+Super",      # 既存データ互換性
            "win+shift": "Shift+Super",      # 既存データ互換性
            "alt+super": "Alt+Super",
            "super+alt": "Alt+Super",        # 順序統一
            "alt+win": "Alt+Super",          # 既存データ互換性
            "win+alt": "Alt+Super",          # 既存データ互換性
            "ctrl+shift+alt": "Ctrl+Shift+Alt",
            "ctrl+alt+shift": "Ctrl+Shift+Alt",  # 順序統一
            "shift+ctrl+alt": "Ctrl+Shift+Alt",  # 順序統一
            "shift+alt+ctrl": "Ctrl+Shift+Alt",  # 順序統一
            "alt+ctrl+shift": "Ctrl+Shift+Alt",  # 順序統一
            "alt+shift+ctrl": "Ctrl+Shift+Alt",  # 順序統一
            "ctrl+shift+super": "Ctrl+Shift+Super",
            "ctrl+super+shift": "Ctrl+Shift+Super",  # 順序統一
            "shift+ctrl+super": "Ctrl+Shift+Super",  # 順序統一
            "shift+super+ctrl": "Ctrl+Shift+Super",  # 順序統一
            "super+ctrl+shift": "Ctrl+Shift+Super",  # 順序統一
            "super+shift+ctrl": "Ctrl+Shift+Super",  # 順序統一
            "ctrl+shift+win": "Ctrl+Shift+Super",    # 既存データ互換性
            "ctrl+win+shift": "Ctrl+Shift+Super",    # 既存データ互換性
            "shift+ctrl+win": "Ctrl+Shift+Super",    # 既存データ互換性
            "shift+win+ctrl": "Ctrl+Shift+Super",    # 既存データ互換性
            "win+ctrl+shift": "Ctrl+Shift+Super",    # 既存データ互換性
            "win+shift+ctrl": "Ctrl+Shift+Super",    # 既存データ互換性
            "ctrl+alt+super": "Ctrl+Alt+Super",
            "ctrl+super+alt": "Ctrl+Alt+Super",      # 順序統一
            "alt+ctrl+super": "Ctrl+Alt+Super",      # 順序統一
            "alt+super+ctrl": "Ctrl+Alt+Super",      # 順序統一
            "super+ctrl+alt": "Ctrl+Alt+Super",      # 順序統一
            "super+alt+ctrl": "Ctrl+Alt+Super",      # 順序統一
            "ctrl+alt+win": "Ctrl+Alt+Super",        # 既存データ互換性
            "ctrl+win+alt": "Ctrl+Alt+Super",        # 既存データ互換性
            "alt+ctrl+win": "Ctrl+Alt+Super",        # 既存データ互換性
            "alt+win+ctrl": "Ctrl+Alt+Super",        # 既存データ互換性
            "win+ctrl+alt": "Ctrl+Alt+Super",        # 既存データ互換性
            "win+alt+ctrl": "Ctrl+Alt+Super",        # 既存データ互換性
            "shift+alt+super": "Shift+Alt+Super",
            "shift+super+alt": "Shift+Alt+Super",    # 順序統一
            "alt+shift+super": "Shift+Alt+Super",    # 順序統一
            "alt+super+shift": "Shift+Alt+Super",    # 順序統一
            "super+shift+alt": "Shift+Alt+Super",    # 順序統一
            "super+alt+shift": "Shift+Alt+Super",    # 順序統一
            "shift+alt+win": "Shift+Alt+Super",      # 既存データ互換性
            "shift+win+alt": "Shift+Alt+Super",      # 既存データ互換性
            "alt+shift+win": "Shift+Alt+Super",      # 既存データ互換性
            "alt+win+shift": "Shift+Alt+Super",      # 既存データ互換性
            "win+shift+alt": "Shift+Alt+Super",      # 既存データ互換性
            "win+alt+shift": "Shift+Alt+Super",      # 既存データ互換性
            "ctrl+shift+alt+super": "Ctrl+Shift+Alt+Super",
            # その他のSuperキー含む4キー組み合わせも順序統一
            "ctrl+alt+shift+super": "Ctrl+Shift+Alt+Super",
            "shift+ctrl+alt+super": "Ctrl+Shift+Alt+Super",
            "shift+alt+ctrl+super": "Ctrl+Shift+Alt+Super",
            "alt+ctrl+shift+super": "Ctrl+Shift+Alt+Super",
            "alt+shift+ctrl+super": "Ctrl+Shift+Alt+Super",
            "super+ctrl+shift+alt": "Ctrl+Shift+Alt+Super",
            "super+ctrl+alt+shift": "Ctrl+Shift+Alt+Super",
            "super+shift+ctrl+alt": "Ctrl+Shift+Alt+Super",
            "super+shift+alt+ctrl": "Ctrl+Shift+Alt+Super",
            "super+alt+ctrl+shift": "Ctrl+Shift+Alt+Super",
            "super+alt+shift+ctrl": "Ctrl+Shift+Alt+Super",
            # Winキー含む4キー組み合わせの既存データ互換性
            "ctrl+shift+alt+win": "Ctrl+Shift+Alt+Super",
            "ctrl+alt+shift+win": "Ctrl+Shift+Alt+Super",
            "shift+ctrl+alt+win": "Ctrl+Shift+Alt+Super",
            "shift+alt+ctrl+win": "Ctrl+Shift+Alt+Super",
            "alt+ctrl+shift+win": "Ctrl+Shift+Alt+Super",
            "alt+shift+ctrl+win": "Ctrl+Shift+Alt+Super",
            "win+ctrl+shift+alt": "Ctrl+Shift+Alt+Super",
            "win+ctrl+alt+shift": "Ctrl+Shift+Alt+Super",
            "win+shift+ctrl+alt": "Ctrl+Shift+Alt+Super",
            "win+shift+alt+ctrl": "Ctrl+Shift+Alt+Super",
            "win+alt+ctrl+shift": "Ctrl+Shift+Alt+Super",
            "win+alt+shift+ctrl": "Ctrl+Shift+Alt+Super"
        }

        # キー名の正規化（表示を見やすくするためのみ）
        key_display = self._normalize_key_name(key_name)

        modifier_display = modifier_names.get(modifier, modifier.title())
        return f"{modifier_display}+{key_display}"

    def _normalize_key_name(self, key_name: str) -> str:
        """キー名を表示用に正規化（見やすさのためのみ）"""
        normalizations = {
            "Left Ctrl": "Ctrl",
            "Right Ctrl": "Ctrl",
            "Left Shift": "Shift",
            "Right Shift": "Shift",
            "Left Alt": "Alt",
            "Right Alt": "Alt",
            "Left Win": "Super",
            "Right Win": "Super",
            "Windows": "Super",
            "Space": "Space",
            "Enter": "Enter",
            "Backspace": "BS",
            "Tab": "Tab",
            "Escape": "Esc",
            "Delete": "Del",
            "Insert": "Ins",
            "Home": "Home",
            "End": "End",
            "Page Up": "PgUp",
            "Page Down": "PgDn",
            "Up Arrow": "↑",
            "Down Arrow": "↓",
            "Left Arrow": "←",
            "Right Arrow": "→"
        }

        return normalizations.get(key_name, key_name)

    def _add_compound_modifier_counts(self, modifier: str, count: int, modifier_counts: Dict):
        """複合修飾キー（ctrl+shift等）を適切に分解して統計に加算"""
        modifiers = modifier.split("+")
        for mod in modifiers:
            mod = mod.strip()
            if mod in modifier_counts:
                modifier_counts[mod] += count
            elif mod == "win":  # 既存データ互換性
                modifier_counts["super"] += count
            elif mod == "win":  # 既存データ互換性
                modifier_counts["super"] += count
