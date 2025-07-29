import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

# Definišemo apsolutnu putanju do baze i modela unutar Airflow okruženja
DB_PATH = "/opt/airflow/dags/game_events.db"
MODEL_PATH = "/opt/airflow/dags/churn_model.pkl"

def train_churn_model():
    """
    Učitava agregirane podatke, trenira model za predikciju churn-a i čuva ga.
    """
    if not os.path.exists(DB_PATH):
        print(f"Greška: Baza podataka nije pronađena na putanji: '{DB_PATH}'")
        raise FileNotFoundError(f"Baza podataka {DB_PATH} ne postoji.")

    print("Povezujem se na bazu i učitavam 'player_summary' tabelu...")
    conn = sqlite3.connect(DB_PATH)
    
    try:
        df = pd.read_sql_query("SELECT * FROM player_summary", conn)
        
        if df.empty:
            print("Tabela 'player_summary' je prazna. Preskačem treniranje modela.")
            return

        print(f"Učitano {len(df)} redova. Počinjem sa pripremom podataka...")

        # --- Feature Engineering ---
        df['first_seen'] = pd.to_datetime(df['first_seen'])
        df['last_seen'] = pd.to_datetime(df['last_seen'])
        
        churn_threshold = datetime.now() - timedelta(days=2)
        df['churn'] = (df['last_seen'] < churn_threshold).astype(int)

        df['player_lifetime_days'] = (df['last_seen'] - df['first_seen']).dt.days
        df['avg_revenue'] = df['total_revenue'] / (df['total_purchases'] + 1)

        features = ['total_events', 'total_purchases', 'total_revenue', 'player_lifetime_days', 'avg_revenue']
        target = 'churn'

        X = df[features]
        y = df[target]

        # --- Provera da li imamo obe klase pre treniranja ---
        if y.nunique() < 2:
            print(f"U podacima postoji samo jedna klasa ({y.unique()}). Nije moguće trenirati model.")
            print("✅ Preskačem treniranje modela, zadatak je uspešno završen.")
            # Vraćamo se da bi Airflow označio zadatak kao 'success'
            return

        # Podela podataka na trening i test set
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        print("Treniram model Logističke Regresije...")
        model = LogisticRegression()
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        print(f"Tačnost modela na test setu: {accuracy:.2f}")

        print(f"Čuvam model na putanji: {MODEL_PATH}")
        joblib.dump(model, MODEL_PATH)
        
        print("✅ Treniranje i čuvanje modela je uspešno završeno!")

    except Exception as e:
        print(f"Došlo je do greške tokom treniranja modela: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    train_churn_model()
