#
# Worker server
#
import pickle, jsonpickle
import platform
from PIL import Image
import io
import os
import sys
import pika
import redis
import hashlib
import face_recognition
import codecs

def callback(ch, method, properties, body):
    try:
        print("{} - ---Incoming RabbitMQ message PROCESSING----".format(hostname), file=sys.stderr)
        rabbitMQChannel.basic_publish(exchange='logs', routing_key=debug, body="---Incoming RabbitMQ message PROCESSING----")
        print (jsonpickle.loads(body))
        fileName = jsonpickle.loads(body)['fileName']
        imgHash = jsonpickle.loads(body)['imgHash']
        imgData = pickle.loads(codecs.decode(jsonpickle.loads(body)['imgData'].encode(), "base64"))

        redisNameToHash.set(fileName, imgHash)      # filename -> hash (database1)
        print("redisNameToHash -> Database1 Insertion : <{}><{}>".format(fileName, imgHash), file=sys.stderr)
        rabbitMQChannel.basic_publish(exchange='logs', routing_key=info, body="redisNameToHash -> Database1 Insertion")
        rabbitMQChannel.basic_publish(exchange='logs', routing_key=debug, body="DB1: <{}><{}>".format(fileName, imgHash))

        redisHashToName.sadd(imgHash, fileName)     # hash -> [filename] (database2)
        print("redisHashToName -> Database2 Insertion: <{}><{}>".format(imgHash, redisHashToName.smembers(imgHash)), file=sys.stderr)
        rabbitMQChannel.basic_publish(exchange='logs', routing_key=info, body="redisNameToHash -> Database1 Insertion")
        rabbitMQChannel.basic_publish(exchange='logs', routing_key=debug, body="DB2: <{}><{}>".format(imgHash, redisHashToName.smembers(imgHash)))

        # Loading image and finding the face encoding
        img = face_recognition.load_image_file(imgData)
        unknown_face_encodings = face_recognition.face_encodings(img)

        if len(unknown_face_encodings) > 0:
            for i in unknown_face_encodings:
                redisHashToFaceRec.sadd(imgHash, jsonpickle.dumps(i))     # hash -> face encodings(set) (database3)
                print("redisHashToFaceRec -> Database3 Insertion: <{}><{}>".format(imgHash, redisHashToFaceRec.smembers(imgHash)), file=sys.stderr)

                rabbitMQChannel.basic_publish(exchange='logs', routing_key=info, body="redisHashToFaceRec -> Database3 Insertion")
                rabbitMQChannel.basic_publish(exchange='logs', routing_key=debug, body="DB3: <{}><{}>".format(imgHash, redisHashToFaceRec.smembers(imgHash)))
                for key in redisHashToFaceRec.scan_iter():
                    known_face_encodings = [jsonpickle.loads(j) for j in redisHashToFaceRec.smembers(key)]

                    if any(face_recognition.compare_faces(known_face_encodings, i)):
                        redisHashToHashSet.sadd(imgHash, key)       # hash -> hases(set)  (database 4)
                        redisHashToHashSet.sadd(key, imgHash)       # hash -> hases(set)  (database 4)
                        print("redisHashToHashSet -> Database 4 insertion: <{}><{}>, <{}><{}>".format(imgHash, redisHashToHashSet.smembers(imgHash), key, redisHashToHashSet.smembers(key)), file=sys.stderr)
                        rabbitMQChannel.basic_publish(exchange='logs', routing_key=info, body="redisHashToHashSet -> Database 4 insertion")
                        rabbitMQChannel.basic_publish(exchange='logs', routing_key=debug, body="DB4: <{}><{}>, <{}><{}>".format(imgHash, redisHashToHashSet.smembers(imgHash), key, redisHashToHashSet.smembers(key)))

        print("{} - Finished Processing RabbitMQ message".format(hostname), file=sys.stderr)
        rabbitMQChannel.basic_publish(exchange='logs', routing_key=debug, body="Finished Processing RabbitMQ message")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    except Exception as e:
        #send negative ack
        print ("Error in callback: {}".format(e))
        rabbitMQChannel.basic_publish(exchange='logs', routing_key=debug, body="Error in callback: {}".format(e))
        channel.basic_nack(delivery_tag=method.delivery_tag)


        
hostname = str(platform.node())

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost), file=sys.stderr)

##
## You provide this
##

try:
    #setting up databases
    redisNameToHash = redis.Redis(host=redisHost, db=1)    # Key -> Value Database
    redisHashToName = redis.StrictRedis(host=redisHost, db=2, charset="utf-8", decode_responses=True)    # Key -> Set Database
    redisHashToFaceRec = redis.StrictRedis(host=redisHost, db=3, charset="utf-8", decode_responses=True) # Key -> Set Database
    redisHashToHashSet = redis.StrictRedis(host=redisHost, db=4, charset="utf-8", decode_responses=True) # Key -> Set Database

    #rabbitMQ listener - keeps the chanel open and listens for messages from rest server
    rabbitMQ = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()

    rabbitMQChannel.exchange_declare(exchange='toWorker', exchange_type='direct')
    rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
    result = rabbitMQChannel.queue_declare('', exclusive=True)
    queue_name = result.method.queue

    binding_keys = ['img']

    for key in binding_keys:
        rabbitMQChannel.queue_bind(
                exchange='toWorker', 
                queue=queue_name,
                routing_key=key)

    #routing keys seto up (same as rest server)
    info = hostname + ".worker.info"
    debug = hostname + ".worker.debug"


    print ('start consume (rabbitMQ)', file=sys.stderr)
    rabbitMQChannel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=False)

    rabbitMQChannel.start_consuming()
    
except Exception as e:
    print("Exception occurred, need restart...\nDetail:\n%s" % e)
    try:
        connection.close()
    except:
        pass