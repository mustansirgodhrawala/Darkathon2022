from kafka import KafkaConsumer

topic = input("Kafka topic: ")
choice = input("1 for msg, 2 for nums: ")
consumer = KafkaConsumer(topic)
num = 0
if int(choice) == 2:
    for msg in consumer:
        print(num)
        num += 1

else:
    for msg in consumer:
        print(msg.value)
