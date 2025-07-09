"""
Market Impact Analysis Example

This example demonstrates market impact analysis, including:
- Temporary vs. permanent impact
- Square-root law validation
- Impact decay analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LinearRegression


def simulate_market_impact():
    """Simulate market impact scenarios."""
    
    print("Market Impact Analysis")
    print("=" * 50)
    
    # Generate synthetic trade data with known impact
    np.random.seed(42)
    
    # Trade sizes (in shares)
    trade_sizes = np.random.lognormal(mean=5, sigma=1, size=1000)
    trade_sizes = np.round(trade_sizes).astype(int)
    
    # Base price
    base_price = 100.0
    
    # Impact parameters
    temp_impact_coef = 0.001  # Temporary impact coefficient
    perm_impact_coef = 0.0005  # Permanent impact coefficient
    decay_rate = 0.1  # Impact decay rate
    
    # Generate trades with impact
    trades = []
    current_price = base_price
    
    for i, size in enumerate(trade_sizes):
        # Calculate impact
        temp_impact = temp_impact_coef * np.sign(np.random.randn()) * size**0.5
        perm_impact = perm_impact_coef * np.sign(np.random.randn()) * size**0.5
        
        # Apply impact
        trade_price = current_price + temp_impact
        current_price += perm_impact
        
        # Add some noise
        trade_price += np.random.normal(0, 0.01)
        
        trades.append({
            'trade_id': f'trade_{i}',
            'size': size,
            'price': trade_price,
            'temp_impact': temp_impact,
            'perm_impact': perm_impact,
            'timestamp': i
        })
    
    return pd.DataFrame(trades)


def analyze_square_root_law(trades_df):
    """Analyze the square-root law of market impact."""
    
    print("Square-Root Law Analysis")
    print("-" * 30)
    
    # Calculate absolute price changes
    trades_df['abs_impact'] = np.abs(trades_df['price'] - 100.0)
    
    # Fit square-root law: |Δp| = α * Q^β
    log_sizes = np.log(trades_df['size'])
    log_impacts = np.log(trades_df['abs_impact'] + 1e-10)
    
    # Linear regression
    X = log_sizes.reshape(-1, 1)
    y = log_impacts
    
    model = LinearRegression()
    model.fit(X, y)
    
    alpha = np.exp(model.intercept_)
    beta = model.coef_[0]
    
    print(f"Square-root law parameters:")
    print(f"  α (coefficient): {alpha:.6f}")
    print(f"  β (exponent): {beta:.3f}")
    print(f"  Theoretical β: 0.5")
    print(f"  R²: {model.score(X, y):.3f}")
    print()
    
    return alpha, beta, model


def analyze_impact_decay(trades_df):
    """Analyze impact decay over time."""
    
    print("Impact Decay Analysis")
    print("-" * 30)
    
    # Group trades by size and analyze decay
    size_groups = trades_df.groupby(pd.cut(trades_df['size'], bins=5))
    
    decay_analysis = []
    
    for size_bin, group in size_groups:
        if len(group) < 10:
            continue
        
        # Calculate average impact over time
        group = group.sort_values('timestamp')
        group['cumulative_impact'] = group['temp_impact'].cumsum()
        
        # Fit exponential decay
        times = group['timestamp'].values
        impacts = group['cumulative_impact'].values
        
        if len(impacts) > 1:
            try:
                # Fit exponential decay: I(t) = I₀ * e^(-λt)
                log_impacts = np.log(np.abs(impacts) + 1e-10)
                slope, intercept, r_value, p_value, std_err = stats.linregress(times, log_impacts)
                
                decay_rate = -slope
                decay_analysis.append({
                    'size_bin': size_bin,
                    'decay_rate': decay_rate,
                    'r_squared': r_value**2,
                    'avg_size': group['size'].mean()
                })
            except:
                continue
    
    decay_df = pd.DataFrame(decay_analysis)
    
    if len(decay_df) > 0:
        print("Impact decay rates by trade size:")
        for _, row in decay_df.iterrows():
            print(f"  Size {row['size_bin']}: λ = {row['decay_rate']:.3f} (R² = {row['r_squared']:.3f})")
        print()
    
    return decay_df


def create_impact_visualizations(trades_df, alpha, beta, decay_df):
    """Create visualizations for market impact analysis."""
    
    print("Creating Impact Analysis Visualizations...")
    print("=" * 50)
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Market Impact Analysis', fontsize=16)
    
    # 1. Square-root law validation
    axes[0, 0].scatter(trades_df['size'], trades_df['abs_impact'], alpha=0.6, s=20)
    
    # Plot fitted curve
    size_range = np.linspace(trades_df['size'].min(), trades_df['size'].max(), 100)
    fitted_impact = alpha * size_range**beta
    axes[0, 0].plot(size_range, fitted_impact, 'r-', linewidth=2, label=f'Fitted: α={alpha:.6f}, β={beta:.3f}')
    
    axes[0, 0].set_xlabel('Trade Size')
    axes[0, 0].set_ylabel('Absolute Price Impact')
    axes[0, 0].set_title('Square-Root Law Validation')
    axes[0, 0].set_xscale('log')
    axes[0, 0].set_yscale('log')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Impact vs. Size (log-log)
    axes[0, 1].scatter(np.log(trades_df['size']), np.log(trades_df['abs_impact']), alpha=0.6, s=20)
    
    # Plot fitted line
    log_sizes = np.log(trades_df['size'])
    log_impacts = np.log(trades_df['abs_impact'] + 1e-10)
    model = LinearRegression()
    model.fit(log_sizes.reshape(-1, 1), log_impacts)
    log_size_range = np.linspace(log_sizes.min(), log_sizes.max(), 100)
    fitted_log_impact = model.predict(log_size_range.reshape(-1, 1))
    axes[0, 1].plot(log_size_range, fitted_log_impact, 'r-', linewidth=2)
    
    axes[0, 1].set_xlabel('Log(Trade Size)')
    axes[0, 1].set_ylabel('Log(Price Impact)')
    axes[0, 1].set_title('Log-Log Relationship')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Impact distribution
    axes[1, 0].hist(trades_df['abs_impact'], bins=30, alpha=0.7, color='green')
    axes[1, 0].set_xlabel('Absolute Price Impact')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Impact Distribution')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Decay rates by size
    if len(decay_df) > 0:
        axes[1, 1].scatter(decay_df['avg_size'], decay_df['decay_rate'], s=100, alpha=0.7)
        axes[1, 1].set_xlabel('Average Trade Size')
        axes[1, 1].set_ylabel('Decay Rate (λ)')
        axes[1, 1].set_title('Impact Decay by Trade Size')
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('market_impact_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Visualization saved as 'market_impact_analysis.png'")
    print()


def analyze_temporary_vs_permanent_impact(trades_df):
    """Analyze temporary vs. permanent impact components."""
    
    print("Temporary vs. Permanent Impact Analysis")
    print("-" * 40)
    
    # Calculate impact components
    trades_df['total_impact'] = trades_df['temp_impact'] + trades_df['perm_impact']
    
    # Statistics
    temp_impact_mean = trades_df['temp_impact'].mean()
    perm_impact_mean = trades_df['perm_impact'].mean()
    temp_impact_std = trades_df['temp_impact'].std()
    perm_impact_std = trades_df['perm_impact'].std()
    
    print(f"Temporary Impact:")
    print(f"  Mean: {temp_impact_mean:.6f}")
    print(f"  Std:  {temp_impact_std:.6f}")
    print()
    
    print(f"Permanent Impact:")
    print(f"  Mean: {perm_impact_mean:.6f}")
    print(f"  Std:  {perm_impact_std:.6f}")
    print()
    
    print(f"Impact Ratio (Temp/Perm): {abs(temp_impact_mean/perm_impact_mean):.2f}")
    print()
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Temporary vs Permanent scatter
    ax1.scatter(trades_df['temp_impact'], trades_df['perm_impact'], alpha=0.6, s=20)
    ax1.set_xlabel('Temporary Impact')
    ax1.set_ylabel('Permanent Impact')
    ax1.set_title('Temporary vs. Permanent Impact')
    ax1.grid(True, alpha=0.3)
    
    # Add diagonal line for reference
    impact_range = np.linspace(trades_df['temp_impact'].min(), trades_df['temp_impact'].max(), 100)
    ax1.plot(impact_range, impact_range, 'r--', alpha=0.5, label='y=x')
    ax1.legend()
    
    # Impact components by trade size
    size_bins = pd.cut(trades_df['size'], bins=5)
    impact_by_size = trades_df.groupby(size_bins)[['temp_impact', 'perm_impact']].mean()
    
    x_pos = np.arange(len(impact_by_size))
    width = 0.35
    
    ax2.bar(x_pos - width/2, impact_by_size['temp_impact'], width, label='Temporary', alpha=0.7)
    ax2.bar(x_pos + width/2, impact_by_size['perm_impact'], width, label='Permanent', alpha=0.7)
    
    ax2.set_xlabel('Trade Size Bins')
    ax2.set_ylabel('Average Impact')
    ax2.set_title('Impact Components by Trade Size')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels([str(bin) for bin in impact_by_size.index], rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('impact_components_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Impact components visualization saved as 'impact_components_analysis.png'")
    print()


def main():
    """Main function for market impact analysis."""
    
    print("Market Impact Analysis Example")
    print("=" * 60)
    print()
    
    # Generate synthetic trade data
    trades_df = simulate_market_impact()
    
    # Analyze square-root law
    alpha, beta, model = analyze_square_root_law(trades_df)
    
    # Analyze impact decay
    decay_df = analyze_impact_decay(trades_df)
    
    # Create visualizations
    create_impact_visualizations(trades_df, alpha, beta, decay_df)
    
    # Analyze temporary vs permanent impact
    analyze_temporary_vs_permanent_impact(trades_df)
    
    print("Market impact analysis completed!")
    print("Check the generated files:")
    print("  - market_impact_analysis.png")
    print("  - impact_components_analysis.png")


if __name__ == "__main__":
    main() 