
# ✈️ Flight Booking Service


A lightweight microservice for booking flights, extended with performance benchmarking infrastructure using `k6`, container orchestration via Docker Compose, and detailed analysis tooling.

---

## 📚 Table of Contents

- [Introduction](#introduction)
- [API Reference](#api-reference)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Benchmarking & Analysis](#benchmarking--analysis)
- [Scripts Overview](#scripts-overview)
- [Docker Setup](#docker-setup)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## 📌 Introduction

This project simulates a scalable flight booking service, enhanced with tooling to evaluate system behavior under load and noise conditions. It supports bootstrapped statistical testing, visualization, and controlled resource execution via cgroups.

---

## ✈️ API Reference

### `GET /destinations`

```json
{
  "from": ["TXL", "LHR", "FRA", "JFK", "MUC", "CDG", "AMS", "SFO", "BOS", "MIA"],
  "to": ["TXL", "LHR", "FRA", "JFK", "MUC", "CDG", "AMS", "SFO", "BOS", "MIA"]
}
```

### `GET /flights`, `GET /flights/{id}/seats`, `POST /bookings`, `GET /bookings`  
_Full request/response examples are provided in the original [README.md](https://github.com/christophwitzko/flight-booking-service).

---

## ✨ Features

- Core flight booking microservice.
- Two containerized SUT instances with CPU affinity control.
- Two benchmarking client containers using `k6`.
- Preprocessing and analysis of benchmarking results.
- Relative change computation with bootstrapping.
- Core isolation and noise effect visualization.
- Integration with Google Cloud for result uploads.

---

## 🧰 Installation

Clone the repository:

```bash
git clone https://github.com/FuratH/flight-booking-service.git
cd flight-booking-service
```

Install Python dependencies for analysis:

```bash
pip install pandas numpy scipy matplotlib seaborn
```

---

## 🚀 Usage

Start SUT and client benchmarking containers:

```bash
docker-compose -f docker-compose.yml -f docker-compose-client.yml up --build
```

To run the analysis:

```bash
python preprocessing_filter.py
python rel_change_table.py
python aggregated_analysis_relative_changes.py
```

---

## 📊 Benchmarking & Analysis

Benchmarking results are stored as CSV files and visualized via:

- `timeseries.py` – time-based comparison of HTTP durations.
- `relative_change_plot.py` – sliding window relative % change.
- `rel_change_table.py` – statistical comparison using bootstrapping.
- `aggregated_analysis_relative_changes.py` – compares baseline vs experimental setups.

Results can be exported to LaTeX for inclusion in academic papers.

---

## 📜 Scripts Overview

| Script | Description |
|--------|-------------|
| `run_client.sh` | Run a single `k6` test and upload results. |
| `run_client_docker.sh` | Run both k6 clients in Docker and upload results. |
| `start_in_cgroup.sh` | Run components in specific cgroups with CPU affinity. |
| `manage_cgroups.sh` | Create and manage cgroupv2 limits. |
| `preprocessing_filter.py` | Clean and aggregate k6 CSV data. |
| `rel_change_table.py` | Compute statistical performance differences. |
| `aggregated_analysis_relative_changes.py` | Phase-based comparisons between runs. |
| `timeseries.py`, `relative_change_plot.py` | Visualization utilities. |

---

## 🐳 Docker Setup

### `docker-compose.yml`

Launches 2 SUT instances:

- Port 3000: cores 0–1
- Port 3001: cores 2–3

### `docker-compose-client.yml`

Launches 2 benchmarking clients with matching CPU affinity and `k6` scripts.

---

## ⚙️ Configuration

Modify `start_in_cgroup.sh` to:

- Assign container to specific CPU cores.
- Limit CPU usage per group (via `manage_cgroups.sh`).
- Run either the SUT or client inside a defined cgroup.

Example:

```bash
./start_in_cgroup.sh 3000 v1 SUT
./start_in_cgroup.sh 3000 v1 client <SUT_IP> <timestamp> <bucket_name>
```

---


## 🧯 Troubleshooting

- **Permissions**: Ensure `cgroup2` is mounted and writable.
- **Ports in use**: Check `3000` and `3001` aren’t already bound.
- **Data errors**: Use `preprocessing_filter.py` to normalize k6 output before analysis.
- **Cloud errors**: Verify GCP credentials for `gsutil` uploads.


