from kafka import KafkaConsumer

topic = input("Kafka topic: ")
consumer = KafkaConsumer(topic)
num = 0
for msg in consumer:
    num += 1
    print(num)
