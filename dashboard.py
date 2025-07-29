import streamlit as st
import pandas as pd
import sqlite3
import json
import os
import joblib
from datetime import datetime, timedelta

# ==============================================================================
# KONFIGURACIJA
# ==============================================================================
# Definišemo putanje do baze podataka i sačuvanog modela
DB_PATH = os.path.join("dags", "game_events.db")
MODEL_PATH = os.path.join("dags", "churn_model.pkl")

# ==============================================================================
# Funkcije za pomoć
# ==============================================================================

@st.cache_data(ttl=10)
def load_data(db_path, table_name):
    """Učitava podatke iz određene tabele u SQLite bazi."""
    if not os.path.exists(db_path):
        st.error(f"GREŠKA: Baza podataka nije pronađena na putanji: '{db_path}'")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        table_check_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        if pd.read_sql_query(table_check_query, conn).empty:
            return None
        
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Došlo je do greške pri čitanju podataka iz baze: {e}")
        return pd.DataFrame()

@st.cache_resource
def load_model(model_path):
    """Učitava sačuvani model za predikciju."""
    if not os.path.exists(model_path):
        return None
    try:
        model = joblib.load(model_path)
        return model
    except Exception as e:
        st.error(f"Greška pri učitavanju modela: {e}")
        return None

# ==============================================================================
# Glavna aplikacija
# ==============================================================================

st.set_page_config(layout="wide")
st.title("📊 Game Events Dashboard & Churn Prediction")

if st.button("Osveži podatke"):
    st.cache_data.clear()
    st.cache_resource.clear()

# --- Prikaz sirovih podataka ---
df_raw = load_data(DB_PATH, "raw_events")

if df_raw is None or df_raw.empty:
    st.info("Čekam na podatke... Pokrenite Airflow DAG da biste popunili bazu.")
else:
    # Parsiranje i prikaz sirovih podataka
    details_list = [json.loads(item) for item in df_raw['eventDetails']]
    details_df = pd.DataFrame(details_list)
    df = pd.concat([df_raw.drop('eventDetails', axis=1), details_df], axis=1)
    df['eventTimestamp'] = pd.to_datetime(df['eventTimestamp'])

    st.subheader("Poslednji primljeni događaji")
    st.dataframe(df.tail(5))
    
    # --- Agregirana Analiza ---
    st.divider()
    st.header("Agregirana Analiza Igrača")
    df_summary = load_data(DB_PATH, "player_summary")

    if df_summary is None or df_summary.empty:
        st.warning("Tabela 'player_summary' nije pronađena. Pokrenite Airflow DAG.")
    else:
        kpi_col1, kpi_col2 = st.columns(2)
        avg_revenue_per_user = df_summary['total_revenue'].sum() / df_summary['playerId'].nunique()
        avg_events_per_user = df_summary['total_events'].mean()
        with kpi_col1:
            st.metric("Prosečan prihod po igraču (ARPU)", f"${avg_revenue_per_user:,.2f}")
        with kpi_col2:
            st.metric("Prosečan broj događaja po igraču", f"{avg_events_per_user:,.2f}")
        
        st.dataframe(df_summary.sort_values(by="total_revenue", ascending=False).head(10))

    # ---  Prikaz predikcija ---
    st.divider()
    st.header("🧠 Predikcija Odliva Igrača (Churn)")
    
    model = load_model(MODEL_PATH)
    
    if model is None:
        st.warning("Model za predikciju ('churn_model.pkl') nije pronađen.")
        st.info("Pokrenite Airflow DAG koji uključuje i 'run_training_task' da biste kreirali model.")
    elif df_summary is None or df_summary.empty:
        st.warning("Nema podataka o igračima za predikciju.")
    else:
        # Priprema podataka za predikciju (isti feature engineering kao u treningu)
        df_pred = df_summary.copy()
        df_pred['first_seen'] = pd.to_datetime(df_pred['first_seen'])
        df_pred['last_seen'] = pd.to_datetime(df_pred['last_seen'])
        df_pred['player_lifetime_days'] = (df_pred['last_seen'] - df_pred['first_seen']).dt.days
        df_pred['avg_revenue'] = df_pred['total_revenue'] / (df_pred['total_purchases'] + 1)
        
        features = ['total_events', 'total_purchases', 'total_revenue', 'player_lifetime_days', 'avg_revenue']
        X_pred = df_pred[features]
        
        # Pravljenje predikcija
        df_pred['churn_prediction'] = model.predict(X_pred)
        
        # Prikaz igrača za koje se predviđa churn
        st.subheader("Igrači sa visokim rizikom od odliva")
        churn_risk_df = df_pred[df_pred['churn_prediction'] == 1]
        
        if churn_risk_df.empty:
            st.success("🎉 Nema igrača sa visokim rizikom od odliva trenutno.")
        else:
            st.dataframe(churn_risk_df[['playerId', 'total_events', 'total_revenue', 'last_seen']])
