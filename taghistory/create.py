import json
import boto3
import logging
from os import environ
from datetime import datetime
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

    if "operation" in body and body["operation"].lower() not in ("associate", "disassociate", ):
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": "operation invalid (associate, disassociate)",
            }),
        }

    dt_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    body.update({"createdAt": dt_now})
    body.update({"updatedAt": dt_now})

    try:
        params = {
            "TableName": environ["TagHistoryTable"],
            "ConditionExpression": "attribute_not_exists(tagMac)",
            "Item": {k: TypeSerializer().serialize(str(v)) if isinstance(v, float) else TypeSerializer().serialize(v) for k, v in body.items()}
        }

        # Criando um novo item na tabela
        response = ddb.put_item(**params)

        return {
            "statusCode": 200,
            "body": json.dumps("taghistory created successfully"),
        }

    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": str(e),
            }),
        }