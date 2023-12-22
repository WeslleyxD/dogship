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

    if event["httpMethod"].upper() not in ("PUT", ):
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

    expression_attribute_names = {}
    expression_attribute_values = {}

    update_expression_parts = []
    for attribute_name, attribute_value in body.items():
        # Serializar o valor usando TypeSerializer
        serialized_value = TypeSerializer().serialize(attribute_value)

        # Construir nomes de atributos para expressões
        attribute_name_placeholder = f'#attr_{attribute_name}'
        expression_attribute_names[attribute_name_placeholder] = attribute_name

        # Construir valores de atributos para expressões
        attribute_value_placeholder = f':val_{attribute_name}'
        expression_attribute_values[attribute_value_placeholder] = serialized_value

        update_expression_parts.append(f"{attribute_name_placeholder} = {attribute_value_placeholder}")

    update_expression = "SET " + ", ".join(update_expression_parts)

    params = {
        "TableName": environ["BLETagsTable"],
        "Key":{"tagMac": {"S": event['pathParameters']['tagMac']}},
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
            "body": json.dumps("bletag updated successfully"),
        }

    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": str(e),
            }),
        }