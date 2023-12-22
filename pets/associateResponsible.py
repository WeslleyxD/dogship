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

    expression_attribute_names = {f"#attr_responsibleId": "responsibleId"}
    expression_attribute_values = {f":val_responsibleId": {"S": (event['pathParameters']['responsibleId'])}}
    update_expression_parts = [f"{name} = {value}" for name, value in zip(expression_attribute_names, expression_attribute_values)]
    
    update_expression = "SET " + ", ".join(update_expression_parts)

    params = {
        "TableName": environ["PetsTable"],
        "Key":{"petId": {"S": event['pathParameters']['petId']}},
        "ConditionExpression": "attribute_exists(petId)",
        "UpdateExpression": update_expression,
        "ExpressionAttributeNames": expression_attribute_names,
        "ExpressionAttributeValues": expression_attribute_values,
        "ReturnValues": "NONE"
    }

    try:
        response = ddb.update_item(**params)

        return {
            "statusCode": 200,
            "body": json.dumps("pet associated with responsible successfully"),
        }

    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": str(e),
            }),
        }