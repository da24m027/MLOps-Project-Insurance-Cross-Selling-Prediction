# Insurance Cross-Selling Prediction

A full-stack MLOps project for predicting which customers are likely to purchase vehicle insurance, featuring a modern FastAPI web app, machine learning pipeline, monitoring with Prometheus & Grafana, and reproducible workflows with DVC and Docker.

---

## Features

- **Customer Prediction Web App**: User-friendly interface for entering customer details and getting real-time predictions.
- **ML Pipeline**: Data preprocessing, model training (Random Forest), and prediction using scikit-learn, orchestrated with DVC.
- **Experiment Tracking**: MLflow integration for tracking experiments, parameters, and metrics.
- **Monitoring**: Prometheus metrics and Grafana dashboards for real-time monitoring of app and model performance.
- **Containerized Deployment**: Docker and Docker Compose for easy, reproducible deployment.
- **Metrics & Health Endpoints**: `/metrics` for Prometheus scraping, `/health` for health checks.

---

## Project Structure

```
.
├── main.py                # FastAPI app entry point
├── src/                   # ML pipeline: training, prediction, preprocessing
├── templates/             # Jinja2 HTML templates (UI)
├── static/                # Static files (CSS, JS)
├── models/                # Trained ML models
├── data/                  # Raw and processed data
├── config/                # YAML config files
├── requirements.txt       # Python dependencies
├── Dockerfile             # App containerization
├── docker-compose.yaml    # Multi-service orchestration
├── prometheus/            # Prometheus config
├── grafana/               # Grafana dashboards & provisioning
├── dvc.yaml, dvc.lock     # DVC pipeline definitions
└── README.md
```

---

## Quickstart

### 1. Clone the repository

```bash
git clone <repo-url>
cd MLOps-Project-Insurance-Cross-Selling-Prediction
```

### 2. Build and run with Docker Compose

```bash
docker-compose up --build
```

- FastAPI app: [http://localhost:8000](http://localhost:8000)
- Prometheus: [http://localhost:9091](http://localhost:9091)
- Grafana: [http://localhost:3000](http://localhost:3000) (default login: `admin`/`admin`)

### 3. Local development (optional)

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
uvicorn main:app --reload
```

---

## Usage

- **Web UI**: Enter customer details to get a prediction and see cross-sell opportunities.
- **API Endpoints**:
  - `POST /predict`: Get prediction for a customer (JSON).
  - `GET /customers`: List all customer entries.
  - `GET /positive-customers`: List customers likely to purchase insurance.
  - `GET /metrics`: Prometheus metrics.
  - `GET /health`: Health check.

---

## Machine Learning Pipeline

- **Data Preprocessing**: `src/data_preprocessing.py` (run via DVC).
- **Model Training**: `src/train.py` (Random Forest, tracked/logged with MLflow).
- **Prediction**: `src/predict.py` (loads latest model, applies preprocessing).
- **Configuration**: All parameters in `config/params.yaml`.

To reproduce the pipeline:

```bash
dvc repro
```

---

## Monitoring & Observability

- **Prometheus**: Collects app and prediction metrics (request count, latency, prediction stats).
- **Grafana**: Visualizes metrics with pre-built dashboards.
- **Custom Metrics**: Number of positive predictions, request/response stats.

---

## Customization

- **Model/Feature Engineering**: Edit `src/train.py` and `src/data_preprocessing.py`.
- **Config**: Change hyperparameters, data paths, and experiment settings in `config/params.yaml`.
- **UI**: Modify `templates/index.html` and static assets for branding or new features.

---

## Requirements

- Python 3.9+
- Docker & Docker Compose
- DVC (for pipeline management)
- (Optional) MLflow server for remote experiment tracking

---

## License

MIT License

---

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [scikit-learn](https://scikit-learn.org/)
- [MLflow](https://mlflow.org/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [DVC](https://dvc.org/)

---

