from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    # Data generation
    stock_symbols: list[str] = field(default_factory=lambda: ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"])
    base_prices: dict[str, float] = field(
        default_factory=lambda: {
            "AAPL": 180.0,
            "MSFT": 420.0,
            "GOOGL": 165.0,
            "AMZN": 190.0,
            "NVDA": 900.0,
        }
    )
    volume_range: tuple[int, int] = (100, 5000)
    records_per_second: float = 20.0
    total_records: int = 200

    # Processing
    moving_average_window: int = 10
    volatility_window: int = 10
    batch_window_seconds: int = 5

    # Unique feature: adaptive streaming controller
    adaptive_rate_enabled: bool = True
    min_records_per_second: float = 5.0
    max_records_per_second: float = 40.0
    target_processing_latency_ms: float = 25.0

    # Storage
    output_dir: Path = Path("output")
    csv_raw_file: str = "raw_stream.csv"
    csv_processed_file: str = "processed_stream.csv"
    sqlite_file: str = "financial_pipeline.db"

    # ML
    model_file: str = "linear_model.joblib"

    # Visualization
    chart_dir: Path = Path("output/charts")

    def ensure_directories(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chart_dir.mkdir(parents=True, exist_ok=True)
