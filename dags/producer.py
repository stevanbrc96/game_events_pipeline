# ==============================================================================
# FAJL: producer.py
# LOKACIJA: /opt/airflow/dags/
# IZMENA: Povremeno generiše događaje sa starijim datumom da bi se kreirali 'churn' podaci.
# ==============================================================================
import time
import json
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
from kafka import KafkaProducer, errors

def create_kafka_producer():
    """Pokušava da se poveže na Kafku unutar Docker mreže."""
    bootstrap_server_address = 'kafka:29092'
    print(f"Pokušavam da se povežem na Kafku na adresi: {bootstrap_server_address}...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=[bootstrap_server_address],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5, request_timeout_ms=30000
        )
        print("✅ Kafka Producer je uspešno povezan.")
        return producer
    except errors.NoBrokersAvailable:
        print(f"❌ Greška: Kafka broker nije dostupan na adresi {bootstrap_server_address}.")
        return None

def generate_event(faker_instance):
    """Generiše jedan nasumični događaj iz igre, povremeno sa starijim datumom."""
    event_type = random.choice(['level_completed', 'purchase', 'session_start', 'ad_watched'])
    
    # U 20% slučajeva, generiši događaj koji je star između 3 i 10 dana
    if random.random() < 0.20:
        event_time = datetime.utcnow() - timedelta(days=random.randint(3, 10))
    else:
        event_time = datetime.utcnow()

    event = {
        'eventId': str(uuid.uuid4()),
        'eventTimestamp': event_time.isoformat(),
        'eventType': event_type,
        'playerId': faker_instance.uuid4(),
        'eventDetails': {}
    }
    if event_type == 'purchase':
        event['eventDetails'] = {'itemId': random.choice(['pack_1', 'pack_2']), 'priceUSD': round(random.uniform(1, 50), 2)}
    elif event_type == 'level_completed':
        event['eventDetails'] = {'level': random.randint(1, 100)}
    return event

def run_producer_for_duration(duration_seconds=60):
    """Pokreće producer na određeno vreme."""
    fake = Faker()
    producer = create_kafka_producer()
    if not producer:
        raise ConnectionError("Nije moguće povezati se na Kafku.")

    KAFKA_TOPIC = 'game_events'
    print(f"Pokretanje producer-a na {duration_seconds} sekundi...")
    
    start_time = time.time()
    try:
        while time.time() - start_time < duration_seconds:
            game_event = generate_event(fake)
            producer.send(KAFKA_TOPIC, value=game_event)
            print(f"Poslat događaj: {game_event['eventType']} @ {game_event['eventTimestamp']}")
            time.sleep(random.uniform(0.1, 0.5)) # Ubrzavamo generisanje
    except Exception as e:
        print(f"Došlo je do greške u producer-u: {e}")
    finally:
        producer.flush()
        producer.close()
        print(f"Producer je radio {time.time() - start_time:.2f} sekundi i zatvoren je.")

if __name__ == "__main__":
    run_producer_for_duration(60) # Povećavamo vreme za ručno testiranje
