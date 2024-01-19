# Deployment repository 

 All manifests files within the ./deploy directory in this repository will be applied to the namespace specified by targetNamespace in the cluster. The Git repository contains the main directory and its associated subdirectories:

                                      
```
- deploy
   - api-client-pod.yaml
   - kafka-settings.yaml
```


Due to the application's authentication requirement using a password, simultaneous deployment of the Python Web Server application with the cluster is not feasible. To address this, we will follow a two-step deployment process: 


* Ensure accessibility of the cluster both externally and internally
* Push the file to the Git repository, allowing FluxCD to detect and apply the changes.

To connect a client to your Kafka, you need to create the 'client.properties' configuration files with the content below:

```
security.protocol=SASL_PLAINTEXT
sasl.mechanism=SCRAM-SHA-256
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
    username="user1" \
    password="$(kubectl get secret kafka-user-passwords --namespace kafka-2 -o jsonpath='{.data.client-passwords}' | base64 -d | cut -d , -f 1)";
```

We will be using the configuration to test connectivity both externally and internally.

## Testing External Connectivity



To test if the kafka brokers are correctly exposed externally through a NodePort, 
you can use the Kafka command-line scripts. Make sure that you have the the kafka scripts installed locally.

PRODUCER:
```
kafka-console-producer.sh \
--producer.config client.properties \
--broker-list localhost:30120,localhost:30121,localhost:30122 \
--topic mytest
```
CONSUMER:
```
kafka-console-consumer.sh \
--consumer.config client.properties \
--bootstrap-server localhost:30120 \
--topic mytest \
--from-beginning      
```


```
kafka-topics.sh \          
--command-config client.properties \                                                    
--bootstrap-server localhost:30120 \
--create --topic another-test
```

If all tests have passed successfully, we can proceed to internally test our cluster.


## Testing Internal Connectivity

Follow the following steps:


* Deploy a Kafka client pod within the same namespace as the Bitnami Kafka cluster:

```
kubectl run kafka-client --restart='Never' --image docker.io/bitnami/kafka:3.6.0-debian-11-r1 --namespace kafka-2 --command -- sleep infinity
```

* Copy the client.properties file to the created pod 

```
kubectl cp --namespace kafka-2 client.properties kafka-client:/tmp/client.properties
``` 

* Access the pod interactively:

```
kubectl exec --tty -i kafka-client --namespace kafka-2 -- bash
```

Execute the following commands within the pod

PRODUCER:
```
kafka-console-producer.sh \
--producer.config /tmp/client.properties \
--broker-list my-release-kafka-controller-0.my-release-kafka-controller-headless.kafka-2.svc.cluster.local:9092,my-release-kafka-controller-1.my-release-kafka-controller-headless.kafka-2.svc.cluster.local:9092 my-release-kafka-controller-2.my-release-kafka-controller-headless.kafka-2.svc.cluster.local:9092:9092 \
--topic new-test
```

CONSUMER:
```
kafka-console-consumer.sh \
--consumer.config /tmp/client.properties \
--bootstrap-server my-release-kafka-controller-0.my-release-kafka-controller-headless.kafka-2.svc.cluster.local:9092 \
--topic new-test \
--from-beginning
```

Keep in mind that each Kafka broker can be accessed via port 9092 on the following DNS name from within your cluster:

*  my-release-kafka-controller-0.my-release-kafka-controller-headless.kafka-2.svc.cluster.local:9092
*  my-release-kafka-controller-1.my-release-kafka-controller-headless.kafka-2.svc.cluster.local:9092
*  my-release-kafka-controller-2.my-release-kafka-controller-headless.kafka-2.svc.cluster.local:9092

If all tests have passed successfully, we can proceed to deploy our producer.

## Deployment of the Python Web Server application

Go to the `src` folder:
```
cd src

docker build -f Dockerfile-http -t py-httpie .

docker build -f Dockerfile -t py-webserver .

```

By following this method, both images will be stored locally and automatically fetched by Kubernetes (that's what `imagePullPolicy: Never` is for). If the api-client-pod crashes due to an unavailable image, simply restart the pod.

To enable application authentication with the Kafka cluster, it is necessary to generate a secret. The application will utilize the username and password specified in the secret for cluster authentication. There is no requirement to specify the authentication type, as it is already predefined in the code (refer to the 'src' directory for details).

```
kubectl create secret generic kafka-cred --from-literal=user=user1 --from-literal=password=<password-defined-in-client.properties> -n kafka-2 
```

Now create a pod.yaml file using the content below:

```
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: py-webserver
  name: py-webserver
  namespace: default
spec:
  containers:
  - image: py-webserver
    name: py-webserver
    imagePullPolicy: Never
    envFrom:
      - configMapRef:
          name: kafka-settings
      - secretRef:
          name: kafka-cred
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
```

Commit the file to the Git repository and monitor the pod's status until it is successfully running.

## Message Production and Consumption Workflow for a Topic 

You can verify the creation of the topic by executing the following command within the created client pod:

```
kafka-topics.sh --command-config /tmp/client.properties \
--bootstrap-server my-release-kafka-controller-0.my-release-kafka-controller-headless.kafka-2.svc.cluster.local:9092 \
--describe --topic new-topic
```
The topic new-topic is defined in the kafka-settings configmap.


Next, open a terminal and run the following command to consume messages from the new-test topic:

```
kafka-console-consumer.sh \
--consumer.config /tmp/client.properties \
--bootstrap-server my-release-kafka-controller-0.my-release-kafka-controller-headless.kafka-2.svc.cluster.local:9092 \
--topic new-test \
--from-beginning
```

Now, execute the api-client-pod and run:

```
http POST 10.1.26.187:8088/api/producer
```

Here's a breakdown of the command:

* http: The command-line HTTP client for sending HTTP requests.
* POST: Specifies the HTTP method, indicating data is being sent to the server.
* 10.1.26.187:8088/api/producer: The URL or endpoint for the POST request, denoting http://10.1.26.187:8088/api/producer. Here, 10.1.26.187 represents the pod's IP, 8088 is the web server port, and /api/producer is the specific endpoint.

Executing this command triggers the production of messages in accordance with the configurations specified in the endpoint. Subsequently, the earlier established consumer will process and consume these generated messages.

