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
        "TableName": environ["TagHistoryTable"],
    }
    items = []

    if event["queryStringParameters"]:
        if "petId" in event["queryStringParameters"] and "startDate" in event["queryStringParameters"] and "endDate" in event["queryStringParameters"]:
            params.update({"IndexName": "petId"})
            params.update({"KeyConditionExpression": "#N1 = :V1 AND #N2 BETWEEN :V2 AND :V3"})
            params.update({"ExpressionAttributeNames": {"#N1": "petId", "#N2": "createdAt"}})
            params.update({"ExpressionAttributeValues": {":V1": {"S": event["queryStringParameters"]["petId"]}, 
                                                        ":V2": {"S": event["queryStringParameters"]["startDate"]},
                                                        ":V3": {"S": event["queryStringParameters"]["endDate"]},
                                                        }})
            try:
                resp = ddb.query(**params)
                items.extend(resp.get("Items", []))

                while "LastEvaluatedKey" in resp:
                    params.update({"ExclusiveStartKey": resp["LastEvaluatedKey"]})
                    resp = ddb.query(**params)
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


        if "petId" in event["queryStringParameters"] and "startDate" not in event["queryStringParameters"] and "endDate" not in event["queryStringParameters"]:
            params.update({"IndexName": "petId"})
            params.update({"KeyConditionExpression": "#N1 = :V1"})
            params.update({"ExpressionAttributeNames": {"#N1": "petId"}})
            params.update({"ExpressionAttributeValues": {":V1": {"S": event["queryStringParameters"]["petId"]}}})

            try:
                resp = ddb.query(**params)
                items.extend(resp.get("Items", []))

                while "LastEvaluatedKey" in resp:
                    params.update({"ExclusiveStartKey": resp["LastEvaluatedKey"]})
                    resp = ddb.query(**params)
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

        if "petId" not in event["queryStringParameters"] and "startDate" in event["queryStringParameters"] and "endDate" in event["queryStringParameters"]:
            params.update({"FilterExpression": "#N1 BETWEEN :V1 AND :V2"})
            params.update({"ExpressionAttributeNames": {"#N1": "createdAt"}})
            params.update({"ExpressionAttributeValues": {":V1": {"S": event["queryStringParameters"]["startDate"]}, ":V2": {"S": event["queryStringParameters"]["endDate"]}}})

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
        
    else:
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