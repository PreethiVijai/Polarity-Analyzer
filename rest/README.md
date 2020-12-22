# REST API and interface

You must create a deployment that creates an external endpoint using a load balancer or ingress node. This deployment external endpoint in your cluster.

You must provide a `rest-server.py` that implements a Flask server that responds to the routes below. We have provided a `rest-client.py` that can send images to the `rest-server.py`.

The REST service takes in named images or URL's for images and sends those to the worker nodes for processing. Because it may take some time to process an image, the REST service returns a hash that can be used for further queries to see if the image contains faces and the names or URL's of matching images. You do not need to store the actual images. You can assume that URL's are unique that that once one has been processed, you don't need to process it again. You can't make the same assumption for filenames. However, you can assume that the hash of an image can be used to uniquely identify the image.

The REST routes are:

+ /scan/image/[filename] [POST] - scan the picture passed as the content of the request and with the specified filename. Compute [a hash of the contents](https://docs.python.org/3/library/hashlib.html) and send the hash and image to a worker using the `toWorker` rabbitmq exchange. The work will add the filename to the Redis database as described in the worker documentation. The response of this API should be a JSON document containing a single field `hash` that is the hash used to identify the provided image for subsequent `match` queries. For example:
```
  { 'hash' : "abcedef...128" }
```
+ /scan/url [POST] - the request body should contain a json message with a URL specifying an image. The format of the json object should be `{ "url" : "http://whatever.jpg"}`. The REST server [should retrieve the image](https://www.tutorialspoint.com/downloading-files-from-web-using-python) and proceed as for `/scan/image` but use the URL as the file name. We assume that URL's are unique, so if you've already processed it once, you don't need to do it again.
+ /match/[hash] [GET] -- using the hash, return a list of the image name or URL's that contain matching faces. If the hash doesn't match or there are no faces in the image, an empty list is returned.

##
## Rabbit MQ timeout
##
RabbitMQ has a [time out mechanism](https://stackoverflow.com/questions/36123006/rabbitmq-closes-connection-when-processing-long-running-tasks-and-timeout-settin) used to monitor connections;
if your REST server isn't receiving requests, it will eventually time out and
by default, the connection will drop and your program will get an exception at that time
which will kill your web server. You'll see your pods in an endless crashloop. 
To prevent this, you should open connections AFTER you receive your REST queries, for each rest query, and then close the channel when you're finished with that request.


### Development Steps
You will need two RabbitMQ exchanges.
+ A `topic` exchange called `logs` used for debugging and logging output
+ A `direct` exchange called `toWorker` used by the REST API to send images to the worker

You should use the topic exchange for debug messages with the topics `[hostname].rest.debug` and `[hostname].rest.info`, substituting the proper hostname. You can include whatever debugging information you want, but you must include a message for each attempted API call and the outcome of that call (successful, etc).

You may find it useful to create a `logs` container and deployment that listen to the logs and dumps them out to `stderr` so you can examine them using `kubectl logs..`.

When installing the `pika` library used to communicate with `rabbitmq`, you should use the `pip` or `pip3` command to install the packages in your container. The solution code uses the following packages:
```
sudo pip3 install --upgrade pika redis jsonpickle requests flask
```
## Accessing Your Service From The Internet

Once you've developed your service, you should deploy it on Google
Container Engine (GKE). The steps to create a "ingress" on GKE are slightly different than the steps for the stand-alone Kubernetes development environment [discussed in the Kubernetes tutorial](https://github.com/cu-csci-4253-datacenter/kubernetes-tutorial/tree/master/05-guestbook). In that example, you [install an ingress extension based on nginx](https://kubernetes.github.io/ingress-nginx/deploy/#docker-for-mac) and then configure the ingress to forward from the host IP address to the specific service you want to access.

For GKE, you [need to use a "load balancer" as the ingress as described in this tutorial](https://cloud.google.com/kubernetes-engine/docs/how-to/load-balance-ingress#gcloud). In general, Google's load balancer can accept connections across multiple datacenters and direct them to your Kubernetes cluster. You first need to enable the load balancer functionality (assuming your cluster is named `mykube`) using:
```
gcloud container clusters update mykube --update-addons=HttpLoadBalancing=ENABLED
```

You can then use [create an ingress that directs web connections to your rest-service using the example from the tutorial](https://cloud.google.com/kubernetes-engine/docs/how-to/load-balance-ingress#creating_an_ingress). 

The GKE load balancer [needs your service to use a specific kind of service called a `NodePort`](https://cloud.google.com/kubernetes-engine/docs/how-to/load-balance-ingress#creating_a_service). You can add that to your service spec by putting
```
spec:
  type: NodePort
```
in the service YAML file and restarting your service.

In addition, the GKE load balancer checks for the "health" of your service -- this means that you need to respond to requests to `/` with a positive response. I added the following route:
```
@app.route('/', methods=['GET'])
def hello():
    return '<h1> Face Rec Server</h1><p> Use a valid endpoint </p>'
```

Once you've created the ingress, you can find the IP address using *e.g.*
```
kubectl get ingress rest-ingress --output yaml
```
and then access the endpoint using the IP address at the end of the output. It should look like:
```
....
status:
  loadBalancer:
    ingress:
    - ip: 34.120.45.70
```
You can check if things are working by sending requests and looking at the output of your `logs` pod or the response you get.

If you have trouble getting your service to work, use
```
kubectl describe ingress rest-ingress
```
and you'll see error messages and diagnostics like this:
```
> kubectl describe ingress rest-ingress
Name:             rest-ingress
Namespace:        default
Address:          34.120.45.70
Default backend:  default-http-backend:80 (10.0.0.9:8080)
Rules:
  Host        Path  Backends
  ----        ----  --------
  *           
              /hello   hello-world:60000 (10.0.0.10:50000,10.0.1.7:50000,10.0.2.7:50000)
              /*       rest-service:5000 (10.0.2.15:5000)
Annotations:  ingress.kubernetes.io/backends:
                {"k8s-be-30496--28fa4eee16792bba":"HEALTHY","k8s-be-30815--28fa4eee16792bba":"HEALTHY","k8s-be-30914--28fa4eee16792bba":"HEALTHY"}
              ingress.kubernetes.io/forwarding-rule: k8s2-fr-pxfi3hd8-default-rest-ingress-zo9uwq5a
              ingress.kubernetes.io/target-proxy: k8s2-tp-pxfi3hd8-default-rest-ingress-zo9uwq5a
              ingress.kubernetes.io/url-map: k8s2-um-pxfi3hd8-default-rest-ingress-zo9uwq5a
              kubernetes.io/ingress.class: gce
Events:
  Type    Reason  Age   From                     Message
  ----    ------  ----  ----                     -------
  Normal  ADD     46m   loadbalancer-controller  default/rest-ingress
  Normal  CREATE  45m   loadbalancer-controller  ip: 34.120.45.70
```
It can take a while for the status of the connections to switch from "Unknown" to "HEALTHY". If that isn't happening, check that you've added the `/` route to your Flask server and try connecting to the IP address.

If you can't get this to work, just use your local Kubernetes setup during your grading interview.