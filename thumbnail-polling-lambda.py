import json
import boto3
import os

s3 = boto3.client('s3')

PROCESSED_BUCKET = 'something-processed-related' 

def lambda_handler(event, context):
    try:
        # If REST API: filename is in queryStringParameters
        # If HTTP API: filename may be in event['queryStringParameters']
        params = event.get("queryStringParameters") or event.get("querystring") or {}
        filename = params.get("filename")
        if not filename:
            return {
                'statusCode': 400,
                'body': json.dumps("Missing filename parameter.")
            }

        processed_key = f"processed-{filename}"
        
        # Try to get object metadata to confirm it exists
        s3.head_object(Bucket=PROCESSED_BUCKET, Key=processed_key)

        # If it exists, generate presigned URL
        url = s3.generate_presigned_url('get_object', Params={
            'Bucket': PROCESSED_BUCKET,
            'Key': processed_key
        }, ExpiresIn=3600)

        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},  # CORS
            'body': json.dumps({'downloadUrl': url})
        }

    except s3.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return {
                'statusCode': 404,
                'headers': {'Access-Control-Allow-Origin': '*'},  # CORS
                'body': json.dumps("Thumbnail not ready yet.")
            }
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},  # CORS
            'body': json.dumps("Error checking file.")
        }
