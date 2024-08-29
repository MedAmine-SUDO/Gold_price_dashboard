# Gold_price_dashboard
This project is a Real-Time Gold Price Dashboard that leverages Apache Kafka for data streaming and Docker for containerization. The dashboard allows users to monitor and visualize gold price fluctuations in real time. It integrates various components, including Kafka, Zookeeper, Schema Registry, and TimescaleDB, to provide a robust and scalable architecture. The gold price data is obtained through web scraping from a Tunisian gold price website, with a continuous loop that extracts the data and sends it to a Kafka topic every 30 seconds.

Technologies Used:
Apache Kafka: For real-time data streaming.
Zookeeper: For managing Kafka brokers.
Schema Registry: For managing data schemas.
TimescaleDB: For storing time-series data.
Docker: For containerization and orchestration.
Web Scraping: To obtain gold price data from a Tunisian website.


