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
    print (event)

    if event["httpMethod"].upper() not in ("DELETE", ):
        return {
            "statusCode": 400,
            "body": json.dumps({
               "error": "method invalid",
            }),
        }

    params = {
        "TableName": environ["PetsTable"],
        "Key":{"petId": {"S": event['pathParameters']['petId']}},
        "ConditionExpression": "attribute_exists(petId)",
        "UpdateExpression": f"REMOVE responsibleId",
        "ReturnValues": "NONE"
    }

    try:
        response = ddb.update_item(**params)

        return {
            "statusCode": 200,
            "body": json.dumps("responsibleId associated with the pet successfully removed"),
        }

    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": str(e),
            }),
        }