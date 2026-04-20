import time
from dataclasses import dataclass

from config import Config
from data_generator import FinancialDataGenerator
from metrics import MetricsCollector
from model import PricePredictionModel
from processor import StreamProcessor
from storage import StorageManager


@dataclass
class PipelineResult:
    processed_records: list[dict]
    metrics: dict
    model_info: dict


class FinancialPipeline:
    def __init__(self, config: Config, storage: StorageManager) -> None:
        self.config = config
        self.generator = FinancialDataGenerator(config)
        self.processor = StreamProcessor(config)
        self.storage = storage
        self.model = PricePredictionModel()

    def _adaptive_rate(self, current_rate: float, latest_latency_ms: float) -> float:
        if not self.config.adaptive_rate_enabled:
            return current_rate

        target = self.config.target_processing_latency_ms
        if latest_latency_ms > target * 1.2:
            current_rate *= 0.9
        elif latest_latency_ms < target * 0.7:
            current_rate *= 1.05

        return max(self.config.min_records_per_second, min(current_rate, self.config.max_records_per_second))

    def run_realtime(self) -> PipelineResult:
        metrics = MetricsCollector(mode="realtime")
        processed_records: list[dict] = []
        current_rate = self.config.records_per_second

        for record in self.generator.stream(num_records=self.config.total_records, records_per_second=current_rate):
            self.storage.save_raw_record(record)

            t0 = time.perf_counter()
            enriched = self.processor.process_record(record)
            latency = time.perf_counter() - t0

            self.storage.save_processed_record(enriched)
            metrics.record_latency(latency)
            processed_records.append(enriched)

            current_rate = self._adaptive_rate(current_rate, latency * 1000.0)

        metrics.stop()
        model_info = self.model.train(processed_records)
        if model_info.get("trained"):
            self.model.save(self.config.output_dir / self.config.model_file)
            prediction = self.model.predict_next_price(processed_records[-1])
            model_info["latest_prediction"] = prediction
            model_info["latest_actual"] = processed_records[-1]["price"]
        return PipelineResult(processed_records=processed_records, metrics=metrics.summary(), model_info=model_info)

    def run_batch(self) -> PipelineResult:
        metrics = MetricsCollector(mode="batch")
        processed_records: list[dict] = []

        buffer: list[dict] = []
        batch_start = time.perf_counter()

        for record in self.generator.stream(num_records=self.config.total_records, records_per_second=self.config.records_per_second):
            self.storage.save_raw_record(record)
            buffer.append(record)

            should_flush = (time.perf_counter() - batch_start) >= self.config.batch_window_seconds
            is_last = (len(processed_records) + len(buffer)) >= self.config.total_records

            if should_flush or is_last:
                bt0 = time.perf_counter()
                enriched_batch = self.processor.process_batch(buffer)
                batch_duration = time.perf_counter() - bt0
                metrics.record_batch_duration(batch_duration)

                per_record_latency = batch_duration / max(len(enriched_batch), 1)
                for enriched in enriched_batch:
                    self.storage.save_processed_record(enriched)
                    metrics.record_latency(per_record_latency)

                processed_records.extend(enriched_batch)
                buffer = []
                batch_start = time.perf_counter()

        metrics.stop()
        model_info = self.model.train(processed_records)
        if model_info.get("trained"):
            self.model.save(self.config.output_dir / self.config.model_file)
            prediction = self.model.predict_next_price(processed_records[-1])
            model_info["latest_prediction"] = prediction
            model_info["latest_actual"] = processed_records[-1]["price"]
        return PipelineResult(processed_records=processed_records, metrics=metrics.summary(), model_info=model_info)
