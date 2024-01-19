import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
from kafka.producer import KafkaProducer
from typing import List
from entity import Company
from command import Command

logger = logging.getLogger()

load_dotenv(verbose=True)


app = FastAPI()

my_list = [
    {
        "id": "1",
        "shared_values": "Teamwork",
        "city": "Utrecht",
        "product": "axual-platform",
    },
    {
        "id": "2",
        "shared_values": "Innovation",
        "city": "Amsterdam",
        "product": "green-energy-solution",
    },
    {
        "id": "3",
        "shared_values": "Innovation",
        "city": "Amsterdam",
        "product": "tech-gadgets",
    },
    {
        "id": "4",
        "shared_values": "Diversity",
        "city": "Amsterdam",
        "product": "software-solution",
    },
    {
        "id": "5",
        "shared_values": "Excellence",
        "city": "Berlin",
        "product": "software-solution",
    },
]


@app.on_event("startup")
async def startup_event():
    logger.warning(os.environ["BOOTSTRAP_SERVERS"])
    logger.warning(os.environ["user"])
    logger.warning(os.environ["password"])
    client = KafkaAdminClient(
        bootstrap_servers=os.environ["BOOTSTRAP_SERVERS"],
        api_version=(0, 10, 2),
        security_protocol="SASL_PLAINTEXT",
        sasl_plain_username=os.environ["user"],
        sasl_plain_password=os.environ["password"],
        sasl_mechanism="SCRAM-SHA-256",
    )
    topic = NewTopic(
        name=os.environ["TOPIC_NAME"],
        num_partitions=int(os.environ["PARTITIONS"]),
        replication_factor=int(os.environ["REPLICAS"]),
    )
    
    try:
        client.create_topics([topic])
    except TopicAlreadyExistsError as e:
        logger.warning("Topic already exist")
    finally:
        client.close()


def make_producer():
    producer = KafkaProducer(
        bootstrap_servers=os.environ["BOOTSTRAP_SERVERS"],
        api_version=(0, 10, 2),
        security_protocol="SASL_PLAINTEXT",
        sasl_plain_username=os.environ["user"],
        sasl_plain_password=os.environ["password"],
        sasl_mechanism="SCRAM-SHA-256",
    )
    return producer


@app.post("/api/producer", status_code=201, response_model=List[Company])
async def create_company():
    companies = []

    producer = make_producer()

    for i in my_list:
        company = Company(
            id=i["id"],
            shared_values=i["shared_values"],
            city=i["city"],
            product=i["product"],
        )

        companies.append(company)
        producer.send(
            topic=os.environ["TOPIC_NAME"],
            key=company.product.encode("utf-8"),
            value=company.json().encode("utf-8"),
        )

    producer.flush()

    return
