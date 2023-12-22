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
    

    body = json.loads(event["body"]) if "body" in event and event.get("body") else None

    if not body:
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": "body not found",
            }),
    }

    if "tagMac" not in body or "petId" not in body:
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": "tagMac or petId not in body",
            }),
    }

    expression_attribute_names = {f"#attr_petId": "petId"}
    expression_attribute_values = {f":val_petId": {"S": body["petId"]}}
    update_expression_parts = [f"{name} = {value}" for name, value in zip(expression_attribute_names, expression_attribute_values)]
    
    update_expression = "SET " + ", ".join(update_expression_parts)

    params = {
        "TableName": environ["BLETagsTable"],
        "Key":{"tagMac": {"S": body["tagMac"]}},
        "ConditionExpression": "attribute_exists(tagMac)",
        "UpdateExpression": update_expression,
        "ExpressionAttributeNames": expression_attribute_names,
        "ExpressionAttributeValues": expression_attribute_values,
        "ReturnValues": "NONE"
    }

    try:
        response = ddb.update_item(**params)

        return {
            "statusCode": 200,
            "body": json.dumps("bletag associated with pet successfully"),
        }

    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": str(e),
            }),
        }