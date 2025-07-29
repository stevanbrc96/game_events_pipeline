
import sqlite3
import json
from kafka import KafkaConsumer, errors

DB_PATH = "/opt/airflow/dags/game_events.db"
KAFKA_TOPIC = 'game_events'

def setup_database():
    """Kreira SQLite bazu i tabelu 'raw_events' ako ne postoje."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_events (
            eventId TEXT PRIMARY KEY,
            eventTimestamp TEXT,
            eventType TEXT,
            playerId TEXT,
            eventDetails TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✅ Baza '{DB_PATH}' i tabela 'raw_events' su spremne.")

def run_consumer_for_batch():
    """Pokreće consumer koji radi dok ne pokupi sve poruke i onda se gasi."""
    setup_database()
    
    # KORISTIMO 'kafka:29092' KAO INTERNU ADRESU
    bootstrap_server_address = 'kafka:29092'
    print(f"Pokušavam da se povežem na Kafku na adresi: {bootstrap_server_address}...")
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[bootstrap_server_address],
            auto_offset_reset='earliest',
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            consumer_timeout_ms=15000
        )
        print("✅ Kafka Consumer je uspešno povezan.")
    except errors.NoBrokersAvailable:
        print(f"❌ Greška: Kafka broker nije dostupan sa adrese {bootstrap_server_address}.")
        raise ConnectionError("Nije moguće povezati se na Kafku iz Airflow-a.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("Čekam na poruke sa Kafka topica...")
    
    message_count = 0
    try:
        for message in consumer:
            event = message.value
            print(f"Primljen događaj: {event['eventType']}")
            cursor.execute(
                'INSERT OR IGNORE INTO raw_events VALUES (?, ?, ?, ?, ?)',
                (event['eventId'], event['eventTimestamp'], event['eventType'],
                 event['playerId'], json.dumps(event['eventDetails']))
            )
            message_count += 1
        conn.commit()
    except Exception as e:
        print(f"Došlo je do greške u consumer-u: {e}")
    finally:
        consumer.close()
        conn.close()
        print(f"Consumer je obradio {message_count} poruka i zatvoren je.")

if __name__ == "__main__":
    run_consumer_for_batch()
