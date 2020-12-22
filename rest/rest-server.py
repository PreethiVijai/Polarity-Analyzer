##
from flask import Flask, request, Response
import jsonpickle, pickle
import platform
import io, os, sys
import pika, redis
import hashlib, requests
import codecs
import socket
from PIL import Image

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost), file=sys.stderr)

##
## You provide this
##

host_name = str(socket.gethostname())

#routing keys -> setup
info = host_name + ".rest.info"
debug = host_name + ".rest.debug"
toworker = "img"

app = Flask(__name__)

@app.route('/scan/image/<filename>', methods=['POST'])
def scan_image(filename):
    r = request

    try:
        #set up rabbitMQ connection and exchange queues
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMQHost))
        channel = connection.channel()

        channel.exchange_declare(exchange='toWorker', exchange_type='direct')
        channel.exchange_declare(exchange='logs', exchange_type='topic')

        #Maintaining logs file using topic exchange
        print (" ----Executing /scan/image---- ", file=sys.stderr)
        channel.basic_publish(exchange='logs', routing_key=info, body="----Executing /scan/image----")

        #data from request --> pillow image type to calculate hash
        ioBuffer = io.BytesIO(r.data)
        img = Image.open(ioBuffer)
        md5hash = hashlib.md5(img.tobytes())
        print("Image hash: {}".format(md5hash.hexdigest()), file=sys.stderr)
        channel.basic_publish(exchange='logs', routing_key=debug, body=jsonpickle.dumps({'response': 'hash - {}'.format(md5hash.hexdigest())}))

        #send to details to worker (direct exchange)
        channel.basic_publish(exchange='toWorker', routing_key=toworker, body=jsonpickle.dumps({'fileName': filename, 'imgHash': md5hash.hexdigest(), 'imgData': codecs.encode(pickle.dumps(ioBuffer), "base64").decode()}))
        print ('/scan/image successful <200>', file=sys.stderr)
        channel.basic_publish(exchange='logs', routing_key=info, body=jsonpickle.dumps({'/scan/image status': 'Successful'}))

        response = {
            'hash' : md5hash.hexdigest()
            }
    except Exception as e:
        print(e, file=sys.stderr)
        response = { 'ScanError' : e}
        channel.basic_publish(exchange='logs', routing_key=debug, body=jsonpickle.dumps({'Error': e}))
        channel.basic_publish(exchange='logs', routing_key=info, body=jsonpickle.dumps({'/scan/image API status': 'Failed'}))
    
    response_pickled = jsonpickle.encode(response)

    connection.close()

    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/scan/url', methods=['POST'])
def scan_url():
    r = request
    
    try:
        #set up rabbitMQ connection and exchange queues
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMQHost))
        channel = connection.channel()

        channel.exchange_declare(exchange='toWorker', exchange_type='direct')
        channel.exchange_declare(exchange='logs', exchange_type='topic')

        #Maintaining logs file using topic exchange
        print ("----Executing /scan/url----", file=sys.stderr)
        channel.basic_publish(exchange='logs', routing_key=info, body="----Executing /scan/url/----")


        #data from request --> pillow image type to calculate hash
        img_url = jsonpickle.loads(r.data)['url']
        print ("Image url: {}".format(img_url), file=sys.stderr)
        channel.basic_publish(exchange='logs', routing_key=debug, body=jsonpickle.dumps({'Image Url': img_url}))
        img_data = requests.get(img_url, allow_redirects=True)
        ioBuffer = io.BytesIO(img_data.content)
        img = Image.open(ioBuffer)
        md5hash = hashlib.md5(img.tobytes())
        print("Image hash: {}".format(md5hash.hexdigest()), file=sys.stderr)
        channel.basic_publish(exchange='logs', routing_key=toworker, body=jsonpickle.dumps({'response': 'hash - {}'.format(md5hash.hexdigest())}))

        #send to details to worker (direct exchange)
        channel.basic_publish(exchange='toWorker', routing_key=toworker, body=jsonpickle.dumps({'fileName': img_url, 'imgHash': md5hash.hexdigest(), 'imgData': codecs.encode(pickle.dumps(ioBuffer), "base64").decode()}))
        print ('/scan/url -- successful <200>', file=sys.stderr)
        channel.basic_publish(exchange='logs', routing_key=info, body=jsonpickle.dumps({'/scan/url status': 'Successful'}))

        response = {
            'hash' : md5hash.hexdigest()
            }
    except Exception as e:
        print(e, file=sys.stderr)
        response = { 'ScanError' : e}
        channel.basic_publish(exchange='logs', routing_key=debug, body=jsonpickle.dumps({'Error': e}))
        channel.basic_publish(exchange='logs', routing_key=info, body=jsonpickle.dumps({'/scan/url status': 'Failed'}))
    
    response_pickled = jsonpickle.encode(response)

    connection.close()

    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/match/<hash>', methods=['GET'])
def match(hash):
    r = request
    result = []
    try:
        #set up rabbitMQ connection and exchange queues
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMQHost))
        channel = connection.channel()
        
        channel.exchange_declare(exchange='logs', exchange_type='topic')

        #Maintaining logs file using topic exchange
        print("----Executing /match----", file=sys.stderr)
        channel.basic_publish(exchange='logs', routing_key=info, body="----Executing /match----")

        #checking database
        redisHashToHashSet = redis.StrictRedis(host=redisHost, db=4, charset="utf-8", decode_responses=True)
        img_hash_list = redisHashToHashSet.smembers(hash)
        if(img_hash_list):
            redisHashToName = redis.StrictRedis(host=redisHost, db=2, charset="utf-8", decode_responses=True)
            for i in img_hash_list:
                img_name_list = redisHashToName.smembers(i)
                if(img_name_list):
                    result.append(img_name_list)
        print("Result for hash: {} - {}".format(hash, result), file=sys.stderr)
        channel.basic_publish(exchange='logs', routing_key=debug, body=jsonpickle.dumps({'Result': '{} - {}'.format(hash, result)}))
        print ('/match successful <200>', file=sys.stderr)
        channel.basic_publish(exchange='logs', routing_key=info, body=jsonpickle.dumps({'/match status': 'Successful'}))

        response = {
            'result' : result
            }
    except Exception as e:
        response = { 'result' : result}
        print(e, file=sys.stderr)
        channel.basic_publish(exchange='logs', routing_key=debug, body=jsonpickle.dumps({'Error': e}))
        channel.basic_publish(exchange='logs', routing_key=info, body=jsonpickle.dumps({'/match status': 'Failed'}))
    
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/', methods=['GET'])
def hello():
    return '<h1> Lab-7 FACE RECOGNITION</h1><p> Use a valid method </p>'


# start flask app
app.run(host="0.0.0.0", port=5000)