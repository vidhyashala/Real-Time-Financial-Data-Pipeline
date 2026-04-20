from collections import defaultdict, deque
from statistics import mean, pstdev

from config import Config


class StreamProcessor:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.price_windows: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max(config.moving_average_window, config.volatility_window))
        )
        self.previous_price: dict[str, float] = {}

    def process_record(self, record: dict) -> dict:
        symbol = record["stock_symbol"]
        price = float(record["price"])

        window = self.price_windows[symbol]
        window.append(price)

        ma_window = list(window)[-self.config.moving_average_window :]
        vol_window = list(window)[-self.config.volatility_window :]

        moving_average = mean(ma_window)
        volatility = pstdev(vol_window) if len(vol_window) > 1 else 0.0

        prev = self.previous_price.get(symbol)
        price_change_pct = ((price - prev) / prev * 100.0) if prev else 0.0
        self.previous_price[symbol] = price

        enriched = {
            **record,
            "moving_average": round(moving_average, 4),
            "volatility": round(volatility, 6),
            "price_change_pct": round(price_change_pct, 6),
        }
        return enriched

    def process_batch(self, records: list[dict]) -> list[dict]:
        return [self.process_record(record) for record in records]
