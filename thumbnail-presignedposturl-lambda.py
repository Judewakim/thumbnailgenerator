import json
import boto3
import mimetypes
from datetime import datetime
import re

s3 = boto3.client('s3')
UPLOAD_BUCKET = 'something-uploads-related'

def sanitize_text(text):
    # Keep alphanumeric, dashes, underscores; replace spaces with hyphens
    return re.sub(r'[^a-zA-Z0-9_-]', '', text.replace(' ', '-'))

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        user_filename = body.get('filename')  # Optional override
        text = body.get('text', 'thumbnail')
        requested_type = body.get('filetype', '').lower()

        # Sanitize for safe filenames
        safe_text = sanitize_text(text) or "thumbnail"
        today = datetime.utcnow().strftime("%Y-%m-%d")

        # Default to JPEG
        file_ext = "jpg"
        content_type = "image/jpeg"

        # Priority 1: Use full filename if given and extract its type
        if user_filename:
            guessed_type, _ = mimetypes.guess_type(user_filename)
            if guessed_type in ['image/jpeg', 'image/png']:
                content_type = guessed_type
                file_ext = 'png' if guessed_type == 'image/png' else 'jpg'
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Only JPG and PNG files are allowed'})
                }

        # Priority 2: If no filename, use filetype field
        elif requested_type in ['jpg', 'jpeg', 'png']:
            file_ext = 'png' if requested_type == 'png' else 'jpg'
            content_type = 'image/png' if file_ext == 'png' else 'image/jpeg'

        # Fallback: default to .jpg if all else fails

        # Construct final filename
        filename = f"{today}-{safe_text}.{file_ext}"

        presigned_url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': UPLOAD_BUCKET,
                'Key': filename,
                'Metadata': {
                    'text': text,
                    'filetype': file_ext
                },
                'ContentType': content_type
            },
            ExpiresIn=300
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': 'http://thumbnail-webpage.s3-website-us-east-1.amazonaws.com', 
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'url': presigned_url,
                'filename': filename
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': 'http://thumbnail-webpage.s3-website-us-east-1.amazonaws.com',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'error': str(e)})
        }
import json
import boto3
import mimetypes
from datetime import datetime
import re

s3 = boto3.client('s3')
UPLOAD_BUCKET = 'something-uploads-related'

def sanitize_text(text):
    # Keep alphanumeric, dashes, underscores; replace spaces with hyphens
    return re.sub(r'[^a-zA-Z0-9_-]', '', text.replace(' ', '-'))

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        user_filename = body.get('filename')  # Optional override
        text = body.get('text', 'thumbnail')
        requested_type = body.get('filetype', '').lower()

        # Sanitize for safe filenames
        safe_text = sanitize_text(text) or "thumbnail"
        today = datetime.utcnow().strftime("%Y-%m-%d")

        # Default to JPEG
        file_ext = "jpg"
        content_type = "image/jpeg"

        # Priority 1: Use full filename if given and extract its type
        if user_filename:
            guessed_type, _ = mimetypes.guess_type(user_filename)
            if guessed_type in ['image/jpeg', 'image/png']:
                content_type = guessed_type
                file_ext = 'png' if guessed_type == 'image/png' else 'jpg'
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Only JPG and PNG files are allowed'})
                }

        # Priority 2: If no filename, use filetype field
        elif requested_type in ['jpg', 'jpeg', 'png']:
            file_ext = 'png' if requested_type == 'png' else 'jpg'
            content_type = 'image/png' if file_ext == 'png' else 'image/jpeg'

        # Fallback: default to .jpg if all else fails

        # Construct final filename
        filename = f"{today}-{safe_text}.{file_ext}"

        presigned_url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': UPLOAD_BUCKET,
                'Key': filename,
                'Metadata': {
                    'text': text,
                    'filetype': file_ext
                },
                'ContentType': content_type
            },
            ExpiresIn=300
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': 'http://thumbnail-webpage.s3-website-us-east-1.amazonaws.com', 
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'url': presigned_url,
                'filename': filename
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': 'http://thumbnail-webpage.s3-website-us-east-1.amazonaws.com',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'error': str(e)})
        }
