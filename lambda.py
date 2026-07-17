import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("movies")

VALID_MOVIES = [
    "chhava",
    "pushpa2",
    "cocktail2",
    "jawan",
    "krishnavataram",
    "alpha",
    "spiderman"
]

def lambda_handler(event, context):

    method = event["requestContext"]["http"]["method"]

    # ==========================
    # GET /seats
    # ==========================
    if method == "GET":

        movie = "chhava"

        if event.get("queryStringParameters"):
            movie = event["queryStringParameters"].get("movieId", "chhava").lower()

        if movie not in VALID_MOVIES:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "message": "Invalid Movie"
                })
            }

        response = table.query(
            KeyConditionExpression=Key("movieId").eq(movie)
        )

        seats = [item["seatId"] for item in response.get("Items", [])]

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(seats)
        }

    # ==========================
    # POST /book
    # ==========================
    elif method == "POST":

        body = json.loads(event["body"])

        movie = body["movieId"].lower()
        seat = body["seatId"]
        name = body["name"]
        email = body["email"]

        if movie not in VALID_MOVIES:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "message": "Invalid Movie"
                })
            }

        response = table.get_item(
            Key={
                "movieId": movie,
                "seatId": seat
            }
        )

        if "Item" in response:

            return {
                "statusCode": 409,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "message": "Seat Already Booked"
                })
            }

        table.put_item(
            Item={
                "movieId": movie,
                "seatId": seat,
                "name": name,
                "email": email,
                "status": "Booked",
                "bookingTime": datetime.now().isoformat()
            }
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "Booking Successful"
            })
        }

    return {
        "statusCode": 400,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "message": "Invalid Request"
        })
    }