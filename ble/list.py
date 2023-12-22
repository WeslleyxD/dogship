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
    print (event)

    if event["queryStringParameters"] and event["queryStringParameters"].get("status", "").lower() not in ("all", "associated", "not_associated", ):
        return {
            "statusCode": 400,
            "body": json.dumps({
               "error": "query parameter status invalid (all, associated, not_associated)",
            }),
        }

    if event["httpMethod"].upper() not in ("GET", ):
        return {
            "statusCode": 400,
            "body": json.dumps({
               "error": "method invalid",
            }),
        } 

    params = {
        "TableName": environ["BLETagsTable"],
    }

    if event["queryStringParameters"]:
        match event["queryStringParameters"].get("status", "").lower():
            case "associated":
                params.update({"FilterExpression": "attribute_exists(petId)"})
            case "not_associated":
                params.update({"FilterExpression": "attribute_not_exists(petId)"})

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