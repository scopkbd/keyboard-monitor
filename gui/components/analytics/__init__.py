"""
Analytics components package
"""

from .analytics_page import AnalyticsPage
# from .basic_stats_card import BasicStatsCard  # 現在未使用（ステータスバー表示に統合）
from .key_frequency_card import KeyFrequencyCard
from .modifier_analysis_card import ModifierAnalysisCard

__all__ = [
    # 'BasicStatsCard',  # 現在未使用
    'KeyFrequencyCard',
    'ModifierAnalysisCard',
    'AnalyticsPage'
]