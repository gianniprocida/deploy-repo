import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError


logger = logging.getLogger()

load_dotenv(verbose=True)


app = FastAPI()

# BOOTSTRAP_SERVERS=os.environ["BOOTSTRAP_SERVERS"].split(",")
# security_protocol = 'SASL_SSL'
# sasl_plain_username='user1'
# sasl_plain_password=''
# sasl_mechanism="SCRAM-SHA-256"
#api_version=(0, 10, 2),
@app.on_event('startup')
async def startup_event():
    print(os.environ["BOOTSTRAP_SERVERS"])
    client = KafkaAdminClient(bootstrap_servers=os.environ["BOOTSTRAP_SERVERS"],security_protocol='SASL_PLAINTEXT', 
                              sasl_plain_username='user1',sasl_plain_password='xqXGqU7vq8',sasl_mechanism='SCRAM-SHA-256')
    topic = NewTopic(name=os.environ["TOPIC_NAME"],num_partitions=int(os.environ["PARTITIONS"]),
                     replication_factor=int(os.environ["REPLICAS"]))
    try:
        client.create_topics([topic])
    except TopicAlreadyExistsError as e:
        logger.warning("Topic already exist")
    finally:
        client.close()

