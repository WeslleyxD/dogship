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
        "TableName": environ["SectorsTable"],
        "Key": {'id': {'S': event['pathParameters']['id']}}
    }

    try:
        resp = ddb.get_item(**params)

        return {
            "statusCode": 200,
            "body": json.dumps({k: TypeDeserializer().deserialize(v) for k, v in resp["Item"].items()}, default=str),
        }

    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": str(e),
            }),
        }