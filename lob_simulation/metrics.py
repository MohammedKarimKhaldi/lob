"""
Market Quality Metrics and Analysis

This module implements comprehensive market quality metrics including:
- Liquidity measures (spread, depth, resilience)
- Price impact analysis (square-root law)
- Market microstructure statistics
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from scipy import stats
from sklearn.linear_model import LinearRegression


@dataclass
class MarketMetrics:
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
    trade_size_distribution: Dict[str, float] = None
    
    def __post_init__(self):
        if self.trade_size_distribution is None:
            self.trade_size_distribution = {}
    
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


@dataclass
class LiquidityMetrics:
    """Liquidity provision and market depth metrics."""
    
    # Market depth
    avg_depth: float = 0.0
    depth_imbalance: float = 0.0
    depth_volatility: float = 0.0
    
    # Liquidity resilience
    resilience_score: float = 0.0
    recovery_time: float = 0.0
    
    # Order book statistics
    order_flow_imbalance: float = 0.0
    order_cancellation_rate: float = 0.0
    
    def calculate(self, orderbook, price_df: pd.DataFrame, volume_df: pd.DataFrame):
        """Calculate liquidity metrics."""
        self._calculate_depth_metrics(volume_df)
        self._calculate_resilience_metrics(price_df, volume_df)
        self._calculate_order_flow_metrics(orderbook)
    
    def _calculate_depth_metrics(self, volume_df: pd.DataFrame):
        """Calculate market depth metrics."""
        if len(volume_df) == 0:
            return
        
        # Average depth
        total_depth = volume_df['bid_volume'] + volume_df['ask_volume']
        self.avg_depth = total_depth.mean()
        
        # Depth imbalance
        bid_depth = volume_df['bid_volume'].mean()
        ask_depth = volume_df['ask_volume'].mean()
        total_avg_depth = bid_depth + ask_depth
        
        if total_avg_depth > 0:
            self.depth_imbalance = (bid_depth - ask_depth) / total_avg_depth
        
        # Depth volatility
        self.depth_volatility = total_depth.std()
    
    def _calculate_resilience_metrics(self, price_df: pd.DataFrame, volume_df: pd.DataFrame):
        """Calculate market resilience metrics."""
        if len(price_df) < 10 or len(volume_df) < 10:
            return
        
        # Simple resilience measure based on price recovery after volume shocks
        price_changes = price_df['mid_price'].pct_change().abs()
        volume_changes = volume_df['bid_volume'] + volume_df['ask_volume']
        volume_changes = volume_changes.pct_change().abs()
        
        # Correlation between price changes and volume changes
        correlation = price_changes.corr(volume_changes)
        self.resilience_score = 1 - abs(correlation) if not np.isnan(correlation) else 0.0
        
        # Recovery time (simplified)
        self.recovery_time = self._estimate_recovery_time(price_df)
    
    def _calculate_order_flow_metrics(self, orderbook):
        """Calculate order flow metrics."""
        # This would require more detailed order flow data
        # For now, use placeholder values
        self.order_flow_imbalance = 0.0
        self.order_cancellation_rate = 0.1  # 10% cancellation rate
    
    def _estimate_recovery_time(self, price_df: pd.DataFrame) -> float:
        """Estimate market recovery time after shocks."""
        if len(price_df) < 20:
            return 0.0
        
        # Simple approach: measure time to return to moving average
        ma = price_df['mid_price'].rolling(window=10).mean()
        deviations = (price_df['mid_price'] - ma).abs()
        
        # Find periods of high deviation and measure recovery
        threshold = deviations.quantile(0.9)
        high_deviation = deviations > threshold
        
        if high_deviation.sum() == 0:
            return 0.0
        
        # Calculate average time to return to MA
        recovery_times = []
        in_deviation = False
        start_time = 0
        
        for i, dev in enumerate(high_deviation):
            if dev and not in_deviation:
                in_deviation = True
                start_time = i
            elif not dev and in_deviation:
                in_deviation = False
                recovery_times.append(i - start_time)
        
        return np.mean(recovery_times) if recovery_times else 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of liquidity metrics."""
        return {
            'depth_metrics': {
                'avg_depth': self.avg_depth,
                'depth_imbalance': self.depth_imbalance,
                'depth_volatility': self.depth_volatility
            },
            'resilience_metrics': {
                'resilience_score': self.resilience_score,
                'recovery_time': self.recovery_time
            },
            'order_flow_metrics': {
                'order_flow_imbalance': self.order_flow_imbalance,
                'cancellation_rate': self.order_cancellation_rate
            }
        }


