##
## You provide this to build your docker image
##

docker build -t gcr.io/datacenter-292201/worker -f /home/nike9852/lab-7-facerec-kube-nivethakesavan2203/worker/Dockerfile-worker .

docker push gcr.io/datacenter-292201/worker:latest

kubectl apply -f worker-deployment.yaml