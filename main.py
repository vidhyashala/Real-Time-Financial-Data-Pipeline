import json
from pathlib import Path

import matplotlib.pyplot as plt

from config import Config
from pipeline import FinancialPipeline
from storage import StorageManager


def build_storage(config: Config, suffix: str) -> StorageManager:
    db = config.output_dir / f"{suffix}_{config.sqlite_file}"
    raw = config.output_dir / f"{suffix}_{config.csv_raw_file}"
    processed = config.output_dir / f"{suffix}_{config.csv_processed_file}"
    storage = StorageManager(db, raw, processed)
    storage.reset_outputs()
    return storage


def print_experiment_result(name: str, result: dict, model_info: dict) -> None:
    print(f"\n=== {name} ===")
    print(json.dumps(result, indent=2))
    print("Model info:")
    print(json.dumps(model_info, indent=2, default=str))


def save_comparison_charts(batch_metrics: dict, realtime_metrics: dict, output_dir: Path) -> None:
    labels = ["Batch", "Real-time"]

    latency_values = [batch_metrics["avg_latency_ms"], realtime_metrics["avg_latency_ms"]]
    throughput_values = [batch_metrics["throughput_rps"], realtime_metrics["throughput_rps"]]
    proc_time_values = [batch_metrics["total_duration_sec"], realtime_metrics["total_duration_sec"]]

    charts = [
        ("Latency Comparison (ms)", latency_values, "latency_comparison.png", "Average Latency (ms)"),
        ("Throughput Comparison (records/sec)", throughput_values, "throughput_comparison.png", "Throughput (rps)"),
        ("Processing Time Comparison (sec)", proc_time_values, "processing_time_comparison.png", "Total Processing Time (s)"),
    ]

    for title, values, filename, ylabel in charts:
        plt.figure(figsize=(8, 5))
        bars = plt.bar(labels, values, color=["#1f77b4", "#ff7f0e"])
        plt.title(title)
        plt.ylabel(ylabel)
        plt.grid(axis="y", linestyle="--", alpha=0.5)
        for bar, val in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{val:.2f}", ha="center", va="bottom")
        plt.tight_layout()
        plt.savefig(output_dir / filename, dpi=200)
        plt.close()


def main() -> None:
    config = Config()
    config.ensure_directories()

    batch_pipeline = FinancialPipeline(config, build_storage(config, "batch"))
    batch_result = batch_pipeline.run_batch()

    realtime_pipeline = FinancialPipeline(config, build_storage(config, "realtime"))
    realtime_result = realtime_pipeline.run_realtime()

    print_experiment_result("Test Case 1: Batch Processing", batch_result.metrics, batch_result.model_info)
    print_experiment_result("Test Case 2: Real-time Processing", realtime_result.metrics, realtime_result.model_info)

    save_comparison_charts(batch_result.metrics, realtime_result.metrics, config.chart_dir)
    print(f"\nCharts saved in: {config.chart_dir.resolve()}")


if __name__ == "__main__":
    main()
