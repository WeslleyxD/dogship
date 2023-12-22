import json
import boto3
import logging
from os import environ
from boto3.dynamodb.types import TypeDeserializer

# import requests

logger = logging.getLogger()
session = boto3.Session()
ddb = session.client("dynamodb")


def lambda_handler(event, context):
    logger.info(event)

    if event["httpMethod"].upper() not in ("GET", ):
        return {
            "statusCode": 400,
            "body": json.dumps({
               "error": "method invalid",
            }),
        } 

    params = {
        "TableName": environ["ClientsTable"],
    }

    items = []
    try:
        resp = ddb.scan(**params)
        items.extend(resp.get("Items", []))

        while "LastEvaluatedKey" in resp:
            params.update({"ExclusiveStartKey": resp["LastEvaluatedKey"]})
            resp = ddb.scan(**params)
            items.extend(resp.get("Items", []))

        return {
            "statusCode": 200,
            "body": json.dumps([{k: TypeDeserializer().deserialize(v) for k, v in item.items()} for item in items], default=str),
        }

    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": str(e),
            }),
        }