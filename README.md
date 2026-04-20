# Real-Time Financial Data Pipeline (Empirical Study)

A locally runnable, production-style Python project for the paper:

**"An Empirical Study on Real-Time Financial Data Pipelines for Low-Latency Analytics and Intelligent Decision-Making"**

## Features

- Synthetic real-time stock data generation (`timestamp`, `stock_symbol`, `price`, `volume`)
- Two processing modes:
  - **Batch** (windowed chunk processing)
  - **Real-time** (record-by-record processing)
- Analytics:
  - Moving average
  - Volatility
  - Price change percentage
- Lightweight ML:
  - Linear regression next-price prediction
  - Model artifact persistence
- Persistence:
  - CSV outputs
  - SQLite outputs
- Empirical metrics:
  - Latency
  - Throughput
  - Processing time
- Visualization:
  - Latency, throughput, and processing-time comparisons
- Unique feature:
  - **Adaptive streaming rate** based on observed processing latency

## Project Structure

- `config.py` – centralized configuration
- `data_generator.py` – synthetic stream source
- `processor.py` – financial analytics transformations
- `model.py` – linear-regression training and prediction
- `storage.py` – CSV + SQLite output writer
- `metrics.py` – performance metric collector
- `pipeline.py` – batch and real-time pipeline execution
- `main.py` – experiment orchestration + chart generation

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Run

Single-command execution:

```bash
python main.py
```

## Outputs

Generated under `output/`:

- Batch and real-time raw/processed CSV files
- Batch and real-time SQLite databases
- Trained model (`.joblib`)
- Comparison charts:
  - `latency_comparison.png`
  - `throughput_comparison.png`
  - `processing_time_comparison.png`

## Suggested Paper Reporting Fields

- Avg latency per mode
- Throughput per mode
- End-to-end processing duration per mode
- Model MAE and latest prediction vs actual
