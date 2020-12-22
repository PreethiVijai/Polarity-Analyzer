# facerec Worker

The steps you need to take:

+ Develop a Python program that listens to the `toWorkers` RabbitMQ exchange, receives a message and scans for a face.
+ Create a Docker image that can execute the face recognition software, run RabbitMQ clients and has access to a remote Redis database


## Creating a worker image
The worker will use the [face recognition software](https://github.com/ageitgey/face_recognition) software. This is an open-source face recognition library based on `dlib`. The software we're using [comes with a sample Dockerfile](https://github.com/ageitgey/face_recognition/blob/master/Dockerfile) and I have [provided a pre-built Docker image](https://hub.docker.com/repository/docker/dirkcgrunwald/facerec) based on that Dockerfile. The resulting Docker image is 1.9GB -- if you have a slow network connection, you can build this yourself, but it takes a while to do that.

Recall that you can extend a Docker image using `FROM`, then adding additional files and over-riding the `CMD` or `RUN` commands. That means you do **not** need to build the original Docker container yourself and when you "push" your image to Docker hub, you should have to upload very little data.

## Program to process images

You will need two RabbitMQ exchanges.
+ A `topic` exchange called `logs` used for debugging and logging output
+ A `direct` exchange called `toWorker` used by the REST API to send images to the worker

You can use whatever method you like to get data from the REST API to the worker. For example, you could create a Python datatype including the image, then [`pickle` the image](https://stackoverflow.com/questions/30469575/how-to-pickle-and-unpickle-to-portable-string-in-python-3) and send it via RabbitMQ. Or, you could store the image in Google object storage and send a smaller message.

Images sent by the REST front-end have an associated hash value that is used to identify the image and a name (either file name or URL). For each image (hash) we will use a Redis database that maps the hash to a set of hashes that have matching faces. Redis is a Key-Value store. Redis supports a [number of datatypes including lists and sets](https://redis.io/topics/data-types); you can read more about [the Python interface](https://github.com/andymccurdy/redis-py).  In many cases, the set data type will be the most appropriate because we only want a single instance of a data item associated with a key (*.e.g*, the hashes of all images that match faces in this image).

The worker should extract the list of faces in the image using `face_recognition.face_encodings` (see below). Then, for each face in that list, you should add the face and corresponding image to the Redis database and then *compare those faces to all other faces in each image the database*. For each image containing any matching face, you would add the images (hashes) of each image to the other such that eventually we can determine the set of images that contain matching faces. Once this process is completed, you acknowledge the message.

Because Redis is a simple key-value store, we need to construct the following databases:
1. $ name \rightarrow imghash $ - Hash from image name
1. $ imghash \rightarrow \{  name \} $ - Set of origin name or url of image
1. $ imghash \rightarrow [ facrec ] $ - List or set of face recognition data for an image
1. $ imghash \rightarrow \{ imghash \} $ - Set of images containing matching faces

If an image hash has already been added, it doesn't need to be scanned again, but you should add the name to the set of origin names/urls for that image.

We will be using 4 Redis databases. Redis uses numbers for database names, and we'll be using 1, 2, 3 & 4. The '0' database is the default. You can declare the different databases using something like the following:
```
redisNameToHash = redis.Redis(host=redisHost, db=1)    # Key -> Value
redisHashToName = redis.Redis(host=redisHost, db=2)    # Key -> Set
redisHashToFaceRec = redis.Redis(host=redisHost, db=3) # Key -> Set
redisHashToHashSet = redis.Redis(host=redisHost, db=4) # Key -> Set
```

Once the database has been updated or you determine nothing needs to be done you should then `acknowledge` the RabbitMQ message. You should only acknowledge it after you've processed it.

## Recognizing Faces
The face recognition library also contains [a sample implementation of a web-service to compare images to a pre-analyzed picture of Barak Obama](https://github.com/ageitgey/face_recognition/blob/master/examples/web_service_example.py) that shows how to compare matching faces.

The important code is excerpted below:
```
    # Load the uploaded image file
    img = face_recognition.load_image_file(file_stream)
    # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(img)
    ...
    if len(unknown_face_encodings) > 0:
        face_found = True
        # See if the first face in the uploaded image matches the known face of Obama
        match_results = face_recognition.compare_faces([known_face_encoding], unknown_face_encodings[0])
        if match_results[0]:
            is_obama = True
```
This uses [the `face_recognition.face_encodings` function](https://face-recognition.readthedocs.io/en/latest/face_recognition.html) to retrieve a vector/list of characteristics concerning the image.

## Debugging Support

At each step of your processing, you should log debug information using the `topic` queue and `[hostname].worker.debug`. When you've added the data to the database, you *must* log that as `[hostname].worker.info`, substituting the proper worker name.

When installing the `pika` library used to communicate with `rabbitmq`, you should use the `pip` or `pip3` command to install the packages. The solution used the following Python packages
```
sudo pip3 install --upgrade pika redis jsonpickle requests
```

## Suggested Development Steps
You should get the hostname for Redis and RabbitMQ from environment variables that you can either set in the shell or override in your `worker-deployment.yaml`. We've provided template code for that.

Rather than immediately push everything to your Kubernetes cluster, you should first deploy Redis and Rabbitmq and the use the `kubectl port-forward` mechanism listed in the corresponding README.md files to expose those services on your local machine. We've provided a script `deploy-local-dev.sh` for that purpose.

You can then work on your server by running e.g. `docker run --rm -it -v $(pwd):/app dirkcgrunwald/facerec /bin/bash` and then trying your code in `/app` in the container rather than building and installing the face recognition software locally. You will need to set your `REDIS_HOST` and `RABBITMQ_HOST` variables to the IP address of you laptop so that the worker can connect to the appropriate ports. On MacOS, you use `ipconfig` to find this and on Windows/WSL2 or Linux you use `ip addr`. For example, on my Windows/WSL2 host, I determined the IP address using `ip addr show dev eth0` and then I set:
```
root@b484bccd251a:/app# export REDIS_HOST=172.26.159.126
root@b484bccd251a:/app# export RABBITMQ_HOST=172.26.159.126
root@b484bccd251a:/app# python3 worker-server.py
Connecting to rabbitmq(172.26.159.126) and redis(172.26.159.126)
 [*] Waiting for messages. To exit press CTRL+C
 ```
 
You should used the provide `log_info` and `log_debug` routines that write to the `logs` topic to simplify your development. You won't be able to figure out what is going on without logs. We've provided template code for that.

If you structure your code correctly, you should be able to test your server by loading input from the local directory or command line rather than waiting for RabbitMQ messages. You can then develop your REST server and client locally before you package things up in a Dockerfile and build images to deploy.

## Database consistency

Although Redis is basically a key-value store, it [still supports transactions within a particular database](https://fabioconcina.github.io/blog/transactions-in-redis-with-python/). You may want to use this to prevent inconsistencies within the database (i.e. your worker may abort after entering some information but before entering other from processing the face recognition). This can also be problematic if your REST front-end uses the database to avoid re-fetch URL's that it has already loaded -- you may have entered the URL name in `redisNameToHash` but not yet processed the image completely.