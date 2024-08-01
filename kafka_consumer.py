import json
import uuid
from confluent_kafka import Consumer, KafkaException

KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'  
KAFKA_TOPIC = 'gold_prices'  

# Generate a unique consumer group ID
consumer_group_id = f"gold-price-consumer-group-{uuid.uuid4()}"

def consume_from_kafka():
    # Initialize Kafka consumer
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': consumer_group_id,
        'auto.offset.reset': 'earliest'  
    })

    consumer.subscribe([KAFKA_TOPIC])

    try:
        while True:
            msg = consumer.poll(1.0)  # Timeout of 1 second

            if msg is None:
                continue
            
            if msg.error():
                # Handle any errors
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    continue
                else:
                    print(f"Error occurred: {msg.error()}")
                    break
            
            # Message is valid
            gold_data = json.loads(msg.value().decode('utf-8'))
            print(f'Received message: {gold_data}')

    except KeyboardInterrupt:
        print("Consumer interrupted by user")
    except KafkaException as e:
        print(f"Kafka error: {e}")
    

if __name__ == "__main__":
    consume_from_kafka()