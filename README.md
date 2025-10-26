# Game Events Analytics Pipeline

## Project Description

This project is an end-to-end data pipeline that simulates the collection, processing, storage, and analysis of events from a mobile game. The pipeline is orchestrated using Apache Airflow and includes a machine learning component that predicts player churn.

## Architecture

![Architecture Diagram](architecture.png)

## Technologies

| Component          | Technology             |
|--------------------|------------------------|
| Orchestration      | Apache Airflow         |
| Data Streaming     | Apache Kafka           |
| Containerization   | Docker, Docker Compose |
| Database           | SQLite                 |
| ETL/Analytics      | Pandas                 |
| Machine Learning   | Scikit-learn           |
| Visualization      | Streamlit              |

## How to Run the Project

### Prerequisites

- Docker and Docker Compose
- Python 3.8+

### Steps to Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo.git
    cd your-repo

    ```

2.  **Build and run the Docker containers:**
    This command will start Airflow, Kafka, and all other services.
    ```bash
    docker-compose up --build -d
    ```

3.  **Access the Airflow UI:**
    Open a browser and go to `http://localhost:8080`. Log in with `airflow` / `airflow`.

4.  **Run the DAG:**
    In the Airflow UI, enable (un-pause) the `game_events_pipeline` DAG and trigger it manually.

5.  **Run the Dashboard:**
    After the DAG has run successfully, start the Streamlit dashboard in a new terminal:
    ```bash
    pip install -r requirements.txt
    streamlit run dashboard.py
    ```
    *(Note: The `pip install` command installs the necessary libraries for Streamlit in your local Python environment, separate from Docker.)*
    
## Future Improvements: Cloud Migration to Azure

This project serves as a local proof-of-concept, demonstrating the core principles of a data pipeline. For a real-world, production-grade system, the entire architecture would be migrated to a cloud platform like Microsoft Azure. This transition would provide significant benefits in scalability, reliability, security, and maintainability.

The following table outlines a clear migration path, replacing each local component with its equivalent, fully-managed Azure service:
    | Component          | Azure Service                                           |
|--------------------|---------------------------------------------------------|
| Data Ingestion     | **Azure Event Hubs** |
| Data Storage       | **Azure SQL Database** |
| Orchestration & ETL| **Azure Data Factory** |
| Machine Learning   | **Azure Machine Learning** |
| Visualization      | **Azure App Service** (hosting a Streamlit app)         |

Migrating to this serverless, cloud-native architecture would create a more robust and efficient system, allowing the data team to focus on developing new features rather than managing infrastructure.
