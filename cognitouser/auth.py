import json
import boto3
import logging
from os import environ

# import requests

logger = logging.getLogger()
session = boto3.Session()
idp = session.client('cognito-idp')


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
    username = body.get("Username")
    password = body.get("Password")

    if not username or not password:
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": "Username or Password in body not found",
            }),
        }
        
    try:
        resp = idp.initiate_auth(
            ClientId=environ["ClientId"],
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps(resp["AuthenticationResult"]),
        }

    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
               "error": str(e),
            }),
        }