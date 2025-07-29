# Game Events Analytics Pipeline

## Opis projekta

Ovaj projekat je end-to-end data pipeline koji simulira prikupljanje, obradu, skladištenje i analizu događaja iz mobilne igre. Pipeline je orkestriran pomoću Apache Airflow-a i uključuje i komponentu za mašinsko učenje koja predviđa odliv igrača (churn).

## Arhitektura

<svg width="800" height="200" xmlns="http://www.w3.org/2000/svg" font-family="Arial, sans-serif">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>

  <!-- Komponente i strelice -->
  <g>
    <!-- Producer -->
    <rect x="10" y="70" width="100" height="60" fill="#e8f5e9" stroke="#333" stroke-width="1.5" rx="8" />
    <text x="60" y="100" font-size="14px" text-anchor="middle" dominant-baseline="middle" fill="#333">Producer</text>
  </g>
  <line x1="110" y1="100" x2="140" y2="100" stroke="#333" stroke-width="1.5" marker-end="url(#arrowhead)" />

  <g>
    <!-- Kafka -->
    <rect x="140" y="70" width="100" height="60" fill="#e0f7fa" stroke="#333" stroke-width="1.5" rx="8" />
    <text x="190" y="100" font-size="14px" text-anchor="middle" dominant-baseline="middle" fill="#333">Kafka</text>
  </g>
  <line x1="240" y1="100" x2="270" y2="100" stroke="#333" stroke-width="1.5" marker-end="url(#arrowhead)" />

  <g>
    <!-- Consumer -->
    <rect x="270" y="70" width="100" height="60" fill="#e8f5e9" stroke="#333" stroke-width="1.5" rx="8" />
    <text x="320" y="100" font-size="14px" text-anchor="middle" dominant-baseline="middle" fill="#333">Consumer</text>
  </g>
  <line x1="370" y1="100" x2="400" y2="100" stroke="#333" stroke-width="1.5" marker-end="url(#arrowhead)" />

  <g>
    <!-- SQLite -->
    <rect x="400" y="70" width="100" height="60" fill="#fffde7" stroke="#333" stroke-width="1.5" rx="8" />
    <text x="450" y="92" font-size="14px" text-anchor="middle" dominant-baseline="middle" fill="#333">SQLite</text>
    <text x="450" y="112" font-size="10px" text-anchor="middle" dominant-baseline="middle" fill="#333">raw_events</text>
  </g>
  
  <!-- Strelica na dole i na gore -->
  <path d="M 450 130 Q 450 150 470 150 L 530 150 Q 550 150 550 130" stroke="#333" stroke-width="1.5" fill="none" marker-end="url(#arrowhead)"/>
  
  <g>
    <!-- Aggregation & ML -->
    <rect x="550" y="70" width="120" height="60" fill="#f3e5f5" stroke="#333" stroke-width="1.5" rx="8" />
    <text x="610" y="92" font-size="14px" text-anchor="middle" dominant-baseline="middle" fill="#333">Aggregation</text>
    <text x="610" y="112" font-size="14px" text-anchor="middle" dominant-baseline="middle" fill="#333">& ML Model</text>
  </g>
  <line x1="670" y1="100" x2="700" y2="100" stroke="#333" stroke-width="1.5" marker-end="url(#arrowhead)" />

  <g>
    <!-- Dashboard -->
    <rect x="700" y="70" width="100" height="60" fill="#ffebee" stroke="#333" stroke-width="1.5" rx="8" />
    <text x="750" y="100" font-size="14px" text-anchor="middle" dominant-baseline="middle" fill="#333">Dashboard</text>
  </g>

</svg>

## ⚙️ Tehnologije

| Komponenta         | Tehnologija           |
|--------------------|------------------------|
| Orkestracija       | Apache Airflow         |
| Streaming          | Apache Kafka           |
| Kontejnerizacija   | Docker, Docker Compose |
| Baza podataka      | SQLite                 |
| ETL/Analitika      | Pandas                 |
| Mašinsko učenje    | Scikit-learn           |
| Vizualizacija      | Streamlit              |

## Kako pokrenuti projekat

### Preduslovi

- Docker i Docker Compose
- Python 3.8+

### Koraci za pokretanje

1.  **Klonirajte repozitorijum:**
    ```bash
    git clone [https://github.com/tvoje-ime/tvoj-repo.git](https://github.com/tvoje-ime/tvoj-repo.git)
    cd tvoj-repo
    ```

2.  **Izgradite i pokrenite Docker kontejnere:**
    Ova komanda će podići Airflow, Kafku i sve ostale servise.
    ```bash
    docker-compose up --build -d
    ```

3.  **Pristupite Airflow UI:**
    Otvorite pretraživač i idite na `http://localhost:8080`. Ulogujte se sa `airflow` / `airflow`.

4.  **Pokrenite DAG:**
    U Airflow UI, omogućite (un-pause) `game_events_pipeline` DAG i pokrenite ga ručno.

5.  **Pokrenite Dashboard:**
    Nakon što se DAG uspešno izvrši, pokrenite Streamlit dashboard u novom terminalu:
    ```bash
    pip install -r requirements.txt
    streamlit run dashboard.py
    ````
