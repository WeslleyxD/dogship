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

    if event["httpMethod"].upper() not in ("DELETE", ):
        return {
            "statusCode": 400,
            "body": json.dumps({
               "error": "method invalid",
            }),
        } 

    try:
        params = {
            "TableName": environ["BLETagsTable"],
            "ConditionExpression": "attribute_exists(tagMac)",
            "Key": {'tagMac': {'S': event['pathParameters']['tagMac']}}
        }

        # Criando um novo item na tabela
        response = ddb.delete_item(**params)

        return {
            "statusCode": 200,
            "body": json.dumps("bletag deleted successfully"),
        }

    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": str(e),
            }),
        }