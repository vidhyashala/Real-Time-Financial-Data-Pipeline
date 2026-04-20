import csv
import sqlite3
from pathlib import Path


class StorageManager:
    def __init__(self, db_path: Path, raw_csv_path: Path, processed_csv_path: Path) -> None:
        self.db_path = db_path
        self.raw_csv_path = raw_csv_path
        self.processed_csv_path = processed_csv_path
        self._initialize_db()

    def _initialize_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS raw_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    stock_symbol TEXT,
                    price REAL,
                    volume INTEGER
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    stock_symbol TEXT,
                    price REAL,
                    volume INTEGER,
                    moving_average REAL,
                    volatility REAL,
                    price_change_pct REAL
                )
                """
            )
            conn.commit()

    @staticmethod
    def _append_csv(path: Path, row: dict, fieldnames: list[str]) -> None:
        file_exists = path.exists()
        with path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

    def save_raw_record(self, record: dict) -> None:
        self._append_csv(self.raw_csv_path, record, ["timestamp", "stock_symbol", "price", "volume"])
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO raw_data (timestamp, stock_symbol, price, volume) VALUES (?, ?, ?, ?)",
                (record["timestamp"], record["stock_symbol"], record["price"], record["volume"]),
            )
            conn.commit()

    def save_processed_record(self, record: dict) -> None:
        self._append_csv(
            self.processed_csv_path,
            record,
            [
                "timestamp",
                "stock_symbol",
                "price",
                "volume",
                "moving_average",
                "volatility",
                "price_change_pct",
            ],
        )
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO processed_data
                (timestamp, stock_symbol, price, volume, moving_average, volatility, price_change_pct)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["timestamp"],
                    record["stock_symbol"],
                    record["price"],
                    record["volume"],
                    record["moving_average"],
                    record["volatility"],
                    record["price_change_pct"],
                ),
            )
            conn.commit()

    def reset_outputs(self) -> None:
        for path in (self.raw_csv_path, self.processed_csv_path, self.db_path):
            if path.exists():
                path.unlink()
        self._initialize_db()
