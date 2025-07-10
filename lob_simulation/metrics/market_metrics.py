"""
Market Metrics

Market quality metrics and statistics.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from scipy import stats

from .base import BaseMetrics


@dataclass
class MarketMetrics(BaseMetrics):
    """Market quality metrics and statistics."""
    
    # Price statistics
    price_volatility: float = 0.0
    price_trend: float = 0.0
    price_efficiency: float = 0.0
    
    # Volume statistics
    total_volume: int = 0
    avg_trade_size: float = 0.0
    volume_imbalance: float = 0.0
    
    # Spread statistics
    avg_spread: float = 0.0
    spread_volatility: float = 0.0
    effective_spread: float = 0.0
    
    # Trade statistics
    num_trades: int = 0
    trade_frequency: float = 0.0
    trade_size_distribution: Dict[str, float] = field(default_factory=dict)
    
    def calculate(self, price_df: pd.DataFrame, spread_df: pd.DataFrame, 
                  volume_df: pd.DataFrame, trades_df: pd.DataFrame):
        """Calculate all market metrics."""
        self._calculate_price_metrics(price_df)
        self._calculate_volume_metrics(volume_df, trades_df)
        self._calculate_spread_metrics(spread_df, trades_df)
        self._calculate_trade_metrics(trades_df)
    
    def _calculate_price_metrics(self, price_df: pd.DataFrame):
        """Calculate price-related metrics."""
        if len(price_df) < 2:
            return
        
        # Price volatility (standard deviation of returns)
        returns = price_df['mid_price'].pct_change().dropna()
        self.price_volatility = returns.std() * np.sqrt(252 * 24 * 3600)  # Annualized
        
        # Price trend (linear regression slope)
        x = np.arange(len(price_df))
        y = price_df['mid_price'].values
        slope, _, _, _, _ = stats.linregress(x, y)
        self.price_trend = slope
        
        # Price efficiency (random walk test)
        self.price_efficiency = self._calculate_efficiency_ratio(returns)
    
    def _calculate_volume_metrics(self, volume_df: pd.DataFrame, trades_df: pd.DataFrame):
        """Calculate volume-related metrics."""
        if len(volume_df) == 0:
            return
        
        # Total volume
        self.total_volume = volume_df['bid_volume'].sum() + volume_df['ask_volume'].sum()
        
        # Volume imbalance
        bid_volume = volume_df['bid_volume'].sum()
        ask_volume = volume_df['ask_volume'].sum()
        total_vol = bid_volume + ask_volume
        if total_vol > 0:
            self.volume_imbalance = (bid_volume - ask_volume) / total_vol
        
        # Average trade size
        if len(trades_df) > 0:
            self.avg_trade_size = trades_df['quantity'].mean()
    
    def _calculate_spread_metrics(self, spread_df: pd.DataFrame, trades_df: pd.DataFrame):
        """Calculate spread-related metrics."""
        if len(spread_df) == 0:
            return
        
        # Average spread
        self.avg_spread = spread_df['spread'].mean()
        
        # Spread volatility
        self.spread_volatility = spread_df['spread'].std()
        
        # Effective spread (if trades data available)
        if len(trades_df) > 0:
            self.effective_spread = self._calculate_effective_spread(trades_df)
    
    def _calculate_trade_metrics(self, trades_df: pd.DataFrame):
        """Calculate trade-related metrics."""
        if len(trades_df) == 0:
            return
        
        self.num_trades = len(trades_df)
        
        # Trade frequency (trades per second)
        if len(trades_df) > 1:
            time_span = trades_df['timestamp'].max() - trades_df['timestamp'].min()
            if time_span > 0:
                self.trade_frequency = self.num_trades / time_span
        
        # Trade size distribution
        quantities = trades_df['quantity'].values
        self.trade_size_distribution = {
            'mean': np.mean(quantities),
            'median': np.median(quantities),
            'std': np.std(quantities),
            'min': np.min(quantities),
            'max': np.max(quantities),
            'q25': np.percentile(quantities, 25),
            'q75': np.percentile(quantities, 75)
        }
    
    def _calculate_efficiency_ratio(self, returns: pd.Series) -> float:
        """Calculate price efficiency ratio."""
        if len(returns) < 2:
            return 0.0
        
        # Variance ratio test
        var_1 = returns.var()
        var_k = returns.rolling(window=5).mean().var()
        
        if var_1 > 0:
            return var_k / var_1
        return 0.0
    
    def _calculate_effective_spread(self, trades_df: pd.DataFrame) -> float:
        """Calculate effective spread from trades."""
        # This is a simplified calculation
        # In practice, you'd need bid/ask quotes at trade time
        return self.avg_spread  # Placeholder
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        return {
            'price_metrics': {
                'volatility': self.price_volatility,
                'trend': self.price_trend,
                'efficiency': self.price_efficiency
            },
            'volume_metrics': {
                'total_volume': self.total_volume,
                'avg_trade_size': self.avg_trade_size,
                'imbalance': self.volume_imbalance
            },
            'spread_metrics': {
                'avg_spread': self.avg_spread,
                'spread_volatility': self.spread_volatility,
                'effective_spread': self.effective_spread
            },
            'trade_metrics': {
                'num_trades': self.num_trades,
                'trade_frequency': self.trade_frequency,
                'size_distribution': self.trade_size_distribution
            }
        } 