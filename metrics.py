import time
from dataclasses import dataclass, field


@dataclass
class MetricsCollector:
    mode: str
    start_time: float = field(default_factory=time.perf_counter)
    end_time: float = 0.0
    processing_latencies_ms: list[float] = field(default_factory=list)
    record_count: int = 0
    batch_durations_ms: list[float] = field(default_factory=list)

    def record_latency(self, seconds: float) -> None:
        self.processing_latencies_ms.append(seconds * 1000.0)
        self.record_count += 1

    def record_batch_duration(self, seconds: float) -> None:
        self.batch_durations_ms.append(seconds * 1000.0)

    def stop(self) -> None:
        self.end_time = time.perf_counter()

    def summary(self) -> dict:
        duration = max(self.end_time - self.start_time, 1e-9)
        avg_latency = sum(self.processing_latencies_ms) / len(self.processing_latencies_ms) if self.processing_latencies_ms else 0.0
        throughput = self.record_count / duration
        avg_batch_time = sum(self.batch_durations_ms) / len(self.batch_durations_ms) if self.batch_durations_ms else 0.0
        return {
            "mode": self.mode,
            "total_records": self.record_count,
            "total_duration_sec": duration,
            "avg_latency_ms": avg_latency,
            "throughput_rps": throughput,
            "avg_batch_time_ms": avg_batch_time,
        }
