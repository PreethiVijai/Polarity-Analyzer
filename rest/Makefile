##
## You provide this to build and push your docker images
##

docker build -t gcr.io/datacenter-292201/rest -f /home/nike9852/lab-7-facerec-kube-nivethakesavan2203/rest/Dockerfile-rest .
docker build -t gcr.io/datacenter-292201/logs -f /home/nike9852/lab-7-facerec-kube-nivethakesavan2203/rest/Dockerfile-logs .

docker push gcr.io/datacenter-292201/rest:latest
docker push gcr.io/datacenter-292201/logs:latest

kubectl apply -f rest-deployment.yaml
kubectl apply -f rest-service.yaml
kubectl apply -f rest-ingress.yaml
kubectl apply -f logs-deployment.yaml