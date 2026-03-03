 Real-Time Fraud Detection Pipeline
A production-style streaming data pipeline that detects suspicious financial transactions in real time using Apache Kafka, Spark Structured Streaming, and PostgreSQL — fully containerised with Docker.


 Project Overview
Financial fraud costs the global economy billions of dollars every year. Traditional batch-based fraud detection systems only flag suspicious activity hours or days after a transaction occurs — far too late to prevent losses.
This project tackles that problem by building a real-time streaming pipeline that:

Continuously ingests a stream of simulated bank transactions
Applies rule-based anomaly detection as each transaction arrives
Immediately persists flagged transactions to a PostgreSQL database for review
Can be extended with a machine learning scoring layer for more sophisticated detection

The architecture mirrors real-world Fintech fraud systems used at companies like Moniepoint, Paystack, and Flutterwave — where transaction monitoring must happen at low latency and high throughput across millions of events per day.

<img width="606" height="455" alt="Screenshot 2026-03-03 at 12 21 17" src="https://github.com/user-attachments/assets/a49e5cd2-df9a-4bb3-be0b-84f8d26ac56f" />

<img width="512" height="366" alt="Screenshot 2026-03-03 at 12 22 48" src="https://github.com/user-attachments/assets/aa31072a-f62c-40ae-aaf3-e08502994bdf" />

How to Run
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
bashgit clone https://github.com/AdeoluAdegboye/fraud-detection-pipeline.git
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
venv\Scripts\activate         # Windows 
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

<img width="674" height="240" alt="Screenshot 2026-03-03 at 12 49 17" src="https://github.com/user-attachments/assets/5d0f3854-5d1d-4250-8287-5c95e6624de3" />


Future Improvements

1. ML-based scoring — Replace hard-coded thresholds with a trained anomaly detection model (Isolation Forest or AutoEncoder) served via MLflow
2. Velocity checks — Flag users who make more than N transactions within a sliding time window using Spark's windowed aggregations
3. GCP Dataflow deployment — Migrate the Spark streaming job to Google Cloud Dataflow for managed, autoscaling execution
4. Real-time dashboard — Connect the PostgreSQL sink to a Grafana or Metabase dashboard for live fraud monitoring
5. Alerting — Integrate with PagerDuty or send Slack alerts when the flagged transaction rate exceeds a threshold
6. Dead letter queue — Route malformed or unparseable messages to a separate Kafka topic for investigation
7. Multi-rule engine — Add geographic velocity checks (same user transacting in two distant cities within minutes)
