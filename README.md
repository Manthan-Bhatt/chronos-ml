# Chronos ML
### AI Model Versioning and Experiment Tracking System
**Live Demo:** https://chronos-ml-fhzc36rejpjgmdcdjfwzlw.streamlit.app 

---

## Overview
Chronos ML is a system for tracking AI model versions, training runs, hyperparameters, evaluation metrics, and deployments. Built as part of the IT214 DBMS course at DA-IICT.
---

## Database Design
Built this for our DBMS project. The focus was on getting the schema right — all 15 relations are proven to be in BCNF.

### Schema Overview

The database `chronos_ml` consists of **15 relations** covering users, models, datasets, training runs, hyperparameters, evaluation metrics, artifacts, and deployments.

```
chronos_ml
├── Users                  — system users with role-based access
├── Model                  — ML model registry
├── Model_Version          — model versions
├── Model_Created          — user–model ownership and access levels
├── Dataset                — dataset registry
├── Dataset_Version        — dataset versions
├── Registers              — user–dataset contribution tracking
├── Training_Run           — individual training job records
├── Hyperparameter         — key-value hyperparameters per run
├── Evaluation_Metric      — per-snapshot metrics per run
├── Dataset_Used           — datasets consumed by a training run
├── Model_Artifact         — stored model files per run
├── Files                  — file types associated with an artifact
├── Deployment             — model deployment records
└── Deploys                — user–deployment role assignments
```

### Entity Relationship

Key relationships in the schema:

- A `User` can create many `Model`s (via `Model_Created`) and register on many `Dataset`s (via `Registers`)
- A `Model` has many `Model_Version`s; each version can have many `Training_Run`s
- A `Training_Run` records many `Hyperparameter`s, many `Evaluation_Metric` , and uses many `Dataset_Version`s (via `Dataset_Used`)
- A `Training_Run` produces many `Model_Artifact`s, each with multiple `Files`
- A `Model_Version` can be deployed through `Deployment`; deployments can reference each other by `Compared_With` for A/B comparison


## DDL

The full DDL script creates the `chronos_ml` schema and all 15 tables with primary keys, foreign keys, CHECK constraints, and DEFAULT values. It is located at the root of this repository.

To run it on a fresh PostgreSQL database:

```sql
CREATE SCHEMA chronos_ml;
SET search_path TO chronos_ml;
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Database | PostgreSQL (hosted on Neon) |
| Backend / Queries | Python, psycopg2 |
| Frontend | Streamlit |
| Deployment | Streamlit Community Cloud |

---

## Running Locally

**Prerequisites:** Python 3.10+, PostgreSQL

```bash
git clone https://github.com/Manthan-Bhatt/chronos-ml.git
cd chronos-ml
pip install streamlit psycopg2-binary pandas plotly
```

Create `.streamlit/secrets.toml`:
```toml
DATABASE_URL = "postgresql://user:password@host/dbname?sslmode=require"
```

Run the DDL script on your database, then:
```bash
python -m streamlit run app.py
```
