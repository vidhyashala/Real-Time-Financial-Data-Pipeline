from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LinearRegression


class PricePredictionModel:
    def __init__(self) -> None:
        self.model = LinearRegression()
        self.is_trained = False

    @staticmethod
    def _build_dataset(processed_records: list[dict]) -> tuple[np.ndarray, np.ndarray]:
        # Lightweight autoregressive-style features.
        x_data, y_data = [], []
        for i in range(1, len(processed_records)):
            prev = processed_records[i - 1]
            curr = processed_records[i]
            x_data.append([prev["price"], prev["moving_average"], prev["volatility"], prev["volume"]])
            y_data.append(curr["price"])

        if not x_data:
            return np.empty((0, 4)), np.empty((0,))
        return np.array(x_data, dtype=float), np.array(y_data, dtype=float)

    def train(self, processed_records: list[dict]) -> dict:
        x, y = self._build_dataset(processed_records)
        if len(x) < 5:
            return {"trained": False, "message": "Insufficient data to train model", "mae": None}

        self.model.fit(x, y)
        preds = self.model.predict(x)
        mae = float(np.mean(np.abs(preds - y)))
        self.is_trained = True
        return {"trained": True, "message": "Model trained successfully", "mae": mae}

    def predict_next_price(self, latest_record: dict) -> float | None:
        if not self.is_trained:
            return None
        x = np.array(
            [[latest_record["price"], latest_record["moving_average"], latest_record["volatility"], latest_record["volume"]]],
            dtype=float,
        )
        return float(self.model.predict(x)[0])

    def save(self, model_path: Path) -> None:
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, model_path)

    def load(self, model_path: Path) -> None:
        self.model = joblib.load(model_path)
        self.is_trained = True
