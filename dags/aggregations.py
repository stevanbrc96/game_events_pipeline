import sqlite3
import pandas as pd
import json
import os

# Definišemo apsolutnu putanju do baze unutar Airflow okruženja
DB_PATH = "/opt/airflow/dags/game_events.db"

def run_aggregation():
    """
    Čita podatke iz 'raw_events', vrši agregaciju i upisuje ih u novu tabelu 'player_summary'.
    """
    if not os.path.exists(DB_PATH):
        print(f"Greška: Baza podataka nije pronađena na putanji: '{DB_PATH}'")
        raise FileNotFoundError(f"Baza podataka {DB_PATH} ne postoji.")

    print("Povezujem se na bazu i učitavam podatke za agregaciju...")
    # DODAT TIMEOUT: Čekaj do 10 sekundi ako nije moguće odmah pristupiti bazi
    conn = sqlite3.connect(DB_PATH, timeout=10)
    
    try:
        df = pd.read_sql_query("SELECT * FROM raw_events", conn)
        
        if df.empty:
            print("Tabela 'raw_events' je prazna. Nema šta da se agregira.")
            return

        print(f"Učitano {len(df)} događaja. Počinjem sa agregacijom...")

        # Parsiranje JSON-a
        details_list = [json.loads(item) for item in df['eventDetails']]
        details_df = pd.DataFrame(details_list)
        df = pd.concat([df.drop('eventDetails', axis=1), details_df], axis=1)
        df['eventTimestamp'] = pd.to_datetime(df['eventTimestamp'])

        # Agregacija podataka
        player_summary = df.groupby('playerId').agg(
            total_events=('eventId', 'count'),
            total_purchases=('eventType', lambda x: (x == 'purchase').sum()),
            total_revenue=('priceUSD', 'sum'),
            first_seen=('eventTimestamp', 'min'),
            last_seen=('eventTimestamp', 'max')
        ).reset_index()

        # Upisivanje rezultata u novu tabelu
        print(f"Upisujem {len(player_summary)} redova u tabelu 'player_summary'...")
        player_summary.to_sql('player_summary', conn, if_exists='replace', index=False)
        
        print("✅ Agregacija je uspešno završena!")

    except Exception as e:
        print(f"Došlo je do greške tokom agregacije: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_aggregation()
