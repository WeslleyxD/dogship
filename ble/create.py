import json
import boto3
import logging
from os import environ
from uuid import uuid4
from boto3.dynamodb.types import TypeSerializer

# import requests

logger = logging.getLogger()
session = boto3.Session()
ddb = session.client("dynamodb")


def lambda_handler(event, context):
    logger.info(event)

    if event["httpMethod"].upper() not in ("POST", ):
        return {
            "statusCode": 400,
            "body": json.dumps({
               "error": "method invalid",
            }),
        } 

    body = json.loads(event["body"]) if "body" in event and event.get("body") else None

    if not body:
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": "body not found",
            }),
    }

    body.update({"petId": str(uuid4())})
    try:
        params = {
            "TableName": environ["BLETagsTable"],
            "ConditionExpression": "attribute_not_exists(tagMac)",
            "Item": {k: TypeSerializer().serialize(str(v)) if isinstance(v, float) else TypeSerializer().serialize(v) for k, v in body.items()}
        }

        # Criando um novo item na tabela
        response = ddb.put_item(**params)

        return {
            "statusCode": 200,
            "body": json.dumps("bletag created successfully"),
        }

    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": str(e),
            }),
        }