@dataclass
class ImpactMetrics:
    """Price impact analysis metrics."""
    
    # Impact coefficients
    temporary_impact: float = 0.0
    permanent_impact: float = 0.0
    impact_decay_rate: float = 0.0
    
    # Square-root law parameters
    sqrt_law_coefficient: float = 0.0
    sqrt_law_exponent: float = 0.5
    
    # Cross-impact analysis
    cross_impact_matrix: Optional[np.ndarray] = None
    
    def calculate(self, trades_df: pd.DataFrame, price_df: pd.DataFrame):
        """Calculate price impact metrics."""
        if len(trades_df) == 0 or len(price_df) == 0:
            return
        
        self._calculate_impact_coefficients(trades_df, price_df)
        self._calculate_sqrt_law_parameters(trades_df, price_df)
    
    def _calculate_impact_coefficients(self, trades_df: pd.DataFrame, price_df: pd.DataFrame):
        """Calculate temporary and permanent impact coefficients."""
        if len(trades_df) < 10:
            return
        
        # Calculate price changes around trades
        trade_impacts = []
        
        for _, trade in trades_df.iterrows():
            trade_time = trade['timestamp']
            
            # Find price before and after trade
            before_trade = price_df[price_df['timestamp'] < trade_time]
            after_trade = price_df[price_df['timestamp'] > trade_time]
            
            if len(before_trade) > 0 and len(after_trade) > 0:
                price_before = before_trade['mid_price'].iloc[-1]
                price_after = after_trade['mid_price'].iloc[0]
                
                # Calculate impact
                impact = (price_after - price_before) * np.sign(trade['quantity'])
                trade_impacts.append({
                    'impact': impact,
                    'quantity': abs(trade['quantity']),
                    'time_diff': after_trade['timestamp'].iloc[0] - trade_time
                })
        
        if len(trade_impacts) == 0:
            return
        
        # Separate temporary and permanent impact
        impacts_df = pd.DataFrame(trade_impacts)
        
        # Temporary impact (immediate)
        immediate_impacts = impacts_df[impacts_df['time_diff'] < 1.0]  # Within 1 second
        if len(immediate_impacts) > 0:
            self.temporary_impact = immediate_impacts['impact'].mean()
        
        # Permanent impact (long-term)
        long_term_impacts = impacts_df[impacts_df['time_diff'] > 60.0]  # After 1 minute
        if len(long_term_impacts) > 0:
            self.permanent_impact = long_term_impacts['impact'].mean()
        
        # Impact decay rate
        self.impact_decay_rate = self._estimate_decay_rate(impacts_df)
    
    def _calculate_sqrt_law_parameters(self, trades_df: pd.DataFrame, price_df: pd.DataFrame):
        """Calculate square-root law parameters."""
        if len(trades_df) < 10:
            return
        
        # Prepare data for regression
        quantities = []
        impacts = []
        
        for _, trade in trades_df.iterrows():
            trade_time = trade['timestamp']
            
            # Find price change around trade
            before_trade = price_df[price_df['timestamp'] < trade_time]
            after_trade = price_df[price_df['timestamp'] > trade_time]
            
            if len(before_trade) > 0 and len(after_trade) > 0:
                price_before = before_trade['mid_price'].iloc[-1]
                price_after = after_trade['mid_price'].iloc[0]
                
                impact = abs(price_after - price_before)
                quantity = abs(trade['quantity'])
                
                if impact > 0 and quantity > 0:
                    quantities.append(quantity)
                    impacts.append(impact)
        
        if len(quantities) < 5:
            return
        
        # Fit square-root law: I = α * Q^β
        log_quantities = np.log(quantities)
        log_impacts = np.log(impacts)
        
        # Linear regression
        X = log_quantities.reshape(-1, 1)
        y = log_impacts
        
        try:
            model = LinearRegression()
            model.fit(X, y)
            
            self.sqrt_law_coefficient = np.exp(model.intercept_)
            self.sqrt_law_exponent = model.coef_[0]
        except:
            # Fallback to theoretical values
            self.sqrt_law_coefficient = 0.1
            self.sqrt_law_exponent = 0.5
    
    def _estimate_decay_rate(self, impacts_df: pd.DataFrame) -> float:
        """Estimate impact decay rate."""
        if len(impacts_df) < 10:
            return 0.0
        
        # Group by time difference and calculate average impact
        time_groups = impacts_df.groupby(pd.cut(impacts_df['time_diff'], bins=10))
        avg_impacts = time_groups['impact'].mean()
        
        if len(avg_impacts) < 2:
            return 0.0
        
        # Fit exponential decay: I(t) = I₀ * e^(-λt)
        times = avg_impacts.index.mid.values
        impacts = avg_impacts.values
        
        # Remove any NaN values
        valid_mask = ~(np.isnan(times) | np.isnan(impacts))
        times = times[valid_mask]
        impacts = impacts[valid_mask]
        
        if len(times) < 2:
            return 0.0
        
        # Linear regression on log scale
        log_impacts = np.log(np.abs(impacts) + 1e-10)
        
        try:
            slope, _, _, _, _ = stats.linregress(times, log_impacts)
            return -slope
        except:
            return 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of impact metrics."""
        return {
            'impact_coefficients': {
                'temporary_impact': self.temporary_impact,
                'permanent_impact': self.permanent_impact,
                'decay_rate': self.impact_decay_rate
            },
            'sqrt_law_parameters': {
                'coefficient': self.sqrt_law_coefficient,
                'exponent': self.sqrt_law_exponent
            },
            'cross_impact': {
                'matrix_shape': self.cross_impact_matrix.shape if self.cross_impact_matrix is not None else None
            }
        } 