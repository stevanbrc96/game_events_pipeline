# Počinjemo od zvanične Airflow slike koju već koristite
FROM apache/airflow:2.8.1

# Postavljamo korisnika na 'airflow' da bismo izbegli probleme sa dozvolama
USER airflow

# Kopiramo naš fajl sa potrebnim bibliotekama u kontejner
COPY requirements.txt .

# Instaliramo biblioteke koristeći pip
RUN pip install --no-cache-dir --user -r requirements.txt