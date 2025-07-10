from typing import Dict, List, Any, Tuple

def update_market_stats(self):
    self.best_bid = self.bid_prices[0] if self.bid_prices else 0.0
    self.best_ask = self.ask_prices[0] if self.ask_prices else float('inf')
    if self.best_bid > 0 and self.best_ask < float('inf'):
        self.mid_price = (self.best_bid + self.best_ask) / 2
        self.spread = self.best_ask - self.best_bid
    else:
        self.mid_price = 0.0
        self.spread = float('inf')

def get_bid_volume(self) -> int:
    if not self.bid_prices:
        return 0
    return self.bid_volume[self.bid_prices[0]]

def get_ask_volume(self) -> int:
    if not self.ask_prices:
        return 0
    return self.ask_volume[self.ask_prices[0]]

def get_depth(self, levels: int = 5) -> Dict[str, List[Tuple[float, int]]]:
    bids = []
    for price in self.bid_prices[:levels]:
        bids.append((price, self.bid_volume[price]))
    asks = []
    for price in self.ask_prices[:levels]:
        asks.append((price, self.ask_volume[price]))
    return {'bids': bids, 'asks': asks}

def get_state(self) -> Dict[str, Any]:
    return {
        'best_bid': self.best_bid,
        'best_ask': self.best_ask,
        'mid_price': self.mid_price,
        'spread': self.spread,
        'bid_volume': get_bid_volume(self),
        'ask_volume': get_ask_volume(self),
        'depth': get_depth(self),
        'num_orders': len(self.orders),
        'num_trades': len(self.trades)
    }

def reset(self):
    self.orders.clear()
    self.bids.clear()
    self.asks.clear()
    self.bid_prices.clear()
    self.ask_prices.clear()
    self.bid_volume.clear()
    self.ask_volume.clear()
    self.trades.clear()
    self.best_bid = 0.0
    self.best_ask = float('inf')
    self.mid_price = 0.0
    self.spread = float('inf')
