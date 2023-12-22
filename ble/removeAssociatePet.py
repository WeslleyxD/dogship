import json
import boto3
import logging
from os import environ
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


    params = {
        "TableName": environ["BLETagsTable"],
        "Key":{"tagMac": {"S": event['pathParameters']['tagMac']}},
        "ConditionExpression": "attribute_exists(petId)",
        "UpdateExpression": f"REMOVE petId",
        "ReturnValues": "NONE"
    }

    try:
        response = ddb.update_item(**params)

        return {
            "statusCode": 200,
            "body": json.dumps("tagMac associated with the pet successfully removed"),
        }

    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": str(e),
            }),
        }