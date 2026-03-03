🔍 Real-Time Fraud Detection Pipeline
A production-style streaming data pipeline that detects suspicious financial transactions in real time using Apache Kafka, Spark Structured Streaming, and PostgreSQL — fully containerised with Docker.


📌 Project Overview
Financial fraud costs the global economy billions of dollars every year. Traditional batch-based fraud detection systems only flag suspicious activity hours or days after a transaction occurs — far too late to prevent losses.
This project tackles that problem by building a real-time streaming pipeline that:

Continuously ingests a stream of simulated bank transactions
Applies rule-based anomaly detection as each transaction arrives
Immediately persists flagged transactions to a PostgreSQL database for review
Can be extended with a machine learning scoring layer for more sophisticated detection

The architecture mirrors real-world Fintech fraud systems used at companies like Moniepoint, Paystack, and Flutterwave — where transaction monitoring must happen at low latency and high throughput across millions of events per day.

day.

🏗️ Architecture
┌─────────────────────┐
│   Transaction       │
│   Producer          │  Simulates a stream of bank transactions
│   (src/producer.py) │  including injected fraud patterns (5%)
└────────┬────────────┘
         │  Publishes to topic: transactions
         ▼
┌─────────────────────┐
│   Apache Kafka      │  Distributed message broker
│   + Zookeeper       │  Decouples producer from consumer
│   (Docker)          │  Retains messages for fault tolerance
└────────┬────────────┘
         │  Subscribes to topic: transactions
         ▼
┌─────────────────────┐
│   Spark Structured  │  Reads stream in micro-batches
│   Streaming         │  Parses JSON payloads
│   (src/fraud_       │  Applies fraud detection rules
│    detector.py)     │  (amount thresholds, velocity checks)
└────────┬────────────┘
         │  Writes flagged records via JDBC
         ▼
┌─────────────────────┐
│   PostgreSQL        │  Stores flagged transactions
│   (Docker)          │  for analyst review and reporting
│   fraud_db          │
└─────────────────────┘

🛠️ Tech Stack
Technology              Version                       Role
ApacheKafka             7.4.0(Confluent)           Message broker / event stream
Apache Zookeeper        7.4.0(Confluent)           Kafka cluster coordination
Apache Spark(PySpark)   3.4.0                      Structured Streaming engine
PostgreSQL              15                         Sink for flagged transactions
Docker + Docker Compose Latest                     Local infrastructure
Python                  3.10+                      Pipeline code
Faker                   Latest                     Synthetic transaction data generation


📁 Project Structure
fraud-detection-pipeline/
├── docker-compose.yml        # Kafka, Zookeeper, PostgreSQL services
├── requirements.txt          # Python dependencies
├── README.md
├── src/
│   ├── __init__.py
│   ├── producer.py           # Kafka transaction producer
│   └── fraud_detector.py     # Spark Structured Streaming consumer
├── data/                     # Optional: sample CSV snapshots
└── tests/                    # Unit tests

⚙️ How to Run
Prerequisites

Docker Desktop installed and running
Python 3.10+
Java 17 (required by Spark — see note below)


Java Note: Spark 3.4 requires Java 17. If you are on Java 21+, install Java 17 via Homebrew:
bashbrew install openjdk@17
Then add these lines to the top of src/fraud_detector.py:
pythonimport os
os.environ['JAVA_HOME'] = '/opt/homebrew/opt/openjdk@17'


Step 1 — Clone the Repository
bashgit clone https://github.com/YOUR_USERNAME/fraud-detection-pipeline.git
cd fraud-detection-pipeline
Step 2 — Start Infrastructure
bashdocker-compose up -d
Verify all 3 services are running:
bashdocker ps
You should see zookeeper, kafka, and postgres containers all with status Up.

Port conflict? If port 5432 is already in use (local PostgreSQL running), change the postgres ports in docker-compose.yml to 5433:5432 and update the JDBC connection string in fraud_detector.py accordingly.

Step 3 — Set Up Python Environment
bashpython -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
pip install -r requirements.txt

Step 4 — Create the PostgreSQL Table
bash# Connect to the database
psql "postgresql://admin:admin123@localhost:5432/fraud_db"
sql
         CREATE TABLE flagged_transactions (
             transaction_id  VARCHAR(100) PRIMARY KEY,
             user_id         VARCHAR(50),
             amount          NUMERIC(18, 2),
             merchant        VARCHAR(200),
             location        VARCHAR(100),
             timestamp       TIMESTAMP,
             fraud_flag      VARCHAR(50)
         );

Step 5 — Run the Pipeline
Open two separate terminals:
Terminal 1 — Start the Spark consumer first:
bashsource venv/bin/activate
python src/fraud_detector.py
Wait until you see Spark session started before starting the producer.
Terminal 2 — Start the transaction producer:
bashsource venv/bin/activate
python src/producer.py
You will see transactions being published in Terminal 2 and Spark processing them in Terminal 1.
Step 6 — Verify Flagged Transactions
Open a third terminal and query PostgreSQL:
bashpsql "postgresql://admin:admin123@localhost:5432/fraud_db"
sql-- Count flagged transactions by type
SELECT fraud_flag, COUNT(*) AS total
FROM flagged_transactions
GROUP BY fraud_flag;

-- View the highest-value flagged transactions
SELECT transaction_id, user_id, amount, fraud_flag, timestamp
FROM flagged_transactions
ORDER BY amount DESC
LIMIT 10;
Step 7 — Shut Down
bashdocker-compose down

📊 Sample Output
After running the pipeline for ~2 minutes, a query on the flagged_transactions table returns:
 fraud_flag        | total
-------------------+-------
 HIGH_AMOUNT       |   48
 SUSPICIOUS_AMOUNT |   91
(2 rows)

 transaction_id                        | user_id   |   amount    | fraud_flag   | timestamp
---------------------------------------+-----------+-------------+--------------+---------------------
 3f2a1c89-4d5e-4f6b-8a7c-1b2d3e4f5a6b | USER_4821 | 4,987,234.50| HIGH_AMOUNT  | 2024-03-02 14:23:11
 a1b2c3d4-e5f6-7890-abcd-ef1234567890 | USER_3317 | 4,812,009.75| HIGH_AMOUNT  | 2024-03-02 14:23:14
 9f8e7d6c-5b4a-3c2d-1e0f-9a8b7c6d5e4f | USER_7654 | 3,201,450.00| HIGH_AMOUNT  | 2024-03-02 14:23:18
(10 rows)

🚀 Future Improvements

1. ML-based scoring — Replace hard-coded thresholds with a trained anomaly detection model (Isolation Forest or AutoEncoder) served via MLflow
2. Velocity checks — Flag users who make more than N transactions within a sliding time window using Spark's windowed aggregations
3. GCP Dataflow deployment — Migrate the Spark streaming job to Google Cloud Dataflow for managed, autoscaling execution
4. Real-time dashboard — Connect the PostgreSQL sink to a Grafana or Metabase dashboard for live fraud monitoring
5. Alerting — Integrate with PagerDuty or send Slack alerts when the flagged transaction rate exceeds a threshold
6. Dead letter queue — Route malformed or unparseable messages to a separate Kafka topic for investigation
7. Multi-rule engine — Add geographic velocity checks (same user transacting in two distant cities within minutes)
