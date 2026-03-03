# src/producer.py
import json, time, random
from kafka import KafkaProducer
from faker import Faker
from datetime import datetime

fake = Faker()
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_transaction(fraud=False):
    return {
        'transaction_id': fake.uuid4(),
        'user_id': f'USER_{random.randint(1000, 9999)}',
        'amount': round(random.uniform(500000, 5000000), 2) if fraud
                  else round(random.uniform(100, 50000), 2),
        'merchant': fake.company(),
        'location': fake.city(),
        'timestamp': datetime.utcnow().isoformat(),
        'is_fraud_label': fraud   # ground truth for testing
    }

print('Starting transaction stream...')
while True:
    # Inject fraud 5% of the time
    is_fraud = random.random() < 0.05
    txn = generate_transaction(fraud=is_fraud)
    producer.send('transactions', txn)
    print(f'Sent: {txn["transaction_id"]} | Amount: {txn["amount"]} | Fraud: {is_fraud}')
    time.sleep(0.5)