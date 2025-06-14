"""
Statistics Analysis Module

キーボード使用統計の分析機能を提供するモジュール
"""

import logging
import math
import os
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# プロジェクトのsrcディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from data_store import DataStore


class StatisticsAnalyzer:
    """統計分析クラス"""

    def __init__(self, data_store: DataStore):
        """
        統計分析クラスの初期化

        Args:
            data_store: データストレージインスタンス
        """
        self.data_store = data_store
        self.config = get_config()
        self.logger = logging.getLogger(__name__)

    def get_basic_statistics(self) -> Dict[str, Any]:
        """
        基本統計情報を取得する

        Returns:
            基本統計情報
        """
        data = self.data_store.get_statistics()
        total_stats = data['total_statistics']

        basic_stats = {
            'total_keystrokes': total_stats['total_keystrokes'],
            'first_record_date': total_stats['first_record_date'],
            'last_record_date': total_stats['last_record_date'],
            'unique_keys': len(data['key_statistics']),
            'version': total_stats.get('version', '1.0')
        }

        # 記録期間の計算
        if total_stats['first_record_date'] and total_stats['last_record_date']:
            first_date = datetime.fromisoformat(total_stats['first_record_date'])
            last_date = datetime.fromisoformat(total_stats['last_record_date'])
            days = (last_date - first_date).days + 1

            basic_stats['recording_days'] = days
            basic_stats['average_keystrokes_per_day'] = (
                total_stats['total_keystrokes'] / days if days > 0 else 0
            )
        else:
            basic_stats['recording_days'] = 0
            basic_stats['average_keystrokes_per_day'] = 0

        return basic_stats

    def get_top_keys_analysis(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        使用頻度上位キーの分析

        Args:
            limit: 取得する上位件数

        Returns:
            上位キーの詳細分析
        """
        top_keys = self.data_store.get_top_keys(limit)
        total_keystrokes = self.get_basic_statistics()['total_keystrokes']

        # パーセンテージと詳細情報を追加
        for key_info in top_keys:
            key_info['percentage'] = (
                (key_info['count'] / total_keystrokes * 100)
                if total_keystrokes > 0 else 0
            )

            # プログレスバー文字列を生成
            key_info['progress_bar'] = self._generate_progress_bar(
                key_info['percentage'], max_width=20
            )

        return top_keys

    def get_modifier_analysis(self) -> Dict[str, Any]:
        """
        モディファイアキー組み合わせの分析

        Returns:
            モディファイア分析結果
        """
        modifier_stats = self.data_store.get_modifier_analysis()
        total_keystrokes = sum(modifier_stats.values())

        analysis = {
            'total_with_modifiers': total_keystrokes,
            'combinations': []
        }

        # 組み合わせ別の詳細分析
        for modifier, count in sorted(modifier_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_keystrokes * 100) if total_keystrokes > 0 else 0

            analysis['combinations'].append({
                'modifier': modifier,
                'display_name': self._get_modifier_display_name(modifier),
                'count': count,
                'percentage': percentage,
                'progress_bar': self._generate_progress_bar(percentage, max_width=15)
            })

        return analysis

    def get_sequence_analysis(self, sequence_type: str = "bigrams", limit: int = 10) -> Dict[str, Any]:
        """
        シーケンス分析

        Args:
            sequence_type: シーケンスタイプ（'bigrams' または 'trigrams'）
            limit: 取得する上位件数

        Returns:
            シーケンス分析結果
        """
        sequences = self.data_store.get_sequence_analysis(sequence_type)

        if not sequences:
            return {
                'sequence_type': sequence_type,
                'total_sequences': 0,
                'unique_sequences': 0,
                'top_sequences': []
            }

        total_sequences = sum(seq['count'] for seq in sequences)

        # 上位のシーケンスに詳細情報を追加
        top_sequences = []
        for seq in sequences[:limit]:
            percentage = (seq['count'] / total_sequences * 100) if total_sequences > 0 else 0

            top_sequences.append({
                'sequence': seq['sequence'],
                'sequence_key': seq['sequence_key'],
                'count': seq['count'],
                'percentage': percentage,
                'progress_bar': self._generate_progress_bar(percentage, max_width=15)
            })

        return {
            'sequence_type': sequence_type,
            'total_sequences': total_sequences,
            'unique_sequences': len(sequences),
            'top_sequences': top_sequences
        }

    def get_typing_pattern_analysis(self) -> Dict[str, Any]:
        """
        タイピングパターンの分析

        Returns:
            タイピングパターン分析結果
        """
        data = self.data_store.get_statistics()
        key_stats = data['key_statistics']

        # キー種別の分類
        letter_count = 0
        number_count = 0
        special_count = 0

        for key_code, stats in key_stats.items():
            vk = int(key_code)
            count = stats['count']

            if 65 <= vk <= 90:  # A-Z
                letter_count += count
            elif 48 <= vk <= 57:  # 0-9
                number_count += count
            else:
                special_count += count

        total = letter_count + number_count + special_count

        pattern_analysis = {
            'letter_usage': {
                'count': letter_count,
                'percentage': (letter_count / total * 100) if total > 0 else 0
            },
            'number_usage': {
                'count': number_count,
                'percentage': (number_count / total * 100) if total > 0 else 0
            },
            'special_usage': {
                'count': special_count,
                'percentage': (special_count / total * 100) if total > 0 else 0
            }
        }

        # 文字使用パターンの分析
        if letter_count > 0:
            pattern_analysis['letter_distribution'] = self._analyze_letter_distribution(key_stats)

        return pattern_analysis

    def get_efficiency_analysis(self) -> Dict[str, Any]:
        """
        タイピング効率の分析

        Returns:
            効率分析結果
        """
        data = self.data_store.get_statistics()

        # ホームポジションキーの使用率
        home_row_keys = ['65', '83', '68', '70', '74', '75', '76']  # A, S, D, F, J, K, L
        home_row_usage = sum(
            data['key_statistics'].get(key, {}).get('count', 0)
            for key in home_row_keys
        )

        total_keystrokes = data['total_statistics']['total_keystrokes']
        home_row_percentage = (
            (home_row_usage / total_keystrokes * 100)
            if total_keystrokes > 0 else 0
        )

        # 左右の手の使用バランス
        left_hand_keys = ['81', '87', '69', '82', '84', '65', '83', '68', '70', '90', '88', '67', '86']
        right_hand_keys = ['89', '85', '73', '79', '80', '72', '74', '75', '76', '78', '77']

        left_hand_usage = sum(
            data['key_statistics'].get(key, {}).get('count', 0)
            for key in left_hand_keys
        )
        right_hand_usage = sum(
            data['key_statistics'].get(key, {}).get('count', 0)
            for key in right_hand_keys
        )

        total_hand_usage = left_hand_usage + right_hand_usage

        efficiency_analysis = {
            'home_row_usage': {
                'count': home_row_usage,
                'percentage': home_row_percentage,
                'recommendation': self._get_home_row_recommendation(home_row_percentage)
            },
            'hand_balance': {
                'left_hand': {
                    'count': left_hand_usage,
                    'percentage': (left_hand_usage / total_hand_usage * 100) if total_hand_usage > 0 else 0
                },
                'right_hand': {
                    'count': right_hand_usage,
                    'percentage': (right_hand_usage / total_hand_usage * 100) if total_hand_usage > 0 else 0
                },
                'balance_score': self._calculate_balance_score(left_hand_usage, right_hand_usage)
            }
        }

        return efficiency_analysis

    def get_comprehensive_report(self) -> Dict[str, Any]:
        """
        包括的な分析レポートを生成

        Returns:
            包括的分析レポート
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'basic_statistics': self.get_basic_statistics(),
            'top_keys': self.get_top_keys_analysis(),
            'modifier_analysis': self.get_modifier_analysis(),
            'bigram_analysis': self.get_sequence_analysis('bigrams'),
            'trigram_analysis': self.get_sequence_analysis('trigrams'),
            'typing_patterns': self.get_typing_pattern_analysis(),
            'efficiency_analysis': self.get_efficiency_analysis()
        }

        # 改善提案を追加
        report['recommendations'] = self._generate_recommendations(report)

        return report

    def _generate_progress_bar(self, percentage: float, max_width: int = 20) -> str:
        """
        パーセンテージからプログレスバーを生成

        Args:
            percentage: パーセンテージ
            max_width: 最大幅

        Returns:
            プログレスバー文字列
        """
        filled_width = int((percentage / 100) * max_width)
        bar = '█' * filled_width + '░' * (max_width - filled_width)
        return bar

    def _get_modifier_display_name(self, modifier: str) -> str:
        """モディファイアの表示名を取得"""
        display_names = {
            'none': '通常入力',
            'ctrl': 'Ctrl+キー',
            'shift': 'Shift+キー',
            'alt': 'Alt+キー',
            'win': 'Win+キー',
            'ctrl+shift': 'Ctrl+Shift+キー',
            'ctrl+alt': 'Ctrl+Alt+キー',
            'ctrl+win': 'Ctrl+Win+キー',
            'shift+alt': 'Shift+Alt+キー',
            'shift+win': 'Shift+Win+キー',
            'alt+win': 'Alt+Win+キー',
            'ctrl+shift+alt': 'Ctrl+Shift+Alt+キー',
            'ctrl+shift+win': 'Ctrl+Shift+Win+キー',
            'ctrl+alt+win': 'Ctrl+Alt+Win+キー',
            'shift+alt+win': 'Shift+Alt+Win+キー',
            'ctrl+shift+alt+win': 'Ctrl+Shift+Alt+Win+キー'
        }
        return display_names.get(modifier, modifier)

    def _analyze_letter_distribution(self, key_stats: Dict[str, Any]) -> Dict[str, Any]:
        """文字使用分布の分析"""
        vowels = ['65', '69', '73', '79', '85']  # A, E, I, O, U
        consonants = []

        # 子音のVirtual Key Codeを生成
        for vk in range(65, 91):  # A-Z
            if str(vk) not in vowels:
                consonants.append(str(vk))

        vowel_count = sum(key_stats.get(vk, {}).get('count', 0) for vk in vowels)
        consonant_count = sum(key_stats.get(vk, {}).get('count', 0) for vk in consonants)

        total_letters = vowel_count + consonant_count

        return {
            'vowels': {
                'count': vowel_count,
                'percentage': (vowel_count / total_letters * 100) if total_letters > 0 else 0
            },
            'consonants': {
                'count': consonant_count,
                'percentage': (consonant_count / total_letters * 100) if total_letters > 0 else 0
            }
        }

    def _get_home_row_recommendation(self, percentage: float) -> str:
        """ホームポジション使用率に基づく推奨事項"""
        if percentage >= 40:
            return "優秀: ホームポジションをよく活用しています"
        elif percentage >= 30:
            return "良好: ホームポジションの使用率が良いです"
        elif percentage >= 20:
            return "普通: ホームポジションの使用を意識してみましょう"
        else:
            return "改善の余地あり: ホームポジションのタイピング練習をお勧めします"

    def _calculate_balance_score(self, left_usage: int, right_usage: int) -> float:
        """左右の手の使用バランススコアを計算"""
        if left_usage + right_usage == 0:
            return 0.0

        total = left_usage + right_usage
        left_ratio = left_usage / total
        right_ratio = right_usage / total

        # 理想的なバランス（50:50）からの偏差を計算
        deviation = abs(left_ratio - 0.5) * 2
        balance_score = (1 - deviation) * 100

        return max(0, balance_score)

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """分析結果に基づく改善提案を生成"""
        recommendations = []

        # ホームポジション使用率に基づく提案
        home_row_percentage = report['efficiency_analysis']['home_row_usage']['percentage']
        if home_row_percentage < 30:
            recommendations.append(
                "ホームポジションタイピングの練習をお勧めします。タイピング効率が向上します。"
            )

        # 手のバランスに基づく提案
        balance_score = report['efficiency_analysis']['hand_balance']['balance_score']
        if balance_score < 70:
            left_percentage = report['efficiency_analysis']['hand_balance']['left_hand']['percentage']
            if left_percentage > 60:
                recommendations.append(
                    "右手の使用が少ないようです。両手をバランスよく使う練習をしてみましょう。"
                )
            elif left_percentage < 40:
                recommendations.append(
                    "左手の使用が少ないようです。両手をバランスよく使う練習をしてみましょう。"
                )

        # モディファイアキー使用に基づく提案
        modifier_analysis = report['modifier_analysis']
        ctrl_usage = next(
            (combo['percentage'] for combo in modifier_analysis['combinations']
             if combo['modifier'] == 'ctrl'),
            0
        )
        if ctrl_usage > 15:
            recommendations.append(
                "Ctrlキーを頻繁に使用しています。ショートカットキーを効率的に活用していますね。"
            )

        # シーケンス分析に基づく提案
        bigram_analysis = report['bigram_analysis']
        if bigram_analysis['unique_sequences'] > 100:
            recommendations.append(
                "多様な文字パターンを使用しています。バリエーション豊かなタイピングです。"
            )

        if not recommendations:
            recommendations.append("現在のタイピングパターンは良好です。この調子を維持しましょう。")

        return recommendations

    def export_analysis_report(self, file_path: str, format_type: str = "json") -> bool:
        """
        分析レポートをエクスポート

        Args:
            file_path: エクスポート先ファイル
            format_type: エクスポート形式

        Returns:
            エクスポートが成功したかどうか
        """
        try:
            report = self.get_comprehensive_report()

            if format_type == "json":
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)

            elif format_type == "txt":
                self._export_text_report(report, file_path)

            else:
                raise ValueError(f"サポートされていない形式: {format_type}")

            self.logger.info(f"分析レポートをエクスポートしました: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"分析レポートのエクスポートに失敗しました: {e}")
            return False

    def _export_text_report(self, report: Dict[str, Any], file_path: str) -> None:
        """テキスト形式で分析レポートをエクスポート"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("キーボード使用分析レポート\n")
            f.write("=" * 50 + "\n\n")

            # 基本統計
            basic = report['basic_statistics']
            f.write("基本統計:\n")
            f.write(f"  総キーストローク数: {basic['total_keystrokes']:,}\n")
            f.write(f"  記録期間: {basic['recording_days']} 日\n")
            f.write(f"  1日平均: {basic['average_keystrokes_per_day']:.1f} 回\n\n")

            # トップキー
            f.write("使用頻度上位キー:\n")
            for i, key in enumerate(report['top_keys'], 1):
                f.write(f"  {i:2}. {key['key_name']:8}: {key['count']:6,} 回 ({key['percentage']:5.1f}%)\n")
            f.write("\n")

            # 改善提案
            f.write("改善提案:\n")
            for i, rec in enumerate(report['recommendations'], 1):
                f.write(f"  {i}. {rec}\n")
            f.write("\n")

            f.write(f"レポート生成日時: {report['generated_at']}\n")
