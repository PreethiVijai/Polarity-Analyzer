import sys
import os
import pika
import jsonpickle

##
## Configure test vs. production
##
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
print("Using host", rabbitMQHost, file=sys.stderr)

rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()

rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
result = rabbitMQChannel.queue_declare('', exclusive=True)
queue_name = result.method.queue

binding_keys = ['#']

for key in binding_keys:
    rabbitMQChannel.queue_bind(
            exchange='logs', 
            queue=queue_name,
            routing_key=key)

def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body), file=sys.stderr)


rabbitMQChannel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

rabbitMQChannel.start_consuming()