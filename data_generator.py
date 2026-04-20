import random
import time
from collections.abc import Generator
from datetime import datetime, timezone

from config import Config


class FinancialDataGenerator:
    """Generates synthetic financial tick data with random-walk price movements."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.current_prices = dict(config.base_prices)

    def _next_price(self, symbol: str) -> float:
        current = self.current_prices[symbol]
        drift = random.uniform(-0.0005, 0.0005)
        shock = random.gauss(0, 0.004)
        next_price = max(1.0, current * (1 + drift + shock))
        self.current_prices[symbol] = next_price
        return round(next_price, 2)

    def stream(self, num_records: int | None = None, records_per_second: float | None = None) -> Generator[dict, None, None]:
        total = num_records or self.config.total_records
        rate = records_per_second or self.config.records_per_second
        sleep_time = 1.0 / max(rate, 0.001)

        for _ in range(total):
            symbol = random.choice(self.config.stock_symbols)
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stock_symbol": symbol,
                "price": self._next_price(symbol),
                "volume": random.randint(*self.config.volume_range),
            }
            yield record
            time.sleep(sleep_time)
